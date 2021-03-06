
.. currentmodule:: xarray_regex.file_finder

Finding files
-------------

The main entry point of this package is the :class:`FileFinder` class.
This is the object that will find files according to a regular expression.
An instance is created using the root directory containing the files, and
a pre-regular expression (abbreviated pre-regex) that will be transformed into
a proper regex later.

When asking to find files, the finder will first create a regular-expression
out of the pre-regex.
It will then recursively find *all* files in the root directory and its
subfolders, though not descending deeper than :attr:`FileFinder.max_depth_scan`
folders (default is 3).
The finder only keeps files that match the regex.
The files can be retrieved using :func:`FileFinder.get_files`.


Pre-regex
=========

The pre-regex specifies the structure of the filenames relative to the root
directory.
It is a regular expression with the added feature of *matchers*.

A matcher is a part of the filename that vary from file to file.
In the pre-regex, it is enclosed by parenthesis and preceded by '%'.
It is represented by the :class:`xarray_regex.matcher.Matcher` class.

.. warning::

   Anything outside matchers in the pre-regex will be considered constant across
   files.
   For example, if we have daily files '`sst_2003-01-01.nc`' with the date
   changing for each file, we could use the regex '`sst_.*\.nc`' which would
   match correctly all files, but the finder would in fact consider that *all*
   files are '`sst_2003-01-01.nc`' (the first file found).

Inside the matchers parenthesis can be indicated multiple elements, separated by
colons:

- a group name (optional)
- a name that will dictate the matcher regex using a correspondance table
- a custom regex if correspondances are not enough (optional)
- a keyword that will discard that matcher when retrieving information from a
  filename (optional)

The full syntax is as follows: '`%([group:]name[:custom=custom
regex:][:discard])`'.

.. note::

   The matchers are uniquely identified by their index in the pre-regex
   (starting at 0).

Name
####

The name of the matcher will dictate the regex used for that matcher (unless
overriden by a custom regex), and how it will be used by functions that
retrieve information from the filename.
The :attr:`Matcher.NAME_RGX<xarray_regex.matcher.Matcher.NAME_RGX>` class
attribute will make the correspondance between name and regex:

+--------------+--------------+-------------------+
| Name         | Regex        |                   |
+--------------+--------------+-------------------+
| idx          | \\d*         | Index             |
+--------------+--------------+-------------------+
| text         | [a-zA-Z]*    | Letters           |
+--------------+--------------+-------------------+
| char         | \\S*         | Character         |
+--------------+--------------+-------------------+
| F            | %Y-%m-%d     | Date (YYYY-MM-DD) |
+--------------+--------------+-------------------+
| x            | %Y%m%d       | Date (YYYYMMDD)   |
+--------------+--------------+-------------------+
| X            | %H%M%S       | Time (HHMMSS)     |
+--------------+--------------+-------------------+
| Y            | \\d\\d\\d\\d | Year (YYYY)       |
+--------------+--------------+-------------------+
| m            | \\d\\d       | Month (MM)        |
+--------------+--------------+-------------------+
| d            | \\d\\d       | Day of month (DD) |
+--------------+--------------+-------------------+
| j            | \\d\\d\\d    | Day of year (DDD) |
+--------------+--------------+-------------------+
| B            | [a-zA-Z]*    | Month name        |
+--------------+--------------+-------------------+
| H            | \\d\\d       | Hour 24 (HH)      |
+--------------+--------------+-------------------+
| M            | \\d\\d       | Minute (MM)       |
+--------------+--------------+-------------------+
| S            | \\d\\d       | Seconds (SS)      |
+--------------+--------------+-------------------+

This table *mostly* follows the
`strftime <https://linux.die.net/man/3/strftime>`__ format specifications.

So for example, '`%(Y)`' will be replaced by a regex searching for 4 digits, and
:func:`library.get_date<xarray_regex.library.get_date>` will use it to find the
date year.

A letter preceded by a percent sign '`%`' in the regex will be recursively
replaced by the corresponding name in the table. This can be used in the
custom regex. This still counts as a single matcher and its name will not
be changed, only the regex.
So '`%x`' will be replaced by '`%Y%m%d`', in turn replaced by
'`\\d\\d\\d\\d\\d\\d\\d`'.
A percentage character in the regex is escaped by another percentage (`'%%'`).


Custom regex
############

All the possible use cases are not covered in the `NAME_RGX` table and one might
want to use a specific regex::

  sst_%(Y:custom=\d\d:)-%(doy:custom=\d\d\d:discard)


.. warning::

   The custom regex must be terminated with a colon.


Discard keyword
###############

doc:`Information can be retrieved<retrieving_values>` from the matches in the
filename, but one might discard a matcher so it would not be used.
For example for a file of weekly averages with a filename indicated the start
and end dates of the average, we might want to only recover the starting date::

  sst_%(x)-%(x:discard)


Nesting files
=============

Found files can be retrieved using :func:`FileFinder.get_files`. This outputs
a list of all files (relative to the finder root, or as absolute paths), sorted
alphabetically.
They can also be returned as a nested lists of filenames.
This is aimed to work with `xarray.open_mfdataset()
<http://xarray.pydata.org/en/stable/generated/xarray.open_mfdataset.html>`__,
which will merge files in a specific order when supplied a nested list of files.

To this end, one must specify group names to the `nested` argument of the same
function. The rightmost group will correspond to the innermost level.

An example is available in the :ref:`examples<Nested files>`.
