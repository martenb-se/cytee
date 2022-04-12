from api.analyzer.analyzer import analyze_files, AnalyzeJS


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
