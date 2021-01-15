
.. currentmodule:: xarray_regex.file_finder

File Finder
-----------

The main entry point of this package is the :class:`FileFinder` class.
This is the object that will find files according to a regular expression.
An instance is created using the root directory containing the files, and
a pre-regular expression (abbreviated pre-regex) that will be transformed into
a proper regex later.

When asking to find files, the finder will first create a regular-expression
out of the pre-regex.
It will then recursively find *all* files in the root directory and its
subfolders, though not descending deeper than :attr:`FileFinder.MAX_DEPTH_SCAN`
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

Information can be retrieved from the matches in the filename, but one might
discard a matcher so it will not be used in that case.
For example for a file of weekly averages with a filename indicated the start
and end dates of the average, we might want to only recover the starting date::

  sst_%(x)-%(x:discard)


Retrieve information
====================

As some metadata might only be found in the filenames, FileFinder offer the
possibility to retrieve it easily using the :func:`FileFinder.get_matches`
method.
This match a filename to the regex of the finder and returns a dictionnary of
the matches found.

The package supply a function to retrieve a datetime object::

  from xarray_regex.library import get_date
  matches = finder.get_matches(filename)
  date = get_date(matches)


In Xarray, this can be used to add metadata when opening a multi-file
dataset using xarray.open_mfdataset.
