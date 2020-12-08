# -*- coding: utf-8 -*-
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import sys

from builtins import object
from io import StringIO
from string import Template

import pexpect

from .exception import ConfigurationError, OperationError, BackupError
from .helpers import string_types
from .version import MarabuntaVersion


class Migration(object):

    def __init__(self, versions, options):
        self._versions = versions
        self.options = options

    @property
    def versions(self):
        return sorted(self._versions, key=lambda v: MarabuntaVersion(v.number))


class MigrationOption(object):

    def __init__(self, install_command=None, install_args=None, backup=None):
        """Options block in a migration.

        :param install_command: Command ran for addons install
        :type install_command: String
        :param install_args: Arguments for an install command
        :type install_args: String
        :param backup: Backup options
        :type backup: Dict
        """
        self.install_command = install_command or u'odoo'
        self.install_args = install_args or u''
        self.backup = backup


class MigrationBackupOption(object):

    def __init__(self, command, ignore_if, stop_on_failure=True):
        """Backup option in migration.

        Migration allows using a backup command in order to perform specific
        commands (unless explicitly opted-out) before the migration step.

        The command can contain placeholders that will be replaced by the
        current configuration values:

         * ``$database``
         * ``$db_user``
         * ``$db_password``
         * ``$db_host``
         * ``$db_port``

        :param command: Backup command to execute
        :type command: String
        :param ignore_if: A command, that is evaluated
                          without error -> backup is ignored
        :type ignore_if: String
        :param stop_on_failure: To either stop migration
                                if backup commands fails or to ignore it
        :type stop_on_failure: Boolean
        """
        self._command = command
        self._ignore_if = ignore_if
        self._stop_on_failure = stop_on_failure
        self._ignore_if = ignore_if

    def command_operation(self, config):
        template = Template(self._command)
        command = template.safe_substitute(
            database=config.database,
            db_user=config.db_user,
            db_password=config.db_password,
            db_port=config.db_port,
            db_host=config.db_host,
        )
        return BackupOperation(
            command,
            shell=True,
            stop_on_failure=self._stop_on_failure,
        )

    def ignore_if_operation(self):
        if self._ignore_if is None or self._ignore_if is False:
            # if ignore_if parameter was not specified - always backup
            return SilentOperation('false', shell=True)
        elif self._ignore_if is True:
            # if it is specifically True
            return SilentOperation('true', shell=True)
        return SilentOperation(self._ignore_if, shell=True)


class Version(object):

    def __init__(self, number, options):
        """Base class for a migration version.

        :param number: Valid version number
        :type number: String
        :param options: Version options
        :type options: Instance of a MigrationOption class
        """
        try:
            MarabuntaVersion().parse(number)
        except ValueError:
            raise ConfigurationError(
                u'{} is not a valid version'.format(number)
            )
        self.number = number
        self._version_modes = {}
        self.options = options
        self.backup = False

    def is_processed(self, db_versions):
        """Check if version is already applied in the database.

        :param db_versions:
        """
        return self.number in (v.number for v in db_versions if v.date_done)

    def is_noop(self):
        """Check if version is a no operation version.
        """
        has_operations = [mode.pre_operations or mode.post_operations
                          for mode in self._version_modes.values()]
        has_upgrade_addons = [mode.upgrade_addons or mode.remove_addons
                              for mode in self._version_modes.values()]
        noop = not any((has_upgrade_addons, has_operations))
        return noop

    def skip(self, db_versions):
        """Version is either noop, or it has been processed already.
        """
        return self.is_noop() or self.is_processed(db_versions)

    def _get_version_mode(self, mode=None):
        """Return a VersionMode for a mode name.

        When the mode is None, we are working with the 'base' mode.
        """
        version_mode = self._version_modes.get(mode)
        if not version_mode:
            version_mode = self._version_modes[mode] = VersionMode(name=mode)
        return version_mode

    def add_operation(self, operation_type, operation, mode=None):
        """Add an operation to the version

        :param mode: Name of the mode in which the operation is executed
        :type mode: str
        :param operation_type: one of 'pre', 'post'
        :type operation_type: str
        :param operation: the operation to add
        :type operation: :class:`marabunta.model.Operation`
        """
        version_mode = self._get_version_mode(mode=mode)
        if operation_type == 'pre':
            version_mode.add_pre(operation)
        elif operation_type == 'post':
            version_mode.add_post(operation)
        else:
            raise ConfigurationError(
                u"Type of operation must be 'pre' or 'post', got %s" %
                (operation_type,)
            )

    def add_upgrade_addons(self, addons, mode=None):
        version_mode = self._get_version_mode(mode=mode)
        version_mode.add_upgrade_addons(addons)

    def add_remove_addons(self, addons, mode=None):
        version_mode = self._get_version_mode(mode=mode)
        version_mode.add_remove_addons(addons)
        raise ConfigurationError(
            u'Removing addons is not yet supported because it cannot be done '
            u'using the command line. You have to uninstall addons using '
            u'an Odoo (\'import openerp\') script'
        )

    def pre_operations(self, mode=None):
        """ Return pre-operations only for the mode asked """
        version_mode = self._get_version_mode(mode=mode)
        return version_mode.pre_operations

    def post_operations(self, mode=None):
        """ Return post-operations only for the mode asked """
        version_mode = self._get_version_mode(mode=mode)
        return version_mode.post_operations

    def upgrade_addons_operation(self, addons_state, mode=None):
        """ Return merged set of main addons and mode's addons """
        installed = set(a.name for a in addons_state
                        if a.state in ('installed', 'to upgrade'))

        base_mode = self._get_version_mode()
        addons_list = base_mode.upgrade_addons.copy()
        if mode:
            add_mode = self._get_version_mode(mode=mode)
            addons_list |= add_mode.upgrade_addons

        to_install = addons_list - installed
        to_upgrade = installed & addons_list

        return UpgradeAddonsOperation(self.options, to_install, to_upgrade)

    def remove_addons_operation(self):
        raise NotImplementedError

    def __repr__(self):
        return u'Version<{}>'.format(self.number)


