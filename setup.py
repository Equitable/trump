import os

from setuptools import setup

def read(*p):
    """Build a file path from paths and return the contents."""
    with open(os.path.join(*p), 'r') as fi:
        return fi.read()

v = '0.0.1'

setup(
  name = 'Trump',
  version = v,
  packages = ['trump'],
  description = 'Objectified Indexed Data',
  install_requires=['smuggle','pandas','SQLAlchemy']
  long_description=(read('README.rst')),
  author = 'Jeffrey McLarty',
  author_email = 'jeffrey.mclarty@gmail.com',
  url = 'https://github.com/Equitable/trump/'
  download_url = 'https://github.com/Equitable/trump/tarball/' + v,
  keywords = ['data', 'timeseries', 'time series', 'indexed', 'objectified', 'trump', 'monotonic', 'RDD', 'relational database', 'pandas', 'SQLAlchemy']
  classifiers = ['Development Status :: 1 - Planning',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: BSD License',
                 'Topic :: Database',
                 'Topic :: Office/Business',
                 'Topic :: Scientific/Engineering',
                 'Operating System :: OS Independent',             
                 'Programming Language :: Python :: 2.7'])