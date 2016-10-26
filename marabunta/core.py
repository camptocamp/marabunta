# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
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

import time

from .config import Config, get_args_parser
from .database import Database, MigrationTable
from .output import safe_print
from .parser import YamlParser
from .runner import Runner

__version__ = "0.5.1"

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


def migrate(config):
    """Perform a migration according to config.

    :param config: The configuration to be applied
    :type config: Config
    """
    migration_parser = YamlParser.parse_from_file(config.migration_file)
    migration = migration_parser.parse()
    database = Database(config)
    with database.connect() as conn:
        with conn.cursor() as cursor:
            try:
                # If the migration is run concurrently (in several
                # containers, hosts, ...), only 1 is allowed to proceed
                # with the migration. It will be the first one to win
                # the advisory lock. The others will be flagged as 'replica'.
                replica = False
                while not pg_advisory_lock(cursor, ADVISORY_LOCK_IDENT):
                    if not replica:  # print only the first time
                        safe_print('A concurrent process is already '
                                   'running the migration')
                    replica = True
                    time.sleep(0.5)
                else:
                    # when a replica could finally acquire a lock, it
                    # means that the main process has finished the
                    # migration. In that case, the replica should just
                    # exit because the migration already took place. We
                    # wait till then to be sure we won't run Odoo before
                    # the main process could finish the migration.
                    if replica:
                        return

                table = MigrationTable(cursor)
                runner = Runner(config, migration, cursor, table)
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
    """Parse the command line and run :func:`migrate`."""
    parser = get_args_parser()
    args = parser.parse_args()
    config = Config.from_parse_args(args)
    migrate(config)

if __name__ == '__main__':
    main()
