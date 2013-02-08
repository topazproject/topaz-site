from ConfigParser import RawConfigParser


def read_config(conf_file):
    config = RawConfigParser()
    with open(conf_file) as f:
        config.readfp(f)
    return dict([
        (section, dict(config.items(section)))
        for section in config.sections()
    ])
