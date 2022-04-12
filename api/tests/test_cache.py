import pytest
from api.tests.fixtures.mocking.open import mocker_open
from api.tests.fixtures.mocking.os.path.isfile import mocker_os_path_isfile
import hashlib
from api.cache import read_file, save_file, compare_file_cache

MOCK_CACHE_ROOT = \
    "/home/icean/ownCloud/Study/Exjobb/project/cytee/.analyze_cache"
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
    project_root_hash = __copied_cache_hash_function(MOCK_PROJECT_ROOT)
    file_mocks_open = {}
    for mock_file in MOCK_FILES_AND_CONTENTS.keys():
        file_mocks_open[
            f"{MOCK_CACHE_ROOT}/"
            f"{project_root_hash}/"
            f"{__copied_cache_hash_function(mock_file)}.js"] = \
            MOCK_FILES_AND_CONTENTS[mock_file]

    file_mocks_isfile = []
    for mock_file in MOCK_FILES_AND_CONTENTS.keys():
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


def test_cache_read_file_nonexistant(mock_cache_files):
    file_contents = read_file("/my/mocked/project", "dir/to/missing_file")
    assert file_contents is False


def test_cache_read_file_existing(mock_cache_files):
    file_contents = read_file("/my/mocked/project", "dir/to/some_file")
    assert file_contents == "Some file contents here"


def test_cache_save_file(mock_cache_files):
    project_root = "/my/mocked/project"
    project_root_hash = __copied_cache_hash_function(project_root)
    file_id = "dir/to/some_file"
    file_id_hash = __copied_cache_hash_function(file_id)
    file_contents_to_write = "These are the file contents!"

    mock_cache_files_objects = mock_cache_files
    save_file(project_root, file_id, file_contents_to_write)

    written_file_contents = \
        mock_cache_files_objects["open_write_content_drain"][
            f"{MOCK_CACHE_ROOT}/"
            f"{project_root_hash}/"
            f"{file_id_hash}.js"]

    assert written_file_contents == file_contents_to_write


def test_compare_file_cache_test(mock_cache_files):
    project_root = "/my/mocked/project"
    file_id = "dir/to/another_file"

    file_compare = compare_file_cache(
        project_root,
        file_id,
        "This file has\nsome\nlines!\n")

    expected_result = "  This file has\n- many\n+ some\n  lines!"

    assert file_compare == expected_result
