
.. currentmodule:: xarray_regex.file_finder

Retrieve information
--------------------

As some metadata might only be found in the filenames, FileFinder offer the
possibility to retrieve it easily using the :func:`FileFinder.get_matches`
method.
This returns a :class:`Matches<xarray_regex.matcher.Matches>` object,
containing a list of :class:`Match<xarray_regex.matcher.Match>` objects.
Each match retain its position in the filename string (relative to the root),
the matched characters, and if available its parsed value.

A specific match can be obtained using :func:`Matches.get_matches()
<xarray_regex.matcher.Matches.get_matches>` and either:

  - the index of the matcher in the pre-regex (starting at 0)
  - a string specifying the name of the matcher, or its group and name (with
    the syntax 'group:name'). If multiple matches correspond to the string, a list
    of matches is returned.

The package supply the function :func:`library.get_date
<xarray_regex.library.get_date>` to retrieve a datetime object from those
matches::

  from xarray_regex.library import get_date
  matches = finder.get_matches(filename)
  date = get_date(matches)


Combine with Xarray
===================

Retrieving information can be used when opening multiple files with
`xarray.open_mfdataset()
<http://xarray.pydata.org/en/stable/generated/xarray.open_mfdataset.html>`__.

:func:`FileFinder.get_func_process_filename` will turn a function into a
suitable callable for the `preprocess` argument of `xarray.open_mfdataset`.
The function should take an `xarray.Dataset`, a filename, a
:class:`FileFinder`, and eventual additional arguments as input, and return
an `xarray.Dataset`.
This allows to use the finder and the dataset filename in the pre-processing.
This following example show how to add a time dimension using the filename to
find the timestamp::

  def preprocess(ds, filename, finder):
    matches = finder.get_matches(filename)
    date = library.get_date(matches)

    ds = ds.assign_coords(time=pandas.to_datetime([value]))
    return ds

  ds = xr.open_mfdataset(finder.get_files(),
                         preprocess=f.get_func_process_filename(preprocess))


.. note::

   The filename path sent to the function is automatically made relative to
   the finder root directory, so that it can be used directly with
   :func:`FileFinder.get_matches`.
