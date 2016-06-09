# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import unittest

from io import StringIO

from marabunta.parser import YamlParser, YAML_EXAMPLE


class ParseTestSuite(unittest.TestCase):

    def test_parse_yaml_example(self):
        file_example = StringIO(YAML_EXAMPLE)
        parser = YamlParser.parser_from_buffer(file_example)
        migration = parser.parse()
        self.assertEqual(len(migration.versions), 4)


if __name__ == '__main__':
    unittest.main()
