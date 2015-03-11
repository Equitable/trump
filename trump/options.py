import os
import ConfigParser

def _read_options(p):
    def reader_func():
        """Reads the configuration for trump"""
           
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        config_dir = os.path.join(cur_dir,*p)
        config_files = [(f,f[:-4]) for f in os.listdir(config_dir) if f[-4:] == ".cfg"]
        
        config = {}
        
        for fil,src in config_files:
            config[src] = {}
            cp = ConfigParser.ConfigParser()
            cp.read(os.path.join(config_dir,fil))
            for section in cp.sections():
                config[src][section] = dict(cp.items(section))
        
        return config
    return reader_func

read_config = _read_options(["config"])
read_settings = _read_options(["templating","settings"])

if __name__ == '__main__':
    config = read_config()
    settings = read_settings()