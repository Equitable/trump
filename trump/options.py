###############################################################################
#
# PyLint tests that will never be applied by Trump.
#
# Invalid constant name, the variables defined here aren't constants.
# pylint: disable-msg=C0103
#
# Used * or ** magic, we're not getting rid of this, it's imperative to Trump.
# pylint: disable-msg=W0142

"""
Parses config files at runtime, but still enables importing of this module
"""
import os
import ConfigParser
import warnings

def get_from_nested(keys, adict):
    if len(keys) > 0:
        if keys[0] in adict:
            return get_from_nested(keys[1:],adict[keys[0]])
        else:
            raise KeyError("{} not found.".format(keys[0]))
    else:
        return adict

def _read_options(paths,fname_def=None):
    """Builds a configuration reader function"""
    def reader_func(fname=fname_def, sect=None, sett=None, default=None):
        """Reads the configuration for trump"""

        cur_dir = os.path.dirname(os.path.realpath(__file__))
        config_dir = os.path.join(cur_dir, *paths)

        config_files = [(f[:-4], f)
                        for f in os.listdir(config_dir) if f[-4:] == ".cfg"]
        sample_files = [(f[:-11], f)
                        for f in os.listdir(config_dir) if f[-11:] == ".cfg_sample"]

        if fname:
            config_files = [f for f in config_files if f[0] == fname]
            sample_files = [f for f in sample_files if f[0] == fname]


        config_files = dict(config_files)
        sample_files = dict(sample_files)

        cfg_files = sample_files
        for fn, f in config_files.iteritems():
            cfg_files[fn] = f

        sample_files_exposed = []

        confg = {}

        for src, fil in cfg_files.iteritems():
            confg[src] = {}
            cfpr = ConfigParser.ConfigParser()
            cfpr.read(os.path.join(config_dir, fil))
            for sec in cfpr.sections():
                confg[src][sec] = dict(cfpr.items(sec))

            if ".cfg_sample" in fil:
                sample_files_exposed.append(fil)


        if len(sample_files_exposed) > 0:
            msg = ", ".join(sample_files_exposed)
            body = "{} sample configuration files have been exposed. " \
                  "Rename *.cfg_sample to *.cfg, and populate the " \
                  "correct settings in the config and settings " \
                  "directories to avoid this warning."
            msg = body.format(msg)
            warnings.warn(msg)

        keys = []

        if fname:
            keys.append(fname)
            if sect:
                keys.append(sect)
                if sett:
                    keys.append(sett)
        try:
            return get_from_nested(keys, confg)
        except KeyError:
            if default is not None:
                return default
            else:
                raise

    return reader_func

read_config = _read_options(["config"], 'trump')
read_settings = _read_options(["templating", "settings"])

if __name__ == '__main__':
    config = read_config()
    print config
    
    raise_by_default = read_config(sect='options', sett='raise_by_default')
    print raise_by_default

    eng_str = read_config(sect='readwrite', sett='engine')
    print eng_str

    settings = read_settings(fname='Quandl', sect='userone', sett='authtoken')
    print settings

    settings = read_settings(fname='Quandl', sect='userone', sett='authkey', default='XXXX')
    print settings

    settings = read_settings()
    print settings