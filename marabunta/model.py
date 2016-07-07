# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import shlex
import subprocess
from distutils.version import StrictVersion

from .exception import ConfigurationError, OperationError
from .helpers import string_types


class Migration(object):

    def __init__(self, versions):
        self._versions = versions

    @property
    def versions(self):
        return sorted(self._versions, key=lambda v: StrictVersion(v.number))


class MigrationOption(object):

    def __init__(self, install_command=None, install_args=None):
        self.install_command = install_command or 'odoo.py'
        self.install_args = install_args or ''


class Version(object):

    def __init__(self, number, options):
        try:
            StrictVersion().parse(number)
        except ValueError:
            raise ConfigurationError(
                '{} is not a valid version'.format(number)
            )
        self.number = number
        self._version_modes = {}
        self.options = options

    def is_processed(self, db_versions):
        return self.number in (v.number for v in db_versions if v.date_done)

    def is_noop(self):
        has_operations = (mode.pre_operations or mode.post_operations
                          for mode in self._version_modes.values())
        has_upgrade_addons = (mode.upgrade_addons or mode.remove_addons
                              for mode in self._version_modes.values())
        noop = (not has_operations and not has_upgrade_addons)
        return noop

    def skip(self, db_versions):
        """ Version is either noop either it has been processed already """
        return self.is_noop() or self.is_processed(db_versions)

    def _get_version_mode(self, mode=None):
        """ Return a VersionMode for a mode name.

        When the mode is None, we are working with the 'base' mode.

        """
        version_mode = self._version_modes.get(mode)
        if not version_mode:
            version_mode = self._version_modes[mode] = VersionMode(name=mode)
        return version_mode

    def add_operation(self, operation_type, operation, mode=None):
        """ Add an operation to the version

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
                "Type of operation must be 'pre' or 'post', got %s" %
                (operation_type,)
            )

    def add_upgrade_addons(self, addons, mode=None):
        version_mode = self._get_version_mode(mode=mode)
        version_mode.add_upgrade_addons(addons)

    def add_remove_addons(self, addons, mode=None):
        version_mode = self._get_version_mode(mode=mode)
        version_mode.add_remove_addons(addons)
        raise ConfigurationError(
            'Removing addons is not yet supported because it cannot be done '
            'using the command line. You have to uninstall addons using '
            'an Odoo (\'import openerp\') script'
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
            'Removing addons is not yet supported because it cannot be done '
            'using the command line. You have to uninstall addons using '
            'an Odoo (\'import openerp\') script'
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
        install_args += [u'--workers=0', u'--stop-after-init']

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

    def __init__(self, command):
        if isinstance(command, string_types):
            command = shlex.split(command)
        self.command = command

    def __nonzero__(self):
        return bool(self.command)

    def execute(self, log):
        log(u'{}'.format(u' '.join(self.command)))
        proc = subprocess.Popen(self.command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        for line in iter(proc.stdout.readline, b''):
            log(line.decode('utf-8', errors='replace'), raw=True)
        proc.wait()
        if proc.returncode != 0:
            raise OperationError(
                "command '{}' returned {}".format(
                    ' '.join(self.command),
                    proc.returncode
                )
            )

    def __repr__(self):
        return u'Operation<{}>'.format(' '.join(self.command))
