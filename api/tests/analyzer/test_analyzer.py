import os
import esprima.nodes
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
     "global_function.js"),

    # Dependency
    ("/project/src/dependency_import_default.js",
     "dependency/dependency_import_default.js"),
    ("/project/src/dependency_import_named.js",
     "dependency/dependency_import_named.js"),

    # Export
    ("/project/src/export_default.js",
     "export/export_default.js"),
    ("/project/src/export_default_class.js",
     "export/export_default_class.js"),
    ("/project/src/export_default_function.js",
     "export/export_default_function.js"),
    ("/project/src/export_default_object.js",
     "export/export_default_object.js"),
    ("/project/src/export_named.js",
     "export/export_named.js"),
    ("/project/src/export_named_same_name.js",
     "export/export_named_same_name.js"),

    ("/project/src/no_export_arrow_function.js",
     "export/no_export_arrow_function.js"),
    ("/project/src/no_export_class.js",
     "export/no_export_class.js"),
    ("/project/src/no_export_function.js",
     "export/no_export_function.js"),
    ("/project/src/no_export_object_property_function.js",
     "export/no_export_object_property_function.js")

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


def __debug_created_functions(analyzer=None):
    WIN_SIZE = 150

    created_functions = analyzer.get_functions()

    if created_functions is None:
        created_functions = {}

    for created_function in created_functions:
        export_info = created_functions[created_function]['export_info']
        export_name = created_functions[created_function]['export_name']
        created_function_keys = ""
        for index, key in \
                enumerate(created_functions[created_function].keys()):
            created_function_keys += \
                f"{index:>3} " \
                f"{' ' + key:.>{WIN_SIZE - 4}}\n"

        call_chain = ""
        for index, call in \
                enumerate(created_functions[created_function]['call_chain']):
            if len(call['arguments']) > 0:
                call_args = f"({call['arguments']})"
            else:
                call_args = ""

            call_chain += \
                f"{index + 1:>3} " \
                f"{' ' + call['name'] + call_args:.>{WIN_SIZE - 4}}\n"

        print()
        print(f"{'- [ ' + created_function + ' ]':-<{WIN_SIZE}}")
        print(f"created_functions.keys():\n{created_function_keys}")
        print(f"call chain:\n{call_chain}")

        function_dependencies_list = ""
        function_dependencies = analyzer.get_method_calls(created_function)
        for index_file, file_identity in enumerate(function_dependencies):
            for index_func, string_identity in \
                    enumerate(function_dependencies[file_identity]):
                if string_identity != '!unknown' and \
                        string_identity != '!ignore':
                    function_dependencies_list += \
                        f"{index_file + 1:0>2}.{index_func + 1:0>3} " \
                        f"{' ' + file_identity + ' : ' + string_identity:.>{WIN_SIZE - 7}}\n"

        print(f"function dependencies:\n{function_dependencies_list}")

        print(f"export_info {'> ' + export_info:->{WIN_SIZE - 12}}")
        if len(export_name) > 0:
            print(f"export_name {'> ' + export_name:->{WIN_SIZE - 12}}")

        print()


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


# TODO: TEST MORE CLASS METHODS


#
# TESTING BAD SYNTAX
#


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


#
# TESTING VERSION SUPPORT
#


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


#
# TESTING SYNTAX "GENERAL"
#


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


#
# TESTING SYNTAX "DEPENDENCY"
#

def test_analyzejs_begin_analyze_dependency_import_default(
        mock_project_files):
    file_location = "/project/src/dependency_import_default.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_dependent_method_id = "dependentFunction"
    expected_dependency_import_file_id = "shared/importedDefault"
    expected_dependency_import_function_id = "importedFunctionDependency"

    function_dependencies = \
        analyzer.get_method_calls(expected_dependent_method_id)

    assert \
        expected_dependency_import_file_id in function_dependencies and \
        expected_dependency_import_function_id in \
        function_dependencies[expected_dependency_import_file_id]


def test_analyzejs_begin_analyze_dependency_import_named(
        mock_project_files):
    file_location = "/project/src/dependency_import_named.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_dependent_method_id = "dependentFunction"
    expected_dependency_import_file_id = "shared/importedNamed"
    expected_dependency_import_function_id = "importedNamedFunctionDepency"

    function_dependencies = \
        analyzer.get_method_calls(expected_dependent_method_id)

    assert \
        expected_dependency_import_file_id in function_dependencies and \
        expected_dependency_import_function_id in \
        function_dependencies[expected_dependency_import_file_id]


#
# TESTING SYNTAX "EXPORT"
#


def test_class_esprimaanalyze_begin_analyze_export_default(
        mock_project_files):
    file_location = "/project/src/export_default.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_method_id = "exportedFunction"
    expected_export_info = "export default"

    created_functions = analyzer.get_functions()

    assert \
        expected_method_id in created_functions and \
        created_functions[expected_method_id]["export_info"] == \
        expected_export_info and \
        created_functions[expected_method_id]["export_name"] == \
        expected_method_id


