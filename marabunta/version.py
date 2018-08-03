# -*- coding: utf-8 -*-
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import re
from distutils.version import Version


FIRST_VERSION = 'setup'


class MarabuntaVersion(Version):

    """Version numbering for Camptocamp software idealists.
    Implements the Camptocamp interface for version number classes as
    described above. A version number consists of three or five
    dot-separated numeric components, without any options.

    The following are valid version numbers (shown in the order that
    would be obtained by sorting according to the supplied cmp function):

        0.4.0       0.0.0.4.0  (these two are equivalent)
        0.4.1       0.0.0.4.1  (these two are equivalent)
        9.9.6       9.0.0.9.6  (these two are equivalent)
        10.0.4
        9.0.1.2.3
        10.0.0.1.2
        11.1.2.3.4

    The following are examples of invalid version numbers:

        1
        0.4
        0.5a1
        0.5b3
        2.7.2.2
        1.3.a4
        1.3pl1
        1.3c4
        11.0.1.2.3a1

    """

    version_re = re.compile(
        r'^(\d+)\.(\d+)\.(\d+)(\.(\d+)\.(\d+))?$|^' + FIRST_VERSION + '$',
        re.VERBOSE
    )

    def parse(self, version_str):
        match = self.version_re.match(version_str)
        if not match:
            raise ValueError("invalid version number '%s'" % version_str)

        if match.string == FIRST_VERSION:
            self.version = match.string
        else:
            (major, minor, patch, revision, build) = \
                match.group(1, 2, 3, 5, 6)

            if build:
                self.version = tuple(map(int, [
                    major, minor, patch, revision, build
                ]))
            else:
                self.version = tuple(map(int, [
                    major, 0, 0, minor, patch
                ]))

    def __str__(self):

        if self.version == FIRST_VERSION:
            return self.version

        version_str = '.'.join(map(str, self.version))

        return version_str

    def __cmp__(self, other):
        return self._cmp(other)

    def _cmp(self, other):
        if isinstance(other, str):
            other = MarabuntaVersion(other)

        if self.version != other.version:
            if self.version == FIRST_VERSION:
                return -1
            if other.version == FIRST_VERSION:
                return 1
            if self.version < other.version:
                return -1
            else:
                return 1
        return 0
