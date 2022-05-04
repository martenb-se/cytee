import os
import esprima.nodes
import pytest
from api.tests.fixtures.mocking.open import mocker_open
from api.analyzer.analyzer import AnalyzeJS
from api.analyzer.process import analyze_files

MOCK_PROJECT_ROOT = "/project/src"
MOCK_FILES_AND_CONTENTS = [
    # (FAKED FILE,
    # REAL FILE IN "analyzer_test_data" FOLDER)

    # Syntax Testing
    (MOCK_PROJECT_ROOT + "/bad_code.js",
     "bad_code.js"),

    # Version Check
    (MOCK_PROJECT_ROOT + "/supported_object_spreading.js",
     "version_check/ecmascript-2018_object_spreading.js"),
    (MOCK_PROJECT_ROOT + "/unsupported_optional_catch_bind.js",
     "version_check/ecmascript-2019_optional_catch_bind.js"),
    (MOCK_PROJECT_ROOT + "/unsupported_private_class_variable.js",
     "version_check/ecmascript-2020_private_class_variable.js"),
    (MOCK_PROJECT_ROOT + "/unsupported_logical_assignment.js",
     "version_check/ecmascript-2021_logical_assignment.js"),
    (MOCK_PROJECT_ROOT + "/unsupported_private_slot_check.js",
     "version_check/ecmascript-2022_private_slot_check.js"),

    # Verify get_file_identity()
    (MOCK_PROJECT_ROOT + "/App.js",
     "test_surface/export_default.js"),
    (MOCK_PROJECT_ROOT + "/api/externalCall.js",
     "test_surface/export_default.js"),
    (MOCK_PROJECT_ROOT + "/components/ComponentName/index.js",
     "test_surface/export_default.js"),
    (MOCK_PROJECT_ROOT + "/components/ComponentName/ComponentName.js",
     "test_surface/export_default.js"),

    # Test Surfaces
    (MOCK_PROJECT_ROOT + "/no_export_multiple.js",
     "test_surface/no_export_multiple.js"),

    (MOCK_PROJECT_ROOT + "/export_default.js",
     "test_surface/export_default.js"),
    (MOCK_PROJECT_ROOT + "/export_default_class.js",
     "test_surface/export_default_class.js"),
    (MOCK_PROJECT_ROOT + "/export_default_function.js",
     "test_surface/export_default_function.js"),
    (MOCK_PROJECT_ROOT + "/export_default_object.js",
     "test_surface/export_default_object.js"),

    (MOCK_PROJECT_ROOT + "/export_named.js",
     "test_surface/export_named.js"),
    (MOCK_PROJECT_ROOT + "/export_named_same_name.js",
     "test_surface/export_named_same_name.js"),
    (MOCK_PROJECT_ROOT + "/export_named_declare_class.js",
     "test_surface/export_named_declare_class.js"),
    (MOCK_PROJECT_ROOT + "/export_named_declare_function.js",
     "test_surface/export_named_declare_function.js"),
    (
        MOCK_PROJECT_ROOT + "/export_named_declare_variable_const_arrow_function.js",
        "test_surface/export_named_declare_variable_const_arrow_function.js"),
    (
        MOCK_PROJECT_ROOT + "/export_named_declare_variable_let_arrow_function.js",
        "test_surface/export_named_declare_variable_let_arrow_function.js"),

    # Dependency
    (MOCK_PROJECT_ROOT + "/import_default.js",
     "dependency/import_default.js"),
    (MOCK_PROJECT_ROOT + "/import_named.js",
     "dependency/import_named.js"),
    (MOCK_PROJECT_ROOT + "/import_named_renamed.js",
     "dependency/import_named_renamed.js")

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
                enumerate(created_functions[created_function]['identity']):
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


# Validating AnalyzeJS construction requirements

def test_analyzejs_init_file_location_not_string():
    file_location = False
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except TypeError as e:
        assert str(e) == "'path_target_file' must be a STRING"
    except Exception:
        assert False


def test_analyzejs_init_file_location_empty():
    file_location = ""
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except ValueError as e:
        assert str(e) == "'path_target_file' cannot be empty"
    except Exception:
        assert False


def test_analyzejs_init_project_root_not_string():
    file_source = "/some/path/to/file.js"
    project_root = False
    try:
        AnalyzeJS(file_source, project_root)
        assert False
    except TypeError as e:
        assert str(e) == "'path_project_root' must be a STRING"
    except Exception:
        assert False


def test_analyzejs_init_project_root_empty():
    file_location = "/some/path/to/file.js"
    project_root = ""
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except ValueError as e:
        assert str(e) == "'path_project_root' cannot be empty"
    except Exception:
        assert False


def test_analyzejs_init_file_nonexistant():
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


# Validating AnalyzeJS dependency integrity
# Esprima reaction to bad code

def test_analyzejs_init_bad_code(mock_project_files):
    file_location = "/project/src/bad_code.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except SyntaxError as e:
        assert str(e) == \
               "Contents in file at '/project/src/bad_code.js' string could " \
               "not be parsed.\nInformation from esprima:\nLine 1: Missing " \
               "initializer in const declaration"
    except Exception:
        assert False


# Validating AnalyzeJS dependency version
# Esprima reaction to handling newer ECMAScript:
# Should have support for syntax from:
# - ES2018
# Should not have support for syntax from:
# - ES2019
# - ES2020
# - ES2021
# - ES2022

def test_analyzejs_init_es2018_supported(mock_project_files):
    file_location = "/project/src/unsupported_object_spreading.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert True
    except SyntaxError as e:
        assert False
    except Exception:
        assert False


def test_analyzejs_init_es2019_unsupported(mock_project_files):
    file_location = "/project/src/unsupported_optional_catch_bind.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except SyntaxError as e:
        assert str(e) == \
               "Contents in file at " \
               "'/project/src/unsupported_optional_catch_bind.js' string " \
               "could not be parsed.\nInformation from esprima:\nLine 4: " \
               "Unexpected token {"
    except Exception:
        assert False


def test_analyzejs_init_es2020_unsupported(mock_project_files):
    file_location = "/project/src/unsupported_private_class_variable.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except SyntaxError as e:
        assert str(e) == \
               "Contents in file at " \
               "'/project/src/unsupported_private_class_variable.js' string " \
               "could not be parsed.\nInformation from esprima:\nLine 3: " \
               "Unexpected token ILLEGAL"
    except Exception:
        assert False


def test_analyzejs_init_es2021_unsupported(mock_project_files):
    file_location = "/project/src/unsupported_logical_assignment.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except SyntaxError as e:
        assert str(e) == \
               "Contents in file at " \
               "'/project/src/unsupported_logical_assignment.js' string " \
               "could not be parsed.\nInformation from esprima:\nLine 4: " \
               "Unexpected token ="
    except Exception:
        assert False


def test_analyzejs_init_es2022_unsupported(mock_project_files):
    file_location = "/project/src/unsupported_private_slot_check.js"
    project_root = MOCK_PROJECT_ROOT
    try:
        AnalyzeJS(file_location, project_root)
        assert False
    except SyntaxError as e:
        assert str(e) == \
               "Contents in file at " \
               "'/project/src/unsupported_private_slot_check.js' string " \
               "could not be parsed.\nInformation from esprima:\nLine 11: " \
               "Unexpected token ILLEGAL"
    except Exception:
        assert False


# Validating AnalyzeJS get_file_identity

def test_analyzejs_get_file_identity_in_root(mock_project_files):
    path_target_file = MOCK_PROJECT_ROOT + "/App.js"
    path_project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(path_target_file, path_project_root)

    expected_file_identity = "App"
    result_file_identity = analyzer.get_file_identity()

    assert result_file_identity == expected_file_identity


def test_analyzejs_get_file_identity_in_api_dir(mock_project_files):
    path_target_file = MOCK_PROJECT_ROOT + "/api/externalCall.js"
    path_project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(path_target_file, path_project_root)

    expected_file_identity = "api/externalCall"
    result_file_identity = analyzer.get_file_identity()

    assert result_file_identity == expected_file_identity


def test_analyzejs_get_file_identity_component_index(mock_project_files):
    path_target_file = MOCK_PROJECT_ROOT + "/components/ComponentName/index.js"
    path_project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(path_target_file, path_project_root)

    expected_file_identity = "components/ComponentName/index"
    result_file_identity = analyzer.get_file_identity()

    assert result_file_identity == expected_file_identity


def test_analyzejs_get_file_identity_component(mock_project_files):
    path_target_file = \
        MOCK_PROJECT_ROOT + "/components/ComponentName/ComponentName.js"
    path_project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(path_target_file, path_project_root)

    expected_file_identity = "components/ComponentName/ComponentName"
    result_file_identity = analyzer.get_file_identity()

    assert result_file_identity == expected_file_identity


# Validating AnalyzeJS Post Process get_test_surfaces

def test_ajspp_get_test_surfaces_no_exports(mock_project_files):
    file_location = "/project/src/no_export_multiple.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_number_found_test_surfaces = 0

    result_test_surfaces = analyzer.get_test_surfaces()

    assert \
        expected_number_found_test_surfaces == len(result_test_surfaces)


def test_ajspp_get_test_surfaces_export_default(mock_project_files):
    file_location = "/project/src/export_default.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_test_surface = {
        'pathToProject': '/project/src',
        'fileId': 'export_default',
        'arguments':
            [['exportedFunction',
              [{'type': 'Identifier', 'name': 'argA', 'range': [26, 30]},
               {'type': 'Identifier', 'name': 'argB', 'range': [32, 36]}]]],
        'functionRange': (25, 97),
        'functionHash':
            '873365059effe0f88849bebd7399b854331de9d82823667d556012710a94a6e2',
        'exportInfo': 'export default',
        'exportName': 'exportedFunction',
        'functionId': 'exportedFunction'}

    result_test_surfaces = analyzer.get_test_surfaces()

    assert len(result_test_surfaces) == 1 and \
           result_test_surfaces[0] == expected_found_test_surface


