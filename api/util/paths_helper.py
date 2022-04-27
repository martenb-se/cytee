import os
import re
from api.instances.config_urang import config_urang


def get_base_directory():
    if 'directory' in config_urang and 'base' in config_urang['directory']:
        base_directory = config_urang['directory']['base']
    else:
        base_directory = os.path.dirname(os.path.abspath(__file__))

    return base_directory


def sub_directory_to_full_path(sub_directory):
    base_directory = get_base_directory()
    full_path = base_directory + "/" + sub_directory

    if not re.match(
            re.escape(base_directory),
            os.path.abspath(full_path)):
        full_path = base_directory

    return full_path


def full_path_to_correct_sub_directory(full_path):
    return re.sub(
        r"^" + re.escape(os.path.abspath(get_base_directory())),
        '',
        os.path.abspath(full_path))