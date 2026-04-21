# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import sys

LOG_DECORATION = "|> "

supports_colors = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def print_decorated(message: str, *args, **kwargs) -> None:
    message = f"{LOG_DECORATION}{message}"
    if supports_colors:
        message = f"\033[1m{message}\033[0m"
    safe_print(message, *args, **kwargs)


def safe_print(ustring: str, errors: str = "replace", **kwargs) -> None:
    """Safely print a unicode string"""
    print(ustring, **kwargs)
