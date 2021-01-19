
.. currentmodule:: xarray_regex.file_finder

Fix matchers
============

The package allows to dynamically change the regular expression easily. This is
done by replacing matchers in the regular expression by a given string, using
the :func:`FileFinder.fix_matcher` method.

Matchers to replace can be selected
either by their index in the pre-regex (starting from 0), or by their name, or
their group and name following the syntax `'group:name'`.
If using a matcher name or group+name, multiple matchers can be fixed to the
same value at once.

For instance, when using the following pre-regex::

  '%(time:m)/SST_%(time:Y)%(time:m)%(time:d)\.nc'

we can keep only the files corresponding to january using any of::

  finder.fix_matcher(0, '01')
  finder.fix_matcher('m', '01')
  finder.fix_matcher('time:m', '01')

We could also select specific days using a regular expression::

  finder.fix_matcher('d', '01|03|05|07')

This would create the following regular expression::

  '(\d\d)/SST_(\d\d\d\d)(\d\d)(01|03|05|07)\.nc'
