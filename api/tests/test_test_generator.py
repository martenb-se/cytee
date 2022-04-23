import pytest
from api.test_generator.test_generator import *
from api.tests.fixtures.mocking.open import mocker_open
from api.instances.database_main import *

MOCKED_FILES = {
    "/home/user/projects/cool_project/src/shared/utils/api": "bibibobobo",
    "/home/user/projects/cool_project/urangutest/shared/utils/api": ""
}
TEST_INFO_DATA = [
    {
        'pathToProject': '/home/jobe/tidab3/exjobb/jira_clone/client/src/',
        'fileId': 'shared/utils/api',
        'functionId': 'func1',
        "customName": "",
        "moduleData": {
            "argumentList": [
                {
                    "argument": "number_arg",
                    "type": "number",
                    "value": 2
                },
                {
                    "argument": "float_number_arg",
                    "type": "number",
                    "value": 2.37
                },
                {
                    "argument": "string_arg",
                    "type": "string",
                    "value": "wawawewa"
                },
                {
                    "argument": "bool_arg",
                    "type": "boolean",
                    "value": False
                },
                {
                    "argument": "undefined_arg",
                    "type": "undefined"
                },
                {
                    "argument": "null_arg",
                    "type": "null"
                },
                {
                    "argument": "obj_arg",
                    "type": "object",
                    "value": [
                        {
                            "argument": "inner_object_arg_1",
                            "type": "string",
                            "value": "asdasd"
                        },
                        {
                            "argument": "inner_object_arg_2",
                            "type": "undefined",
                        },
                        {
                            "argument": "inner_object_arg_3",
                            "type": "object",
                            "value": [
                                {
                                    "argument": "inner_inner_object_arg_1",
                                    "type": "number",
                                    "value": 73
                                },
                            ]
                        }
                    ]
                },
                {
                    "argument": "arry_arg",
                    "type": "array",
                    "value": [
                        {
                            "argument": "inner_array_arg",
                            "type": "number",
                            "value": 7
                        }
                    ]
                },
                {
                    "argument": "inner_obj_arg",
                    "type": "string",
                    "value": "this is an inner object arg",
                },
                {
                    "argument": "inner_arry_arg",
                    "type": "string",
                    "value": "this is an inner array arg",
                },
                {
                    "argument": "...",
                    "type": "boolean",
                    "value": True
                },
                {
                    "argument": "...",
                    "type": "number",
                    "value": 100
                }
            ],
            "returnValue": {
                "type": "string",
                "value": "asdasd"
            }
        }
    },
    {
        'pathToProject': '/home/user/projects/cool_project/src/',
        'fileId': 'shared/utils/api',
        'functionId': 'default.get',
        "customName": "",
        "moduleData": {
            "argumentList": [
                {
                    "argument": "arg1",
                    "type": "number",
                    "value": 2,
                },
                {
                    "argument": "arg2",
                    "type": "string",
                    "value": "wawawewa"
                },
                {
                    "argument": "arg3",
                    "type": "boolean",
                    "value": True
                },
                {
                    "argument": "arg4",
                    "type": "number",
                    "value": 10.123
                },
                {
                    "argument": "arg4",
                    "type": "null",
                },
                #{
                #    "argument": "arg5",
                #    "type": "bigInt",
                #    "value": "BigInt(90071999254740991)",
                #},
                {
                    "argument": "arg6",
                    "type": "object",
                    "value": [
                        {
                            "argument": "obj_arg1",
                            "type": "string",
                            "value": "wowowowowowowwo"
                        },
                        {
                            "argument": "obj_arg2",
                            "type": "number",
                            "value": 2
                        }
                    ]
                },
                {
                    "argument": "arg4",
                    "type": "undefined",
                },
            ],
            "returnValue": {
                "type": "string",
                "value": "asdasd"
            }
        }
    },
    {
        'pathToProject': '/home/user/projects/cool_project/src/',
        'fileId': 'shared/utils/api',
        'functionId': 'userObject.userFunction.(new userClass()).func2',
        "customName": "",
        "moduleData": {
            "argumentList": [
                {
                    "argument": "user_function_arg1",
                    "type": "string",
                    "value": "word"
                },
                {
                    "argument": "user_class_arg1",
                    "type": "number",
                    "value": 1
                },
                {
                    "argument": "user_class_arg2",
                    "type": "boolean",
                    "value": True
                },
                {
                    "argument": "func2_arg1",
                    "type": "string",
                    "value": "asdf"
                },
                {
                    "argument": "func2_arg2",
                    "type": "number",
                    "value": 73
                },
                {
                    "argument": "func2_arg3",
                    "type": "array",
                    "value": [
                        {
                            "argument": "",
                            "type": "number",
                            "value": 2
                        },
                        {
                            "argument": "",
                            "type": "number",
                            "value": 7
                        },
                        {
                            "argument": "",
                            "type": "number",
                            "value": 13
                        }
                    ]
                }
            ],
            "returnValue": {
                "type": "string",
                "value": "asdasd"
            }
        }
    },
]


