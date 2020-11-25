"""Matcher object."""

import re


class Matcher():

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

        self.match = m.group()

        self.set_regex(m)

    def set_regex(self, m: re.match):
        group = m.group('group')
        name = m.group('name')
        custom = m.group('cus') is not None
        rgx = m.group('cus_rgx')

        if rgx is not None:
            if rgx == "":
                raise ValueError("Custom regex cannot be empty.")
            if name is None:
                raise KeyError("Matcher must have either a name "
                               "or a custom regex specified.")
        else:
            if name == "":
                raise ValueError("Element cannot be empty.")
        self.group = group
        self.name = name
        self.custom = custom

        if custom:
            self.rgx = rgx
        else:
            self.rgx = self.NAME_RGX[name]

    @classmethod
    def process_regex(cls, rgx: str) -> str:
        """Replace matchers by true regex.

        '%' followed by a single letter is replaced by the corresponding regex
        from `NAME_RGX`. '%%' is replaced by a single percentage character.
        """
        def replace(match):
            group = match.group(1)
            if group == '%':
                return '%'
            if group in cls.NAME_RGX:
                replacement = cls.NAME_RGX[group]
                if '%' in replacement:
                    return cls.process_regex(replacement)
                return replacement
            raise KeyError("Unknown replacement '{}'.".format(match.group(0)))
        return re.sub("%([a-zA-Z%])", replace, rgx)

    def get_regex(self) -> str:
        """Replace matchers by true regex.

        '%' followed by a single letter is replaced by the corresponding regex
        from `NAME_RGX`. '%%' is replaced by a single percentage character.
        """
        return self.process_regex(self.rgx)

    def __repr__(self):
        s = '{0}:{1}, idx={2}'.format(self.coord, self.name, self.idx)
        if self.discard:
            s += ', discard'
        return s
