.. :changelog:

Release History
---------------

Unreleased
++++++++++

**Features**

**Bugfixes**

**Improvements**

**Documentation**

**Build**

* Test for python 3.6, 3.7 and 3.8

0.10.6 (2021-09-14)
+++++++++++++++++++

**Improvements**

* Web server returns status 503 instead of 200
* New option 'web-healthcheck-path'

0.10.5 (2020-12-08)
+++++++++++++++++++

**Bugfixes**

* Fix backup operation if force_version is set

**Improvements**

* Prevent text from bouncing in maintenance page
* raise an exception if there is duplicate keys in migration file

0.10.4 (2019-02-15)
+++++++++++++++++++

**Bugfixes**

* Fix BoolEnvDefault when envvar is not defined

0.10.3 (2019-02-13)
+++++++++++++++++++

**Bugfixes**

* ALLOW_SERIES shouldn't be true if a false value is given.

0.10.2 (2018-12-12)
+++++++++++++++++++

**Bugfixes**

* Crash when forcing upgrade of a version and no backup command is configured

0.10.1 (2018-11-09)
+++++++++++++++++++

**Build**

* The lib is now automaticaly published to Pypi by Travis when a tag is added


0.10.0 (2018-11-06)
+++++++++++++++++++

**Backward incompatible change**

* In the migration yaml file, the ``command`` and ``command_args`` options are
  now all merged into ``command``

**Features**

* Backup command and backup's ignore_if are now run in a 'sh' shell so we can
  inject environment variables in the commands
* Backup command can now use ``$database``, ``$db_host``, ``$db_port``,
  ``$db_user``, ``$db_password`` that will be substituted by the current
  configuration values

**Bugfixes**

* When starting 2 concurrent marabunta process and the first fail, it releases
  the lock and the second would start odoo without actually run the migration.
  Now, when the migration lock is released, the other process(es) will recheck
  all versions as well before running odoo.

**Documentation**

* Add some high-level documentation


0.9.0 (2018-09-04)
++++++++++++++++++

**Features**


* 1st version it's always "setup"

  In all projects' usecases the 1st version is always to setup the initial state.
  Adopting `setup` as the 1st version makes also easier to squash intermediate version
  all in one as the project and its releases grow up.

* Support 5 digits version

  Now you can use 5 digits versions as per odoo modules.
  For instance: `11.0.3.0.1`. This give us better numbering for patches
  and makes versionig withing Odoo world more consistent.
  Old 3 digits versions are still supported for backward compat.

Full rationale for above changes available here

https://github.com/camptocamp/marabunta/commit/9b96acaff8e7eecbf82ff592b7bb927b4cd82f02

* Backup option

  Migration allows using a `backup` command in order to perform specific
  commands (unless explicitly opted-out) before the migration step.

  No backup machinery provided as you are suppose to run your own command
  to execute the backup.


**Bugfixes**

* Build Py3 wheel on release


0.8.0 (2017-11-16)
++++++++++++++++++

Python3!

0.7.3 (2017-11-01)
++++++++++++++++++

**Bugfixes**

* Support special chars (such as +) in Postgres passwords. The passwords were
  incorrectly passed through unquote_plus, which transform the + char to a
  space.

0.7.2 (2017-09-15)
++++++++++++++++++

**Bugfixes**

* Use --no-xmlrpc option when running odoo as the new web server use the same port,
  it's not needed anyway

0.7.1 (2017-09-11)
++++++++++++++++++

**Bugfixes**

* Include maintenance html file in the distribution


0.7.0 (2017-09-08)
++++++++++++++++++

**Features**

* Publish a maintenance web page during migration. The host and port are
  configurable with new options. By default the port match odoo's (8069). A
  default maintenance is provided, but it can be configured as well.
* When a migration fails, the log alongside the traceback are logged in the
  ``marabunta_version`` table.

**Bugfixes**

* Commands with unicode chars make the migration fail

**Build**

* Removed python3 from tox, it doesn't run on py3 and we can't make them run
  now. Odoo is still python2, py3 compat will come when it'll switch.


0.6.3 (2016-12-12)
++++++++++++++++++


**Bugfixes**

* The new connection opened in 0.6.2 might suffer from the same issue of
  timeout than before 0.6.0: the connection is long-lived but there is no
  keep-alive for this connection. Open a new connection for each update in
  marabunta_version, which might be spaced between long subprocess operations


0.6.2 (2016-12-12)
++++++++++++++++++

**Bugfixes**

* Autocommit the operations done in the marabunta_version table.  Previously,
  after an exception, the changes to marabunta_version were rollbacked, which
  is not the expected behavior (it makes the migration restart ceaseless).
  As a side effect, Marabunta now opens 2 connections. The connection opened
  for the adsivory lock cannot commit before the end because it would release
  the lock.


0.6.1 (2016-11-25)
++++++++++++++++++

Important bugfix! The changes in the ``marabunta_version`` were never
committed, so migration would run again.

