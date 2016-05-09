#!/usr/bin/env python
# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Load migration instructions from a YAML file and execute them if required.

TODO: move in its own project
TODO: new name: Marabunta? (migrating ants)
"""

from __future__ import print_function

import argparse
import json
import os
import subprocess
import urllib

from collections import namedtuple
from contextlib import contextmanager
from datetime import datetime

import psycopg2
import yaml

__version__ = "0.0.1"

LOG_DECORATION = u'|> '


class Database(object):

    def __init__(self, config):
        self.config = config

    def dsn(self):
        cfg = self.config
        host = 'host=%s' % cfg.db_host if cfg.db_host else ''
        port = 'port=%s' % cfg.db_port if cfg.db_port else ''
        name = 'dbname=%s' % cfg.database
        user = 'user=%s' % cfg.db_user if cfg.db_user else ''
        password = ('password=%s' % urllib.unquote_plus(cfg.db_password)
                    if cfg.db_password else '')
        return '%s %s %s %s %s' % (host, port, name, user, password)

    @contextmanager
    def connect(self):
        conn = psycopg2.connect(self.dsn())
        yield conn
        conn.close()


class MigrationTable(object):

    def __init__(self, cursor):
        self.cursor = cursor
        self.table_name = 'migration_version'
        self.VersionRecord = namedtuple(
            'VersionRecord',
            'number date_start date_done log addons'
        )

    def create_if_not_exists(self):
        query = """
        CREATE TABLE IF NOT EXISTS {} (
            number VARCHAR NOT NULL,
            date_start TIMESTAMP NOT NULL,
            date_done TIMESTAMP,
            log TEXT,
            addons TEXT,

            CONSTRAINT version_pk PRIMARY KEY (number)
        );
        """.format(self.table_name)
        self.cursor.execute(query)

    def lock(self):
        """ Lock the entire migration table

        The lock is released the next commit or rollback.
        The purpose is to prevent 2 processes to execute the same migration at
        the same time.

        The other transaction should because if they exit, whey will either be
        dead, either run Odoo and we want neither of them.

        """
        query = """
        LOCK TABLE {};
        """.format(self.table_name)
        self.cursor.execute(query)

    def versions(self):
        query = """
        SELECT number,
               date_start,
               date_done,
               log,
               addons
        FROM {}
        """.format(self.table_name)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        versions = []
        for row in rows:
            row = list(row)
            # convert 'addons' to json
            row[4] = json.loads(row[4]) if row[4] else []
            versions.append(
                self.VersionRecord(*row)
            )
        return versions

    def start_version(self, number, start):
        query = """
        INSERT INTO {}
        (number, date_start)
        VALUES (%s, %s);
        """.format(self.table_name)
        self.cursor.execute(query, (number, start))

    def finish_version(self, number, end, log, addons):
        query = """
        UPDATE {}
        SET date_done = %s,
            log = %s,
            addons = %s
        WHERE number = %s;
        """.format(self.table_name)
        self.cursor.execute(query, (end, log, json.dumps(addons), number))


# TODO: split parser and models, parse the full file so we can check its
# validity before running the operations

class ProjectFileParser(object):

    def __init__(self, filename):
        self.filename = filename
        self.parsed = {}

    def parse(self):
        with open(self.filename, 'rU') as fh:
            self.parsed = yaml.load(fh.read())

    @property
    def name(self):
        if not self.parsed.get('name'):
            raise Exception("'name' key is missing")
        return self.parsed['name']

    @property
    def migrations(self):
        if not self.parsed.get('migrations'):
            raise Exception("'migrations' key is missing")
        return MigrationDefinition(self, self.parsed['migrations'])


class MigrationDefinition(object):

    def __init__(self, project, migrations):
        self.project = project
        self.migrations = migrations

    @property
    def install_command(self):
        options = self.migrations.get('options', {})
        return options.get('install_command', 'odoo.py')

    @property
    def install_args(self):
        options = self.migrations.get('options', {})
        return options.get('install_args', '').split()

    @property
    def versions(self):
        return [MigrationVersion(self, version)
                for version in self.migrations['versions']]


class MigrationVersion(object):

    def __init__(self, migrations, version_info):
        self.project = migrations.project
        self.migrations = migrations
        self.version_info = version_info

    @property
    def number(self):
        return self.version_info['version']

    def is_noop(self):
        return bool(self.version_info.get('noop'))

    def _get_operations(self, optype):
        operations = self.version_info.get('operations') or {}
        return operations.get(optype, [])

    @property
    def pre_operations(self):
        return self._get_operations('pre')

    @property
    def post_operations(self):
        return self._get_operations('post')

    @property
    def demo_operations(self):
        return self._get_operations('demo')

    def _addons(self, optype):
        addons = self.version_info.get('addons') or {}
        return set(addons.get(optype) or [])

    @property
    def install_addons(self):
        return self._addons('install')

    @property
    def update_addons(self):
        return self._addons('update')

    @property
    def uninstall_addons(self):
        return self._addons('uninstall')

    def __repr__(self):
        return u'MigrationVersion<{}>'.format(self.number)


class MigrationOperation(object):

    def __init__(self, optype, action):
        self.optype = optype
        self.action = action


class Runner(object):

    def __init__(self, config, migrations, cursor, table):
        self.config = config
        self.migrations = migrations
        self.cursor = cursor
        self.table = table

    def log(self, message):
        message = u'\033[1m{}migration:{}\033[0m'.format(
            LOG_DECORATION,
            message,
        )
        print(message)

    def perform(self):
        self.table.create_if_not_exists()
        self.table.lock()  # locked until end of transaction

        unprocessed = self.filter_versions()
        # TODO: if we have more than one version to process,
        # raise an error indicating to process the previous(?) docker image
        for version in unprocessed:
            self.log(u'processing version {}'.format(version.number))
            VersionRunner(self, version).perform()

    def filter_versions(self):
        db_versions = self.table.versions()
        db_version_numbers = set(v.number for v in db_versions)

        unprocessed = []
        for version in self.migrations.versions:
            # the filtered versions are shown before the unprocessed one,
            # which cause weird results sometimes
            if version.number in db_version_numbers:
                self.log(
                    u'version {} already installed'.format(version.number)
                )
                continue

            if version.is_noop():
                self.log(u'version {} noop'.format(version.number))
                continue
            unprocessed.append(version)
        return unprocessed


class VersionRunner(object):

    def __init__(self, runner, version):
        self.runner = runner
        self.table = runner.table
        self.migrations = runner.migrations
        self.config = runner.config
        self.cursor = runner.cursor
        self.version = version
        self.logs = []

    def log(self, message, raw=False):
        if raw:
            print(message, end='')
        else:
            app_message = u'\033[1m{}version {}: {}\033[0m'.format(
                LOG_DECORATION,
                self.version.number,
                message,
            )
            print(app_message)
        self.logs.append(message.strip() if raw else message)

    def start(self):
        self.log('start')
        self.table.start_version(self.version.number, datetime.now())

    def finish(self):
        addons_query = """
        SELECT name, state
        FROM ir_module_module
        """
        self.cursor.execute(addons_query)
        rows = self.cursor.fetchall()
        addons = [dict(zip(('name', 'state'), row)) for row in rows]
        self.log('done')
        self.table.finish_version(self.version.number, datetime.now(),
                                  '\n'.join(self.logs), addons)

    def perform(self):
        self.start()

        self.log(u'executing pre-operations')
        for operation in self.version.pre_operations:
            self.execute(operation.split())

        self.perform_addons()

        self.log(u'executing post-operations')
        for operation in self.version.post_operations:
            self.execute(operation.split())
        if self.config.demo:
            self.log(u'executing post-operations')
            for operation in self.version.demo_operations:
                self.execute(operation.split())

        self.finish()

    def perform_addons(self):
        version = self.version
        if version.install_addons or version.update_addons:
            install_command = self.migrations.install_command
            install_args = self.migrations.install_args
            install_args += [u'--workers=0', u'--stop-after-init']
            if version.install_addons:
                install_args += [u'-i', u','.join(version.install_addons)]
            if version.update_addons:
                install_args += [u'-u', u','.join(version.update_addons)]

            self.execute([install_command] + install_args)

        if version.uninstall_addons:
            # TODO uninstall with odoo.py's shell
            self.log(u'uninstall: {}'.format(version.uninstall_addons))

    # could be moved to the 'operation' model, with addons updates being
    # operations themselves
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
        # TODO: add 'show' mode that do nothing, only prints messages


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


def migrate(config):
    project_file = ProjectFileParser(config.project_file)
    project_file.parse()
    database = Database(config)
    with database.connect() as conn:
        with conn.cursor() as cursor:
            try:
                table = MigrationTable(cursor)
                runner = Runner(config, project_file.migrations, cursor, table)
                runner.perform()
            except:
                # We want to commit even if we had an error in a migration
                # script! Thus we have an entry in the migration table
                # indicating that a migration has been started but not
                # finished
                conn.commit()
                raise
            else:
                conn.commit()
            finally:
                conn.close()


def main():
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
    args = parser.parse_args()
    config = Config(args.project_file,
                    args.database,
                    db_user=args.db_user,
                    db_password=args.db_password,
                    db_port=args.db_port,
                    db_host=args.db_host,
                    demo=args.demo)
    migrate(config)

if __name__ == '__main__':
    main()
