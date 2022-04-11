import pytest
# from api.database import DatabaseHandler
from api.database import *
from bson.objectid import ObjectId
from pprint import pprint


@pytest.fixture
def mock_db(mocker, mongodb):
    db_mock = mocker.patch('api.database.MongoClient')
    db_mock().admin.command.return_value = 1
    db_mock().urangutest = mongodb
    t_db = DatabaseHandler("mongodb://address:00000")
    t_db.connect_to_db()
    yield t_db
    try:
        t_db.disconnect_from_db()
    except RuntimeError:
        return


def __function_info_data(
        proj_path: str = "/path/to/project/proj1",
        path_to_file: str = "/path/to/project/proj1/src/utl",
        file_name: str = "file.js",
        function_name: str = "function1",
        function_hash: str = "123jh213j1l23hj23hk1j23",
        dependents: int = 6,
        dependencies: int = 4,
        number_of_tests: int = 7,
        have_function_changed: bool = False):
    data = {
        "pathToProject": proj_path,
        "pathToFile": path_to_file,
        "fileName": file_name,
        "functionName": function_name,
        "functionHash": function_hash,
        "pathToCache": f"/cache{path_to_file}",
        "dependents": dependents,
        "dependencies": dependencies,
        "numberOfTests": number_of_tests,
        "haveFunctionChanged": have_function_changed
    }
    return data


def __test_info_data(
        proj_path: str = "/path/to/project/proj1",
        full_path: str = "/path/to/project/proj1/external/util.js",
        function_name: str = "function1",
        custom_name: str = ""):
    data = {
        "pathToProject": proj_path,
        "fullPath": full_path,
        "functionName": function_name,
        "customName": custom_name,
        "moduleData": {
            "argumentList": [
                {
                    "argument": "arg1",
                    "type": "undefined"
                },
                {
                    "argument": "arg2",
                    "type": "string",
                    "value": "wawawewa"
                }
            ],
            "returnValue": {
                "type": "string",
                "value": "asdasd"
            }
        }
    }
    return data


def __function_coupling_data(
        function: str =
        "/path/to/project/proj1/external/util.js-deleteAllFiles",
        dependent_functions: list = None):
    if dependent_functions is None:
        dependent_functions = [
            "/path/to/project/proj1/internal/util.js-deleteNoFiles",
            "/path/to/project/proj1/internal/util.js-deleteSomeFiles",
            "/path/to/project/proj1/internal/util.js-deleteThreeFiles"]
    data = {
        "function": function,
        "dependentFunctions": dependent_functions
    }
    return data


def __compare_objects(
        resulting_item: dict, expected_item: dict,
        *, white_list: list = None, black_list: list = None
):
    if white_list:
        for attribute in white_list:
            assert resulting_item[attribute] == expected_item[attribute]
    else:
        for attribute, attribute_value in resulting_item.items():
            if black_list and attribute in black_list:
                continue
            assert attribute_value == expected_item[attribute]


def test_check_valid_document_attribute_valid_arguments():
    try:
        check_valid_document_attribute(
            '_id',
            '0123456789ab0123456789ab',
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )
    except Exception:
        pytest.fail()


