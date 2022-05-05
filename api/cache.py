import datetime
import hashlib
import os
import difflib
import shutil

# TODO: Move configuration to config.urangu.yaml
CONFIG_LOCATION_CACHE = \
    os.path.abspath(
        os.path.dirname(os.path.abspath(__file__)) + "/../.analyze_cache")

__MEMORY_MAX_TIME = 600  # 10 minutes
__MEMORY = {}


def __get_cache_path(project_root: str) -> str:
    """Get cache path for the current project.

    :param project_root: The project root directory.
    :type project_root: str

    :return: The project's cache path.
    :rtype: str
    """
    project_root_hash = hashlib.sha256(str.encode(project_root)).hexdigest()
    return CONFIG_LOCATION_CACHE + f"/{project_root_hash}"


def __get_cache_file(project_root: str, file_id: str) -> str:
    """Get cache path to the file for the current project.

    :param project_root: The project root directory.
    :type project_root: str
    :param file_id: The file ID for the file to get the path for.
    :type file_id: str

    :return: The cache path for the file in the project.
    :rtype: str
    """
    file_id_hash = hashlib.sha256(str.encode(file_id)).hexdigest()
    return f"{__get_cache_path(project_root)}/{file_id_hash}.js"


def __get_old_cache_file(project_root: str, file_id: str) -> str:
    """Get old cache path to the file for the current project.

    :param project_root: The project root directory.
    :type project_root: str
    :param file_id: The file ID for the file to get the path for.
    :type file_id: str

    :return: The cache path for the file in the project.
    :rtype: str
    """
    file_id_hash = hashlib.sha256(str.encode(file_id)).hexdigest()
    return f"{__get_cache_path(project_root)}/{file_id_hash}[OLD].js"


def clear_cache(project_root: str) -> None:
    """Clear the entire cache for the given project.

    :param project_root: The project root directory.
    :type project_root: str

    :return: None
    """
    if os.path.isdir(__get_cache_path(project_root)):
        shutil.rmtree(__get_cache_path(project_root))


def save_file(project_root: str, file_id: str, file_data: str):
    """Save cache to the given file in the given project with the specified
    data.

    :param project_root: The project root directory.
    :type project_root: str
    :param file_id: The file ID for the file to save in cache.
    :type file_id: str
    :param file_data: The data to save to the cache.
    :type file_data: str

    :return: Nothing

    :raises TypeError: If any of the given arguments are of the wrong type.
    :raises ValueError: If any of the given arguments are missing necessary
    data.
    """
    if not isinstance(project_root, str):
        raise TypeError("'project_root' must be a STRING")
    elif len(project_root) < 1:
        raise ValueError("'project_root' cannot be empty")

    if not isinstance(file_id, str):
        raise TypeError("'file_id' must be a STRING")
    elif len(file_id) < 1:
        raise ValueError("'file_id' cannot be empty")

    if not isinstance(file_data, str):
        raise TypeError("'file_data' must be a STRING")
    elif len(file_data) < 1:
        raise ValueError("'file_data' cannot be empty")

    if not os.path.isdir(__get_cache_path(project_root)):
        os.makedirs(__get_cache_path(project_root), exist_ok=True)

    # Save old cache contents before overwriting new ones.
    try:
        old_cache_contents = read_file(project_root, file_id)
        with open(__get_old_cache_file(project_root, file_id), 'w') as \
                old_cache_file:
            old_cache_file.write(old_cache_contents)

    except FileNotFoundError:
        # No old cache contents, first time saving cache
        pass

    with open(__get_cache_file(project_root, file_id), 'w') as cache_file:
        cache_file.write(file_data)


def read_file(project_root: str, file_id: str) -> str:
    """Read cache file for the given file in the given project.

    :param project_root: The project root directory.
    :type project_root: str
    :param file_id: The file ID for the file to read from cache.
    :type file_id: str

    :return: The contents of the cache file.
    :rtype: str

    :raises TypeError: If any of the given arguments are of the wrong type.
    :raises ValueError: If any of the given arguments are missing necessary
    data.
    :raises FileNotFoundError: If there is no cache saved for the given
    project and file ID.
    """
    if not isinstance(project_root, str):
        raise TypeError("'project_root' must be a STRING")
    elif len(project_root) < 1:
        raise ValueError("'project_root' cannot be empty")

    if not isinstance(file_id, str):
        raise TypeError("'file_id' must be a STRING")
    elif len(file_id) < 1:
        raise ValueError("'file_id' cannot be empty")

    if not os.path.isfile(__get_cache_file(project_root, file_id)):
        raise FileNotFoundError(
            f"For project in '{project_root}', there is no cache for file "
            f"with ID '{file_id}'")

    with open(__get_cache_file(project_root, file_id), 'r') as cache_file:
        file_contents = cache_file.read()
    return file_contents


