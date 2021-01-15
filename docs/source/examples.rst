
Examples
========

Plain time serie
################

Here the files are all in the same folder. Only the timestamp differ from one
file to the other::

    Data
    ├── SSH
    │   ├── SSH_20070101.nc
    │   ├── SSH_20070109.nc
    │   └── ...
    └── SST
        ├── A_2007001_2007008.L3m_8D_sst.nc
        ├── A_2007008_2007016.L3m_8D_sst.nc
        └── ...

We will scan for SST files::

  from xarray_regex import FileFinder, library

  root = 'Data/SST'
  pregex = 'A_%(Y)%(j)_%(Y)%(j:discard)%(suffix)'
  finder = FileFinder(root, pregex, suffix=r'\.L3m_8D_sst\.nc')

  files = finder.get_files()

We would like to open all these files using Xarray, however the files lacks a
defined 'time' dimensions to concatenate all files. To make it work, we can
use the 'preprocess' argument of `xarray.open_mfdataset`::

  def preprocess(ds, filename, finder):
    matches = finder.get_matches(filename)
    date = library.get_date(matches)

    ds = ds.assign_coords(time=pd.to_datetime([value]))
    return ds

  ds = xr.open_mfdataset(files,
                         preprocess=f.get_func_process_filename(preprocess))