def test_check_valid_document_attribute_non_existent_attribute():
    with pytest.raises(ValueError):
        check_valid_document_attribute(
            'not_a_real_attribute',
            '0123456789ab0123456789ab',
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_check_valid_document_attribute_wrong_attribute_value_type():
    with pytest.raises(TypeError):
        check_valid_document_attribute(
            '_id',
            123,
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_check_valid_document_attribute_attribute_value_ignores_cond_id():
    with pytest.raises(ValueError):
        check_valid_document_attribute(
            '_id',
            "123123123",
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_check_valid_document_attribute_attribute_value_ignores_cond_string():
    with pytest.raises(ValueError):
        check_valid_document_attribute(
            'pathToProject',
            "",
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_check_valid_document_attribute_attribute_value_ignores_cond_number():
    with pytest.raises(ValueError):
        check_valid_document_attribute(
            'dependents',
            -1,
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_check_valid_document_valid_arguments():
    func_inf = __function_info_data()
    try:
        check_valid_document(
            func_inf,
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )
    except Exception:
        pytest.fail()


def test_check_valid_document_non_existing_attribute():
    func_inf = __function_info_data()
    func_inf['not_a_valid_argument'] = "bob"
    with pytest.raises(ValueError):
        check_valid_document(
            func_inf,
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_check_valid_document_wrong_attribute_type():
    func_inf = __function_info_data()
    func_inf['_id'] = 123
    with pytest.raises(TypeError):
        check_valid_document(
            func_inf,
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_check_valid_document_attribute_value_ignores_cond():
    func_inf = __function_info_data()
    func_inf['_id'] = '123123'
    with pytest.raises(ValueError):
        check_valid_document(
            func_inf,
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_check_valid_attribute_filter_valid_arguments():
    try:
        check_valid_attribute_filter(
            '_id',
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )
    except Exception:
        pytest.fail()


def test_check_valid_argument_filter_wrong_attribute_type():
    with pytest.raises(TypeError):
        check_valid_attribute_filter(
            123,
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_check_valid_argument_filter_invalid_attribute_value():
    with pytest.raises(ValueError):
        check_valid_attribute_filter(
            '',
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_check_valid_argument_filer_non_existent_attribute():
    with pytest.raises(ValueError):
        check_valid_attribute_filter(
            'not_real_attribute',
            FUNCTION_INFO_ATTRIBUTE_CHECKER
        )


def test_connect_to_db_standard(mocker):
    db_mock = mocker.patch('api.database.MongoClient')
    db_mock().admin.command.return_value = 1
    db_mock().urangutest = "Super_real_database"
    db_mock().close.return_value = 1
    try:
        t_db = DatabaseHandler("mongodb://localhost:27017")
        t_db.connect_to_db()
        t_db.disconnect_from_db()
    except RuntimeError:
        pytest.fail("Could not connect to database.")


def test_connect_to_db_bad_arguments():
    with pytest.raises(TypeError):
        DatabaseHandler(3)

    with pytest.raises(ValueError):
        DatabaseHandler("")


def test_connect_to_db_multiple_times(mocker):
    db_mock = mocker.patch('api.database.MongoClient')
    db_mock().admin.command.return_value = 1
    db_mock().urangutest = "Super_real_database"
    db_mock().close.return_value = 1
    with pytest.raises(RuntimeError):
        t_db = DatabaseHandler("mongodb://localhost:27017")
        t_db.connect_to_db()
        t_db.connect_to_db()


def test_disconnect_from_db_without_connection():
    with pytest.raises(RuntimeError):
        t_db = DatabaseHandler("mongodb://localhost:27017")
        t_db.disconnect_from_db()


def test__get_query_by_id(mock_db):
    t_db = mock_db

    document = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value='0123456789ab0123456789ab',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='_id'
    )

    assert len(document) == 1
    assert document[0]['_id'] == '0123456789ab0123456789ab'


def test__get_query_by_bad_attribute(mock_db):
    t_db = mock_db
    documents = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value='/path/to/project/proj1',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='pathToProject'
    )
    assert len(documents) == 3
    for doc in documents:
        assert doc['pathToProject'] == '/path/to/project/proj1'


def test__get_query_by_bool(mock_db):
    t_db = mock_db
    documents = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value=True,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='haveFunctionChanged'
    )
    assert len(documents) == 2
    for doc in documents:
        assert doc['haveFunctionChanged'] is True


def test__get_query_act_on_first_match(mock_db):
    t_db = mock_db
    documents = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value='/path/to/project/proj1',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='pathToProject',
        act_on_first_match=True
    )
    assert len(documents) == 1
    assert documents[0]['pathToProject'] == '/path/to/project/proj1'


def test__get_query_non_existent_doc(mock_db):
    t_db = mock_db
    documents = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value='0123456789ab0123456789af',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='_id'
    )
    assert documents is None


def test__get_query_custom_query_function(mock_db):
    t_db = mock_db

    def custom_query(db_attribute_value):
        return t_db.database['test_info'].find_one({
            '_id': db_attribute_value
        })

    documents = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value='0123456789ab0123456789ab',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='_id',
        query_function=custom_query
    )
    assert str(documents['_id']) == '0123456789ab0123456789ab'


def test__add_query_valid_arguments(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()
    func_inf_id = t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )
    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value=func_inf_id,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='_id'
    )[0]
    func_inf['_id'] = func_inf_id
    __compare_objects(func_inf, returned_func_inf)


def test__add_query_custom_query_function(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()

    def custom_query(db_document):
        db_document['secret'] = 'secret_value'
        db_result = t_db.database['function_info'].insert_one(db_document)
        return str(db_result.inserted_id)

    func_inf_id = t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
        query_function=custom_query
    )

    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value=func_inf_id,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='_id'
    )[0]

    func_inf['_id'] = func_inf_id
    __compare_objects(
        func_inf,
        returned_func_inf,
        black_list=['secret']
    )
    assert returned_func_inf['secret'] == 'secret_value'


def test__query_set_one_filter_attribute_in_updated_doc(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()

    func_inf_id = t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )

    updated_fun_inf = func_inf.copy()
    updated_fun_inf['_id'] = func_inf_id
    updated_fun_inf['pathToProject'] = '/path/is/changed'
    updated_fun_inf['fileName'] = 'newFile.js'
    updated_fun_inf['functionName'] = 'doNotDeleteAllFiles'
    updated_fun_inf['dependencies'] = 3
    updated_fun_inf['haveFunctionChanged'] = True

    t_db._DatabaseHandler__query_set_one(
        collection='function_info',
        updated_document_data=updated_fun_inf,
        filter_attribute='_id',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES
    )

    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value=func_inf_id,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='_id'
    )[0]

    __compare_objects(
        returned_func_inf,
        updated_fun_inf,
    )


def test__query_set_one_filter_attribute_not_in_updated_doc(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()

    func_inf_id = t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )

    updated_fun_inf = func_inf.copy()
    updated_fun_inf['pathToProject'] = '/path/is/changed'
    updated_fun_inf['fileName'] = 'newFile.js'
    updated_fun_inf['functionName'] = 'doNotDeleteAllFiles'
    updated_fun_inf['dependencies'] = 3
    updated_fun_inf['haveFunctionChanged'] = True

    t_db._DatabaseHandler__query_set_one(
        collection='function_info',
        updated_document_data=updated_fun_inf,
        filter_attribute='_id',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
        filter_attribute_value=func_inf_id,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,

    )

    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value=func_inf_id,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='_id'
    )[0]

    __compare_objects(
        returned_func_inf,
        updated_fun_inf,
        black_list=['_id']
    )


