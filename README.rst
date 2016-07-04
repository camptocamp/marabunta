🐜🐜🐜 Marabunta 🐜🐜🐜
=======================

.. image:: https://travis-ci.org/camptocamp/marabunta.svg?branch=master
    :target: https://travis-ci.org/camptocamp/marabunta

Marabunta is a name given to the migration of the legionary ants or to the ants
themselves. Restless, they eat and digest everything in their way.

This tool aims to run migrations for Odoo versions as efficiently as a
Marabunta migration.

It loads migration instructions from a YAML file and run the operations if
required.

Run the tests
-------------

To run ``marabunta`` tests, it is a good idea to do an *editable*
install of it in a virtualenv, and then intall and run ``pytest`` as
follows::

  $ git clone https://github.com/camptocamp/marabunta.git
  Cloning into 'marabunta'...
  $ cd marabunta
  $ python2 -m virtualenv env
  $ source env/bin/activate
  $ pip install -e .
  $ pip install pytest
  $ py.test tests

