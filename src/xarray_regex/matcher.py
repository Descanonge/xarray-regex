"""Matcher object."""

# This file is part of the 'xarray-regex' project
# (http://github.com/Descanonge/xarray-regex) and subject
# to the MIT License as defined in the file 'LICENSE',
# at the root of this project. © 2021 Clément Haëck

import re
from .format import generate_expression

from typing import Any


class Matcher():
    """Manage a matcher inside the pre-regex.

    Parameters
    ----------
    m: re.match
        Match object obtained to find matchers in the pre-regex.
    idx: int
        Index inside the pre-regex.

    Attributes
    ----------
    idx: int
        Index inside the pre-regex.
    group: str
        Group name.
    name: str
        Matcher name.
    custom: bool
        If there is a custom regex to use preferentially.
    rgx: str
        Regex.
    discard: bool
        If the matcher should not be used when retrieving values from matches.
    match: str
        The string that created the matcher `%(match)`.
    """

    DEFAULT_ELTS = {
        "idx": [r"\d+", 'd'],
        "Y": [r"\d\d\d\d", '04d'],
        "m": [r"\d\d", '02d'],
        "d": [r"\d\d", '02d'],
        "j": [r"\d\d\d", '03d'],
        "H": [r"\d\d", '02d'],
        "M": [r"\d\d", '02d'],
        "S": [r"\d\d", '02d'],
        "x": [r"%Y%m%d", '08d'],
        "X": [r"%H%M%S", '08d'],
        "F": [r"%Y-%m-%d", 's'],
        "B": [r"[a-zA-Z]*", 's'],
        "text": [r"[a-zA-Z]*", 's'],
        "char": [r"\S*", 's']
    }
    """Regex str for each type of element."""

    REGEX = (r"%\((?:(?P<group>[a-zA-Z]*):)?"
             r"(?P<name>[a-zA-Z]*)"
             r"(:rgx=(?P<rgx>.*?))?"
             r"(:fmt=(?P<fmt>.*?))?"
             r"(?P<discard>:discard)?\)")
    """Regex to find matcher in pre-regex."""

    def __init__(self, m: re.match, idx: int = 0):
        self.idx = idx
        self.group = None
        self.name = None
        self.rgx = None
        self.discard = False
        self.fmt = None

        self.match = m.group()[2:-1]  # slicing removes %()

        self.set_matcher(m)

    def __repr__(self):
        return '\n'.join([super().__repr__(), self.__str__()])

    def __str__(self):
        return '{}: {}'.format(self.idx, self.match)

    def set_matcher(self, m: re.match):
        """Find attributes from match.

        Raises
        ------
        NameError
            No name.
        ValueError
            Empty custom regex.
        """
        group = m.group('group')
        name = m.group('name')
        rgx = m.group('rgx')
        fmt = m.group('fmt')

        if name is None:
            raise NameError("Matcher name cannot be empty.")
        if rgx is not None and rgx == '':
            raise ValueError("Matcher custom regex cannot be empty.")
        if fmt is not None and fmt == '':
            raise ValueError("Matcher custom format cannot be empty.")

        self.group = group
        self.name = name
        self.discard = m.group('discard') is not None

        if name in self.DEFAULT_ELTS:
            self.rgx, self.format = self.DEFAULT_ELTS[name]

        if rgx:
            self.rgx = rgx
        if fmt:
            self.fmt = fmt
            if not rgx and name not in self.DEFAULT_ELTS:
                self.rgx = generate_expression(fmt)

    def format(self, value: Any):
        return '{{:{}}}'.format(self.fmt).format(value)

    def get_regex(self) -> str:
        """Get matcher regex.

        Replace the matchers name by regex from `Matcher.NAME_RGX`. If there is
        a custom regex, recursively replace '%' followed by a single letter by
        the corresponding regex from `NAME_RGX`. '%%' is replaced by a single
        percentage character.

        Raises
        ------
        KeyError
            Unknown replacement.
        """
        def replace(match):
            group = match.group(1)
            if group == '%':
                return '%'
            if group in self.NAME_RGX:
                replacement = self.NAME_RGX[group]
                if '%' in replacement:
                    return self.get_regex(replacement)
                return replacement
            raise KeyError("Unknown replacement '{}'.".format(match.group(0)))

        return re.sub("%([a-zA-Z%])", replace, self.rgx)
