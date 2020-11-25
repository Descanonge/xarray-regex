"""Find files using a pre-regex."""

import os
import logging
import re

from typing import List, Union

from xarray_regex.matcher import Matcher

log = logging.getLogger(__name__)


class FileFinder():

    MAX_DEPTH_SCAN = 3
    """Limit descending into lower directories when finding files."""

    def __init__(self, root: Union[str, List[str]], pregex: str, **replacements: str):

        if isinstance(root, (list, tuple)):
            root = os.path.join(*root)
        if not os.path.isdir(root):
            raise ValueError(f"'{root}' directory does not exist.")
        self.root = root

        self.pregex = ''
        self.regex = None
        self.matchers = []
        self.segments = []
        self.fixed_matcher = dict()
        self.files = []
        self.scanned = False

        self.set_pregex(pregex, **replacements)

    @property
    def n_matchers(self):
        return len(self.matchers)

    def set_pregex(self, pregex: str, **replacements: str):
        pregex = pregex.strip()
        for k, z in replacements.items():
            pregex = pregex.replace("%({:s})".format(k), z)
        self.pregex = pregex

    def fix_matcher(self, idx: int, value: str):
        self.fixed_matcher[idx] = value

    def create_regex(self):
        self.scan_pregex()

        segments = self.segments.copy()
        for idx, m in enumerate(self.matchers):
            segments[2*idx+1] = m.get_regex()

        for idx, value in self.fixed_matcher.items():
            segments[2*idx+1] = value

        self.regex = ''.join(segments)
        self.pattern = re.compile(self.regex + "$")

    def scan_pregex(self):
        """Scan pregex for matchers."""
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

    def find_files(self):
        """Find files to scan.

        Uses os.walk. Limit search to `MAX_DEPTH_SCAN` levels of directories
        deep.

        If `file_override` is set, bypass this search, just use it.

        Sort files alphabetically.

        :raises AttributeError: If no regex is set.
        :raises IndexError: If no files are found.
        """
        if self.regex is None:
            self.create_regex()
        if self.regex == '':
            raise AttributeError("Finder is missing a regex.")

        files = []
        for root, _, files_ in os.walk(self.root):
            depth = len(os.path.relpath(root, self.root).split(os.sep)) - 1
            if depth > self.MAX_DEPTH_SCAN:
                break
            files += [os.path.relpath(os.path.join(root, file), self.root)
                      for file in files_]
        files.sort()

        if len(files) == 0:
            raise IndexError(f"No files were found in {self.root}")
        log.debug("Found %s files in %s", len(files), self.root)

        files_matched = [f for f in files
                         if self.pattern.match(f) is not None]

        self.scanned = True
        self.files = files_matched

    def get_files(self, relative=False):
        if not self.scanned:
            self.find_files()
        files = self.files
        if not relative:
            files = [os.path.join(self.root, f) for f in files]
        return files

    def get_matches(self, filename):
        m = self.pattern.match(filename)
        if m is None:
            raise ValueError("Filename did not match pattern.")
        if len(m.groups()) != self.n_matchers:
            raise IndexError("Not as many groups as matches.")
        matches = {}
        for i in range(self.n_matchers):
            matcher = self.matchers[i]
            if matcher.discard:
                continue
            matches[matcher.name] = {
                'match': m.group(i+1),
                'start': m.start(i+1),
                'end': m.end(i+1),
                'matcher': matcher
            }
        return matches

    def get_func_process_filename(self, func, relative=True, *args, **kwargs):
        def f(ds):
            filename = ds.encoding['source']
            if relative:
                filename = os.path.relpath(filename, self.root)
            return func(ds, filename, self, *args, **kwargs)
        return f
