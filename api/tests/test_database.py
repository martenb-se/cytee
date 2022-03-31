import pytest
from api.database import TestDatabase
from bson.objectid import ObjectId

@pytest.fixture
def mock_db(mocker, mongodb):
    db_mock = mocker.patch('api.database.MongoClient')
    db_mock().admin.command.return_value = 1
    db_mock().urangutest = mongodb
    t_db = TestDatabase("mongodb://address:00000")
    t_db.connect_to_db()
    yield t_db


def function_info_data(
        proj_path: str,
        file_name: str,
        function_name: str,
        function_hash: str,
        path_to_cache: str,
        cc: int,
        dependents: int,
        dependencies: int,
        number_of_tests: int,
        have_function_changed: bool):
    data = {
        "pathToProject": proj_path,
        "pathToFile": f"{proj_path}/{file_name}",
        "fileName": file_name,
        "functionName": function_name,
        "functionHash": function_hash,
        "pathToCache": path_to_cache,
        "cyclomaticComplexity": cc,
        "dependents": dependents,
        "dependencies": dependencies,
        "numberOfTests": number_of_tests,
        "haveFunctionChanged": have_function_changed
    }
    return data


def test_connect_to_db_standard():
    try:
        t_db = TestDatabase("mongodb://localhost:27017")
        t_db.connect_to_db()
        t_db.disconnect_from_db()
    except RuntimeError:
        pytest.fail("Could not connect to database.")


def test_connect_to_db_bad_arguments():
    with pytest.raises(TypeError):
        t_db = TestDatabase(3)

    with pytest.raises(ValueError):
        t_db = TestDatabase("")


def test_connect_to_db_multiple_times():
    with pytest.raises(RuntimeError):
        t_db = TestDatabase("mongodb://localhost:27017")
        t_db.connect_to_db()
        t_db.connect_to_db()


def test_disconnect_from_db_without_connection():
    with pytest.raises(RuntimeError):
        t_db = TestDatabase("mongodb://localhost:27017")
        t_db.disconnect_from_db()



