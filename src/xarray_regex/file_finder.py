"""Find files using a pre-regex."""

# This file is part of the 'xarray-regex' project
# (http://github.com/Descanonge/xarray-regex) and subject
# to the MIT License as defined in the file 'LICENSE',
# at the root of this project. © 2021 Clément Haëck

import os
import logging
import re

from typing import Callable, Dict, List, Union

from xarray_regex.matcher import Matcher

log = logging.getLogger(__name__)


class FileFinder():
    """Find files using a regular expression.

    Provides abilities to 'fix' some part of the regular expression,
    to retrieve values from matches in the expression, and to
    create an advanced pre-processing function for `xarray.open_mfdataset`.

    Parameters
    ----------
    root : str
        The root directory of a filetree where all files can be found.
    pregex: str
        The pre-regex. A regular expression with added 'Matchers'.
        Only the matchers vary from file to file. See documentation
        for details.
    replacements : str, optional
        Matchers to replace by a string:
        `'matcher name' = 'replacement string'`.

    Attributes
    ----------
    max_depth_scan: int
        Maximum authorized depth when descending into filetree to scan files.
    root: str
        The root directory of the finder.
    pregex: str
        Pre-regex.
    regex: str
        Regex obtained from the pre-regex.
    pattern: re.pattern
        Compiled pattern obtained from the regex.
    matchers: list of Matchers
        List of matchers for this finder, in order.
    segments: list of str
        Segments of the pre-regex. Used to replace specific matchers.
        `['text before matcher 1', 'matcher 1',
        'text before matcher 2, 'matcher 2', ...]`
    fixed_matchers: dict
        Dictionnary of matchers with a set value.
        'matcher index': 'replacement string'
    files: list of str
        List of scanned files.
    scanned: bool
        If the finder has scanned files.
    """

    def __init__(self, root: str, pregex: str, **replacements: str):

        self.max_depth_scan = 3

        if isinstance(root, (list, tuple)):
            root = os.path.join(*root)
        if not os.path.isdir(root):
            raise ValueError(f"'{root}' directory does not exist.")
        self.root = root

        self.pregex = ''
        self.regex = ''
        self.pattern = None
        self.matchers = []
        self.segments = []
        self.fixed_matchers = dict()
        self.files = []
        self.scanned = False

        self.set_pregex(pregex, **replacements)
        self.create_regex()

    @property
    def n_matchers(self) -> int:
        """Number of matchers in pre-regex."""
        return len(self.matchers)

    def __repr__(self):
        return '\n'.join([super().__repr__(), self.__str__()])

    def __str__(self):
        s = ['root: {}'.format(self.root)]
        s += ["pre-regex: {}".format(self.pregex)]
        if self.regex is not None:
            s += ["regex: {}".format(self.regex)]
        else:
            s += ["regex not created"]
        if self.fixed_matchers:
            s += ["fixed matchers:"]
            s += ["\t fixed #{} to {}".format(i, v)
                  for i, v in self.fixed_matchers.items()]
        if not self.scanned:
            s += ["not scanned"]
        else:
            s += ["scanned: found {} files".format(len(self.files))]
        return '\n'.join(s)

    def get_files(self, relative: bool = False,
                  nested: List[str] = None) -> List[str]:
        """Return files that matches the regex.

        Lazily scan files: if files were already scanned, just return
        the stored list of files.

        Parameters
        ----------
        relative : bool
            If True, filenames are returned relative to the finder
            root directory. If not, filenames are absolute. Defaults to False.
        nested : list of str
            If not None, return nested list of filenames with each level
            corresponding to a group in this argument. Last group in the list is
            at the innermost level. A level specified as None refer to matchers
            without a group.

        Raises
        ------
        KeyError: A level in `nested` is not in the pre-regex groups.
        """
        def make_abs(f):
            return os.path.join(self.root, f)

        def get_match(m, group):
            return ''.join([m_['match'] for m_ in m
                            if m_['matcher'].group == group])

        def nest(files_matches, groups, relative):
            if len(groups) == 0:
                return [make_abs(f) if not relative else f
                        for f, m in files_matches]

            group = groups[0]
            files_grouped = []
            matches = {}
            for f, m in files_matches:
                match = get_match(m, group)
                if match not in matches:
                    matches[match] = len(matches)
                    files_grouped.append([])
                files_grouped[matches[match]].append((f, m))

            return [nest(grp, groups[1:], relative) for grp in files_grouped]

        if not self.scanned:
            self.find_files()

        if nested is None:
            files = [make_abs(f) if not relative else f
                     for f, m in self.files]
        else:
            groups = [m.group for m in self.matchers]
            for g in nested:
                if g not in groups:
                    raise KeyError(f'{g} is not in FileFinder groups.')
            files = nest(self.files, nested, relative)

        return files

    def fix_matcher(self, key: Union[int, str], value: str):
        """Fix a matcher to a string.

        Parameters
        ----------
        key : int, or str, or tuple of str of lenght 2.
            If int, is matcher index, starts at 0.
            If str, can be matcher name, or a group and name combination with
            the syntax 'group:name'.
            When using strings, if multiple matchers are found with the same
            name or group/name combination, all are fixed to the same value.
        value : str
            Will replace the match for all files.

        Raises
        ------
        TypeError: Value must be a string.
        TypeError: key is neither int nor str.
        """
        if not isinstance(value, str):
            raise TypeError("Value must be a str.")
        if isinstance(key, int):
            self.fixed_matchers[key] = value
        elif isinstance(key, str):
            for m in self.get_matchers(key):
                self.fixed_matchers[m.idx] = value
        else:
            raise TypeError("Key must be int or str.")

        self.update_regex()

    def fix_matchers(self, fixes: Dict[Union[int, str], str] = None):
        """Fix multiple values at once.

        Parameters
        ----------
        fixes: dict
           Dictionnary of matcher key: value. See :func:`fix_matcher` for
           details. If None, no matcher will be fixed.
        """
        if fixes is None:
            fixes = {}
        for f in fixes.items():
            self.fix_matcher(*f)

    def get_matches(self, filename: str,
                    relative: bool = True) -> Dict[str, Dict]:
        """Get matches for a given filename.

        Apply regex to `filename` and return a dictionary of the results.

        Parameters
        ----------
        filename:
            Filename to retrieve matches from.
        relative:
            Is true if the filename is relative to the finder root directory.
            If false, the filename is made relative before being matched.
            Default to true.

        Returns
        -------
        list of dict
            [{'match': string matched,
              'start': start index in filename,
              'end': end index in filename,
              'matcher': Matcher object}, ...]

        Raises
        ------
        AttributeError: The regex is empty.
        ValueError: The filename did not match the pattern.
        IndexError: Not as many matches as matchers.
        """
        if not self.regex:
            raise AttributeError("Finder is missing a regex.")

        if not relative:
            filename = os.path.relpath(filename, self.root)

        m = self.pattern.match(filename)
        if m is None:
            raise ValueError("Filename did not match pattern.")
        if len(m.groups()) != self.n_matchers:
            raise IndexError("Not as many matches as matchers.")
        matches = []
        for i in range(self.n_matchers):
            matcher = self.matchers[i]
            matches.append({
                'match': m.group(i+1),
                'start': m.start(i+1),
                'end': m.end(i+1),
                'matcher': matcher
            })
        return matches

    def get_func_process_filename(self, func: Callable, relative: bool = True,
                                  *args, **kwargs) -> Callable:
        r"""Get a function that can preprocess a dataset.

        Written to be used as the 'process' argument of `xarray.open_mfdataset`.
        Allows to use a function with additional arguments, that can retrieve
        information from the filename.

        Parameters
        ----------
        func: Callable
            Input arguments (`xarray.Dataset`, filename: `str`,
            `FileFinder`, \*args, \*\*kwargs)
            Should return a Dataset.
            Filename is retrieved from the dataset encoding attribute.
        relative: If True, `filename` is made relative to finder root.
            This is necessary to match the filename against the finder regex.
            Defaults to True.
        args: optional
            Passed to `func` when called.
        kwargs: optional
            Passed to `func` when called.

        Returns
        -------
        Callable
             Function with the signature of the 'process' argument of
             `xarray.open_mfdataset`.

        Examples
        --------
        This retrieve the date from the filename, and add a time dimensions
        to the dataset with the corresponding value.
        >>> from xarray_regex import library
        ... def process(ds, filename, finder, default_date=None):
        ...     matches = finder.get_matches(filename)
        ...     date = library.get_date(matches, default_date=default_date)
        ...     ds = ds.assign_coords(time=[date])
        ...     return ds
        ...
        ... ds = xr.open_mfdataset(finder.get_files(),
        ...                        preprocess=finder.get_func_process_filename(
        ...     process, default_date={'hour': 12}))
        """
        def f(ds):
            filename = ds.encoding['source']
            if relative:
                filename = os.path.relpath(filename, self.root)
            return func(ds, filename, self, *args, **kwargs)
        return f

    def set_pregex(self, pregex: str, **replacements: str):
        """Set pre-regex.

        Apply replacements.
        """
        pregex = pregex.strip()
        for k, z in replacements.items():
            pregex = pregex.replace("%({:s})".format(k), z)
        self.pregex = pregex

    def create_regex(self):
        """Create regex from pre-regex. """
        self.scan_pregex()
        self.update_regex()

    def scan_pregex(self):
        """Scan pregex for matchers.

        Add matchers objects to self.
        Set segments attribute.
        """
        regex = (r"%\((?:(?P<group>[a-zA-Z]*):)??"
                 r"(?P<name>[a-zA-Z]*)"
                 r"(?P<cus>:custom=)?(?(cus)(?P<cus_rgx>[^:]*):)"
                 r"(?P<discard>(?(cus)|:)discard)?\)")
        splits = [0]
        self.matchers = []
        for i, m in enumerate(re.finditer(regex, self.pregex)):
            self.matchers.append(Matcher(m, i))
            splits += [m.start(), m.end()]
        self.segments = [self.pregex[i:j]
                         for i, j in zip(splits, splits[1:]+[None])]

        # Replace matcher by its regex
        for idx, m in enumerate(self.matchers):
            self.segments[2*idx+1] = '({})'.format(m.get_regex())

    def update_regex(self):
        """Update regex.

        Set fixed matchers. Re-compile pattern. Scrap previous scanning.
        """
        self.set_fixed_matchers_in_segments()
        self.regex = ''.join(self.segments)
        self.pattern = re.compile(self.regex + "$")
        self.scanned = False
        self.files = []

    def set_fixed_matchers_in_segments(self):
        for idx, value in self.fixed_matchers.items():
            self.segments[2*idx+1] = '({})'.format(value)

    def find_files(self):
        """Find files to scan.

        Uses os.walk. Limit search to `max_depth_scan` levels of directories
        deep.
        Sort files alphabetically.

        Raises
        ------
        AttributeError
            If no regex is set.
        IndexError
            If no files are found in the filetree.
        """
        if self.regex is None:
            self.create_regex()
        if self.regex == '':
            raise AttributeError("Finder is missing a regex.")

        files = []
        for root, _, files_ in os.walk(self.root):
            depth = len(os.path.relpath(root, self.root).split(os.sep)) - 1
            if depth > self.max_depth_scan:
                break
            files += [os.path.relpath(os.path.join(root, file), self.root)
                      for file in files_]
        files.sort()

        if len(files) == 0:
            raise IndexError(f"No files were found in {self.root}")
        log.debug("Found %s files in %s", len(files), self.root)

        files_matched = []
        for f in files:
            try:
                matches = self.get_matches(f, relative=True)
            except ValueError:
                pass
            else:
                files_matched.append((f, matches))

        self.scanned = True
        self.files = files_matched

    def get_matchers(self, key: str) -> List[Matcher]:
        """Return list of matchers corresponding to key.

        Parameters
        ----------
        key: str
            Can be matcher name, or group+name combination with the syntax:
            'group:name'.

        Raises
        ------
        KeyError: No matcher found.
        """
        k = key.split(':')
        if len(k) == 1:
            name, group = k[0], None
        else:
            name, group = k[:2]
        selected = []
        for m in self.matchers:
            if m.name == name and (group is None or group == m.group):
                selected.append(m)

        if len(selected) == 0:
            raise KeyError(f"No matcher found for key '{key}'")
        return selected
