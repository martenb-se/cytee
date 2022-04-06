import base64
import pytest
from api.analyzer.analyzer import analyze_files, EsprimaAnalyze
from api.tests.analyzer.mock_data_test_analyzer import CONTENTS_FILE_jira_clone_client_src_shared_utils_api, \
    CONTENTS_FILE_jira_clone_client_src_shared_utils_authToken, CONTENTS_FILE_projectgroup2_src_external_dataPersist


@pytest.fixture()
def mocker_open(mocker):
    class MockOpen:
        def __init__(self, filename, operation):
            self.filename = filename
            self.operation = operation
            self.status = "open"

        # Used for: "with open(...):"
        def __enter__(self):
            return self

        # Used for: "with open(...):"
        def __exit__(self, arg1, arg2, arg3):
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

    # Function to pass to patcher
    def patcher_open(filename, operation):
        return MockOpen(filename, operation)

    mock_open = mocker.patch('api.analyzer.analyzer.open', side_effect=patcher_open)
    # yield mock_open


def test_class_esprimaanalyze_init_not_string():
    file_source = False
    try:
        EsprimaAnalyze(file_source)
        assert False
    except TypeError as e:
        assert str(e) == "'file_source' must be a STRING"
    except Exception:
        assert False


def test_class_esprimaanalyze_init_no_content():
    file_source = ""
    try:
        EsprimaAnalyze(file_source)
        assert False
    except ValueError as e:
        assert str(e) == "'file_source' cannot be empty"
    except Exception:
        assert False


# TODO: Use test..
def test_class_esprimaanalyze_process_functions_fun_a():
    file_source = """const defaults = {
  baseURL: process.env.API_URL || 'http://localhost:3000',
  headers: () => ({
    'Content-Type': 'application/json',
    Authorization: getStoredAuthToken() ? `Bearer ${getStoredAuthToken()}` : undefined,
  }),
  error: {
    code: 'INTERNAL_ERROR',
    message: 'Something went wrong. Please check your internet connection or contact our support.',
    status: 503,
    data: {},
  },
  stuff: {
      cookie: () => ({
          stuff: '123'
      }),
      dragon: {
          whoops: () => ({
              thisstuff: '333'
          })
      }
  }
};"""

    """source_handler = HandleEsprima(file_source)
    source_handler.process_functions()"""
    assert True


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


# TODO: Continue with testing
"""
def test_debug(mocker_open):
    list_of_files = [
        "/jira_clone/client/src/shared/utils/api.js",
        "/jira_clone/client/src/shared/utils/authToken.js",
        "/project-group-2/src/external/dataPersist.js"
    ]

    analyze_files(list_of_files)

    assert False
"""