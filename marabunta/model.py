# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import subprocess


class Migration(object):

    def __init__(self, versions):
        self.versions = versions


class MigrationOption(object):

    def __init__(self, install_command=None, install_args=None):
        self.install_command = install_command or 'odoo.py'
        self.install_args = install_args or ''


class Version(object):

    def __init__(self, number, options):
        self.number = number
        self._operations = {
            'pre': [],
            'post': [],
            'demo': [],
        }
        self._upgrade_addons = set()
        self._remove_addons = set()
        self.options = options

    def is_noop(self):
        # true if we have no operations
        return

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

    def upgrade_addons(self, addons):
        self._upgrade_addons.update(addons)

    def remove_addons(self, addons):
        self._remove_addons.update(addons)

    def __repr__(self):
        return u'Version<{}>'.format(self.number)


class Operation(object):

    def __init__(self, command):
        self.command = command

    @staticmethod
    def run_command_iter(command):
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        return iter(p.stdout.readline, b'')

    def execute(self, command):
        self.log(u'{}'.format(u' '.join(command)))
        for line in self.run_command_iter(command):
            self.log(line, raw=True)
