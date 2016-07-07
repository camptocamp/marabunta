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
        # we keep the addons upgrading during a run in this set,
        # this is only useful when using 'allow_serie',
        # if an addon has just been installed or updated,
        # we don't want to do it again for another version
        self.upgraded_addons = set()

    def log(self, message):
        print_decorated(u'migration: {}'.format(message))

    def perform(self):
        self.table.create_if_not_exists()
        self.table.lock()  # locked until end of transaction

        db_versions = self.table.versions()

        if not self.config.force_version:
            unfinished = [db_version for db_version
                          in db_versions
                          if not db_version.date_done]
            if unfinished:
                raise MigrationError(
                    'Upgrade of version {} has been attempted and failed. '
                    'You may want to restore the backup or to run again the '
                    'migration with the MARABUNTA_FORCE_VERSION '
                    'environment variable '
                    'or to fix it manually (in that case, you will have to '
                    'update the  \'marabunta_version\' table yourself.'
                    .format(','.join(v.number for v in unfinished))
                )

        unprocessed = [version for version in self.migration.versions
                       if not version.skip(db_versions)]

        if not self.config.allow_serie:
            if len(unprocessed) > 1:
                raise MigrationError(
                    'Only one version can be upgraded at a time.\n'
                    'The following versions need to be applied: {}.\n'.format(
                        [v.number for v in unprocessed]
                        )
                )

        if not self.config.force_version and db_versions:
            installed = max(StrictVersion(v.number) for v in db_versions)
            next_unprocess = min(StrictVersion(v.number) for v in unprocessed)
            if installed > next_unprocess:
                raise MigrationError(
                    'The version you are trying to install ({}) is below '
                    'the current database version.'.format(
                        next_unprocess, installed
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
        self.log(u'start')
        self.table.start_version(self.version.number, datetime.now())

    def finish(self):
        self.log(u'done')
        module_table = IrModuleModule(self.cursor)
        addons_state = module_table.read_state()
        self.table.finish_version(self.version.number, datetime.now(),
                                  u'\n'.join(self.logs),
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
            self.log(u'execute base pre-operations')
            for operation in version.pre_operations():
                operation.execute(self.log)
            if self.config.mode:
                self.log(u'execute %s pre-operations' % self.config.mode)
                for operation in version.pre_operations(mode=self.config.mode):
                    operation.execute(self.log)

            self.perform_addons()

            self.log(u'execute base post-operations')
            for operation in version.post_operations():
                operation.execute(self.log)
            if self.config.mode:
                self.log(u'execute %s post-operations' % self.config.mode)
                for operation in version.post_operations(self.config.mode):
                    operation.execute(self.log)

        self.finish()

    def perform_addons(self):
        version = self.version

        module_table = IrModuleModule(self.cursor)
        addons_state = module_table.read_state()

        upgrade_operation = version.upgrade_addons_operation(
            addons_state,
            mode=self.config.mode
        )
        # exclude the addons already installed or updated during this run
        # when 'allow_serie' is active
        exclude = self.runner.upgraded_addons
        self.log(u'installation / upgrade of addons')
        operation = upgrade_operation.operation(exclude_addons=exclude)
        if operation:
            operation.execute(self.log)
        self.runner.upgraded_addons |= (upgrade_operation.to_install |
                                        upgrade_operation.to_upgrade)