def test__query_set_one_custom_query(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()

    func_inf_id = t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )

    updated_fun_inf = func_inf.copy()
    updated_fun_inf['pathToProject'] = '/path/is/changed'
    updated_fun_inf['fileName'] = 'newFile.js'
    updated_fun_inf['functionName'] = 'doNotDeleteAllFiles'
    updated_fun_inf['dependencies'] = 3
    updated_fun_inf['haveFunctionChanged'] = True

    def custom_query(db_document, filter_attribute, db_document_filter):
        db_document['secret'] = 'secret_value'
        t_db.database['function_info'].update_one(
            {filter_attribute: db_document_filter},
            {'$set': db_document})

    t_db._DatabaseHandler__query_set_one(
        collection='function_info',
        updated_document_data=updated_fun_inf,
        filter_attribute='_id',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
        filter_attribute_value=func_inf_id,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        query_function=custom_query
    )

    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value=func_inf_id,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='_id'
    )[0]

    __compare_objects(
        returned_func_inf,
        updated_fun_inf,
        black_list=['_id', 'secret']
    )

    assert returned_func_inf['secret'] == 'secret_value'


def test__query_remove_one_by_id(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()
    func_inf_id = t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )
    t_db._DatabaseHandler__query_remove_one(
        collection='function_info',
        filter_attribute='_id',
        filter_attribute_value=func_inf_id,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        act_on_first_match=True
    )
    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value=func_inf_id,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='_id'
    )
    assert returned_func_inf is None


def test__query_remove_one_act_on_first_match_by_project(mock_db):
    t_db = mock_db
    func_inf = __function_info_data(
        proj_path='/secret/proj/path'
    )
    t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )
    t_db._DatabaseHandler__query_remove_one(
        collection='function_info',
        filter_attribute='pathToProject',
        filter_attribute_value='/secret/proj/path',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        act_on_first_match=True
    )
    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value='/secret/proj/path',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='pathToProject'
    )
    assert returned_func_inf is None


