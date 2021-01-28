"""Functions to retrieve values from filename."""

# This file is part of the 'xarray-regex' project
# (http://github.com/Descanonge/xarray-regex) and subject
# to the MIT License as defined in the file 'LICENSE',
# at the root of this project. © 2021 Clément Haëck

import logging
from typing import Dict, List

from datetime import datetime, timedelta

log = logging.getLogger(__name__)


def get_date(matches: List, default_date: Dict = None,
             group: str = None) -> datetime:
    """Retrieve date from matched elements.

    If any element is not found in the filename, it will be replaced by the
    element in the default date. If no match is found, None is returned.

    Supports matches with names from `Matcher.NAME_RGX`.

    Parameters
    ----------
    matches: list
        Matches from a filename, returned by `FileFinder.get_matches`
    group: str
        If not None, restrict matcher to this group.
    default_date: dict, optional
        Default date. Dictionnary with keys: year, month, day, hour, minute,
        and second. Defaults to 1970-01-01 00:00:00

    Raises
    ------
    KeyError: If no matchers are found to create a date from.
    """
    date = {"year": 1970, "month": 1, "day": 1,
            "hour": 00, "minute": 0, "second": 0}

    if default_date is None:
        default_date = {}
    date.update(default_date)

    elts = {m['matcher'].name: m['match'] for m in matches
            if (not m['matcher'].discard
                and (group is None or m['matcher'].group == group))}

    elts_needed = {'x', 'X', 'Y', 'm', 'd', 'B', 'j', 'H', 'M', 'S'}
    if len(set(elts.keys()) & elts_needed) == 0:
        log.warning("No matchers to retrieve a date from."
                    " Returning default date.")

    elt = elts.pop("x", None)
    if elt is not None:
        elts["Y"] = elt[:4]
        elts["m"] = elt[4:6]
        elts["d"] = elt[6:8]

    elt = elts.pop("X", None)
    if elt is not None:
        elts["H"] = elt[:2]
        elts["M"] = elt[2:4]
        if len(elt) > 4:
            elts["S"] = elt[4:6]

    elt = elts.pop("Y", None)
    if elt is not None:
        date["year"] = int(elt)

    elt = elts.pop("m", None)
    if elt is not None:
        date["month"] = int(elt)

    elt = elts.pop("B", None)
    if elt is not None:
        elt = _find_month_number(elt)
        if elt is not None:
            date["month"] = elt

    elt = elts.pop("d", None)
    if elt is not None:
        date["day"] = int(elt)

    elt = elts.pop("j", None)
    if elt is not None:
        elt = datetime(date["year"], 1, 1) + timedelta(days=int(elt)-1)
        date["month"] = elt.month
        date["day"] = elt.day

    elt = elts.pop("H", None)
    if elt is not None:
        date["hour"] = int(elt)

    elt = elts.pop("M", None)
    if elt is not None:
        date["minute"] = int(elt)

    elt = elts.pop("S", None)
    if elt is not None:
        date["second"] = int(elt)

    return datetime(**date)


def _find_month_number(name: str) -> int:
    """Find a month number from its name.

    Name can be the full name (January) or its three letter abbreviation (jan).
    The casing does not matter.
    """
    names = ['january', 'february', 'march', 'april',
             'may', 'june', 'july', 'august', 'september',
             'october', 'november', 'december']
    names_abbr = [c[:3] for c in names]

    name = name.lower()
    if name in names:
        return names.index(name)
    if name in names_abbr:
        return names_abbr.index(name)

    return None
