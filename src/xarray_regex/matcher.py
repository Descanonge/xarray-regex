"""Matcher object."""

import re


class Matcher():

    ELT_RGX = {"idx": r"\d+",
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

    def __init__(self, m: re.match):
        self.name = None
        self.elt = None
        self.custom = False
        self.rgx = None

        self.group = m.group()

        self.set_regex(m)

    def set_regex(self, m: re.match):
        name = m.group('name')
        elt = m.group('elt')
        custom = m.group('cus') is not None
        rgx = m.group('cus_rgx')

        if rgx is not None:
            if rgx == "":
                raise ValueError("Custom regex cannot be empty.")
            if elt is None:
                raise KeyError("Matcher must have either an element "
                               "or a custom regex specified.")
        else:
            if elt == "":
                raise ValueError("Element cannot be empty.")
        self.name = name
        self.elt = elt
        self.custom = custom

        if custom:
            self.rgx = rgx
        else:
            self.rgx = self.ELT_RGX[elt]

    @classmethod
    def process_regex(cls, rgx: str) -> str:
        """Replace matchers by true regex.

        '%' followed by a single letter is replaced by the corresponding regex
        from `ELT_RGX`. '%%' is replaced by a single percentage character.
        """
        def replace(match):
            group = match.group(1)
            if group == '%':
                return '%'
            if group in cls.ELT_RGX:
                replacement = cls.ELT_RGX[group]
                if '%' in replacement:
                    return cls.process_regex(replacement)
                return replacement
            raise KeyError("Unknown replacement '{}'.".format(match.group(0)))
        return re.sub("%([a-zA-Z%])", replace, rgx)

    def get_regex(self) -> str:
        """Replace matchers by true regex.

        '%' followed by a single letter is replaced by the corresponding regex
        from `ELT_RGX`. '%%' is replaced by a single percentage character.
        """
        return self.process_regex(self.rgx)

    def replace_itself(self, regex: str) -> str:
        return regex.replace(self.group, '({})'.format(self.get_regex()))

    def __repr__(self):
        s = '{0}:{1}, idx={2}'.format(self.coord, self.elt, self.idx)
        if self.dummy:
            s += ', dummy'
        return s
