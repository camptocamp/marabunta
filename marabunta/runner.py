# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import print_function

from datetime import datetime
from distutils.version import StrictVersion

from .database import IrModuleModule
from .exception import MigrationError
from .output import print_decorated

LOG_DECORATION = u'|> '


class Runner(object):

    def __init__(self, config, migration, cursor, table):
        self.config = config
        self.migration = migration
        self.cursor = cursor
        self.table = table

    def log(self, message):
        print_decorated('migration: {}'.format(message))

    def perform(self):
        self.table.create_if_not_exists()
        self.table.lock()  # locked until end of transaction

        db_versions = self.table.versions()

        # integrity checks
        if not self.config.force:

            unfinished = [not db_version.date_done for db_version
                          in db_versions]
            if unfinished:
                raise MigrationError(
                    'Upgrade of version {} has been attempted and failed. '
                    'You may want to restore the backup, run again the '
                    'migration with the MARABUNTA_FORCE environment variable '
                    'or fix it manually (in that case, you will have to '
                    'update the  \'marabunta_version\' table yourself.'
                    .format(','.join(v.number for v in unfinished))
                )

            unprocessed = [version for version in self.migration.versions
                           if not version.skip(db_versions)]
            if len(unprocessed) > 1:
                raise MigrationError(
                    'Only one version can be upgraded at a time.\n'
                    'The following versions need to be applied: {}.\n'.format(
                        [v.number for v in unprocessed]
                        )
                )

            installed = max(StrictVersion(v.number) for v in db_versions)
            if installed > StrictVersion(unprocessed.number):
                raise MigrationError(
                    'The version you are trying to install ({}) is below '
                    'the current database version.'.format(
                        unprocessed.number, installed
                    )
                )

        for version in self.migration.versions:
            # when we force-execute one version, we skip all the others
            if self.config.force_version:
                if self.config.force_version != version.number:
                    continue
                else:
                    self.log(
                        u'force-execute version {}'.format(version.number)
                    )

            self.log(u'processing version {}'.format(version.number))
            VersionRunner(self, version).perform()


class VersionRunner(object):

    def __init__(self, runner, version):
        self.runner = runner
        self.table = runner.table
        self.migration = runner.migration
        self.config = runner.config
        self.cursor = runner.cursor
        self.version = version
        self.logs = []

    def log(self, message, raw=False):
        if raw:
            print(message, end='')
        else:
            app_message = u'version {}: {}'.format(
                self.version.number,
                message,
            )
            print_decorated(app_message)
        self.logs.append(message.strip() if raw else message)

    def start(self):
        self.log('start')
        self.table.start_version(self.version.number, datetime.now())

    def finish(self):
        self.log('done')
        module_table = IrModuleModule(self.cursor)
        addons_state = module_table.read_state()
        self.table.finish_version(self.version.number, datetime.now(),
                                  '\n'.join(self.logs),
                                  [state._asdict() for state in addons_state])

    def perform(self):
        db_versions = self.table.versions()

        version = self.version
        if (version.is_processed(db_versions) and
                not self.config.force_version == self.version.number):
            self.log(
                u'version {} is already installed'.format(version.number)
            )
            return

        self.start()

        if version.is_noop():
            self.log(u'version {} is a noop'.format(version.number))

        else:
            self.log(u'execute pre-operations')
            for operation in version.pre_operations:
                operation.execute(self.log)

            self.perform_addons()

            self.log(u'execute post-operations')
            for operation in version.post_operations:
                operation.execute(self.log)

            if self.config.demo:
                self.log(u'execute demo-operations')
                for operation in version.demo_operations:
                    operation.execute(self.log)

        self.finish()

    def perform_addons(self):
        version = self.version

        module_table = IrModuleModule(self.cursor)
        addons_state = module_table.read_state()

        # TODO: when we force execution of all releases, then we should
        # exclude updated addons which have already been updated in a previous
        # release. (upgrade an addon only once per run)
        upgrade_operation = version.upgrade_addons_operation(addons_state)
        self.log(u'installation / upgrade of addons')
        upgrade_operation.execute(self.log)
