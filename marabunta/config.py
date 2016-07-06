# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import argparse
import os


class Config(object):

    def __init__(self,
                 migration_file,
                 database,
                 db_user=None,
                 db_password=None,
                 db_port=5432,
                 db_host='localhost',
                 mode=None,
                 allow_serie=False,
                 force_version=None):
        self.migration_file = migration_file
        self.database = database
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port
        self.db_host = db_host
        self.mode = mode
        self.allow_serie = allow_serie
        self.force_version = force_version
        if force_version and not allow_serie:
            self.allow_serie = True

    @classmethod
    def from_parse_args(cls, args):
        """Constructor from command line args.

        :param args: parse command line arguments
        :type args: argparse.ArgumentParser

        """

        return cls(args.migration_file,
                   args.database,
                   db_user=args.db_user,
                   db_password=args.db_password,
                   db_port=args.db_port,
                   db_host=args.db_host,
                   mode=args.mode,
                   allow_serie=args.allow_serie,
                   force_version=args.force_version,
                   )


class EnvDefault(argparse.Action):

    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default is not None:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def get_args_parser():
    """Return a parser for command line options."""
    parser = argparse.ArgumentParser(
        description='Marabunta: Migrating ants for Odoo')
    parser.add_argument('--migration-file', '-f',
                        action=EnvDefault,
                        envvar='MARABUNTA_MIGRATION_FILE',
                        required=True,
                        help='The yaml file containing the migration steps')
    parser.add_argument('--database', '-d',
                        action=EnvDefault,
                        envvar='MARABUNTA_DATABASE',
                        required=True,
                        help="Odoo's database")
    parser.add_argument('--db-user', '-u',
                        action=EnvDefault,
                        envvar='MARABUNTA_DB_USER',
                        required=True,
                        help="Odoo's database user")
    parser.add_argument('--db-password', '-w',
                        action=EnvDefault,
                        envvar='MARABUNTA_DB_PASSWORD',
                        required=True,
                        help="Odoo's database password")
    parser.add_argument('--db-port', '-p',
                        default=os.environ.get('MARABUNTA_DB_PORT', 5432),
                        help="Odoo's database port")
    parser.add_argument('--db-host', '-H',
                        default=os.environ.get('MARABUNTA_DB_HOST',
                                               'localhost'),
                        help="Odoo's database host")
    parser.add_argument('--mode',
                        action=EnvDefault,
                        envvar='MARABUNTA_MODE',
                        required=False,
                        help="Specify the mode in which we run the migration,"
                             "such as 'demo' or 'prod'. Additional operations "
                             "of this mode will be executed after the main "
                             "operations and the addons list of this mode "
                             "will be merged with the main addons list.")
    parser.add_argument('--allow-serie',
                        action='store_true',
                        required=False,
                        default=bool(os.environ.get('MARABUNTA_ALLOW_SERIE')),
                        help='Allow to run more than 1 version upgrade at a '
                             'time.')
    parser.add_argument('--force-version',
                        required=False,
                        default=os.environ.get('MARABUNTA_FORCE_VERSION'),
                        help='Force upgrade of a version, even if it has '
                             'already been applied.')
    return parser
