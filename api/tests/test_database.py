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
        path_to_project: str =
        "/home/user/web_dev_projects/jira_clone/client/src",
        file_id: str = "shared/utils/api",
        function_id: str = "default.get",
        arguments: list = None,
        function_range: tuple = None,
        function_hash: str = "sdg7sdfg98fsd7g98dfs7df",
        dependents: int = 24,
        dependencies: int = 10,
        number_fo_tests: int = 90,
        have_function_changed: bool = False,
        export_info: str = "export default",
        export_name: str = ""
):
    if not arguments:
        arguments = [{"args": ""}]

    if not function_range:
        function_range = (1, 10)

    data = {
        "pathToProject": path_to_project,
        "fileId": file_id,
        "functionId": function_id,
        "arguments": arguments,
        "functionRange": function_range,
        "functionHash": function_hash,
        "dependents": dependents,
        "dependencies": dependencies,
        "numberOfTests": number_fo_tests,
        "haveFunctionChanged": have_function_changed,
        "exportInfo": export_info,
        "exportName": export_name
    }
    return data


def __test_info_data(
        path_to_project: str =
        "/home/user/web_dev_projects/jira_clone/client/src",
        file_id: str = "shared/utils/api",
        function_id: str = "default.get",
        custom_name: str = ""):
    data = {
        "pathToProject": path_to_project,
        "fileId": file_id,
        "functionId": function_id,
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
        path_to_project: str = '/path/to/project/proj1',
        file_id: str = 'file1',
        function_id: str = 'api',
        called_file_id: str = 'TokenHandler',
        called_function_id: str = 'getToken'
):
    data = {
        'pathToProject': path_to_project,
        'fileId': file_id,
        'functionId': function_id,
        'calledFileId': called_file_id,
        'calledFunctionId': called_function_id
    }
    return data


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


# TODO: write tests for check_valid_document_attributes

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
    expected_document = __function_info_data()
    expected_document['_id'] = "0123456789ab0123456789ab"
    resulting_document = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={"_id": "0123456789ab0123456789ab"},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER,
    )[0]
    __compare_objects(resulting_document, expected_document)


def test__get_query_by_argument_that_needs_to_be_transformed(mock_db):
    t_db = mock_db

    received_documents = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={
            'pathToProject':
                "/home/user/web_dev_projects/jira_clone/client/src"},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    for doc in received_documents:
        assert doc['pathToProject'] == \
               "/home/user/web_dev_projects/jira_clone/client/src"


def test__get_query_by_several_attributes(mock_db):
    t_db = mock_db
    received_documents = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={
            'pathToProject':
                "/home/user/web_dev_projects/jira_clone/client/src",
            'haveFunctionChanged': False
        },
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    for doc in received_documents:
        assert doc['pathToProject'] == \
               "/home/user/web_dev_projects/jira_clone/client/src"
        assert doc['haveFunctionChanged'] is False


def test__get_query_act_on_first_match(mock_db):
    t_db = mock_db
    received_documents = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={
            'pathToProject':
                "/home/user/web_dev_projects/jira_clone/client/src"},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        act_on_first_match=True
    )
    assert len(received_documents) == 1
    assert received_documents[0]['pathToProject'] == \
           "/home/user/web_dev_projects/jira_clone/client/src"


def test__get_query_non_existent_doc(mock_db):
    t_db = mock_db
    resulting_document = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={"_id": "ffffffffffffffffffffffff"},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER,
    )
    assert resulting_document is None


def test__get_query_custom_query_function(mock_db):
    t_db = mock_db

    def custom_query(db_attribute_value):
        result_document = t_db.database[FUNCTION_INFO_COLLECTION].find_one({
            '_id': ObjectId("0123456789ab0123456789ac")
        })
        app_result_document = db_to_app_doc_conv(
            result_document,
            FUNCTION_INFO_ATTRIBUTE_CHECKER)
        return [app_result_document]

    expected_document = __function_info_data(
        file_id="shared/utils/tokenize",
        function_id="getToken",
        export_info="export"
    )
    expected_document['_id'] = "0123456789ab0123456789ac"

    resulting_document = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={"_id": "0123456789ab0123456789ab"},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        query_function=custom_query
    )[0]

    __compare_objects(resulting_document, expected_document)


