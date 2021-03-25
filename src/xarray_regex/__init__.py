
import warnings

from .file_finder import FileFinder

__version__ = "0.2.2"

__all__ = [
    'FileFinder'
]

warnings.warn(("Xarray-regex is now deprecated and has been "
               "replaced by https://github.com/Descanonge/filefinder"))
