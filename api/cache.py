import hashlib
import os
import difflib

# TODO: Move configuration to config.urangu.yaml
CONFIG_LOCATION_CACHE = \
    os.path.abspath(
        os.path.dirname(os.path.abspath(__file__)) + "/../.analyze_cache")


def __get_cache_path(project_root):
    project_root_hash = hashlib.sha256(str.encode(project_root)).hexdigest()
    return CONFIG_LOCATION_CACHE + f"/{project_root_hash}"


def __get_cache_file(project_root, file_id):
    file_id_hash = hashlib.sha256(str.encode(file_id)).hexdigest()
    return f"{__get_cache_path(project_root)}/{file_id_hash}.js"


def save_file(project_root, file_id, file_data):
    if not os.path.isdir(__get_cache_path(project_root)):
        os.makedirs(__get_cache_path(project_root), exist_ok=True)
    with open(__get_cache_file(project_root, file_id), 'w') as cache_file:
        cache_file.write(file_data)


def read_file(project_root, file_id):
    file_contents = False
    if os.path.isfile(__get_cache_file(project_root, file_id)):
        with open(__get_cache_file(project_root, file_id), 'r') as cache_file:
            file_contents = cache_file.read()
    return file_contents


def compare_file_cache(project_root, file_id, new_file_data):
    cache_file_contents = read_file(project_root, file_id).splitlines()
    new_file_data = new_file_data.splitlines()
    differ = difflib.Differ()
    differences = \
        differ.compare(cache_file_contents, new_file_data)
    return '\n'.join(differences)
