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


def _read_options(paths, fname=None):
    """Builds a configuration reader function"""
    def reader_func(section=None):
        """Reads the configuration for trump"""

        cur_dir = os.path.dirname(os.path.realpath(__file__))
        config_dir = os.path.join(cur_dir, *paths)
        config_files = [(f, f[:-4])
                        for f in os.listdir(config_dir) if f[-4:] == ".cfg"]

        confg = {}

        for fil, src in config_files:
            confg[src] = {}
            cfpr = ConfigParser.ConfigParser()
            cfpr.read(os.path.join(config_dir, fil))
            for sec in cfpr.sections():
                confg[src][sec] = dict(cfpr.items(sec))

        if fname in confg:
            if section in confg[fname]:
                return confg[fname][section]
            return confg[fname]
        return confg

    return reader_func

read_config = _read_options(["config"], 'trump')
read_settings = _read_options(["templating", "settings"])

if __name__ == '__main__':
    config = read_config()
    settings = read_settings()