@pytest.fixture
def mock_os_make_dirs(mocker):
    mocker.patch('api.test_generator.test_generator.os.makedirs',
                 return_value=None)
    mocker.patch('api.test_generator.test_generator.os.mkdir',
                 return_value=None)


def test_test_generator(mock_os_make_dirs, mocker_open):
    data = TEST_INFO_DATA[0]
    content_drain = {}
    mocker_open(
        'api.test_generator.test_generator.open',
        file_mocks=MOCKED_FILES,
        content_drain=content_drain
    )

    generate_test(data)
    print("")
    print(content_drain)


def test_test_generator2(mock_os_make_dirs, mocker_open):
    data = TEST_INFO_DATA[2]
    content_drain = {}
    mocker_open(
        'api.test_generator.test_generator.open',
        file_mocks=MOCKED_FILES,
        content_drain=content_drain
    )

    generate_test(data)
    print("")
    print(content_drain)


def test_super():
    #test_info = {
    #    'pathToProject': '/home/jobe/tidab3/exjobb/react_test_project/src/',
    #    'fileId': 'shared/utils/file1', 'functionId': 'test_function_1',
    #    'customName': "", 'moduleData': {"argumentList": [
    #        {'argument': "arg1", 'type': "string", 'value': "thisIsAString"},
    #        {'argument': "arg2", 'type': "number", 'value': 1},
    #        {'argument': "arg3", 'type': "boolean", 'value': False}, ],
    #                                     "returnValue": {"type": "string",
    #                                                     "value": "ok"}}}
    #generate_test(test_info)
    pass

def test_test_test():
    stringo = object_var_formatter(TEST_INFO_DATA[1]['moduleData']['argumentList'], TYPE_MATCHER_DICT)
    print("")
    #pprint(stringo)


def test_generate_tests():
    test_list = [{'pathToProject':'/home/jobe/tidab3/exjobb/jira_clone/client/src/','fileId':'shared/utils/api','functionId':'func1'},{'pathToProject':'/home/jobe/tidab3/exjobb/jira_clone/client/src/','fileId':'shared/utils/api','functionId':'func2'},{'pathToProject':'/home/jobe/tidab3/exjobb/jira_clone/client/src/','fileId':'shared/utils/api','functionId':'func2'},{'pathToProject':'/home/jobe/tidab3/exjobb/jira_clone/client/src/','fileId':'shared/utils/api','functionId':'func3'},{'pathToProject':'/home/jobe/tidab3/exjobb/jira_clone/client/src/','fileId':'shared/utils/socket','functionId':'func4'},{'pathToProject':'/home/jobe/tidab3/exjobb/jira_clone/client/src/','fileId':'shared/utils/socket','functionId':'func5'},{'pathToProject':'/home/jobe/tidab3/exjobb/jira_clone/client/src/','fileId':'shared/utils/socket','functionId':'func5'},{'pathToProject':'/home/jobe/tidab3/exjobb/jira_clone/client/src/','fileId':'shared/utils/login','functionId':'func6'},{'pathToProject':'/home/jobe/tidab3/exjobb/jira_clone/client/src/','fileId':'shared/utils/login','functionId':'func7'},{'pathToProject':'/home/jobe/tidab3/exjobb/jira_clone/client/src/','fileId':'shared/utils/create_account','functionId':'func8'},]
    generate_tests(test_list)
