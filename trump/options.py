import os
import ConfigParser

def _read_options(p,fname=None):
    def reader_func(section=None):
        """Reads the configuration for trump"""
           
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        config_dir = os.path.join(cur_dir,*p)
        config_files = [(f,f[:-4]) for f in os.listdir(config_dir) if f[-4:] == ".cfg"]
        
        config = {}
        
        for fil,src in config_files:
            config[src] = {}
            cp = ConfigParser.ConfigParser()
            cp.read(os.path.join(config_dir,fil))
            for sec in cp.sections():
                config[src][sec] = dict(cp.items(sec))
        
        if fname in config:
            if section in config[fname]:
                return config[fname][section]
            return config[fname]
        return config
        
    return reader_func

read_config = _read_options(["config"],'trump')
read_settings = _read_options(["templating","settings"])

if __name__ == '__main__':
    config = read_config()
    settings = read_settings()