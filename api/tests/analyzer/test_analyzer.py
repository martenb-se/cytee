import os
import pytest
from api.tests.fixtures.mocking.open import mocker_open
from api.analyzer.analyzer import analyze_files, AnalyzeJS

MOCK_PROJECT_ROOT = "/project/src/"
MOCK_FILES_AND_CONTENTS = [
    # (FAKED FILE,
    # REAL FILE IN "analyzer_test_data" FOLDER)

    # Syntax Testing
    ("/project/src/bad_code.js",
     "bad_code.js"),

    # Version Check
    ("/project/src/supported_object_spreading.js",
     "version_check/ecmascript-2018_object_spreading.js"),

    ("/project/src/unsupported_optional_catch_bind.js",
     "version_check/ecmascript-2019_optional_catch_bind.js"),

    ("/project/src/unsupported_private_class_variable.js",
     "version_check/ecmascript-2020_private_class_variable.js"),

    ("/project/src/unsupported_logical_assignment.js",
     "version_check/ecmascript-2021_logical_assignment.js"),

    ("/project/src/unsupported_private_slot_check.js",
     "version_check/ecmascript-2022_private_slot_check.js"),

    # Global
    ("/project/src/global_function.js",
     "global_function.js")
]


@pytest.fixture
def mock_project_files(mocker_open):
    file_mocks_open = {}
    for mock_file in MOCK_FILES_AND_CONTENTS:
        faked_file, real_file_path = mock_file
        mocked_file_path = \
            os.path.abspath(
                os.path.dirname(os.path.abspath(__file__)) +
                "/analyzer_test_data/" +
                real_file_path)

        with open(mocked_file_path, "r") as mocked_file:
            file_mocks_open[faked_file] = mocked_file.read()

    mocker_open(
        'api.analyzer.analyzer.open',
        file_mocks=file_mocks_open)

    yield


def test_class_esprimaanalyze_init_file_location_not_string():
    file_location = False
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except TypeError as e:
        assert str(e) == "'file_location' must be a STRING"
    except Exception:
        assert False


def test_class_esprimaanalyze_init_file_location_empty():
    file_location = ""
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
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


def test_class_esprimaanalyze_init_project_root_empty():
    file_location = "/some/path/to/file.js"
    project_root = ""
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except ValueError as e:
        assert str(e) == "'project_root' cannot be empty"
    except Exception:
        assert False


def test_class_esprimaanalyze_init_file_nonexistant():
    file_location = "/project/src/missing_file.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except FileNotFoundError as e:
        assert str(e) == \
               f"File at '{file_location}' cannot be found and analyzed."
    except Exception:
        assert False


def test_class_esprimaanalyze_init_bad_code(mock_project_files):
    file_location = "/project/src/bad_code.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except SyntaxError as e:
        assert str(e) == \
               "Contents in file at 'file_location' string could not be " \
               "parsed.\nInformation from esprima:\nLine 1: Missing " \
               "initializer in const declaration"
    except Exception:
        assert False


def test_class_esprimaanalyze_init_supported_object_spreading(
        mock_project_files):
    file_location = "/project/src/unsupported_object_spreading.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert True
    except SyntaxError as e:
        assert False
    except Exception:
        assert False


def test_class_esprimaanalyze_init_unsupported_optional_catch_bind(
        mock_project_files):
    file_location = "/project/src/unsupported_optional_catch_bind.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except SyntaxError as e:
        assert str(e) == \
               "Contents in file at 'file_location' string could not be " \
               "parsed.\nInformation from esprima:\nLine 4: Unexpected token {"
    except Exception:
        assert False


def test_class_esprimaanalyze_init_unsupported_private_class_variable(
        mock_project_files):
    file_location = "/project/src/unsupported_private_class_variable.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except SyntaxError as e:
        assert str(e) == \
               "Contents in file at 'file_location' string could not be " \
               "parsed.\nInformation from esprima:\nLine 3: Unexpected " \
               "token ILLEGAL"
    except Exception:
        assert False


def test_class_esprimaanalyze_init_unsupported_logical_assignment(
        mock_project_files):
    file_location = "/project/src/unsupported_logical_assignment.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except SyntaxError as e:
        assert str(e) == \
               "Contents in file at 'file_location' string could not be " \
               "parsed.\nInformation from esprima:\nLine 4: Unexpected token ="
    except Exception:
        assert False


def test_class_esprimaanalyze_init_unsupported_private_slot_check(
        mock_project_files):
    file_location = "/project/src/unsupported_private_slot_check.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except SyntaxError as e:
        assert str(e) == \
               "Contents in file at 'file_location' string could not be " \
               "parsed.\nInformation from esprima:\nLine 11: Unexpected " \
               "token ILLEGAL"
    except Exception:
        assert False


# TODO: TEST PRIVATE CLASSES


def test_class_esprimaanalyze_begin_analyze_global_function(
        mock_project_files):
    file_location = "/project/src/global_function.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_found_number_functions = 1
    expected_found_function = "noArguments"

    created_functions = analyzer.get_functions()

    assert \
        expected_found_number_functions == len(created_functions) and \
        expected_found_function in created_functions


# TODO: TEST MORE SPECIFIC CASES AS DIRECTLY ABOVE


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
        assert str(e) == \
               "'list_of_files' must only contain paths to files as STRINGS"
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
