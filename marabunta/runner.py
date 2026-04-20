# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import annotations

import traceback
from datetime import datetime

from .database import IrModuleModule
from .exception import MigrationError, OperationError
from .output import print_decorated, safe_print
from .version import MarabuntaVersion

LOG_DECORATION = "|> "


class Runner:
    def __init__(self, config, migration, database, table):
        self.config = config
        self.migration = migration
        self.database = database
        self.table = table
        # we keep the addons upgrading during a run in this set,
        # this is only useful when using 'allow_serie',
        # if an addon has just been installed or updated,
        # we don't want to do it again for another version
        self.upgraded_addons = set()

    def log(self, message: str, decorated: bool = True, stdout: bool = True) -> None:
        if not stdout:
            return
        if decorated:
            app_message = f"migration: {message}"
            print_decorated(app_message)
        else:
            safe_print(message)

    def perform(self) -> None:
        self.table.create_if_not_exists()

        db_versions = self.table.versions()

        if not self.config.force_version:
            unfinished = [
                db_version for db_version in db_versions if not db_version.date_done
            ]
            if unfinished:
                raise MigrationError(
                    "Upgrade of version {} has been attempted and failed. "
                    "You may want to restore the backup or to run again the "
                    "migration with the MARABUNTA_FORCE_VERSION "
                    "environment variable "
                    "or to fix it manually (in that case, you will have to "
                    "update the  'marabunta_version' table yourself.".format(
                        ",".join(v.number for v in unfinished)
                    )
                )

        unprocessed = [
            version
            for version in self.migration.versions
            if not version.skip(db_versions)
        ]

        if not self.config.allow_serie:
            if len(unprocessed) > 1:
                versions_to_apply = [v.number for v in unprocessed]
                raise MigrationError(
                    "Only one version can be upgraded at a time.\n"
                    "The following versions need to be applied: "
                    f"{versions_to_apply}.\n"
                )

        if not self.config.force_version and db_versions and unprocessed:
            installed = max(MarabuntaVersion(v.number) for v in db_versions)
            next_unprocess = min(MarabuntaVersion(v.number) for v in unprocessed)
            if installed > next_unprocess:
                raise MigrationError(
                    f"The version you are trying to install ({next_unprocess})"
                    f" is below the current database version ({installed})."
                )

        backup_options = self.migration.options.backup
        run_backup = False
        if backup_options:
            run_backup = (
                # If we are forcing a version, we want a backup
                self.config.force_version
                # If any of the version not yet processed, including the noop
                # versions, need a backup, we run it. (note: by default,
                # noop versions don't trigger a backup but it can be
                # explicitly activated)
                or any(
                    version.backup
                    for version in self.migration.versions
                    if not version.is_processed(db_versions)
                )
            )
            if run_backup:
                try:
                    backup_options.ignore_if_operation().execute()
                except OperationError:
                    pass
                else:
                    run_backup = False
        if run_backup:
            backup_operation = backup_options.command_operation(self.config)
            backup_operation.execute(self.log)

        for version in self.migration.versions:
            # when we force-execute one version, we skip all the others
            if self.config.force_version:
                if self.config.force_version != version.number:
                    continue
                else:
                    self.log(f"force-execute version {version.number}")

            self.log(f"processing version {version.number}")
            VersionRunner(self, version).perform()


class VersionRunner:
    def __init__(self, runner, version):
        self.runner = runner
        self.table = runner.table
        self.migration = runner.migration
        self.config = runner.config
        self.database = runner.database
        self.version = version
        self.logs = []

    def log(self, message: str, decorated: bool = True, stdout: bool = True) -> None:
        self.logs.append(message)
        if not stdout:
            return
        if decorated:
            app_message = f"version {self.version.number}: {message}"
            print_decorated(app_message)
        else:
            safe_print(message)

    def start(self) -> None:
        self.log("start")
        self.table.start_version(self.version.number, datetime.now())

    def finish(self) -> None:
        self.log("done")
        module_table = IrModuleModule(self.database)
        addons_state = module_table.read_state()
        self.table.finish_version(
            self.version.number,
            datetime.now(),
            "\n".join(self.logs),
            [state._asdict() for state in addons_state],
        )

    def perform(self):
        """Perform the version upgrade on the database."""
        db_versions = self.table.versions()

        version = self.version
        if (
            version.is_processed(db_versions)
            and not self.config.force_version == self.version.number
        ):
            self.log(f"version {version.number} is already installed")
            return

        self.start()
        try:
            self._perform_version(version)
        except Exception:
            msg = traceback.format_exc()
            error = "\n".join([*self.logs, "\n", msg])
            self.table.record_log(version.number, error)
            raise
        self.finish()

    def _perform_version(self, version):
        """Inner method for version upgrade.

        Not intended for standalone use. This method performs the actual
        version upgrade with all the pre, post operations and addons upgrades.

        :param version: The migration version to upgrade to
        :type version: Instance of Version class
        """
        if version.is_noop():
            self.log(f"version {version.number} is a noop")
        else:
            self.log("execute base pre-operations")
            for operation in version.pre_operations():
                operation.execute(self.log)
            if self.config.mode:
                self.log(f"execute {self.config.mode} pre-operations")
                for operation in version.pre_operations(mode=self.config.mode):
                    operation.execute(self.log)

            self.perform_addons()

            self.log("execute base post-operations")
            for operation in version.post_operations():
                operation.execute(self.log)
            if self.config.mode:
                self.log(f"execute {self.config.mode} post-operations")
                for operation in version.post_operations(self.config.mode):
                    operation.execute(self.log)

    def perform_addons(self):
        version = self.version

        module_table = IrModuleModule(self.database)
        addons_state = module_table.read_state()

        upgrade_operation = version.upgrade_addons_operation(
            addons_state, mode=self.config.mode
        )
        # exclude the addons already installed or updated during this run
        # when 'allow_serie' is active
        exclude = self.runner.upgraded_addons
        self.log("installation / upgrade of addons")
        operation = upgrade_operation.operation(exclude_addons=exclude)
        if operation:
            operation.execute(self.log)
        self.runner.upgraded_addons |= (
            upgrade_operation.to_install | upgrade_operation.to_upgrade
        )
