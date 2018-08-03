# -*- coding: utf-8 -*-
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from marabunta.version import MarabuntaVersion


def test_marabuntaversion():
    versions = (
        ('1.5.1', '1.5.2b2', ValueError),
        ('161', '3.10a', ValueError),
        ('8.02', '8.02', ValueError),
        ('3.4j', '1996.07.12', ValueError),
        ('3.2.pl0', '3.1.1.6', ValueError),
        ('2g6', '11g', ValueError),
        ('0.9', '2.2', ValueError),
        ('1.2.1', '1.2', ValueError),
        ('1.1', '1.2.2', ValueError),
        ('1.2', '1.1', ValueError),
        ('1.2.1', '1.2.2', -1),
        ('1.2.2', '1.2', ValueError),
        ('1.2', '1.2.2', ValueError),
        ('0.4.0', '0.4', ValueError),
        ('1.13++', '5.5.kw', ValueError),

        ('0.4.0', '0.4.0', 0),
        ('0.4.0', '0.4.1', -1),
        ('0.4.1', '0.4.0', 1),
        ('0.4.0', '0.0.0.4.0', 0),
        ('9.9.6', '9.0.0.9.6', 0),
        ('9.0.1.2.3', '9.0.1.2.3', 0),
        ('9.0.1.2.3', '10.0.0.1.2', -1),
        ('10.0.1.2.3', '10.0.3.1.2', -1),
        ('10.0.0.1.0', '10.0.0.1.2', -1),
        ('11.0.0.0.1', '11.0.0.1.0', -1),
        ('9.0.1.2.3', '9.0.1.2.2', 1),
        ('10.0.3.1.2', '10.0.1.2.3', 1),
        ('10.0.0.1.2', '10.0.0.1.0', 1),
        ('11.0.0.1.0', '11.0.0.0.1', 1),

        ('setup', 'setup', 0),
        ('0.0.0', 'setup', 1),
        ('setup', '0.0.0', -1),
        ('0.0.0.0.0', 'setup', 1),
        ('setup', '0.0.0.0.0', -1),
        ('1.2.3', 'setup', 1),
        ('setup', '4.5.6', -1),
        ('11.0.1.0.0', 'setup', 1),
        ('setup', '10.0.0.0.1', -1),
    )

    for v1, v2, expected in versions:
        try:
            actual = MarabuntaVersion(v1)._cmp(MarabuntaVersion(v2))
        except ValueError:
            if expected is ValueError:
                continue
            else:
                raise AssertionError(("cmp(%s, %s) "
                                      "shouldn't raise ValueError")
                                     % (v1, v2))
        assert expected == actual