def test__add_query_valid_arguments(mock_db):
    t_db = mock_db

    func_inf = __function_info_data(
        file_id="shared/api/get",
        function_id="get_http"
    )

    func_inf_id = t_db._DatabaseHandler__add_query(
        collection=FUNCTION_INFO_COLLECTION,
        document=func_inf,
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER
    )

    func_inf['_id'] = func_inf_id

    received_func_inf = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={"_id": func_inf_id},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER
    )[0]

    __compare_objects(received_func_inf, func_inf)


def test__add_query_custom_query_function(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()

    def custom_query(db_document):
        db_document['pathToProject'] = 'this_is_a_secret_path'
        db_result = t_db.database[
            FUNCTION_INFO_COLLECTION] \
            .insert_one(db_document)
        return str(db_result.inserted_id)

    func_inf_id = t_db._DatabaseHandler__add_query(
        collection=FUNCTION_INFO_COLLECTION,
        document=func_inf,
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        query_function=custom_query
    )

    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={"_id": func_inf_id},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER
    )[0]

    func_inf['_id'] = func_inf_id
    func_inf['pathToProject'] = 'this_is_a_secret_path'
    __compare_objects(
        func_inf,
        returned_func_inf
    )


def test__query_set_one_filter_attribute_in_updated_doc(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()

    func_inf_id = t_db._DatabaseHandler__add_query(
        collection=FUNCTION_INFO_COLLECTION,
        document=func_inf,
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    updated_fun_inf = func_inf.copy()
    updated_fun_inf['_id'] = func_inf_id
    updated_fun_inf['pathToProject'] = 'newPath'
    updated_fun_inf['fileId'] = 'newFile'
    updated_fun_inf['functionId'] = 'newFunction'
    updated_fun_inf['dependencies'] = 5
    updated_fun_inf['haveFunctionChanged'] = True

    t_db._DatabaseHandler__set_query(
        collection=FUNCTION_INFO_COLLECTION,
        updated_document_data=updated_fun_inf,
        attribute_filter_dict={'_id': func_inf_id},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER
    )

    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={"_id": func_inf_id},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER
    )[0]

    __compare_objects(
        returned_func_inf,
        updated_fun_inf,
    )


def test__set_query(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()

    func_inf_id = t_db._DatabaseHandler__add_query(
        collection=FUNCTION_INFO_COLLECTION,
        document=func_inf,
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    updated_fun_inf = func_inf.copy()

    updated_fun_inf['pathToProject'] = '/path/is/changed'
    updated_fun_inf['fileId'] = 'newFile.js'
    updated_fun_inf['functionId'] = 'doNotDeleteAllFiles'
    updated_fun_inf['dependencies'] = 3
    updated_fun_inf['haveFunctionChanged'] = True

    t_db._DatabaseHandler__set_query(
        collection=FUNCTION_INFO_COLLECTION,
        updated_document_data=updated_fun_inf,
        attribute_filter_dict={'_id': func_inf_id},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={"_id": func_inf_id},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER
    )[0]

    __compare_objects(
        returned_func_inf,
        updated_fun_inf,
        black_list=['_id']
    )


def test__query_set_one_custom_query(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()

    func_inf_id = t_db._DatabaseHandler__add_query(
        collection=FUNCTION_INFO_COLLECTION,
        document=func_inf,
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    updated_fun_inf = func_inf.copy()

    updated_fun_inf['pathToProject'] = 'this_is_a_secret_path'
    updated_fun_inf['fileId'] = 'newFile.js'
    updated_fun_inf['functionId'] = 'doNotDeleteAllFiles'
    updated_fun_inf['dependencies'] = 3
    updated_fun_inf['haveFunctionChanged'] = True

    def custom_query(db_document, db_attribute_filter_dict):
        db_document['pathToProject'] = 'this_is_a_secret_path'
        t_db.database[
            FUNCTION_INFO_COLLECTION] \
            .update_one(db_attribute_filter_dict,
                        {'$set': db_document})

    t_db._DatabaseHandler__set_query(
        collection=FUNCTION_INFO_COLLECTION,
        updated_document_data=updated_fun_inf,
        attribute_filter_dict={'_id': func_inf_id},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        query_function=custom_query)

    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={"_id": func_inf_id},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER
    )[0]

    __compare_objects(
        returned_func_inf,
        updated_fun_inf,
        black_list=['_id']
    )


def test__query_remove_one_by_id(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()
    func_inf_id = t_db._DatabaseHandler__add_query(
        collection=FUNCTION_INFO_COLLECTION,
        document=func_inf,
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    t_db._DatabaseHandler__remove_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={'_id': func_inf_id},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={"_id": func_inf_id},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER
    )

    assert returned_func_inf is None


def test__query_remove_by_project(mock_db):
    t_db = mock_db
    func_inf = __function_info_data(path_to_project='/secret/proj/path')

    t_db._DatabaseHandler__add_query(
        collection=FUNCTION_INFO_COLLECTION,
        document=func_inf,
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    t_db._DatabaseHandler__add_query(
        collection=FUNCTION_INFO_COLLECTION,
        document=func_inf,
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    t_db._DatabaseHandler__remove_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={'pathToProject': '/secret/proj/path'},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER,
        act_on_first_match=False)

    returned_func_inf = t_db._DatabaseHandler__get_query(
        collection=FUNCTION_INFO_COLLECTION,
        attribute_filter_dict={'pathToProject': '/secret/proj/path'},
        attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    assert returned_func_inf is None


def test_get_function_info_by_id(mock_db):
    t_db = mock_db
    expected_func_inf = __function_info_data()
    expected_func_inf['_id'] = "0123456789ab0123456789ab"
    received_func_inf = t_db.get_function_info(
        {'_id': "0123456789ab0123456789ab"})[0]
    __compare_objects(expected_func_inf, received_func_inf)


def test_get_function_info_by_project(mock_db):
    t_db = mock_db
    documents = t_db.get_function_info({
        'pathToProject': "/home/user/web_dev_projects/jira_clone/client/src"})

    assert len(documents) == 3
    for doc in documents:
        assert doc['pathToProject'] == \
               "/home/user/web_dev_projects/jira_clone/client/src"


def test_get_function_info_by_project_and_have_project_changed(mock_db):
    t_db = mock_db
    documents = t_db.get_function_info({
        'pathToProject': "/home/user/web_dev_projects/jira_clone/client/src",
        'haveFunctionChanged': True}
    )
    assert len(documents) == 1
    for doc in documents:
        assert doc['haveFunctionChanged']


def test_get_test_info_by_id(mock_db):
    t_db = mock_db
    expected_test_info = __test_info_data()
    expected_test_info['_id'] = "0123456789ab0123456789ab"
    received_test_info = t_db.get_test_info({
        '_id': "0123456789ab0123456789ab"})[0]
    __compare_objects(received_test_info, expected_test_info)


def test_get_test_info_by_project(mock_db):
    t_db = mock_db
    documents = t_db.get_test_info({
        'pathToProject': "/home/user/web_dev_projects/jira_clone/client/src"
    })
    assert len(documents) == 3
    for doc in documents:
        assert doc['pathToProject'] == \
               "/home/user/web_dev_projects/jira_clone/client/src"


def test_get_test_info_by_function_id(mock_db):
    t_db = mock_db
    documents = t_db.get_test_info({
        'functionId': "default.get"
    })
    assert len(documents) == 3
    for doc in documents:
        assert doc['functionId'] == "default.get"


def test_get_function_coupling_by_id(mock_db):
    t_db = mock_db
    document = t_db.get_function_dependency({
        "_id": "0123456789ab0123456789ab"
    })
    assert len(document) == 1
    assert document[0]['_id'] == "0123456789ab0123456789ab"


def test_get_function_coupling_by_function(mock_db):
    t_db = mock_db
    document = t_db.get_function_dependency({
        'functionId': 'api'
    })
    assert len(document) == 3
    assert document[0][
               'functionId'] == "api"


def test_get_function_coupling_by_called_function(mock_db):
    t_db = mock_db
    document = t_db.get_function_dependency({
        'calledFunctionId': 'getToken'})
    for doc in document:
        assert doc['calledFunctionId'] == 'getToken'


def test_add_function_info(mock_db):
    t_db = mock_db
    expected_func_inf = __function_info_data()
    func_inf_id = t_db.add_function_info(expected_func_inf)
    expected_func_inf['_id'] = func_inf_id
    received_func_inf = t_db.get_function_info({
        '_id': func_inf_id})[0]
    __compare_objects(received_func_inf, expected_func_inf)


def test_add_test_info(mock_db):
    t_db = mock_db
    expected_test_inf = __test_info_data()
    test_inf_id = t_db.add_test_info(expected_test_inf)
    expected_test_inf['_id'] = test_inf_id
    received_test_inf = t_db.get_test_info({
        '_id': test_inf_id})[0]
    __compare_objects(received_test_inf, expected_test_inf)


def test_add_function_coupling(mock_db):
    t_db = mock_db
    expected_func_coup = __function_coupling_data()
    func_coup_id = t_db.add_function_dependency(expected_func_coup)
    expected_func_coup['_id'] = func_coup_id
    received_func_coup = t_db.get_function_dependency({'_id': func_coup_id})[0]
    __compare_objects(received_func_coup, expected_func_coup)


def test_set_function_info(mock_db):
    t_db = mock_db
    func_inf = __function_info_data()
    func_inf_id = t_db.add_function_info(func_inf)
    expected_func_inf = func_inf.copy()
    expected_func_inf['_id'] = func_inf_id
    expected_func_inf['pathToProject'] = "/path/to/project/proj37"
    expected_func_inf['fileId'] = "superUtil.js"
    expected_func_inf['dependents'] = 36
    expected_func_inf['numberOfTests'] = 700
    expected_func_inf['haveFunctionChanged'] = True
    t_db.set_function_info(
        update_function_info=expected_func_inf,
        attribute_filter_dict={'_id': func_inf_id}
    )
    received_func_inf = t_db.get_function_info({'_id': func_inf_id})[0]
    __compare_objects(received_func_inf, expected_func_inf)


def test_set_test_info(mock_db):
    t_db = mock_db
    test_inf = __test_info_data()
    test_inf_id = t_db.add_test_info(test_inf)
    expected_test_inf = test_inf.copy()
    expected_test_inf['_id'] = test_inf_id
    expected_test_inf['pathToProject'] = "/path/to/project/proj1"
    expected_test_inf['customName'] = "superDuperTest"
    t_db.set_test_info(
        update_test_info=expected_test_inf,
        attribute_filter_dict={'_id': test_inf_id})
    received_test_inf = t_db.get_test_info({'_id': test_inf_id})[0]
    __compare_objects(received_test_inf, expected_test_inf)


def test_set_function_coupling(mock_db):
    t_db = mock_db
    func_coup = __function_coupling_data()
    func_coup_id = t_db.add_function_dependency(func_coup)
    expected_func_coup = func_coup.copy()
    expected_func_coup['_id'] = func_coup_id
    expected_func_coup['functionId'] = 'api_new'
    t_db.set_function_dependency(
        update_function_dependency=expected_func_coup,
        attribute_filter_dict={'_id': func_coup_id})
    received_func_coup = t_db.get_function_dependency({'_id': func_coup_id})[0]
    __compare_objects(received_func_coup, expected_func_coup)


def test_delete_function_info_by_id(mock_db):
    t_db = mock_db
    func_info = __function_info_data()
    func_coup_id = t_db.add_function_info(func_info)
    t_db.remove_function_info({'_id': func_coup_id})
    received_func_inf = t_db.get_function_info({'_id': func_coup_id})
    assert received_func_inf is None


def test_delete_function_info_by_project(mock_db):
    t_db = mock_db
    func_inf = __function_info_data(
        path_to_project="/path/to/project/projSecret"
    )
    t_db.add_function_info(func_inf)
    t_db.add_function_info(func_inf)
    t_db.add_function_info(func_inf)
    t_db.remove_function_info(
        attribute_filter_dict={'pathToProject': "/path/to/project/projSecret"}
    )
    received_func_inf = t_db.get_function_info(
        attribute_filter_dict={'pathToProject': "/path/to/project/projSecret"}
    )
    assert received_func_inf is None


def test_delete_function_info_by_file(mock_db):
    t_db = mock_db
    func_inf = __function_info_data(
        file_id="superSecretFile.js"
    )
    t_db.add_function_info(func_inf)
    t_db.add_function_info(func_inf)
    t_db.add_function_info(func_inf)
    t_db.remove_function_info(
        {'fileId': "superSecretFile.js"}
    )
    received_func_inf = t_db.get_function_info(
        {'fileId': "superSecretFile.js"}
    )
    assert received_func_inf is None


def test_delete_function_info_by_function_name(mock_db):
    t_db = mock_db
    func_inf = __function_info_data(
        function_id="neverDeleteAnyFiles"
    )
    t_db.add_function_info(func_inf)
    t_db.remove_function_info(
        {'functionId': "neverDeleteAnyFiles"}
    )
    received_func_inf = t_db.get_function_info(
        {'functionId': "neverDeleteAnyFiles"}
    )
    assert received_func_inf is None


def test_delete_test_info_by_id(mock_db):
    t_db = mock_db
    test_inf = __test_info_data()
    test_inf_id = t_db.add_test_info(test_inf)
    t_db.remove_test_info({'_id': test_inf_id})
    received_test_inf = t_db.get_test_info({'_id': test_inf_id})
    assert received_test_inf is None


def test_delete_test_info_by_project(mock_db):
    t_db = mock_db
    test_inf = __test_info_data(
        path_to_project="/path/to/project/projSecret"
    )
    t_db.add_test_info(test_inf)
    t_db.add_test_info(test_inf)
    t_db.add_test_info(test_inf)
    t_db.remove_test_info(
        {'pathToProject': "/path/to/project/projSecret"}
    )
    received_test_inf = t_db.get_test_info(
        {'pathToProject': "/path/to/project/projSecret"}
    )
    assert received_test_inf is None


def test_delete_test_info_by_function(mock_db):
    t_db = mock_db
    test_inf = __test_info_data(
        function_id="neverDeleteAnyFiles"
    )
    t_db.add_test_info(test_inf)
    t_db.add_test_info(test_inf)
    t_db.add_test_info(test_inf)
    t_db.remove_test_info(
        {'functionId': 'neverDeleteAnyFiles'}
    )
    received_test_inf = t_db.get_test_info(
        {'functionId': 'neverDeleteAnyFiles'}
    )
    assert received_test_inf is None


def test_delete_function_coupling_by_id(mock_db):
    t_db = mock_db
    func_coup = __function_coupling_data()
    func_coup_id = t_db.add_function_dependency(func_coup)
    t_db.remove_function_dependency({'_id': func_coup_id})
    received_func_coup = t_db.get_function_dependency({'_id': func_coup_id})
    assert received_func_coup is None


def test_delete_function_coupling_by_function(mock_db):
    t_db = mock_db
    func_coup = __function_coupling_data(
        function_id="secret_function"
    )
    func_coup_id = t_db.add_function_dependency(func_coup)
    t_db.remove_function_dependency(
        {'functionId': "secret_function"}
    )
    t_db.remove_function_dependency({'_id': func_coup_id})

    received_func_coup = t_db.get_function_dependency(
        {'_id': func_coup_id}
    )

    assert received_func_coup is None
