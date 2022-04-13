import pytest
from api.tests.fixtures.mocking.open import mocker_open
from api.tests.fixtures.mocking.os.path.isfile import mocker_os_path_isfile
import hashlib
from api.cache import read_file, save_file, compare_file_cache

MOCK_CACHE_ROOT = \
    "/some/place/.analyze_cache"
MOCK_PROJECT_ROOT = \
    "/my/mocked/project"
MOCK_FILES_AND_CONTENTS = {
    "dir/to/some_file": "Some file contents here",
    "dir/to/another_file": "This file has\nmany\nlines!\n"
}


def __copied_cache_hash_function(to_hash):
    return hashlib.sha256(str.encode(to_hash)).hexdigest()


@pytest.fixture
def mock_cache_files(mocker, mocker_open, mocker_os_path_isfile):
    mocker.patch("api.cache.CONFIG_LOCATION_CACHE", MOCK_CACHE_ROOT)

    project_root_hash = __copied_cache_hash_function(MOCK_PROJECT_ROOT)
    file_mocks_open = {}
    file_mocks_isfile = []
    for mock_file in MOCK_FILES_AND_CONTENTS.keys():
        file_mocks_open[
            f"{MOCK_CACHE_ROOT}/"
            f"{project_root_hash}/"
            f"{__copied_cache_hash_function(mock_file)}.js"] = \
            MOCK_FILES_AND_CONTENTS[mock_file]

        file_mocks_isfile.append(
            f"{MOCK_CACHE_ROOT}/"
            f"{project_root_hash}/"
            f"{__copied_cache_hash_function(mock_file)}.js"
        )

    mocker_open_write_content_drain = {}

    mocker_open(
        'api.cache.open',
        file_mocks=file_mocks_open,
        content_drain=mocker_open_write_content_drain)

    mocker_os_path_isfile(
        'api.cache.os.path.isfile',
        file_mocks=file_mocks_isfile)

    mock_os_path_isdir = mocker.patch("api.cache.os.path.isdir")
    mock_os_path_isdir().return_value = True

    yield {
        "open_write_content_drain": mocker_open_write_content_drain
    }


def test_cache_save_file_project_root_not_string():
    project_root = 123
    file_id = "file/id/not/being/tested"
    file_data = "file data not being tested"
    try:
        save_file(project_root, file_id, file_data)
        assert False
    except TypeError as e:
        assert str(e) == "'project_root' must be a STRING"
    except Exception:
        assert False


def test_cache_save_file_project_root_empty():
    project_root = ""
    file_id = "file/id/not/being/tested"
    file_data = "file data not being tested"
    try:
        save_file(project_root, file_id, file_data)
        assert False
    except ValueError as e:
        assert str(e) == "'project_root' cannot be empty"
    except Exception:
        assert False


def test_cache_save_file_file_id_not_string():
    project_root = "project/root/not/being/tested"
    file_id = 123
    file_data = "file data not being tested"
    try:
        save_file(project_root, file_id, file_data)
        assert False
    except TypeError as e:
        assert str(e) == "'file_id' must be a STRING"
    except Exception:
        assert False


def test_cache_save_file_file_id_empty():
    project_root = "project/root/not/being/tested"
    file_id = ""
    file_data = "file data not being tested"
    try:
        save_file(project_root, file_id, file_data)
        assert False
    except ValueError as e:
        assert str(e) == "'file_id' cannot be empty"
    except Exception:
        assert False


def test_cache_save_file_file_data_not_string():
    project_root = "project/root/not/being/tested"
    file_id = "file/id/not/being/tested"
    file_data = 123
    try:
        save_file(project_root, file_id, file_data)
        assert False
    except TypeError as e:
        assert str(e) == "'file_data' must be a STRING"
    except Exception:
        assert False


def test_cache_save_file_file_data_empty():
    project_root = "project/root/not/being/tested"
    file_id = "file/id/not/being/tested"
    file_data = ""
    try:
        save_file(project_root, file_id, file_data)
        assert False
    except ValueError as e:
        assert str(e) == "'file_data' cannot be empty"
    except Exception:
        assert False


def test_cache_save_file(mock_cache_files):
    project_root = "/my/mocked/project"
    project_root_hash = __copied_cache_hash_function(project_root)
    file_id = "dir/to/some_file"
    file_id_hash = __copied_cache_hash_function(file_id)
    file_contents_to_write = "These are the file contents!"

    mock_cache_files_objects = mock_cache_files
    save_file(project_root, file_id, file_contents_to_write)

    written_file_contents = \
        mock_cache_files_objects[
            "open_write_content_drain"
        ][
            f"{MOCK_CACHE_ROOT}/"
            f"{project_root_hash}/"
            f"{file_id_hash}.js"]

    assert written_file_contents == file_contents_to_write


