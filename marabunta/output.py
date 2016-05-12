# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import print_function

LOG_DECORATION = u'|> '


def print_decorated(message, *args, **kwargs):
    message = u'\033[1m{}{}\033[0m'.format(
        LOG_DECORATION,
        message,
    )
    print(message, *args, **kwargs)