**Bugfixes**

* Commit the connection so changes are not rollbacked.

0.6.0 (2016-11-21)
++++++++++++++++++

**Improvements**

* Rework of the database connections:

  * The advisory lock is opened in a cursor in a thread, this cursor
    periodically executes a dummy 'SELECT 1' to be sure that the connection
    stay alive (not killed with a timeout) when a long-running subprocess is
    run.
  * The operations in database are executed in short-lived cursors. This
    prevents an issue we had when the open cursor was locking
    'ir_module_module', preventing odoo to install/update properly.

* Try to disable colors in output if the term does not support colors


0.5.1 (2016-10-26)
++++++++++++++++++

* Fix: marabunta processes run concurrently all tried to run the migration,
  this is better handled with a PostgreSQL advisory lock now


0.5.0 (2016-10-12)
++++++++++++++++++

Odoo 10 Support

**Features**

- Switch the default command line for running odoo to ``odoo`` instead of
  ``odoo.py`` (renamed in Odoo 10). For usage with previous version, you must
  specify the ``install_command`` in the ``migration.yml`` file.


0.4.2 (2016-08-17)
++++++++++++++++++

**Bugfixes**

- Prevent error (25, 'Inappropriate ioctl for device') when
  stdout is not a tty by disabling the interactive mode.


0.4.1 (2016-07-27)
++++++++++++++++++

**Bugfixes**

- Do not print on stdout the result of operations twice


0.4.0 (2016-07-26)
++++++++++++++++++

**Improvements**

- New dependency on ``pexpect``. Used to create a pseudo-tty to execute the
  operations.  It enables line buffering and interactivity for pdb in the
  children processes.

**Fixes**

- Noop operations are really considered as such


0.3.3 (2016-07-12)
++++++++++++++++++

**Fixes**

- Encode print's outputs to the stdout's encoding or to utf8 by default

0.3.2 (2016-07-08)
++++++++++++++++++

**Fixes**

- Failure when there are no version to process

0.3.1 (2016-07-07)
++++++++++++++++++

**Fixes**

- Fix decoding issues with output of subprocesses

0.3.0 (2016-07-06)
++++++++++++++++++

Introducing **modes**.

**Backward incompatible changes**

- ``--demo`` is replaced by a more general ``--mode`` argument,
  the equivalent being ``--mode=demo``
- ``MARABUNTA_DEMO`` is replaced by ``MARABUNTA_MODE``
- the configuration file has now operations and addons by "modes", allowing to
  load some different scripts or install different addons for different modes
  (the addons list are merged and the operations of the modes are executed
  after the main ones)::

    - version: 0.0.1
      operations:
        pre:  # executed before 'addons'
          - echo 'pre-operation'
        post:  # executed after 'addons'
          - anthem songs::install
      addons:
        upgrade:
          - base
      modes:
        prod:
          operations:
            pre:
              - echo 'pre-operation executed only when the mode is prod'
            post:
              - anthem songs::load_production_data
        demo:
          operations:
            post:
              - anthem songs::load_demo_data
          addons:
            upgrade:
              - demo_addon

- ``--force`` renamed to ``--allow-serie``
- ``MARABUNTA_FORCE`` renamed to ``MARABUNTA_ALLOW_SERIE``
- ``--project-file`` renamed to ``--migration-file``
- ``MARABUNTA_PROJECT_FILE`` renamed to ``MARABUNTA_MIGRATION_FILE``

**Improvements**

- When 'allow_serie' is used, the same Odoo addon will not be
  upgraded more than one time when it is in the 'upgrade' section of
  more than one version

**Fixes**

- Fix error when there is no db version in the database
- Fix error ``AttributeError: 'bool' object has no attribute 'number'``
  when there is an unfinished version
- Fix error when the db version is above the unprocessed version

0.2.2 (2016-06-23)
++++++++++++++++++

**Improvements**

- Adapted the README so that it is rendered as ReST on pypi.

0.2.1 (2016-06-23)
++++++++++++++++++

**Bugfixes**

- Fixed the version information of the package and release date.

0.2.0 (2016-06-23)
++++++++++++++++++

**Features**

- Added support for Python 3.4 and 3.5 in addition to 2.7.

**Bugfixes**

- Fixed a crash with empty install args

**Improvements**

- Use YAML ``safe_load`` for added security.

**Documentation**

- Bootstrapped the Sphinx documentation.

**Build**

- Switched to tox for the build. This allow to run the same tests in all
  environment locally like in travis. The travis configuration just calls tox
  now.
- Added runtime dependencies to the package, kept separate from the build and test dependencies (installed separately by tox).

0.1.1 (2016-06-08)
++++++++++++++++++

- Fixed problems with packaging so that now marabunta can be installable from
  pypi.

0.1.0 (2016-06-08)
++++++++++++++++++

Initial release. This corresponds to the initial work of Guewen Baconnier.
