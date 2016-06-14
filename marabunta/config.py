# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import argparse
import os


class Config(object):

    def __init__(self,
                 project_file,
                 database,
                 db_user=None,
                 db_password=None,
                 db_port=5432,
                 db_host='localhost',
                 demo=False,
                 force=False,
                 force_version=None):
        self.project_file = project_file
        self.database = database
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port
        self.db_host = db_host
        self.demo = demo
        self.force = force
        self.force_version = force_version
        if force_version and not force:
            self.force = True

    @classmethod
    def from_parse_args(cls, args):
        """Constructor from command line args.

        :param args: parse command line arguments
        :type args: argparse.ArgumentParser

        """

        return cls(args.project_file,
                   args.database,
                   db_user=args.db_user,
                   db_password=args.db_password,
                   db_port=args.db_port,
                   db_host=args.db_host,
                   demo=args.demo,
                   force=args.force,
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
    parser.add_argument('--project-file', '-f',
                        action=EnvDefault,
                        envvar='MARABUNTA_PROJECT_FILE',
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
    parser.add_argument('--demo',
                        action='store_true',
                        required=False,
                        default=bool(os.environ.get('MARABUNTA_DEMO')),
                        help='Demo mode')
    parser.add_argument('--force',
                        action='store_true',
                        required=False,
                        default=bool(os.environ.get('MARABUNTA_FORCE')),
                        help='Force the upgrade even if the code version '
                             'not match the upgrade(s) to process.'
                             'Only for dev.')
    parser.add_argument('--force-version',
                        required=False,
                        default=os.environ.get('MARABUNTA_FORCE_VERSION'),
                        help='Force upgrade of a version, even if it has '
                             'already been applied. Only for dev.')
    return parser