def test_ajspp_get_test_surfaces_export_default_class(mock_project_files):
    file_location = "/project/src/export_default_class.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_test_surface = {
        'pathToProject': '/project/src',
        'fileId': 'export_default_class',
        'arguments':
            [['someOtherFunction',
              [{'type': 'Identifier',
                'name': 'someOtherArgument',
                'range': [59, 76]}]]],
        'functionRange': (58, 117),
        'functionHash':
            '75ebbf1cba3c4ee813b5f6d146a3882db3bc6fa1525f088572cd63691cf14533',
        'exportInfo': 'export default',
        'exportName': 'ExportedClass',
        'functionId': '(new ExportedClass()).someOtherFunction'}

    result_test_surfaces = analyzer.get_test_surfaces()

    assert len(result_test_surfaces) == 1 and \
           result_test_surfaces[0] == expected_found_test_surface


def test_ajspp_get_test_surfaces_export_default_function(mock_project_files):
    file_location = "/project/src/export_default_function.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_test_surface = {
        'arguments':
            [['exportedFunction',
              [{'name': 'arg', 'range': [41, 44],
                'type': 'Identifier'},
               {'name': 'argB', 'range': [46, 50],
                'type': 'Identifier'}]]],
        'exportInfo': 'export default',
        'exportName': 'exportedFunction',
        'fileId': 'export_default_function',
        'functionHash':
            'e8d5c198b2e1c5f69507b14326bf8db0e06cae460fb6b217bb15e8abdde0f654',
        'functionId': 'exportedFunction',
        'functionRange': (15, 108),
        'pathToProject': '/project/src'}

    result_test_surfaces = analyzer.get_test_surfaces()

    assert len(result_test_surfaces) == 1 and \
           result_test_surfaces[0] == expected_found_test_surface


