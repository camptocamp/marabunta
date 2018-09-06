# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json

import psycopg2

from collections import namedtuple
from contextlib import contextmanager


class Database(object):

    def __init__(self, config):
        self.config = config
        self.name = config.database

    def dsn(self):
        cfg = self.config
        params = {
            'dbname': cfg.database,
        }
        if cfg.db_host:
            params['host'] = cfg.db_host
        if cfg.db_port:
            params['port'] = cfg.db_port
        if cfg.db_user:
            params['user'] = cfg.db_user
        if cfg.db_password:
            params['password'] = cfg.db_password
        return params

    @contextmanager
    def connect(self, autocommit=False):
        with psycopg2.connect(**self.dsn()) as conn:
            if autocommit:
                conn.autocommit = True
            yield conn

    @contextmanager
    def cursor_autocommit(self):
        with self.connect(autocommit=True) as conn:
            with conn.cursor() as cursor:
                yield cursor


VersionRecord = namedtuple(
    'VersionRecord',
    'number date_start date_done log addons'
)


class MigrationTable(object):

    def __init__(self, database):
        self.database = database
        self.table_name = 'marabunta_version'
        self.VersionRecord = VersionRecord
        self._versions = None

    def create_if_not_exists(self):
        with self.database.cursor_autocommit() as cursor:
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
            cursor.execute(query)

    def versions(self):
        """ Read versions from the table

        The versions are kept in cache for the next reads.
        """
        if self._versions is None:
            with self.database.cursor_autocommit() as cursor:
                query = """
                SELECT number,
                       date_start,
                       date_done,
                       log,
                       addons
                FROM {}
                """.format(self.table_name)
                cursor.execute(query)
                rows = cursor.fetchall()
                versions = []
                for row in rows:
                    row = list(row)
                    # convert 'addons' to json
                    row[4] = json.loads(row[4]) if row[4] else []
                    versions.append(
                        self.VersionRecord(*row)
                    )
                self._versions = versions
        return self._versions

    def start_version(self, number, start):
        with self.database.cursor_autocommit() as cursor:
            query = """
            SELECT number FROM {}
            WHERE number = %s
            """.format(self.table_name)
            cursor.execute(query, (number,))
            if cursor.fetchone():
                query = """
                UPDATE {}
                SET date_start = %s,
                    date_done = NULL,
                    log = NULL,
                    addons = NULL
                WHERE number = %s
                """.format(self.table_name)
                cursor.execute(query, (start, number))
            else:
                query = """
                INSERT INTO {}
                (number, date_start)
                VALUES (%s, %s)
                """.format(self.table_name)
                cursor.execute(query, (number, start))
        self._versions = None  # reset versions cache

    def record_log(self, number, log):
        with self.database.cursor_autocommit() as cursor:
            query = """
            UPDATE {}
            SET log = %s
            WHERE number = %s
            """.format(self.table_name)
            cursor.execute(query, (log, number))
            self._versions = None  # reset versions cache

    def finish_version(self, number, end, log, addons):
        with self.database.cursor_autocommit() as cursor:
            query = """
            UPDATE {}
            SET date_done = %s,
                log = %s,
                addons = %s
            WHERE number = %s
            """.format(self.table_name)
            cursor.execute(query, (end, log, json.dumps(addons), number))
            self._versions = None  # reset versions cache


class IrModuleModule(object):

    def __init__(self, database):
        self.database = database
        self.table_name = 'ir_module_module'
        self.ModuleRecord = namedtuple(
            'ModuleRecord',
            'name state'
        )

    def read_state(self):
        with self.database.cursor_autocommit() as cursor:
            if not table_exists(cursor, self.table_name):
                # relation ir_module_module does not exists,
                # this is a new DB, no addon is installed
                return []

            addons_query = """
            SELECT name, state
            FROM {}
            """.format(self.table_name)
            cursor.execute(addons_query)
            rows = cursor.fetchall()
        return [self.ModuleRecord(*row) for row in rows]


def table_exists(cursor, tablename, schema='public'):
    query = """
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = %s
        AND table_name = %s
    )"""
    cursor.execute(query, (schema, tablename))
    res = cursor.fetchone()[0]
    return res
