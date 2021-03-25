
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
It will then recursively find files in the root directory and its subfolders.
Only the subfolders matching (part of) the regex will be looked into.
Subfolders can simply be indicated in the pre-regex with the OS separator.
The finder only keeps files that match the regex.
The files can be retrieved using :func:`FileFinder.get_files`.


Pre-regex
=========

The pre-regex specifies the structure of the filenames relative to the root
directory. Parts that vary from file to file are indicated by *matchers*,
enclosed by parenthesis and preceded by '%'. It is represented by the
:class:`xarray_regex.matcher.Matcher` class.

Inside the matchers parenthesis can be indicated multiple elements, separated by
colons:

- a group name (optional)
- a name that will dictate the matcher regex using a correspondance table
- a format string (optional)
- a custom regex (optional)
- a keyword that will discard that matcher when retrieving information from a
  filename (optional)

The full syntax is as follows: ``%([group:]name[:fmt=format string][:rgx=custom regex][:discard])``.

.. note::

   The matchers are uniquely identified by their index in the pre-regex
   (starting at 0).
   Some other functions (see :func:`FileFinder.get_matches`) can use the string
   ``[group:]name`` to find one or more matchers.


Name
####

The name of the matcher will dictate the regex and format string used for that
matcher (unless overriden by a custom regex), and how it will be used by
functions that retrieve information from the filename.
The :attr:`Matcher.DEFAULT_ELTS<xarray_regex.matcher.Matcher.DEFAULT_ELTS>`
class attribute will make the correspondance between name and regex:

+------+-------------------+-----------+--------+
| Name |                   | Regex     | Format |
+------+-------------------+-----------+--------+
| F    | Date (YYYY-MM-DD) | %Y-%m-%d  |      s |
+------+-------------------+-----------+--------+
| x    | Date (YYYYMMDD)   | %Y%m%d    |    08d |
+------+-------------------+-----------+--------+
| X    | Time (HHMMSS)     | %H%M%S    |    06d |
+------+-------------------+-----------+--------+
| Y    | Year (YYYY)       | \\d{4}    |    04d |
+------+-------------------+-----------+--------+
| m    | Month (MM)        | \\d\\d    |    02d |
+------+-------------------+-----------+--------+
| d    | Day of month (DD) | \\d\\d    |    02d |
+------+-------------------+-----------+--------+
| j    | Day of year (DDD) | \\d{3}    |    03d |
+------+-------------------+-----------+--------+
| B    | Month name        | [a-zA-Z]* |      s |
+------+-------------------+-----------+--------+
| H    | Hour 24 (HH)      | \\d\\d    |    02d |
+------+-------------------+-----------+--------+
| M    | Minute (MM)       | \\d\\d    |    02d |
+------+-------------------+-----------+--------+
| S    | Seconds (SS)      | \\d\\d    |    02d |
+------+-------------------+-----------+--------+
| I    | Index             | \\d*      |      d |
+------+-------------------+-----------+--------+
| text | Letters           | \\w       |      s |
+------+-------------------+-----------+--------+
| char | Character         | \\S*      |      s |
+------+-------------------+-----------+--------+

Those are mainly related to datetime. This table *mostly* follows the `strftime
<https://linux.die.net/man/3/strftime>`__ format specifications.
Matcher with corresponding names will be used by :func:`library.get_date()<xarray_regex.library.get_date>` to find the date from
the filename.

A letter preceded by a percent sign '%' in the regex will be recursively
replaced by the corresponding name in the table. This can be used in the
custom regex. This still counts as a single matcher and its name will not
be changed, only the regex.
So ``%x`` will be replaced by ``%Y%m%d``, in turn replaced by
``\\d{4}\\d\\d\\d\\d``.
A percentage character in the regex is escaped by another percentage ('%%').


Custom format
#############

All the possible use cases are not covered in the table above. A simple way to
specify a matcher is by using a format string following the
`Format Mini Language Specification
<https://docs.python.org/3/library/string.html#formatspec>`__.
This will automatically be transformed into a regular expression.

Having a format specified has other benefits: it can be used convert values
into string to generate a filename from parameters values (using
:func:`FileFinder.get_filename`), or vice-versa to parse filenames matches into
parameters values.

It's easy as::

  scale_%(scale:fmt=.1f)

.. note::

   Only s, d, f, e, and E format types are supported.

   Parsing will fail in some unrealistic cases described in
   :func:`format.Format.parse()<xarray_regex.format.Format.parse>`.


Custom regex
############

Finally, one can directly use a regular expression using. This will supersede
the default regex, or the one generated from the format string if specified.

It can be done like so::

  idx_%(idx:rgx=\d+?)

Discard keyword
###############

doc:`Information can be retrieved<retrieving_values>` from the matches in the
filename, but one might discard a matcher so that it is not used.
For example for a file of weekly averages with a filename indicated the start
and end dates of the average, we might want to only recover the starting date::

  sst_%(x)-%(x:discard)


Regex outside matchers
======================

By default, special characters (`., ^, |, ...`) outside of matchers are escaped.
To use regular expressions outside of matchers, it is necessary to activate the
``use_regex`` argument when creating the FileFinder object.
All characters outside of matchers will then be properly escaped.

.. note::

   When using regex outside matchers, :func:`FileFinder.get_filename` won't
   work.


Obtaining files
===============

Files can be retrieved with the :func:`FileFinder.get_files` function, or
the :attr:`FileFinder.files` attribute. Both will scan the directory for files
if it has not been done yet.
The 'files' attribute also stores the matches. See :ref:`Retrieve information`
for details on how matches are stored.

:func:`FileFinder.get_files` can also return nested lists of filenames.
This is aimed to work with `xarray.open_mfdataset()
<http://xarray.pydata.org/en/stable/generated/xarray.open_mfdataset.html>`__,
which will merge files in a specific order when supplied a nested list of files.

To this end, one must specify group names to the `nested` argument of the same
function. The rightmost group will correspond to the innermost level.

An example is available in the :ref:`examples<Nested files>`.
