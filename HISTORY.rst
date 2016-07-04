.. :changelog:

Release History
---------------

0.3.0-dev
+++++++++

**Backward incompatible changes**

- ``--demo`` is replaced by a more general ``--mode`` argument,
  the equivalent being ``--mode=demo``
- ``MARABUNTA_DEMO`` is replaced by ``MARABUNTA_MODE``
- the configuration file has now operations by "modes", allowing to
  load some different scripts for different modes ("base" is always
  executed and always first)::

    base:
      pre:  # executed before 'addons'
        - echo 'pre-operation'
      post:  # executed after 'addons'
        - anthem songs::install
    prod:
      pre:
        - echo 'pre-operation executed only when the mode is prod'
      post:
        - anthem songs::load_production_data
    demo:
      post:
        - anthem songs::load_demo_data

- ``--force`` renamed to ``--allow-serie``
- ``MARABUNTA_FORCE`` renamed to ``MARABUNTA_ALLOW_SERIE``

**Improvements**

- When 'allow_serie' is used, the same Odoo addon will not be
  upgraded more than one time when it is in the 'upgrade' section of
  more than one version

**Fixes**

- Fix error when there is no db version in the database

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
