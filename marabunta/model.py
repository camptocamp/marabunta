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
        self._operations = {
            'pre': [],
            'post': [],
            'demo': [],
        }
        self._upgrade_addons = set()
        self._remove_addons = set()
        self.options = options

    def is_processed(self, db_versions):
        return self.number in (v.number for v in db_versions if v.date_done)

    def is_noop(self):
        noop = (all(not operations for operations
                    in self._operations.itervalues()) and
                not self._upgrade_addons and not self._remove_addons)
        return noop

    def skip(self, db_versions):
        """ Version is either noop either it has been processed already """
        return self.is_noop() or self.is_processed(db_versions)

    def add_operation(self, operation_type, operation):
        """ Add an operation to the version

        :param operation_type: one of 'pre', 'post', 'demo'
        :type operation_type: str
        :param operation: the operation to add
        :type operation: :class:`marabunta.model.Operation`
        """
        assert operation_type in self._operations, \
            "operation type must be in %s" % ', '.join(self._operations)
        self._operations[operation_type].append(operation)

    def add_upgrade_addons(self, addons):
        self._upgrade_addons.update(addons)

    def add_remove_addons(self, addons):
        self._remove_addons.update(addons)
        raise ConfigurationError(
            'Removing addons is not yet supported because it cannot be done '
            'using the command line. You have to uninstall addons using '
            'an Odoo (\'import openerp\') script'
        )

    @property
    def pre_operations(self):
        return self._operations['pre']

    @property
    def post_operations(self):
        return self._operations['post']

    @property
    def demo_operations(self):
        return self._operations['demo']

    def upgrade_addons_operation(self, addons_state):
        install_command = self.options.install_command
        install_args = self.options.install_args[:] or []
        install_args += [u'--workers=0', u'--stop-after-init']

        installed = set(a.name for a in addons_state
                        if a.state in ('installed', 'to upgrade'))

        to_install = self._upgrade_addons - installed
        to_upgrade = installed & self._upgrade_addons

        if to_install:
            install_args += [u'-i', u','.join(to_install)]
        if to_upgrade:
            install_args += [u'-u', u','.join(to_upgrade)]

        return Operation([install_command] + install_args)

    def remove_addons_operation(self):
        raise NotImplementedError

    def __repr__(self):
        return u'Version<{}>'.format(self.number)


class Operation(object):

    def __init__(self, command):
        if isinstance(command, string_types):
            command = shlex.split(command)
        self.command = command

    def execute(self, log):
        log(u'{}'.format(u' '.join(self.command)))
        proc = subprocess.Popen(self.command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        for line in iter(proc.stdout.readline, b''):
            log(line, raw=True)
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