def test_ajspp_get_test_surfaces_export_default_object(mock_project_files):
    file_location = "/project/src/export_default_object.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_test_surface = {
        'arguments':
            [['exportedFunction',
              [{'name': 'argA', 'range': [38, 42],
                'type': 'Identifier'},
               {'name': 'argB', 'range': [44, 48],
                'type': 'Identifier'}]]],
        'exportInfo': 'export default',
        'exportName': 'exportedFunction',
        'fileId': 'export_default_object',
        'functionHash':
            'd4c3d6638fec1466f012f3eebb2021069219c38fb1aabade19ab741a412499a4',
        'functionId': 'exportedFunction',
        'functionRange': (37, 107),
        'pathToProject': '/project/src'}

    result_test_surfaces = analyzer.get_test_surfaces()

    assert len(result_test_surfaces) == 1 and \
           result_test_surfaces[0] == expected_found_test_surface


def test_ajspp_get_test_surfaces_export_named(mock_project_files):
    file_location = "/project/src/export_named.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_test_surface = {
        'arguments':
            [['exportedOriginalFunction',
              [{'name': 'argA', 'range': [34, 38], 'type': 'Identifier'},
               {'name': 'argB', 'range': [40, 44], 'type': 'Identifier'}]]],
        'exportInfo': 'export',
        'exportName': 'exportedRenamedFunction',
        'fileId': 'export_named',
        'functionHash':
            '11126c06a034248393b86ade508ae990ff35ef5ff8d4a57e293568b44c399fd4',
        'functionId': 'exportedOriginalFunction',
        'functionRange': (33, 97),
        'pathToProject': '/project/src'}

    result_test_surfaces = analyzer.get_test_surfaces()

    assert len(result_test_surfaces) == 1 and \
           result_test_surfaces[0] == expected_found_test_surface


