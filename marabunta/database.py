# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json
import urllib


import psycopg2

from collections import namedtuple
from contextlib import contextmanager


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
        self.table_name = 'marabunta_version'
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
