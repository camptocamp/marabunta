.. :changelog:

Release History
---------------

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
