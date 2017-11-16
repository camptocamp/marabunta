# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import print_function

import sys

LOG_DECORATION = u'|> '

supports_colors = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def print_decorated(message, *args, **kwargs):
    if supports_colors:
        template = u'\033[1m{}{}\033[0m'
    else:
        template = u'{}{}'
    message = template.format(
        LOG_DECORATION,
        message,
    )
    safe_print(message, *args, **kwargs)


def safe_print(ustring, errors='replace', **kwargs):
    """ Safely print a unicode string """
    encoding = sys.stdout.encoding or 'utf-8'
    if sys.version_info[0] == 3:
        print(ustring, **kwargs)
    else:
        bytestr = ustring.encode(encoding, errors=errors)
        print(bytestr, **kwargs)