class VersionMode(object):

    def __init__(self, name=None):
        self.name = name
        self.pre_operations = []
        self.post_operations = []
        self.upgrade_addons = set()
        self.remove_addons = set()

    def add_pre(self, operation):
        self.pre_operations.append(operation)

    def add_post(self, operation):
        self.post_operations.append(operation)

    def __repr__(self):
        name = self.name if self.name else 'base'
        return u'VersionMode<{}>'.format(name)

    def add_upgrade_addons(self, addons):
        self.upgrade_addons.update(addons)

    def add_remove_addons(self, addons):
        self.remove_addons.update(addons)
        raise ConfigurationError(
            u'Removing addons is not yet supported because it cannot be done '
            u'using the command line. You have to uninstall addons using '
            u'an Odoo (\'import openerp\') script'
        )


class UpgradeAddonsOperation(object):

    def __init__(self, options, to_install, to_upgrade):
        self.options = options
        self.to_install = set(to_install)
        self.to_upgrade = set(to_upgrade)

    def operation(self, exclude_addons=None):
        if exclude_addons is None:
            exclude_addons = set()
        install_command = self.options.install_command
        install_args = self.options.install_args[:] or []
        install_args += [u'--workers=0', u'--stop-after-init', u'--no-xmlrpc']

        to_install = self.to_install - exclude_addons
        if to_install:
            install_args += [u'-i', u','.join(to_install)]

        to_upgrade = self.to_upgrade - exclude_addons
        if to_upgrade:
            install_args += [u'-u', u','.join(to_upgrade)]

        if to_install or to_upgrade:
            return Operation([install_command] + install_args)
        else:
            return Operation('')


class Operation(object):

    def __init__(self, command, shell=False):
        """ Wrap a pexpect spawn command

        :param command: the command to run as string
        :param shell: boolean, when True, wraps the command in ``sh -c``
                      so bash environment variables are interpolated
        """
        if not isinstance(command, string_types):
            command = u' '.join(command)
        self.command = command
        self.shell = shell

    def _spawn_command(self):
        if self.shell:
            return "sh", ["-c", self.command]
        else:
            return self.command, []

    def __bool__(self):
        return bool(self.command)

    def _execute(self, log, interactive=True):
        assert self.command
        cmd, options = self._spawn_command()
        child = pexpect.spawn(cmd, options, timeout=None, encoding='utf8')
        # interact() will transfer the child's stdout to
        # stdout, but we also copy the output in a buffer
        # so we can save the logs in the database
        log_buffer = StringIO()
        if interactive:
            # use the interactive mode so we can use pdb in the
            # migration scripts
            child.interact()
        else:
            # set the logfile to stdout so we have an unbuffered
            # output
            child.logfile = sys.stdout
            child.expect(pexpect.EOF)
            # child.before contains all the the output of the child program
            # before the EOF
            # child.before is unicode
            log_buffer.write(child.before)
        child.close()
        if child.signalstatus is not None:
            raise OperationError(
                u"command '{}' has been interrupted by signal {}".format(
                    self.command,
                    child.signalstatus
                )
            )
        elif child.exitstatus != 0:
            raise OperationError(
                u"command '{}' returned {}".format(
                    self.command,
                    child.exitstatus
                )
            )
        log_buffer.seek(0)
        # the pseudo-tty used for the child process returns
        # lines with \r\n endings
        msg = '\n'.join(log_buffer.read().splitlines())
        log(msg, decorated=False, stdout=False)

    def execute(self, log):
        log(u'{}'.format(self.command))
        self._execute(log, interactive=sys.stdout.isatty())

    def __repr__(self):
        return u'Operation<{}>'.format(self.command)


class SilentOperation(Operation):
    """Operation that does not require logging or interactivity. """

    def _execute(self):
        assert self.command
        cmd, options = self._spawn_command()
        child = pexpect.spawn(cmd, options, timeout=None, encoding='utf8')
        child.expect(pexpect.EOF)
        child.close()
        if child.signalstatus is not None:
            raise OperationError(
                u"command '{}' has been interrupted by signal {}".format(
                    ' '.join(self.command),
                    child.signalstatus
                )
            )
        elif child.exitstatus != 0:
            raise OperationError(
                u"command '{}' returned {}".format(
                    ' '.join(self.command),
                    child.exitstatus
                )
            )

    def execute(self):
        self._execute()


class BackupOperation(Operation):

    def __init__(self, command, shell=False, stop_on_failure=True):
        super(BackupOperation, self).__init__(command, shell=shell)
        self.stop_on_failure = stop_on_failure

    def execute(self, log):
        log('Backing up...')
        try:
            self._execute(log, interactive=sys.stdout.isatty())
        except OperationError:
            if self.stop_on_failure:
                raise BackupError(
                    u"Backup command failed, stopping migration."
                )
            else:
                log(u"Backup command failed, ignored by configuration. "
                    u"Resuming migration")
