import os
import yaml


def get_config():
    __dir__ = os.path.dirname(__file__)
    conf = {}
    default_config_path = os.path.join(__dir__, "../default_config.yaml")
    conf.update(yaml.safe_load(open(default_config_path)))
    print(f"Loaded default config from {default_config_path}")
    config_path = os.path.join(__dir__, "../config.yaml")
    try:
        conf.update(yaml.safe_load(open(config_path)))
        print(f"Loaded custom config from {config_path}")
    except IOError:
        # Is ok if we can't load config.yaml
        print(f"WARNING: unable to load custom config from {config_path}")
        pass

    return conf
