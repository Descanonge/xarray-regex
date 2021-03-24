"""Matches management."""

# This file is part of the 'xarray-regex' project
# (http://github.com/Descanonge/xarray-regex) and subject
# to the MIT License as defined in the file 'LICENSE',
# at the root of this project. © 2021 Clément Haëck

import re
import logging
from typing import Any, List, Union

from .format import Format


log = logging.getLogger(__name__)


class Matcher():
    """Manage a matcher inside the pre-regex.

    Parameters
    ----------
    m: re.Match
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
    rgx: str
        Regex.
    discard: bool
        If the matcher should not be used when retrieving values from matches.
    fmt: Format
        Format string object.
    match: str
        The string that created the matcher `%(match)`.
    """

    DEFAULT_ELTS = {
        "I": [r"\d+", 'd'],
        "Y": [r"\d{4}", '04d'],
        "m": [r"\d\d", '02d'],
        "d": [r"\d\d", '02d'],
        "j": [r"\d{3}", '03d'],
        "H": [r"\d\d", '02d'],
        "M": [r"\d\d", '02d'],
        "S": [r"\d\d", '02d'],
        "x": [r"%Y%m%d", '08d'],
        "X": [r"%H%M%S", '06d'],
        "F": [r"%Y-%m-%d", 's'],
        "B": [r"[a-zA-Z]*", 's'],
        "text": [r'\w', 's'],
        "char": [r"\S*", 's']
    }
    """Regex str for each type of element."""

    REGEX = (r"%\((?:(?P<group>\w*):)?"
             r"(?P<name>\w*)"
             r"(:fmt=(?P<fmt>.*?))?"
             r"(:(?:rgx|custom)=(?P<rgx>.*?))?"
             r"(?P<discard>:discard)?\)")
    """Regex to find matcher in pre-regex."""

    def __init__(self, m: re.Match, idx: int = 0):
        self.idx = idx
        self.group = None
        self.name = None
        self.rgx = None
        self.discard = False
        self.fmt = None
        self.match = ''

        self.set_matcher(m)

    def __repr__(self):
        return '\n'.join([super().__repr__(), self.__str__()])

    def __str__(self):
        s = ''
        if self.group:
            s += self.group + ':'
        s += '{}:{:d}'.format(self.name, self.idx)
        return s

    def set_matcher(self, m: re.Match):
        """Find attributes from match.

        Raises
        ------
        NameError
            No name.
        ValueError
            Empty custom regex.
        """
        self.match = m.group()[2:-1]  # slicing removes %()
        self.group = m.group('group')
        self.name = m.group('name')
        self.discard = m.group('discard') is not None

        rgx = m.group('rgx')
        fmt = m.group('fmt')

        if self.name is None:
            raise NameError("Matcher name cannot be empty.")
        if rgx is not None and rgx == '':
            raise ValueError("Matcher custom regex cannot be empty.")
        if fmt is not None and fmt == '':
            raise ValueError("Matcher custom format cannot be empty.")

        # Set defaults if name is known
        if self.name in self.DEFAULT_ELTS:
            self.rgx, fmt_def = self.DEFAULT_ELTS[self.name]
            self.fmt = Format(fmt_def)

        # Override default format
        if fmt:
            self.fmt = Format(fmt)
            if not rgx:  # No need to generate rgx if it is provided
                self.rgx = self.fmt.generate_expression()

        # Override regex
        if rgx:
            self.rgx = rgx

    def format(self, value: Any):
        return self.fmt.format(value)

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
            if group in self.DEFAULT_ELTS:
                replacement = self.DEFAULT_ELTS[group][0]
                if '%' in replacement:
                    return self.get_regex(replacement)
                return replacement
            raise KeyError("Unknown replacement '{}'.".format(match.group(0)))

        return re.sub("%([a-zA-Z%])", replace, self.rgx)


class Match:
    """Match extract from a filename."""

    def __init__(self, matcher: Matcher, match: re.Match, group: int):
        self.matcher = matcher
        self.match_str = match.group(group+1)
        self.start = match.start(group+1)
        self.end = match.end(group+1)

        self.match_parsed = None
        if matcher.fmt is not None:
            try:
                self.match_parsed = matcher.fmt.parse(self.match_str)
            except Exception:
                log.warning('Failed to parse for matcher %s', str(matcher))

    def __repr__(self):
        return '\n'.join([super().__repr__(), self.__str__()])

    def __str__(self):
        return str(self.matcher) + ' = {}'.format(self.match_str)

    def get_match(self, parsed: bool = True):
        """Get match string or value.

        If `parsed` is true, and the parsing was successful, return the
        parsed value instead of the matched string.
        """
        if parsed and self.match_parsed is not None:
            return self.match_parsed
        return self.match_str


class Matches:
    """Store multiples matches."""

    def __init__(self, matchers: List[Matcher], filename: str,
                 pattern: re.Pattern):
        """Creates matches from filename.

        Raises
        ------
        ValueError: Filename did not match pattern.
        IndexError: Not as many matches as matchers.
        """
        self.matches = []
        self.matchers = matchers

        m = pattern.fullmatch(filename)
        if m is None:
            raise ValueError("Filename did not match pattern.")
        if len(m.groups()) != len(matchers):
            raise IndexError("Not as many matches as matchers.")

        for i in range(len(matchers)):
            self.matches.append(Match(matchers[i], m, i))

    def __repr__(self):
        return '\n'.join([super().__repr__(), self.__str__()])

    def __str__(self):
        return '\n'.join([str(m) for m in self.matches])

    def __getitem__(self, key: Union[int, str]):
        return self.get_matches(key)

    def __iter__(self):
        return iter(self.matches)

    def get_matches(self, key: Union[int, str]) -> Union[Match, List[Match]]:
        """Get matches corresponding to key.

        See :func:`FileFinder.get_matchers
        <xarray_regex.file_finder.FileFinder.get_matchers>` for details on
        `key` argument.

        Returns
        -------
        List of Match corresponding to the key. If only one Match corresponds,
        return it directly.
        """
        selected = get_matchers_indices(self.matchers, key)
        return [self.matches[k] for k in selected]


def get_matchers_indices(matchers: List[Matcher],
                         key: Union[int, str]) -> List[int]:
    """Get list of matchers indices corresponding to key.

    Key can be an integer index, or a string of the name, or a combination
    of the group and the name with the syntax 'group:name'

    Raises
    ------
    IndexError: No matcher found corresponding to the key
    TypeError: Key is not int or str
    """
    if isinstance(key, int):
        return [key]
    if isinstance(key, str):
        k = key.split(':')
        if len(k) == 1:
            name, group = k[0], None
        else:
            group, name = k[:2]
        selected = []
        for i, m in enumerate(matchers):
            if m.name == name and (group is None or group == m.group):
                selected.append(i)

        if len(selected) == 0:
            raise IndexError(f"No matcher found for key '{key}'")
        return selected

    raise TypeError("Key must be int or str.")