def test_cache_read_file_project_root_not_string():
    project_root = 123
    file_id = "file/id/not/being/tested"
    try:
        read_file(project_root, file_id)
        assert False
    except TypeError as e:
        assert str(e) == "'project_root' must be a STRING"
    except Exception:
        assert False


def test_cache_read_file_project_root_empty():
    project_root = ""
    file_id = "file/id/not/being/tested"
    try:
        read_file(project_root, file_id)
        assert False
    except ValueError as e:
        assert str(e) == "'project_root' cannot be empty"
    except Exception:
        assert False


def test_cache_read_file_file_id_not_string():
    project_root = "project/root/not/being/tested"
    file_id = 123
    try:
        read_file(project_root, file_id)
        assert False
    except TypeError as e:
        assert str(e) == "'file_id' must be a STRING"
    except Exception:
        assert False


def test_cache_read_file_file_id_empty():
    project_root = "project/root/not/being/tested"
    file_id = ""
    try:
        read_file(project_root, file_id)
        assert False
    except ValueError as e:
        assert str(e) == "'file_id' cannot be empty"
    except Exception:
        assert False


def test_cache_read_file_nonexistant(mock_cache_files):
    project_root = "project/root/not/being/tested"
    file_id = "dir/to/missing_file"
    try:
        read_file(project_root, file_id)
        assert False
    except FileNotFoundError as e:
        assert str(e) == \
               f"For project in '{project_root}', there is no cache for file "\
               f"with ID '{file_id}'"
    except Exception:
        assert False


def test_cache_read_file_existing(mock_cache_files):
    project_root = "/my/mocked/project"
    file_id = "dir/to/some_file"
    expected_result = "Some file contents here"

    result = read_file(project_root, file_id)

    assert result == expected_result


def test_cache_compare_file_project_root_not_string():
    project_root = 123
    file_id = "file/id/not/being/tested"
    new_file_data = "new file data not being tested"
    try:
        compare_file_cache(project_root, file_id, new_file_data)
        assert False
    except TypeError as e:
        assert str(e) == "'project_root' must be a STRING"
    except Exception:
        assert False


def test_cache_compare_file_project_root_empty():
    project_root = ""
    file_id = "file/id/not/being/tested"
    new_file_data = "new file data not being tested"
    try:
        compare_file_cache(project_root, file_id, new_file_data)
        assert False
    except ValueError as e:
        assert str(e) == "'project_root' cannot be empty"
    except Exception:
        assert False


def test_cache_compare_file_file_id_not_string():
    project_root = "project/root/not/being/tested"
    file_id = 123
    new_file_data = "new file data not being tested"
    try:
        compare_file_cache(project_root, file_id, new_file_data)
        assert False
    except TypeError as e:
        assert str(e) == "'file_id' must be a STRING"
    except Exception:
        assert False


def test_cache_compare_file_file_id_empty():
    project_root = "project/root/not/being/tested"
    file_id = ""
    new_file_data = "new file data not being tested"
    try:
        compare_file_cache(project_root, file_id, new_file_data)
        assert False
    except ValueError as e:
        assert str(e) == "'file_id' cannot be empty"
    except Exception:
        assert False


def test_cache_compare_file_new_file_data_not_string():
    project_root = "project/root/not/being/tested"
    file_id = "file/id/not/being/tested"
    new_file_data = 123
    try:
        compare_file_cache(project_root, file_id, new_file_data)
        assert False
    except TypeError as e:
        assert str(e) == "'new_file_data' must be a STRING"
    except Exception:
        assert False


def test_cache_compare_file_new_file_data_empty():
    project_root = "project/root/not/being/tested"
    file_id = "file/id/not/being/tested"
    new_file_data = ""
    try:
        compare_file_cache(project_root, file_id, new_file_data)
        assert False
    except ValueError as e:
        assert str(e) == "'new_file_data' cannot be empty"
    except Exception:
        assert False


def test_cache_compare_file_nonexistant(mock_cache_files):
    project_root = "project/root/not/being/tested"
    file_id = "dir/to/missing_file"
    new_file_data = "new file data not being tested"
    try:
        compare_file_cache(project_root, file_id, new_file_data)
        assert False
    except FileNotFoundError as e:
        assert str(e) == \
               f"For project in '{project_root}', there is no cache for file "\
               f"with ID '{file_id}' to use for comparison."
    except Exception:
        assert False


def test_compare_file_cache_test(mock_cache_files):
    project_root = "/my/mocked/project"
    file_id = "dir/to/another_file"
    new_file_data = "This file has\nsome\nlines!\n"
    expected_result = "  This file has\n- many\n+ some\n  lines!"

    result = compare_file_cache(project_root, file_id, new_file_data)

    assert result == expected_result
