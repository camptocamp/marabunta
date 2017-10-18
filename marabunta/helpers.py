# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import sys
PY3 = sys.version_info[0] == 3
string_types = (str, bytes) if PY3 else (str, unicode)   # noqa
