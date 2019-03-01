# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from io import StringIO
import pytest
from marabunta.parser import YamlParser, YAML_EXAMPLE
from ruamel.yaml.constructor import DuplicateKeyError

YAML_WITH_EXCEPTION = u"""
migration:
  options:
    # --workers=0 --stop-after-init are automatically added
    install_command: odoo
    install_args: --log-level=debug
    backup:
      command: echo "backup command on $database $db_user $db_password $db_host $db_port"
      stop_on_failure: true
      ignore_if: test "${RUNNING_ENV}" != "prod"
  versions:
    - version: setup
      operations:
        pre:  # executed before 'addons'
          - echo 'pre-operation'
      addons:
        upgrade:  # executed as odoo --stop-after-init -i/-u ...
          - base
          - document
        # remove:  # uninstalled with a python script
      operations:
        post:  # executed after 'addons'
          - anthem songs::install
"""  # noqa


def test_parse_yaml_example():
    file_example = StringIO(YAML_EXAMPLE)
    parser = YamlParser.parser_from_buffer(file_example)
    migration = parser.parse()
    assert len(migration.versions) == 4


def test_dublicate_key_exception():
    yaml_file = StringIO(YAML_WITH_EXCEPTION)
    with pytest.raises(DuplicateKeyError):
        parser = YamlParser.parser_from_buffer(yaml_file)
        parser.parse()
