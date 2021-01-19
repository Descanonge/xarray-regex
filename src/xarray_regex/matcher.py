"""Matcher object."""

# This file is part of the 'xarray-regex' project
# (http://github.com/Descanonge/xarray-regex) and subject
# to the MIT License as defined in the file 'LICENSE',
# at the root of this project. © 2021 Clément Haëck

import re


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

    NAME_RGX = {"idx": r"\d+",
                "Y": r"\d\d\d\d",
                "m": r"\d\d",
                "d": r"\d\d",
                "j": r"\d\d\d",
                "H": r"\d\d",
                "M": r"\d\d",
                "S": r"\d\d",
                "x": r"%Y%m%d",
                "X": r"%H%M%S",
                "F": r"%Y-%m-%d",
                "B": r"[a-zA-Z]*",
                "text": r"[a-zA-Z]*",
                "char": r"\S*"}
    """Regex str for each type of element."""

    def __init__(self, m: re.match, idx: int = 0):
        self.idx = idx
        self.group = None
        self.name = None
        self.custom = False
        self.rgx = None
        self.discard = False

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
        custom = m.group('cus') is not None
        rgx = m.group('cus_rgx')

        if name is None:
            raise NameError("Matcher name cannot be empty.")
        if custom and not rgx:
            raise ValueError("Matcher custom regex cannot be empty.")

        self.group = group
        self.name = name
        self.custom = custom

        if custom:
            self.rgx = rgx
        else:
            self.rgx = self.NAME_RGX[name]

    def get_regex(self) -> str:
        """Get matcher regex.

        Replace the matchers name by regex from `Matcher.NAME_RGX`.
        If there is a custom regex, recursively replace '%' followed by a single
        letter by the corresponding regex from `NAME_RGX`. '%%' is replaced by a
        single percentage character.

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
