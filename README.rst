🐜🐜🐜 Marabunta 🐜🐜🐜
=======================

.. image:: https://travis-ci.org/camptocamp/marabunta.svg?branch=master
    :target: https://travis-ci.org/camptocamp/marabunta

*Marabunta is a name given to the migration of the legionary ants or to the ants
themselves. Restless, they eat and digest everything in their way.*

Marabunta is used to provide an easy way to provide updates to Odoo which can be created fast and run easily. It also allows to differentiate between different environment to provide for instance demodata.


Usage
=====
After installing marabunta will be available as a console command. To run properly it requires a migration file () which defines what should be updated/executed) and odoos connection parameters (view options in the options section.

At each run marabunta verifies the versions from the migration file and and processes new ones.
It is very much recomended to configure it, so that marabunta is ran automatically if odoo is started.
For instance adding it to your docker entrypoint.

Features
========

* backup: Marabunta allows for a backup command to be executed before the migration.
* addon upgrades: Marabunta is able to install or upgrade odoo addons.
* addon uninstall: Addons which were previously installed can be removed with marabunta.
* operations: Allows to execute commands before or after upgrading modules.
* modes: Modes allow the user to execute commands only on a certain environment. i.e. creation of demodata on a dev system.
* maintenance page: publish an html page during the migration.

Versioning systems
------------------
Currently Marabunta allows for two different Versioning systems:
The classic Major.Minor.Bugfix and the Five digits long versions for OdooMajor.OdooMinor.Major.Minor.Bugfix.
Although the first marabunta version must be **setup** for the initial setup of your instance. (Find out more about the rationale here <https://github.com/camptocamp/marabunta/commit/9b96acaff8e7eecbf82ff592b7bb927b4cd82f02>)


Options
=======
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | option            | shortcut | envvar                    | purpose                                                           |
    +===================+==========+===========================+===================================================================+
    | --migration-file  | -f       | MARABUNTA_MIGRATION_FILE  | Definition file for the migration.                                |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --database        | -d       | MARABUNTA_DATABASE        | Database we want to run the migration on.                         |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --db-user         | -u       | MARABUNTA_DB_USER         | Database user.                                                    |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --db-password     | -w       | MARABUNTA_DB_PASSWORD     | Database password.                                                |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --db-port         | -p       | MARABUNTA_DB_PORT         | Database port (defaults to 5432).                                 |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --db-host         | -H       | MARABUNTA_DB_HOST         | Database port (defaults to localhost).                            |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --mode            |          | MARABUNTA_MODE            | Mode marabunta runs in for different envs.                        |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --allow-serie     |          | MARABUNTA_ALLOW_SERIE     | Allow multiple versions to be upgraded at once.                   |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --force-version   |          | MARABUNTA_FORCE_VERSION   | Force the upgrade to a version no matter what.                    |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --web-host        |          | MARABUNTA_WEB_HOST        | Interface to bind for the maintenance page. (defaults to 0.0.0.0).|
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --web-port        |          | MARABUNTA_WEB_PORT        | Port for the maintenance page. (defaults to 8069).                |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
    | --web-custom-html |          | MARABUNTA_WEB_CUSTOM_HTML | Path to custom maintenance html page to serve.                    |
    +-------------------+----------+---------------------------+-------------------------------------------------------------------+
                                                          
YAML layout & Example
=====================
.. include:: docs/migration_example.yml


Run the tests
-------------

To run ``marabunta`` tests, it is a good idea to do an *editable*
install of it in a virtualenv, and then intall and run ``pytest`` as
follows::

  $ git clone https://github.com/camptocamp/marabunta.git
  Cloning into 'marabunta'...
  $ cd marabunta
  $ virtualenv -p YOUR_PYTHON env
  $ source env/bin/activate
  $ pip install '.[test]'
  $ py.test tests
