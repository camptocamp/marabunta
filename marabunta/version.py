# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import annotations

import re
from typing import Literal

FIRST_VERSION: Literal["setup"] = "setup"


class MarabuntaVersion:
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

    version: Literal["setup"] | tuple[int, int, int, int, int]

    version_re = re.compile(
        r"^(\d+)\.(\d+)\.(\d+)(\.(\d+)\.(\d+))?$|^" + FIRST_VERSION + "$", re.VERBOSE
    )

    def __init__(self, vstring: str | None = None) -> None:
        if vstring:
            self.parse(vstring)

    def parse(self, version_str: str) -> None:
        match = self.version_re.match(version_str)
        if not match:
            raise ValueError(f"invalid version number '{version_str}'")

        if match.string == FIRST_VERSION:
            self.version = FIRST_VERSION
        else:
            (major, minor, patch, revision, build) = match.group(1, 2, 3, 5, 6)

            if build:
                self.version = (
                    int(major),
                    int(minor),
                    int(patch),
                    int(revision),
                    int(build),
                )
            else:
                self.version = (int(major), 0, 0, int(minor), int(patch))

    def __str__(self) -> str:
        if self.version == FIRST_VERSION:
            return self.version
        return ".".join(map(str, self.version))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} ('{self!s}')"

    def _cmp(self, other) -> int:
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

    def __eq__(self, other) -> bool:
        return self._cmp(other) == 0

    def __ne__(self, other) -> bool:
        return self._cmp(other) != 0

    def __lt__(self, other) -> bool:
        return self._cmp(other) < 0

    def __le__(self, other) -> bool:
        return self._cmp(other) <= 0

    def __gt__(self, other) -> bool:
        return self._cmp(other) > 0

    def __ge__(self, other) -> bool:
        return self._cmp(other) >= 0

    def __hash__(self) -> int:
        return hash(self.version)
