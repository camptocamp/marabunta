# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from marabunta.model import Operation


def test_from_single_unicode():
    op = Operation(u'ls -l')
    assert op.command == ['ls', '-l']


def test_from_single_str():
    op = Operation('ls -l')
    assert op.command == ['ls', '-l']


def test_from_list_of_unicode():
    op = Operation([u'ls', u'-l'])
    assert op.command == ['ls', '-l']


def test_from_list_of_str():
    op = Operation(['ls', '-l'])
    assert op.command == ['ls', '-l']




