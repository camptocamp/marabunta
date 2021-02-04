# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from distutils.util import strtobool
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
                 force_version=None,
                 web_host='localhost',
                 web_port=8069,
                 web_resp_status=503,
                 web_resp_retry_after=300,  # 5 minutes
                 web_custom_html=None,
                 web_healthcheck_path=None):
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
        self.web_host = web_host
        self.web_port = web_port
        self.web_resp_status = web_resp_status
        self.web_resp_retry_after = web_resp_retry_after
        self.web_custom_html = web_custom_html
        self.web_healthcheck_path = web_healthcheck_path

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
                   web_host=args.web_host,
                   web_port=args.web_port,
                   web_resp_status=args.web_resp_status,
                   web_resp_retry_after=args.web_resp_retry_after,
                   web_custom_html=args.web_custom_html,
                   web_healthcheck_path=args.web_healthcheck_path,
                   )


class EnvDefault(argparse.Action):

    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            default = self.get_default(envvar)
        if required and default is not None:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def get_default(self, envvar):
        return os.getenv(envvar)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class BoolEnvDefault(EnvDefault):

    def get_default(self, envvar):
        val = os.getenv(envvar, '')
        try:
            return strtobool(val.lower())
        except ValueError:
            return False


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
                        action=BoolEnvDefault,
                        required=False,
                        envvar='MARABUNTA_ALLOW_SERIE',
                        help='Allow to run more than 1 version upgrade at a '
                             'time.')
    parser.add_argument('--force-version',
                        required=False,
                        default=os.environ.get('MARABUNTA_FORCE_VERSION'),
                        help='Force upgrade of a version, even if it has '
                             'already been applied.')

    group = parser.add_argument_group(
        title='Web',
        description='Configuration related to the internal web server, '
                    'used to publish a maintenance page during the migration.',
    )
    group.add_argument('--web-host',
                       required=False,
                       default=os.environ.get('MARABUNTA_WEB_HOST', '0.0.0.0'),
                       help='Host for the web server')
    group.add_argument('--web-port',
                       required=False,
                       default=os.environ.get('MARABUNTA_WEB_PORT', 8069),
                       help='Port for the web server')
    group.add_argument('--web-resp-status',
                       required=False,
                       default=os.environ.get(
                           'MARABUNTA_WEB_RESP_STATUS', 503
                        ),
                       help='Response HTTP status code of the web server')
    group.add_argument('--web-resp-retry-after',
                       required=False,
                       default=os.environ.get(
                           'MARABUNTA_WEB_RESP_RETRY_AFTER', 300
                       ),
                       help=(
                            '"Retry-After" header value (in seconds) of '
                            'response delivered by the web server')
                       )
    group.add_argument('--web-custom-html',
                       required=False,
                       default=os.environ.get(
                           'MARABUNTA_WEB_CUSTOM_HTML'
                       ),
                       help='Path to a custom html file to publish')
    group.add_argument('--web-healthcheck-path',
                       required=False,
                       default=os.environ.get(
                           'MARABUNTA_WEB_HEALTHCHECK_PATH'
                       ),
                       help=(
                           'URL Path used for health checks HTTP requests. '
                           'Such monitoring requests will return HTTP 200 '
                           'status code instead of the default 503.'
                       ))
    return parser
