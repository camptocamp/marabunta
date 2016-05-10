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
                 demo=False):
        self.project_file = project_file
        self.database = database
        self.db_user = db_user
        self.db_password = db_password
        self.db_port = db_port
        self.db_host = db_host
        self.demo = demo

    @classmethod
    def from_parse_args(cls, args):
        return cls(args.project_file,
                   args.database,
                   db_user=args.db_user,
                   db_password=args.db_password,
                   db_port=args.db_port,
                   db_host=args.db_host,
                   demo=args.demo)


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
    parser = argparse.ArgumentParser(description='Odoo Migration')
    parser.add_argument('--project-file', '-f',
                        action=EnvDefault,
                        envvar='PROJECT_FILE',
                        required=True,
                        help='The yaml file containing the migration steps')
    parser.add_argument('--database', '-d',
                        action=EnvDefault,
                        envvar='DB_NAME',
                        required=True,
                        help='Odoo\'s database')
    parser.add_argument('--db-user', '-u',
                        action=EnvDefault,
                        envvar='DB_USER',
                        required=True,
                        help='Odoo\'s database user')
    parser.add_argument('--db-password', '-w',
                        action=EnvDefault,
                        envvar='DB_PASSWORD',
                        required=True,
                        help='Odoo\'s database password')
    parser.add_argument('--db-port', '-p',
                        action=EnvDefault,
                        envvar='DB_PORT',
                        default='5432',
                        help='Odoo\'s database port')
    parser.add_argument('--db-host', '-H',
                        action=EnvDefault,
                        envvar='DB_HOST',
                        default='localhost',
                        help='Odoo\'s database host')
    parser.add_argument('--demo',
                        action=EnvDefault,
                        envvar='DEMO',
                        default=False,
                        help='Demo mode')
    return parser
