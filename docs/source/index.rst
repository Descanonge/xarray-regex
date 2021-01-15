.. Xarray-regex documentation master file, created by
   sphinx-quickstart on Fri Dec  4 20:00:43 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. currentmodule:: xarray_regex

Xarray-regex documentation
==========================

Welcome to the Xarray-regex package documentation !

Xarray-regex allows to find files based on regular expressions, in order to feed
them to Xarray.
It allows to easily create regular expressions using 'Matchers', to fix some
elements of the expressions to select only certain files, and to easily
retrieve information from filenames.

This package has a main entry point: the :doc:`File finder<file_finder>` object.

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   file_finder
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