def test__query_remove_remove_all_documents_related_to_project(mock_db):
    t_db = mock_db
    func_inf1 = __function_info_data(
        proj_path='/secret/proj/path',
        file_name='file1.js'
    )
    func_inf2 = __function_info_data(
        proj_path='/secret/proj/path',
        file_name='file2.js'
    )
    func_inf3 = __function_info_data(
        proj_path='/secret/proj/path',
        file_name='file3.js'
    )
    t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf1,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )
    t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf2,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )
    t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf3,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )
    t_db._DatabaseHandler__query_remove_one(
        collection='function_info',
        filter_attribute='pathToProject',
        filter_attribute_value='/secret/proj/path',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        act_on_first_match=False
    )
    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value='/secret/proj/path',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='pathToProject'
    )
    assert returned_func_inf is None


def test__query_remove_custom_query(mock_db):
    t_db = mock_db
    func_inf1 = __function_info_data(
        proj_path='/secret/proj/path1'
    )
    func_inf2 = __function_info_data(
        proj_path='/secret/proj/path2'
    )

    t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf1,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )
    t_db._DatabaseHandler__query_add_one(
        collection='function_info',
        document=func_inf2,
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        app_to_db_conv=t_db._DatabaseHandler__function_info_app_to_db_conv,
    )

    def custom_query(filter_attribute, db_attribute_filter):
        t_db.database['function_info'].delete_one({
            'pathToProject': '|secret|proj|path2'})

    t_db._DatabaseHandler__query_remove_one(
        collection='function_info',
        filter_attribute='pathToProject',
        filter_attribute_value='/secret/proj/path1',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        act_on_first_match=True,
        query_function=custom_query
    )
    returned_func_inf_1 = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value='/secret/proj/path1',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='pathToProject'
    )
    returned_func_inf_2 = t_db._DatabaseHandler__get_query(
        collection='function_info',
        attribute_value='/secret/proj/path2',
        attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
        db_to_app_conv=t_db._DatabaseHandler__function_info_db_to_app_conv,
        document_attribute='pathToProject'
    )

    assert returned_func_inf_1 is not None
    assert returned_func_inf_2 is None


def test_get_function_info_by_id(mock_db):
    t_db = mock_db
    expected_func_inf = __function_info_data(
        proj_path='/path/to/project/proj1',
        path_to_file='/path/to/project/proj1/util.js',
        file_name='util.js',
        function_name='deleteAllFiles',
        function_hash="sdg7sdfg98fsd7g98dfs7df",
        dependents=24,
        dependencies=10,
        number_of_tests=90,
        have_function_changed=True
    )
    expected_func_inf['_id'] = "0123456789ab0123456789ab"
    received_func_inf = t_db.get_function_info("0123456789ab0123456789ab")[0]
    __compare_objects(expected_func_inf, received_func_inf)


def test_get_function_info_by_project(mock_db):
    t_db = mock_db
    documents = t_db.get_function_info(
        attribute_value="/path/to/project/proj1",
        document_attribute="pathToProject"
    )
    assert len(documents) == 3
    for doc in documents:
        assert doc['pathToProject'] == "/path/to/project/proj1"


def test_get_function_info_by_have_function_changed(mock_db):
    t_db = mock_db
    documents = t_db.get_function_info(
        attribute_value=True,
        document_attribute="haveFunctionChanged"
    )
    assert len(documents) == 2
    for doc in documents:
        assert doc['haveFunctionChanged']


def test_get_test_info_by_id(mock_db):
    t_db = mock_db
    expected_test_info = __test_info_data()
    expected_test_info['_id'] = "0123456789ab0123456789ab"
    received_test_info = t_db.get_test_info("0123456789ab0123456789ab")[0]
    __compare_objects(received_test_info, expected_test_info)


def test_get_test_info_by_project(mock_db):
    t_db = mock_db
    documents = t_db.get_test_info(
        attribute_value="/path/to/project/proj1",
        document_attribute="pathToProject"
    )
    assert len(documents) == 3
    for doc in documents:
        assert doc['pathToProject'] == "/path/to/project/proj1"


def test_get_test_info_by_function_name(mock_db):
    t_db = mock_db
    documents = t_db.get_test_info(
        attribute_value="deleteAllFiles",
        document_attribute="functionName"
    )
    assert len(documents) == 2
    for doc in documents:
        assert doc['functionName'] == "deleteAllFiles"


def test_get_function_coupling_by_id(mock_db):
    t_db = mock_db
    document = t_db.get_function_coupling("0123456789ab0123456789ab")
    assert len(document) == 1
    assert document[0]['_id'] == "0123456789ab0123456789ab"