def test_ajspp_get_test_surfaces_export_named_same_name(mock_project_files):
    file_location = "/project/src/export_named_same_name.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_test_surface = {
        'arguments':
            [['exportedFunction',
              [{'name': 'argA', 'range': [26, 30], 'type': 'Identifier'},
               {'name': 'argB', 'range': [32, 36], 'type': 'Identifier'}]]],
        'exportInfo': 'export',
        'exportName': 'exportedFunction',
        'fileId': 'export_named_same_name',
        'functionHash':
            '11126c06a034248393b86ade508ae990ff35ef5ff8d4a57e293568b44c399fd4',
        'functionId': 'exportedFunction',
        'functionRange': (25, 89),
        'pathToProject': '/project/src'}

    result_test_surfaces = analyzer.get_test_surfaces()

    assert len(result_test_surfaces) == 1 and \
           result_test_surfaces[0] == expected_found_test_surface


def test_ajspp_get_test_surfaces_named_declare_class(mock_project_files):
    file_location = \
        "/project/src/export_named_declare_class.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_test_surface = {
        'arguments':
            [['someOtherFunction',
              [{'name': 'someOtherArgument',
                'range': [51, 68],
                'type': 'Identifier'}]]],
        'exportInfo': 'export',
        'exportName': 'ExportedClass',
        'fileId': 'export_named_declare_class',
        'functionHash':
            '75ebbf1cba3c4ee813b5f6d146a3882db3bc6fa1525f088572cd63691cf14533',
        'functionId': '(new ExportedClass()).someOtherFunction',
        'functionRange': (50, 109),
        'pathToProject': '/project/src'}

    result_test_surfaces = analyzer.get_test_surfaces()

    assert len(result_test_surfaces) == 1 and \
           result_test_surfaces[0] == expected_found_test_surface


