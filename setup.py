import os
import shutil
import sys
import time

from setuptools import setup, find_packages
from setuptools.command.install import install

v = '0.0.3'

cmds = sys.argv
installing = 'install' in cmds

def copy_cfg_sample_if_not_exists(p):
    for f in os.listdir(p):
        if ".cfg_sample" in f:
            newf = f.replace(".cfg_sample",".cfg")
            if not os.path.isfile(os.path.join(p,newf)):
                print "\nCreating {} from sample file.".format(os.path.join(p,newf))
                shutil.copy(os.path.join(p,f),os.path.join(p,newf))
            else:
                print "\n{} already exists, will overwrite momentarily. Break execution to stop.".format(newf)
                for i in range(5):
                    sys.stdout.write(".")
                    time.sleep(1)
                #if ans.upper()[0] == 'Y':
                print "Overwriting {} from sample file.".format(newf)
                shutil.copy(os.path.join(p,f),os.path.join(p,newf))
                #else:
                #    print "Skipping {}.".format(newf)

class TrumpInstall(install):
    def run(self):
        install.run(self)
        if installing:
            config_path = os.path.join(self.install_lib,'trump','config')
            copy_cfg_sample_if_not_exists(config_path)        
            settings_path = os.path.join(self.install_lib,'trump','templating','settings')
            copy_cfg_sample_if_not_exists(settings_path)  
        
        
def read(*p):
    """Build a file path from paths and return the contents."""
    with open(os.path.join(*p), 'r') as fi:
        return fi.read()

setup(
  name = 'Trump',
  version = v,
  packages = find_packages(),
  description = 'Persistent Objectified Indexed Data',
  install_requires = ['smuggle','pandas','SQLAlchemy','Quandl','validada'],
  long_description = read('README.rst') ,
  package_data = {'': ['config/*.cfg_sample', 'test/*.py', 'test/testdata/*.csv'], 
                  'trump.templating' : ['settings/*.cfg_sample', 'test/*'], 
                  'trump.aggregation' : ['test/*'],
                  #'trump.extensions.source' : ['*'],
                  'trump.extensions' : ['*.py'] + ['source/{}/*'.format(f) for f in ['bbfetch', 'dbapi', 'psycopg2', 'pydatacsv', 'pydatadatareaderst', 'quandl', 'sqlalchemy', 'worldbankst']],
                  'trump.reporting' : ['test/*'],
                  'trump.tools' : ['test/*']},
  cmdclass = {'install': TrumpInstall},
  author = 'Jeffrey McLarty',
  author_email = 'jeffrey.mclarty@gmail.com',
  url = 'http://Equitable.github.com/trump/',
  download_url = 'https://github.com/Equitable/trump/tarball/' + v,
  keywords = ['data', 'timeseries', 'time series', 'indexed', 'objectified', 'trump', 'monotonic', 'RDD', 'relational database', 'pandas', 'SQLAlchemy'],
  classifiers = ['Development Status :: 1 - Planning',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: BSD License',
                 'Topic :: Database',
                 'Topic :: Office/Business',
                 'Topic :: Scientific/Engineering',
                 'Operating System :: OS Independent',             
                 'Programming Language :: Python :: 2.7'])