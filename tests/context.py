# -*- coding: utf-8 -*-

# flake8: noqa
# we want to ignore:
# F401 'marabunta' imported but unused
# E402 module level import not at top of file

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# put the marabunta package in the python path so we can use
# it in tests without the need to be installed in site-packages

import marabunta  # noqa: imported from other test files