def test_get_function_coupling_by_function(mock_db):
    t_db = mock_db
    document = t_db.get_function_coupling(
        attribute_value="""/path/to/project/proj1/external/util.js-deleteAllFiles""",
        document_attribute="function"
    )
    assert len(document) == 1
    assert document[0]['function'] == """/path/to/project/proj1/external/util.js-deleteAllFiles"""


def test_get_function_coupling_by_dependent_function(mock_db):
    t_db = mock_db
    document = t_db.get_function_coupling(
        attribute_value=["""/path/to/project/proj1|internal/bib.js-function1"""],
        document_attribute="dependentFunctions"
    )
    for doc in document:
        assert doc in ["/path/to/project/proj1/external/tools.js-toolest",
                       "/path/to/project/proj1/external/main.js-toolest"]


def test_add_function_info(mock_db):
    t_db = mock_db
    expected_func_inf = __function_info_data()
    func_inf_id = t_db.add_function_info(expected_func_inf)
    expected_func_inf['_id'] = func_inf_id
    received_func_inf = t_db.get_function_info(func_inf_id)[0]
    __compare_objects(received_func_inf, expected_func_inf)


def test_add_test_info(mock_db):
    t_db = mock_db
    expected_test_inf = __test_info_data()
    test_inf_id = t_db.add_test_info(expected_test_inf)
    expected_test_inf['_id'] = test_inf_id
    received_test_inf = t_db.get_test_info(test_inf_id)[0]
    __compare_objects(received_test_inf, expected_test_inf)


def test_add_function_coupling(mock_db):
    t_db = mock_db
    expected_func_coup = __function_coupling_data()
    func_coup_id = t_db.add_function_coupling(expected_func_coup)
    expected_func_coup['_id'] = func_coup_id
    received_func_coup = t_db.get_function_coupling(func_coup_id)[0]
    __compare_objects(received_func_coup, expected_func_coup)


