import os
import yaml

STANDARD_CONFIG_LOCATION = \
    os.path.abspath(
        os.path.dirname(os.path.abspath(__file__)) +
        f"/../../urang.config.yml")

config_urang = yaml.safe_load(open(STANDARD_CONFIG_LOCATION))
