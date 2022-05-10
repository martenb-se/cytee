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
                # {
                #    "argument": "arg5",
                #    "type": "bigInt",
                #    "value": "BigInt(90071999254740991)",
                # },
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
    }, {
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
            "exception": {
                "value": "superException"
            }
        }
    },
    {
        "_id": {"$oid": "626ec2e1f2c11ac961ca4058"},
        "customName": "random_test_1",
        "fileId": "/shared/utils/file1",
        "functionId": "test_function_1",
        "moduleData": {
            "argumentList": [
                {
                    "argument": "arg1",
                    "subFunctionName": "test_function_1",
                    "type": "number",
                    "value": "3"
                },
                {
                    "argument": "arg2",
                    "subFunctionName": "test_function_1",
                    "type": "number",
                    "value": "4"
                },
                {
                    "argument": "arg3",
                    "subFunctionName": "test_function_1",
                    "type": "number",
                    "value": "5"
                }
            ],
            "returnValue": {
                "type": "string",
                "value": "ok"
            }
        },
        "pathToProject": "/home/jobe/tidab3/exjobb/react_test_project/src"
    },
    {
        "_id": {"$oid": "626ec326f2c11ac961ca4059"},
        "customName": "random_test_2",
        "fileId": "/shared/utils/file1",
        "functionId": "test_function_1",
        "moduleData": {
            "argumentList": [
                {
                    "subFunctionName": "test_function_1",
                    "argument": "arg1",
                    "type": "string",
                    "value": "dfgdfg"
                },
                {
                    "subFunctionName": "test_function_1",
                    "argument": "arg2",
                    "type": "boolean",
                    "value": False
                },
                {
                    "subFunctionName": "test_function_1",
                    "argument": "arg3",
                    "type": "undefined"
                }
            ],
            "returnValue": {
                "type": "string",
                "value": "ok"
            }
        },
        "pathToProject": "/home/jobe/tidab3/exjobb/react_test_project/src"
    }

]


@pytest.fixture
def mock_os_make_dirs(mocker):
    mocker.patch('api.test_generator.test_generator.os.makedirs',
                 return_value=None)
    mocker.patch('api.test_generator.test_generator.os.mkdir',
                 return_value=None)


def test_test_generator_generate_tests(mock_os_make_dirs, mocker_open):
    content_drain = {}
    mocker_open(
        'api.test_generator.test_generator.open',
        file_mocks=MOCKED_FILES,
        content_drain=content_drain
    )

    generate_tests([TEST_INFO_DATA[4], TEST_INFO_DATA[5]])

    print("")
    print(content_drain)