def test_set_function_info(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()
    func_inf_id = t_db.add_function_info(func_inf)
    expected_func_inf = func_inf.copy()
    expected_func_inf['_id'] = func_inf_id
    expected_func_inf['pathToProject'] = "/path/to/project/proj37"
    expected_func_inf['fileName'] = "superUtil.js"
    expected_func_inf['dependents'] = 36
    expected_func_inf['numberOfTests'] = 700
    expected_func_inf['haveFunctionChanged'] = True
    t_db.set_function_info(update_function_info=expected_func_inf)
    received_func_inf = t_db.get_function_info(func_inf_id)[0]
    __compare_objects(received_func_inf, expected_func_inf)


def test_set_test_info(mock_db):
    t_db = mock_db
    test_inf = __test_info_data()
    test_inf_id = t_db.add_test_info(test_inf)
    expected_test_inf = test_inf.copy()
    expected_test_inf['_id'] = test_inf_id
    expected_test_inf['pathToProject'] = "/path/to/project/proj1"
    expected_test_inf['customName'] = "superDuperTest"
    t_db.set_test_info(expected_test_inf)
    received_test_inf = t_db.get_test_info(test_inf_id)[0]
    __compare_objects(received_test_inf, expected_test_inf)


def test_set_function_coupling(mock_db):
    t_db = mock_db
    func_coup = __function_coupling_data()
    func_coup_id = t_db.add_function_coupling(func_coup)
    expected_func_coup = func_coup.copy()
    expected_func_coup['_id'] = func_coup_id
    expected_func_coup['dependentFunctions']\
        .append("/path/to/project/proj1/internal/util.js-addEvenMoreFiles")
    t_db.set_function_coupling(expected_func_coup)
    received_func_coup = t_db.get_function_coupling(func_coup_id)[0]
    __compare_objects(received_func_coup, expected_func_coup)


def test_delete_function_info_by_id(mock_db):
    t_db = mock_db
    func_info = __function_info_data()
    func_coup_id = t_db.add_function_info(func_info)
    t_db.delete_function_info(func_coup_id)
    received_func_inf = t_db.get_function_info(func_coup_id)
    assert received_func_inf is None


def test_delete_function_info_by_project(mock_db):
    t_db = mock_db
    func_inf = __function_info_data(
        proj_path="/path/to/project/projSecret"
    )
    t_db.add_function_info(func_inf)
    t_db.add_function_info(func_inf)
    t_db.add_function_info(func_inf)
    t_db.delete_function_info(
        filter_attribute_value="/path/to/project/projSecret",
        filter_attribute="pathToProject",
        act_on_first_match=False
    )
    received_func_inf = t_db.get_function_info(
        document_attribute="pathToProject",
        attribute_value="/path/to/project/projSecret"
    )
    assert received_func_inf is None


def test_delete_function_info_by_file(mock_db):
    t_db = mock_db
    func_inf = __function_info_data(
        file_name="superSecretFile.js"
    )
    t_db.add_function_info(func_inf)
    t_db.add_function_info(func_inf)
    t_db.add_function_info(func_inf)
    t_db.delete_function_info(
        filter_attribute_value="superSecretFile.js",
        filter_attribute="fileName",
        act_on_first_match=False
    )
    received_func_inf = t_db.get_function_info(
        document_attribute="fileName",
        attribute_value="superSecretFile.js"
    )
    assert received_func_inf is None


def test_delete_function_info_by_function_name(mock_db):
    t_db = mock_db
    func_inf = __function_info_data(
        function_name="neverDeleteAnyFiles"
    )
    t_db.add_function_info(func_inf)
    t_db.delete_function_info(
        filter_attribute_value="neverDeleteAnyFiles",
        filter_attribute="functionName",
        act_on_first_match=False
    )
    received_func_inf = t_db.get_function_info(
        document_attribute="functionName",
        attribute_value="neverDeleteAnyFiles"
    )
    assert received_func_inf is None


def test_delete_test_info_by_id(mock_db):
    t_db = mock_db
    test_inf = __test_info_data()
    test_inf_id = t_db.add_test_info(test_inf)
    t_db.delete_test_info(test_inf_id)
    received_test_inf = t_db.get_test_info(test_inf_id)
    assert received_test_inf is None


def test_delete_test_info_by_project(mock_db):
    t_db = mock_db
    test_inf = __test_info_data(
        proj_path="/path/to/project/projSecret"
    )
    t_db.add_test_info(test_inf)
    t_db.add_test_info(test_inf)
    t_db.add_test_info(test_inf)
    t_db.delete_test_info(
        filter_attribute_value="/path/to/project/projSecret",
        filter_attribute="pathToProject",
        act_on_first_match=False
    )
    received_test_inf = t_db.get_test_info(
        document_attribute="pathToProject",
        attribute_value="/path/to/project/projSecret"
    )
    assert received_test_inf is None


def test_delete_test_info_by_function(mock_db):
    t_db = mock_db
    test_inf = __test_info_data(
        function_name="neverDeleteAnyFiles"
    )
    t_db.add_test_info(test_inf)
    t_db.add_test_info(test_inf)
    t_db.add_test_info(test_inf)
    t_db.delete_test_info(
        filter_attribute_value="neverDeleteAnyFiles",
        filter_attribute="functionName",
        act_on_first_match=False
    )
    received_test_inf = t_db.get_test_info(
        document_attribute="functionName",
        attribute_value="neverDeleteAnyFiles"
    )
    assert received_test_inf is None


def test_delete_function_coupling_by_id(mock_db):
    t_db = mock_db
    func_coup = __function_coupling_data()
    func_coup_id = t_db.add_function_coupling(func_coup)
    t_db.delete_function_coupling(func_coup_id)
    received_func_coup = t_db.get_function_coupling(func_coup_id)
    assert received_func_coup is None


def test_delete_function_coupling_by_function(mock_db):
    t_db = mock_db
    func_coup = __function_coupling_data(
        function="secret_function"
    )
    func_coup_id = t_db.add_function_coupling(func_coup)
    t_db.delete_function_coupling(
        filter_attribute="function",
        filter_attribute_value="secret_function",
        act_on_first_match=False
    )
    received_func_coup = t_db.delete_function_coupling(func_coup_id)
    assert received_func_coup is None


def test_delete_function_coupling_by_dependent(mock_db):
    t_db = mock_db
    func_coup = __function_coupling_data(
        function="func1",
        dependent_functions=["secret_function"]
    )
    func_coup = __function_coupling_data(
        function="func2",
        dependent_functions=["secret_function"]
    )
    func_coup = __function_coupling_data(
        function="func3",
        dependent_functions=["secret_function"]
    )

    func_coup_id = t_db.add_function_coupling(func_coup)
    t_db.delete_function_coupling(
        filter_attribute="dependentFunctions",
        filter_attribute_value=["secret_function"],
        act_on_first_match=False
    )

    received_func_coup = t_db.delete_function_coupling(func_coup_id)
    assert received_func_coup is None
