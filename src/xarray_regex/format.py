"""Generate regex from string format, and parse strings.

Parameters of the format-string are retrieved.
See `<https://docs.python.org/3/library/string.html#formatspec>`__ for the
specification of the format mini-language.

Thoses parameters are then used to generate a regular expression, or to parse
a string formed from the format.

Only 's', 'd', and 'f' formats are supported.

The width of the format string is not respected when matching with a regular
expression.

The parsing is quite naive and can fail on some cases.
See :func:`parse` for details.

The regex generation and parsing are tested in `tests/unit/test_format.py`.
"""

import re
from typing import Any, Tuple, Union


def autoprop(*props):
    """Generate properties for class."""
    def factory_get(name):
        def getter(self):
            return self.params[name]
        return getter

    def factory_set(name):
        def setter(self, value):
            self.params[name] = value
        return setter

    def decorator(cls):
        for name in props:
            prop = property(factory_get(name), factory_set(name))
            setattr(cls, name, prop)
        return cls

    return decorator


@autoprop('fill', 'align', 'sign', 'alternate', 'zero',
          'width', 'grouping', 'precision', 'type')
class Format:
    """Parse a format string.

    Out of found parameters:
    - generate regular expression
    - format value
    - parse string into value

    Parameters
    ----------
    fmt: str
        Format string.
    """

    ALLOWED_TYPES = 'fds'
    RGX_ESCAPE = '+*?[]()^$|.'

    def __init__(self, fmt: str):
        self.fmt = fmt
        self.parse_params(fmt)
        self.set_defaults()

    def parse_params(self, format: str):
        """Parse format parameters."""
        p = (r"((?P<fill>.)?(?P<align>[<>=^]))?"
             r"(?P<sign>[-+ ])?(?P<alternate>#)?"
             r"(?P<zero>0)?(?P<width>\d+?)?"
             r"(?P<grouping>[,_])?"
             r"(?P<precision>\.\d+?)?"
             r"(?P<type>[a-zA-Z])")
        m = re.fullmatch(p, format)
        if m is None:
            raise ValueError("Format spec not valid.")
        self.params = m.groupdict()
        if not self.type or self.type not in self.ALLOWED_TYPES:
            raise ValueError('format spec %r not supported' % self.type)

    def set_defaults(self):
        """Set parameters defaults values."""
        if self.type in 'df':
            defaults = dict(
                align='>',
                fill=' ',
                sign='-',
                width='0',
                precision='.6'
            )
            self.alternate = self.alternate == '#'
            self.zero = self.zero == '0'
            if self.align is None and self.zero:
                self.fill = '0'
            for k, v in defaults.items():
                if self.params[k] is None:
                    self.params[k] = v
            self.width = int(self.width)
            self.precision = int(self.precision[1:])

    def format(self, value: Any) -> str:
        """Return formatted string."""
        return '{{:{}}}'.format(self.fmt).format(value)

    def generate_expression(self) -> str:
        """Generate regex from format string."""
        if self.type == 'f':
            return self.generate_expression_f()
        if self.type == 'd':
            return self.generate_expression_d()
        if self.type == 's':
            return self.generate_expression_s()

    def parse(self, s: str) -> Union[str, int, float]:
        """Parse string generated with format.

        This simply use int() and float() to parse strings. Those are thrown
        off when using fill characters (other than 0), or thousands groupings,
        so we remove thoses from the string.

        Parsing will fail when using the '-' fill character.
        """
        if self.type == 'd':
            return self.parse_d(s)
        if self.type == 'f':
            return self.parse_f(s)
        if self.type == 's':
            return s

    @classmethod
    def escape(cls, char: str) -> str:
        """Escape special regex characters."""
        if len(char) > 1:
            raise IndexError("String to escape longer than one character")
        if char in cls.RGX_ESCAPE:
            return r'\{}'.format(char)
        return char

    def generate_expression_s(self) -> str:
        return '.*?'

    def generate_expression_d(self) -> str:
        rgx = ''
        align, loc = self.get_align()
        if loc in ['left', 'center']:
            rgx += align

        rgx += self.get_sign()

        if loc == 'middle':
            rgx += align

        rgx += self.get_left_point()

        if loc in ['right', 'center']:
            rgx += align

        return rgx

    def generate_expression_f(self) -> str:
        rgx = ''
        align, loc = self.get_align()

        if loc in ['left', 'center']:
            rgx += align

        rgx += self.get_sign()

        if loc == 'middle':
            rgx += align

        rgx += self.get_left_point()

        precision = self.precision
        if precision == '':
            precision = 6
        if precision != 0 or self.alternate:
            rgx += r'\.'
        rgx += r'\d{{{:d}}}'.format(precision)

        if loc in ['right', 'center']:
            rgx += align

        return rgx

    def get_sign(self) -> str:
        """Get sign regex."""
        if self.sign == '-':
            rgx = '-?'
        elif self.sign == '+':
            rgx = r'(?:\+|-)'
        elif self.sign == ' ':
            rgx = r'(?:\s|-)'
        else:
            raise KeyError("Sign not in {+- }")
        return rgx

    def get_align(self) -> Tuple[str, str]:
        """Get alignment with fill regex and its location."""
        rgx = ''
        if self.width > 0:
            rgx += '{}*'.format(self.escape(self.fill))

        loc = {
            '=': 'middle',
            '>': 'left',
            '<': 'right',
            '^': 'center'
        }[self.align]

        return rgx, loc

    def get_left_point(self) -> str:
        """Get regex for numbers left of decimal point."""
        if self.grouping is not None:
            rgx = r'\d?\d?\d(?:{}\d{{3}})*'.format(self.grouping)
        else:
            rgx = r'\d*'
        return rgx

    def parse_d(self, s: str) -> int:
        """Parse integer from formatted string. """
        return int(self.remove_special(s))

    def parse_f(self, s: str) -> float:
        """Parse float from formatted string."""
        return float(self.remove_special(s))

    def remove_special(self, s: str) -> int:
        """Remove special characters.

        Remove characters that throw off int() and float() parsing.
        Namely fill and grouping characters.
        Will remove fill, even when fill is '-'.
        """
        to_remove = [',', '_']  # Any grouping char
        if self.fill != '0':
            to_remove.append(self.escape(self.fill))
        pattern = '[{}]'.format(''.join(to_remove))
        return re.sub(pattern, '', s)
