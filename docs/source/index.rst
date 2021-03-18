.. Xarray-regex documentation master file, created by
   sphinx-quickstart on Fri Dec  4 20:00:43 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. currentmodule:: xarray_regex

Xarray-regex documentation
==========================

Welcome to the Xarray-regex package documentation !

Xarray-regex allows to specify the structure of filenames and using that, to
find files matching this structure, select only a subset of thoses files
according to parameters values, retrieve parameters values from found filenames,
or to generate a filename according to a set of parameters values.

The structure of the filename is specified with a single string. The parts
of the structure varying from file to file can be indicated with format strings,
or regular expressions, with some of those pre-defined (mainly for dates).

The package also allows to interface easily with `xarray.open_mfdataset`.

The following example will find all files with the structure `Data/[month]/Temperature_[depth]_[date].nc`::

  finder = FileFinder('/.../Data', '%(m)/Temperature_%(depth:fmt=d)_%(Y)%(m)%(d).nc')
  print(finder.get_files())

We can also only select some files, for instance the first day of each month::

  finder.fix_matcher('d', 1)
  print(finder.get_files())

We can retrieve values from found files::

  matches = get_matches(finder.get_files()[0], relative=False)
  print(matches)
  print(xarray_regex.library.get_date(matches))

And we can generate a filename with a set of parameters::

  print(finder.get_filename(depth=100, Y=2000, m=1, d=1))
  # Specifying the day is optional since we already fixed it to 1.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   find_files
   retrieve_values
   fix_matchers
   examples

.. toctree::
   :maxdepth: 1

   _references/xarray_regex.rst


Source code: `<https://github.com/Descanonge/xarray-regex>`__

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
