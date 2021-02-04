# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

"""
Marabunta is a name given to the migration of the legionary ants or to the ants
themselves. Restless, they eat and digest everything in their way.

This tool aims to run migrations for Odoo versions as efficiencly as a
Marabunta migration.

It loads migration instructions from a YAML file and run the operations if
required.

"""

from __future__ import print_function

import logging
import time
import threading

from .config import Config, get_args_parser
from .database import Database, MigrationTable
from .output import safe_print
from .parser import YamlParser
from .runner import Runner
from .web import WebApp

from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

logging.getLogger('werkzeug').setLevel(logging.ERROR)

# The number below has been generated as below:
# pg_lock accepts an int8 so we build an hash composed with
# contextual information and we throw away some bits
#     lock_name = 'marabunta'
#     hasher = hashlib.sha1()
#     hasher.update('{}'.format(lock_name))
#     lock_ident = struct.unpack('q', hasher.digest()[:8])
# we just need an integer
ADVISORY_LOCK_IDENT = 7141416871301361999


def pg_advisory_lock(cursor, lock_ident):
    cursor.execute('SELECT pg_try_advisory_xact_lock(%s);', (lock_ident,))
    acquired = cursor.fetchone()[0]
    return acquired


class ApplicationLock(threading.Thread):

    def __init__(self, connection):
        self.acquired = False
        self.connection = connection
        self.replica = False
        self.stop = False
        super(ApplicationLock, self).__init__()

    def run(self):
        with self.connection.cursor() as cursor:
            # If the migration is run concurrently (in several
            # containers, hosts, ...), only 1 is allowed to proceed
            # with the migration. It will be the first one to win
            # the advisory lock. The others will be flagged as 'replica'.
            while not pg_advisory_lock(cursor, ADVISORY_LOCK_IDENT):
                if not self.replica:  # print only the first time
                    safe_print('A concurrent process is already '
                               'running the migration')
                self.replica = True
                time.sleep(0.5)
            else:
                self.acquired = True
                idx = 0
                while not self.stop:
                    # keep the connection alive to maintain the advisory
                    # lock by running a query every 30 seconds
                    if idx == 60:
                        cursor.execute("SELECT 1")
                        idx = 0
                    idx += 1
                    # keep the sleep small to be able to exit quickly
                    # when 'stop' is set to True
                    time.sleep(0.5)


class WebServer(threading.Thread):

    def __init__(self, app):
        super(WebServer, self).__init__()
        self.app = app

    def run(self):
        self.app.serve()


def migrate(config):
    """Perform a migration according to config.

    :param config: The configuration to be applied
    :type config: Config
    """
    webapp = WebApp(config.web_host, config.web_port,
                    custom_maintenance_file=config.web_custom_html,
                    resp_status=config.web_resp_status,
                    resp_retry_after=config.web_resp_retry_after,
                    healthcheck_path=config.web_healthcheck_path)

    webserver = WebServer(webapp)
    webserver.daemon = True
    webserver.start()

    migration_parser = YamlParser.parse_from_file(config.migration_file)
    migration = migration_parser.parse()

    database = Database(config)

    with database.connect() as lock_connection:
        application_lock = ApplicationLock(lock_connection)
        application_lock.start()

        while not application_lock.acquired:
            time.sleep(0.5)
        else:
            if application_lock.replica:
                # when a replica could finally acquire a lock, it
                # means that the concurrent process has finished the
                # migration or that it failed to run it.
                # In both cases after the lock is released, this process will
                # verify if it has still to do something (if the other process
                # failed mainly).
                application_lock.stop = True
                application_lock.join()
            # we are not in the replica or the lock is released: go on for the
            # migration

        try:
            table = MigrationTable(database)
            runner = Runner(config, migration, database, table)
            runner.perform()
        finally:
            application_lock.stop = True
            application_lock.join()


def main():
    """Parse the command line and run :func:`migrate`."""
    parser = get_args_parser()
    args = parser.parse_args()
    config = Config.from_parse_args(args)
    migrate(config)


if __name__ == '__main__':
    main()
