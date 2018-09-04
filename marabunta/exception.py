# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


class MarabuntaError(Exception):
    pass


class MigrationError(Exception):
    pass


class ParseError(MarabuntaError):

    def __init__(self, message, example=None):
        super(ParseError, self).__init__(message)
        self.example = example

    def __str__(self):
        if not self.example:
            return super(ParseError, self).__str__()
        msg = (u'An error occured during the parsing of the configuration '
               u'file. Here is an example to help you to figure out '
               u'your issue.\n{}\n{}').format(self.example, self.args[0])
        return msg


class ConfigurationError(MarabuntaError):
    pass


class OperationError(MarabuntaError):
    pass


class BackupError(MigrationError):
    """An error happened during the execution of the backup.
    """
    pass