def test_class_esprimaanalyze_begin_analyze_export_default_class(
        mock_project_files):
    file_location = "/project/src/export_default_class.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_class = "ExportedClass"
    expected_method_id = \
        f"(new {expected_class}()).someOtherFunction"
    expected_export_info = "export default"

    created_functions = analyzer.get_functions()

    assert \
        expected_method_id in created_functions and \
        created_functions[expected_method_id]["export_info"] == \
        expected_export_info and \
        created_functions[expected_method_id]["export_name"] == \
        expected_class


def test_class_esprimaanalyze_begin_analyze_export_default_function(
        mock_project_files):
    file_location = "/project/src/export_default_function.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_method_id = "exportedFunction"
    expected_export_info = "export default"

    created_functions = analyzer.get_functions()

    assert \
        expected_method_id in created_functions and \
        created_functions[expected_method_id]["export_info"] == \
        expected_export_info and \
        created_functions[expected_method_id]["export_name"] == \
        expected_method_id


def test_class_esprimaanalyze_begin_analyze_export_default_object(
        mock_project_files):
    file_location = "/project/src/export_default_object.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_method_id = "exportedFunction"
    expected_export_info = "export default"

    created_functions = analyzer.get_functions()

    assert \
        expected_method_id in created_functions and \
        created_functions[expected_method_id]["export_info"] == \
        expected_export_info and \
        created_functions[expected_method_id]["export_name"] == \
        expected_method_id


def test_class_esprimaanalyze_begin_analyze_export_named(
        mock_project_files):
    file_location = "/project/src/export_named.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_method_id = "exportedOriginalFunction"
    expected_export_name = "exportedRenamedFunction"
    expected_export_info = "export"

    created_functions = analyzer.get_functions()

    assert \
        expected_method_id in created_functions and \
        created_functions[expected_method_id]["export_info"] == \
        expected_export_info and \
        created_functions[expected_method_id]["export_name"] == \
        expected_export_name


def test_class_esprimaanalyze_begin_analyze_export_named_same_name(
        mock_project_files):
    file_location = "/project/src/export_named_same_name.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_method_id = "exportedFunction"
    expected_export_info = "export"

    created_functions = analyzer.get_functions()

    assert \
        expected_method_id in created_functions and \
        created_functions[expected_method_id]["export_info"] == \
        expected_export_info and \
        created_functions[expected_method_id]["export_name"] == \
        expected_method_id


#
# TESTING SYNTAX "NO EXPORT"
#


def test_class_esprimaanalyze_begin_analyze_no_export_arrow_function(
        mock_project_files):
    file_location = "/project/src/no_export_arrow_function.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_method_id = "privateFunction"
    expected_export_info = "private"

    created_functions = analyzer.get_functions()

    assert \
        expected_method_id in created_functions and \
        created_functions[expected_method_id]["export_info"] == \
        expected_export_info and \
        created_functions[expected_method_id]["export_name"] == ""


def test_class_esprimaanalyze_begin_analyze_no_export_class(
        mock_project_files):
    file_location = "/project/src/no_export_class.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_class = "PrivateClass"
    expected_method_id = \
        f"(new {expected_class}()).someFunction"
    expected_export_info = "private"

    created_functions = analyzer.get_functions()

    assert \
        expected_method_id in created_functions and \
        created_functions[expected_method_id]["export_info"] == \
        expected_export_info and \
        created_functions[expected_method_id]["export_name"] == ""


def test_class_esprimaanalyze_begin_analyze_no_export_function(
        mock_project_files):
    file_location = "/project/src/no_export_function.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_method_id = "privateFunction"
    expected_export_info = "private"

    created_functions = analyzer.get_functions()

    assert \
        expected_method_id in created_functions and \
        created_functions[expected_method_id]["export_info"] == \
        expected_export_info and \
        created_functions[expected_method_id]["export_name"] == ""


def test_class_esprimaanalyze_begin_analyze_no_export_object_prop_fn(
        mock_project_files):
    file_location = "/project/src/no_export_object_property_function.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root=project_root)
    analyzer.begin_analyze()

    expected_method_id = "privateObject.objectPropertyFunction"
    expected_export_info = "private"

    created_functions = analyzer.get_functions()

    assert \
        expected_method_id in created_functions and \
        created_functions[expected_method_id]["export_info"] == \
        expected_export_info and \
        created_functions[expected_method_id]["export_name"] == ""


# TODO: CONTINUE TESTING MORE SPECIFIC CASES (AS ABOVE)


def test_analyze_files_arg_not_string():
    project_root = 1
    try:
        analyze_files(project_root)
        assert False
    except ValueError as e:
        assert str(e) == \
               "'project_root' must be a STRING"
    except Exception:
        assert False


def test_analyze_files_arg_empty_string():
    project_root = ""
    try:
        analyze_files(project_root)
        assert False
    except ValueError as e:
        assert str(e) == "'project_root' must be a path"
    except Exception:
        assert False
