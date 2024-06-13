import os
import yaml


def get_config():
    __dir__ = os.path.dirname(__file__)
    conf = {}
    conf.update(
        yaml.safe_load(open(os.path.join(__dir__, "../default_config.yaml")))
    )
    try:
        conf.update(
            yaml.safe_load(open(os.path.join(__dir__, "../config.yaml")))
        )
    except IOError:
        # Is ok if we can't load config.yaml
        pass

    return conf
