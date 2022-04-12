import base64
import pytest
from api.analyzer.analyzer import analyze_files, AnalyzeJS
from api.tests.analyzer.mock_data_test_analyzer import CONTENTS_FILE_jira_clone_client_src_shared_utils_api, \
    CONTENTS_FILE_jira_clone_client_src_shared_utils_authToken, CONTENTS_FILE_projectgroup2_src_external_dataPersist


@pytest.fixture()
def mocker_open(mocker):
    """Pytest mocker for built in function: open(filename, operation)
    :param mocker: Pytest mocker.
    :return: The custom mocker.
    """

    class MockOpen:
        def __init__(self, filename, operation):
            """Mock replacement for build in function open(filename, operation)
            :param filename: The filename (with filepath) to open.
            :type filename: str
            :param operation: The operation code to read the file with. This option is of no importance to this mocker
            and its contents will be ignored.
            :type filename: str
            """
            self.filename = filename
            self.operation = operation
            self.status = "open"

        def __enter__(self):
            """Returns the own class instance.
            Note: Method is called when running "with open(...):" and therefore must be defined, it's effect is of
            no importance to the mocker.
            :return: The class instance.
            """
            return self

        def __exit__(self, arg1, arg2, arg3):
            """Sets the internal file status to "closed".
            Note: Method is called when running "with open(...):" and therefore must be defined, it's effect is of
            no importance to the mocker.
            :param arg1: Positional argument 1 is of no importance to the mocker.
            :param arg2: Positional argument 2 is of no importance to the mocker.
            :param arg3: Positional argument 3 is of no importance to the mocker.
            :return: Nothing
            """
            self.status = "closed"

        def read(self):
            file_contents = ""
            if self.filename == "/jira_clone/client/src/shared/utils/api.js":
                file_contents = base64.b64decode(CONTENTS_FILE_jira_clone_client_src_shared_utils_api).decode("utf-8")
            elif self.filename == "/jira_clone/client/src/shared/utils/authToken.js":
                file_contents = base64.\
                    b64decode(CONTENTS_FILE_jira_clone_client_src_shared_utils_authToken).decode("utf-8")
            elif self.filename == "/project-group-2/src/external/dataPersist.js":
                file_contents = base64.b64decode(CONTENTS_FILE_projectgroup2_src_external_dataPersist).decode("utf-8")

            return file_contents

        def close(self):
            self.status = "closed"

    def patcher_open(filename, operation):
        """The patcher function to use instead of open().
        :param filename: The filename (with filepath) to open.
        :type filename: str
        :param operation: The operation code to read the file with. This option is of no importance to this mocker and
        its contents will be ignored.
        :type filename: str
        :return: The initiated mocker instance.
        """
        return MockOpen(filename, operation)

    def mocker_return(to_mock):
        """Mocker to send back to test.
        :param to_mock: Variant of open() to mock.
        :type to_mock: str
        :return: Nothing
        """
        mocker.patch(to_mock, side_effect=patcher_open)

    yield mocker_return


def test_class_esprimaanalyze_init_file_location_not_string():
    file_location = False
    try:
        AnalyzeJS(file_location)
        assert False
    except TypeError as e:
        assert str(e) == "'file_location' must be a STRING"
    except Exception:
        assert False


def test_class_esprimaanalyze_init_file_location_empty():
    file_location = ""
    try:
        AnalyzeJS(file_location)
        assert False
    except ValueError as e:
        assert str(e) == "'file_location' cannot be empty"
    except Exception:
        assert False


def test_class_esprimaanalyze_init_project_root_not_string():
    file_source = "/some/path/to/file.js"
    project_root = False
    try:
        AnalyzeJS(file_source, project_root)
        assert False
    except TypeError as e:
        assert str(e) == "'project_root' must be a STRING"
    except Exception:
        assert False


def test_analyze_files_arg_not_list():
    list_of_files = ""
    try:
        analyze_files(list_of_files)
        assert False
    except TypeError as e:
        assert str(e) == "'list_of_files' must be a LIST"
    except Exception:
        assert False


def test_analyze_files_arg_empty_list():
    list_of_files = []
    try:
        analyze_files(list_of_files)
        assert False
    except ValueError as e:
        assert str(e) == "'list_of_files' cannot be empty"
    except Exception:
        assert False


def test_analyze_files_arg_list_item_not_string():
    list_of_files = [
        1,
        -7
    ]
    try:
        analyze_files(list_of_files)
        assert False
    except ValueError as e:
        assert str(e) == "'list_of_files' must only contain paths to files as STRINGS"
    except Exception:
        assert False


def test_analyze_files_arg_list_item_empty_string():
    list_of_files = [
        "",
        ""
    ]
    try:
        analyze_files(list_of_files)
        assert False
    except ValueError as e:
        assert str(e) == "Paths in 'list_of_files' cannot be empty strings"
    except Exception:
        assert False