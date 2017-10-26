# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from io import StringIO

from marabunta.parser import YamlParser, YAML_EXAMPLE


def test_parse_yaml_example():
    file_example = StringIO(YAML_EXAMPLE)
    parser = YamlParser.parser_from_buffer(file_example)
    migration = parser.parse()
    assert len(migration.versions) == 4