def read_file_old(project_root: str, file_id: str) -> str:
    """Read old cache file for the given file in the given project.

    :param project_root: The project root directory.
    :type project_root: str
    :param file_id: The file ID for the file to read from cache.
    :type file_id: str

    :return: The contents of the older cache file.
    :rtype: str

    :raises TypeError: If any of the given arguments are of the wrong type.
    :raises ValueError: If any of the given arguments are missing necessary
    data.
    :raises FileNotFoundError: If there is no cache saved for the given
    project and file ID.
    """
    if not isinstance(project_root, str):
        raise TypeError("'project_root' must be a STRING")
    elif len(project_root) < 1:
        raise ValueError("'project_root' cannot be empty")

    if not isinstance(file_id, str):
        raise TypeError("'file_id' must be a STRING")
    elif len(file_id) < 1:
        raise ValueError("'file_id' cannot be empty")

    if not os.path.isfile(__get_old_cache_file(project_root, file_id)):
        raise FileNotFoundError(
            f"For project in '{project_root}', there is no old cache for file "
            f"with ID '{file_id}'")

    with open(__get_old_cache_file(project_root, file_id), 'r') as cache_file:
        file_contents = cache_file.read()
    return file_contents


def compare_file_cache(
        project_root: str, file_id: str, new_file_data: str
) -> str:
    """Compare cache file for the given file in the given project to new
    possible file data.

    :param project_root: The project root directory.
    :type project_root: str
    :param file_id: The file ID for the file to save in cache.
    :type file_id: str
    :param new_file_data: The new file data to compare to.
    :type new_file_data: str

    :return: Comparison information for the cache file and the new data.
    :rtype: str

    :raises TypeError: If any of the given arguments are of the wrong type.
    :raises ValueError: If any of the given arguments are missing necessary
    data.
    :raises FileNotFoundError: If there is no cache saved to compare to
    for the given project and file ID.
    """
    if not isinstance(project_root, str):
        raise TypeError("'project_root' must be a STRING")
    elif len(project_root) < 1:
        raise ValueError("'project_root' cannot be empty")

    if not isinstance(file_id, str):
        raise TypeError("'file_id' must be a STRING")
    elif len(file_id) < 1:
        raise ValueError("'file_id' cannot be empty")

    if not isinstance(new_file_data, str):
        raise TypeError("'new_file_data' must be a STRING")
    elif len(new_file_data) < 1:
        raise ValueError("'new_file_data' cannot be empty")

    if not os.path.isfile(__get_cache_file(project_root, file_id)):
        raise FileNotFoundError(
            f"For project in '{project_root}', there is no cache for file "
            f"with ID '{file_id}' to use for comparison.")

    cache_contents_lines = read_file(project_root, file_id).splitlines()
    new_file_data_lines = new_file_data.splitlines()
    differ_handler = difflib.Differ()
    differences = \
        differ_handler.compare(cache_contents_lines, new_file_data_lines)
    return '\n'.join(differences)


def save_global_session(cache_prop, cache_value):
    """Save cache to the working memory. Useful for saving output from
    expensive operations.

    :param cache_prop: The name of the item in memory to save.
    :type cache_prop: str
    :param cache_value: The value to save to the memory.
    :type cache_value: Any
    :return: Nothing
    """
    __MEMORY[cache_prop] = {
        "value": cache_value,
        "time": datetime.datetime.now()
    }


def read_global_session(cache_prop):
    """Read from the working memory cache. If the cache have expired,
    None will be returned.

    :param cache_prop: The name of the item in memory to read.
    :type cache_prop: str

    :return: The contents of the cache if it exists, otherwise None. Also
    if the contents have expired None is returned.
    """
    if cache_prop in __MEMORY:
        cache_age_seconds = \
            (
                    datetime.datetime.now() - __MEMORY[cache_prop]["time"]
            ).total_seconds()

        if cache_age_seconds <= __MEMORY_MAX_TIME:
            return __MEMORY[cache_prop]["value"]

        else:
            __MEMORY.pop(cache_prop, None)

    return None


def debug_get_cache_info(project_root: str, file_id: str):
    ws = 120
    ns = 20
    print(f"{'project_root cache': <{ns}}: "
          f"{' .' + __get_cache_path(project_root)[62:]:.>{ws}}")
    print(f"{'file_id cache': <{ns}}: "
          f"{' .' + __get_cache_file(project_root, file_id)[127:]:.>{ws}}")
