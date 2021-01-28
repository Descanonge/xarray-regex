
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))


def get_long_description(rel_path):
    with open(path.join(here, rel_path)) as file:
        return file.read()


def get_version(rel_path):
    with open(path.join(here, rel_path)) as file:
        lines = file.read().splitlines()
    for line in lines:
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string")


setup(name='xarray-regex',
      version=get_version('src/xarray_regex/__init__.py'),

      description="Find files using regular expression to feed them to Xarray.",
      long_description=get_long_description('README.md'),
      long_description_content_type='text/markdown',

      keywords='xarray regex files',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
          'Operating System :: OS Independent'
      ],

      url='https://github.com/Descanonge/xarray-regex',
      project_urls={
          'Source': 'https://github.com/Descanonge/xarray-regex',
          'Documentation': 'https://xarray-regex.readthedocs.io'
      },

      author='Clément Haëck',
      author_email='clement.haeck@posteo.net',

      python_requires='>=3.7',

      package_dir={'': 'src'},
      packages=find_packages(where='src'),
      )
