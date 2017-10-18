# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import unittest

from marabunta.model import Operation


class TestOperation(unittest.TestCase):

    def test_from_single_unicode(self):
        op = Operation(u'ls -l')
        self.assertEqual(op.command, ['ls', '-l'])

    def test_from_single_str(self):
        op = Operation('ls -l')
        self.assertEqual(op.command, ['ls', '-l'])

    def test_from_list_of_unicode(self):
        op = Operation([u'ls', u'-l'])
        self.assertEqual(op.command, ['ls', '-l'])

    def test_from_list_of_str(self):
        op = Operation(['ls', '-l'])
        self.assertEqual(op.command, ['ls', '-l'])
