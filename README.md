
# Xarray-regex

> Find files based on regular expression to pass them to Xarray

<div align="left">

[![PyPI version](https://badge.fury.io/py/xarray-regex.svg)](https://badge.fury.io/py/xarray-regex)
[![Release status](https://img.shields.io/github/v/release/Descanonge/xarray-regex)](https://github.com/Descanonge/xarray-regex/releases)

</div>

Xarray-regex allows to find files based on regular expressions, in order to feed
them to Xarray.
It allows to easily create regular expressions using 'Matchers', to fix some
elements of the expressions to select only certain files, and to easily
retrieve information from filenames.

## Minimal example

The following example will find files with names `Data/[month]/SST_[date].nc` (and only those!).
For each file, the date can be retrieved as a datetime object.
``` python
from xarray_regex import FileFinder, library

finder = FileFinder('/.../Data', r'%(m)/SST_%(Y)%(m)%(d)\.nc')
files = finder.get_files()
for f in files:
    print(f, library.get_date(finder.get_matches(f, relative=False)))
```

We can also only select some files, for instance only the first day of each month:
``` python
finder.fix_matcher('d', '01')
print(finder.get_files())
```

## Requirements

Python >= 3.7.

## Installation

From pip:
``` sh
pip install xarray-regex
```

From source:
``` sh
git clone https://github.com/Descanonge/xarray-regex.git
cd xarray-regex
pip install -e .
```

## Documentation

Documentation is available at [xarray-regex.readthedocs.io](https://xarray-regex.readthedocs.io).
