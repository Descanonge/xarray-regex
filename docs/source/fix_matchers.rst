
.. currentmodule:: xarray_regex.file_finder

Fix matchers
============

The package allows to dynamically change the regular expression easily. This is
done by replacing matchers in the regular expression by a given string, using
the :func:`FileFinder.fix_matcher` and :func:`FileFinder.fix_matchers` methods.

Matchers to replace can be selected either by their index in the pre-regex
(starting from 0), or by their name, or their group and name following the
syntax ``group:name``. If using a matcher name or group+name, multiple matchers
can be fixed to the same value at once.

If the corresponding matcher·s have a format specified, and the given value
is not already a string, it will be formatted.
If using a list of values, the string (given or formatted) will be joined by
a regex *OR* (``(value1|value2|...)``).
Special characters will be properly escaped.

For instance, when using the following pre-regex::

  '%(time:m)/SST_%(time:Y)%(time:m)%(time:d).nc'

we can keep only the files corresponding to january using any of::

  finder.fix_matcher(0, 1)
  finder.fix_matcher('m', 1)
  finder.fix_matcher('time:m', '01')

We could also select specific days using a list::

  finder.fix_matcher('d', [1, 3, 5, 7])