def test_ajspp_get_test_surfaces_named_declare_function(mock_project_files):
    file_location = \
        "/project/src/export_named_declare_function.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_test_surface = {
        'arguments':
            [['exportedFunction',
              [{'name': 'argA', 'range': [33, 37], 'type': 'Identifier'},
               {'name': 'argB', 'range': [39, 43], 'type': 'Identifier'}]]],
        'exportInfo': 'export',
        'exportName': 'exportedFunction',
        'fileId': 'export_named_declare_function',
        'functionHash':
            '342aac762a60d694d49a1dd0895a15de20c78c48f44b2e8eb75339d4b66542d3',
        'functionId': 'exportedFunction',
        'functionRange': (7, 93),
        'pathToProject': '/project/src'}

    result_test_surfaces = analyzer.get_test_surfaces()

    assert len(result_test_surfaces) == 1 and \
           result_test_surfaces[0] == expected_found_test_surface


def test_ajspp_get_test_surfaces_named_const_arrow_fn(mock_project_files):
    file_location = \
        "/project/src/export_named_declare_variable_const_arrow_function.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_test_surface = {
        'arguments':
            [['exportedFunction',
              [{'name': 'argA', 'range': [33, 37], 'type': 'Identifier'},
               {'name': 'argB', 'range': [39, 43], 'type': 'Identifier'}]]],
        'exportInfo': 'export',
        'exportName': 'exportedFunction',
        'fileId': 'export_named_declare_variable_const_arrow_function',
        'functionHash':
            'aa0ee4e215fc5a0f2095a6f48acc7f8e57acc7eb6d2b93933aaeaac85cf8393c',
        'functionId': 'exportedFunction',
        'functionRange': (32, 96),
        'pathToProject': '/project/src'}

    result_test_surfaces = analyzer.get_test_surfaces()

    assert len(result_test_surfaces) == 1 and \
           result_test_surfaces[0] == expected_found_test_surface


def test_ajspp_get_test_surfaces_named_let_variable_arrow_function(
        mock_project_files):
    file_location = \
        "/project/src/export_named_declare_variable_let_arrow_function.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_test_surface = {
        'arguments':
            [['exportedFunction',
              [{'name': 'argA', 'range': [31, 35], 'type': 'Identifier'},
               {'name': 'argB', 'range': [37, 41], 'type': 'Identifier'}]]],
        'exportInfo': 'export',
        'exportName': 'exportedFunction',
        'fileId': 'export_named_declare_variable_let_arrow_function',
        'functionHash':
            'aa0ee4e215fc5a0f2095a6f48acc7f8e57acc7eb6d2b93933aaeaac85cf8393c',
        'functionId': 'exportedFunction',
        'functionRange': (30, 94),
        'pathToProject': '/project/src'}

    result_test_surfaces = analyzer.get_test_surfaces()

    assert len(result_test_surfaces) == 1 and \
           result_test_surfaces[0] == expected_found_test_surface


# Validating AnalyzeJS Post Process get_test_surfaces

def test_ajspp_get_dependency_usages_import_default(mock_project_files):
    file_location = "/project/src/import_default.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_dependency = {
        'calledFileId': 'shared/importedDefault',
        'calledFunctionId': 'importedDefault.importedFunctionDependency',
        'fileId': 'import_default',
        'functionId': '!OUTSIDE_TEST_SURFACE',
        'pathToProject': '/project/src'}

    result_dependencies = analyzer.get_dependency_usages()

    assert len(result_dependencies) == 1 and \
           result_dependencies[0] == expected_found_dependency


def test_analyzejs_begin_analyze_dependency_import_named(mock_project_files):
    file_location = "/project/src/import_named.js"
    project_root = MOCK_PROJECT_ROOT
    analyzer = AnalyzeJS(file_location, project_root)
    analyzer.begin_analyze()

    expected_found_dependency = {
        'calledFileId': 'shared/importedNamed',
        'calledFunctionId': 'importedNamedFunctionDepency',
        'fileId': 'import_named',
        'functionId': '!OUTSIDE_TEST_SURFACE',
        'pathToProject': '/project/src'}

    result_dependencies = analyzer.get_dependency_usages()

    assert len(result_dependencies) == 1 and \
           result_dependencies[0] == expected_found_dependency


# Validating analyze_files

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
