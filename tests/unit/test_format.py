"""Test regex generation from format string.

Systematically generate formats, and test some number.
To see what formats are tested, see the global variables:
`signs`, `zeros`, `alts`, `aligns`, `grouping`, `widths`, `precisions`.
To see what numbers are tested, see the global variables:
`numbers_d`, `numbers_f`. (For float formats, both numbers list are tested)

For each combination, generate expression from format, and string
from number and format. Check that the regex match.
Check that we parse correctly the number.
"""

import re

from xarray_regex import format as xfmt

import pytest


numbers_d = [0, 1, -1, -10, 100, 1000, 12509123, -12093124]
numbers_f = [1.123, -3451.1209, 1e-8]


def assert_format(string, fmt):
    pattern = xfmt.generate_expression(fmt)
    m = re.fullmatch(pattern, string)
    assert m is not None, \
        f"No match. Format '{fmt}'. Pattern '{pattern}'. String '{string}'"


def assert_parse(number, string, fmt):
    parsed = xfmt.parse(string, fmt)
    assert number == parsed, \
        f"Not parsed. Format '{fmt}'. Number '{number}'. Parsed '{parsed}'"


signs = ['', '+', '-', ' ']
zeros = ['', '0']
alts = ['', '#']
aligns = ['', '<', '>', '=', '^', 'a>']
groupings = ['', ',', '_']
widths = ['', '0', '3', '6']
precisions = ['', '.0', '.1', '.3', '.6']


@pytest.mark.parametrize('align', aligns)
@pytest.mark.parametrize('sign', signs)
@pytest.mark.parametrize('width', widths)
@pytest.mark.parametrize('grouping', groupings)
@pytest.mark.parametrize('number', numbers_d)
def test_format_d(align, sign, width, grouping, number):
    fmt = align+sign+width+grouping + 'd'
    s = '{{:{}}}'.format(fmt).format(number)
    assert_format(s, fmt)
    assert_parse(number, s, fmt)


@pytest.mark.parametrize('align', aligns)
@pytest.mark.parametrize('sign', signs)
@pytest.mark.parametrize('width', widths)
@pytest.mark.parametrize('grouping', groupings)
@pytest.mark.parametrize('precision', precisions)
@pytest.mark.parametrize('number', numbers_d + numbers_f)
def test_format_f(align, sign, width, grouping, precision, number):
    fmt = align+sign+width+grouping+precision + 'f'
    s = '{{:{}}}'.format(fmt).format(number)
    assert_format(s, fmt)

    if precision == '':
        precision = 6
    else:
        precision = int(precision[-1])
    number = round(number, precision)

    assert_parse(number, s, fmt)
