import pytest
from api.test_generator.test_generator import *
from api.tests.fixtures.mocking.open import mocker_open
from api.instances.database_main import *

MOCKED_FILES = {
    "/home/user/projects/cool_project/src/shared/utils/api": "bibibobobo",
    "/home/user/projects/cool_project/urangutest/shared/utils/api": ""
}

TEST_INFO_DATA = {
    "argument_return_val_test": {
        "_id": {"$oid": "627cd82c21dc71fee6ba634b"},
        "customName": "return",
        "fileId": "shared/utils/file1",
        "functionId": "test_function_1",
        "moduleData": {
            "argumentList": [
                {
                    "argument": "arg1",
                    "subFunctionName": "test_function_1",
                    "type": "boolean",
                    "value": False
                },
                {
                    "argument": "arg2",
                    "subFunctionName": "test_function_1",
                    "type": "number",
                    "value": "5"
                },
                {
                    "argument": "arg3",
                    "subFunctionName": "test_function_1",
                    "type": "null"
                }
            ],
            "returnValue": {
                "type": "string",
                "value": "maybe",
                "equal": True
            }
        },
        "pathToProject": "/home/jobe/tidab3/exjobb/react_test_project/src"
    },
    "argument_return_val_not_equal_test": {
        "_id": {"$oid": "627cd82c21dc71fee6ba634b"},
        "customName": "return",
        "fileId": "shared/utils/file1",
        "functionId": "test_function_1",
        "moduleData": {
            "argumentList": [
                {
                    "argument": "arg1",
                    "subFunctionName": "test_function_1",
                    "type": "boolean",
                    "value": False
                },
                {
                    "argument": "arg2",
                    "subFunctionName": "test_function_1",
                    "type": "number",
                    "value": "5"
                },
                {
                    "argument": "arg3",
                    "subFunctionName": "test_function_1",
                    "type": "null"
                }
            ],
            "returnValue": {
                "type": "string",
                "value": "maybe not",
                "equal": False
            }
        },
        "pathToProject": "/home/jobe/tidab3/exjobb/react_test_project/src"
    },
    "argument_exception_test":
        {
            "_id": {"$oid": "627f5001eaff9d6d6a92ba10"},
            "customName": "exception",
            "fileId": "shared/utils/file1",
            "functionId": "test_function_1",
            "moduleData": {
                "argumentList": [
                    {
                        "argument": "arg1",
                        "subFunctionName": "test_function_1",
                        "type": "boolean",
                        "value": False
                    },
                    {
                        "argument": "arg2",
                        "subFunctionName": "test_function_1",
                        "type": "string",
                        "value": "hmggf"
                    },
                    {
                        "argument": "arg3",
                        "subFunctionName": "test_function_1",
                        "type": "null"
                    }
                ],
                "exception": {
                    "value": "Error",
                    "equal": True
                }
            },
            "pathToProject": "/home/jobe/tidab3/exjobb/react_test_project/src"
        },
    "argument_exception_test_message":
        {
            "_id": {"$oid": "627f7645ba0c5f5becef1ab4"},
            "customName": "exception message",
            "fileId": "shared/utils/file1",
            "functionId": "test_function_1",
            "moduleData": {
                "argumentList": [
                    {
                        "argument": "arg1",
                        "subFunctionName": "test_function_1",
                        "type": "boolean",
                        "value": False
                    },
                    {
                        "argument": "arg2",
                        "subFunctionName": "test_function_1",
                        "type": "string",
                        "value": "hmggf"
                    },
                    {
                        "argument": "arg3",
                        "subFunctionName": "test_function_1",
                        "type": "null"
                    }
                ],
                "exception": {
                    "message": "This is a message",
                    "value": "Error",
                    "equal": True
                }
            },
            "pathToProject": "/home/jobe/tidab3/exjobb/react_test_project/src"
        },
    "argument_exception_not_equal_test":
        {
            "_id": {"$oid": "627f7645ba0c5f5becef1ab4"},
            "customName": "exception message",
            "fileId": "shared/utils/file1",
            "functionId": "test_function_1",
            "moduleData": {
                "argumentList": [
                    {
                        "argument": "arg1",
                        "subFunctionName": "test_function_1",
                        "type": "boolean",
                        "value": False
                    },
                    {
                        "argument": "arg2",
                        "subFunctionName": "test_function_1",
                        "type": "string",
                        "value": "hmggf"
                    },
                    {
                        "argument": "arg3",
                        "subFunctionName": "test_function_1",
                        "type": "null"
                    }
                ],
                "exception": {
                    "message": "This is a message",
                    "value": "Error",
                    "equal": False
                }
            },
            "pathToProject": "/home/jobe/tidab3/exjobb/react_test_project/src"
        },
}


@pytest.fixture
def mock_os_make_dirs(mocker):
    mocker.patch('api.test_generator.test_generator.os.makedirs',
                 return_value=None)
    mocker.patch('api.test_generator.test_generator.os.mkdir',
                 return_value=None)


def test_test_generator_generate_return_value_test(
        mock_os_make_dirs,
        mocker_open
):
    content_drain = {}
    mocker_open(
        'api.test_generator.test_generator.open',
        file_mocks=MOCKED_FILES,
        content_drain=content_drain
    )

    generate_tests([TEST_INFO_DATA["argument_return_val_test"]])

    file_path = '/home/jobe/tidab3/exjobb/react_test_project/src/shared' \
                '/utils/file1.urang.spec.js'

    expected_data = 'test("return", () =>  {' \
                        'let a_0=false;' \
                        'let a_1=5;' \
                        'let a_2=null;' \
                        'let r_1=test_function_1(a_0,a_1,a_2);' \
                        'expect(r_1).toEqual(\'maybe\');' \
                    '});'

    #print("")
    #print(content_drain)
    assert content_drain[file_path] == expected_data


def test_test_generator_generate_not_equal_return_value(
        mock_os_make_dirs,
        mocker_open
):
    content_drain = {}
    mocker_open(
        'api.test_generator.test_generator.open',
        file_mocks=MOCKED_FILES,
        content_drain=content_drain
    )

    generate_tests([TEST_INFO_DATA["argument_return_val_not_equal_test"]])
    file_path = '/home/jobe/tidab3/exjobb/react_test_project/src/shared' \
                '/utils/file1.urang.spec.js'

    expected_data = 'test("return", () =>  {' \
                        'let a_0=false;' \
                        'let a_1=5;' \
                        'let a_2=null;' \
                        'let r_1=test_function_1(a_0,a_1,a_2);' \
                        'expect(r_1).not.toEqual(\'maybe not\');' \
                    '});'

    #print("")
    #print(content_drain)
    assert content_drain[file_path] == expected_data


def test_test_generator_generate_exception_test(
        mock_os_make_dirs,
        mocker_open
):
    content_drain = {}
    mocker_open(
        'api.test_generator.test_generator.open',
        file_mocks=MOCKED_FILES,
        content_drain=content_drain
    )
    generate_tests([TEST_INFO_DATA["argument_exception_test"]])
    file_path = '/home/jobe/tidab3/exjobb/react_test_project/src/shared' \
                '/utils/file1.urang.spec.js'

    expected_data = 'test("exception", () =>  {' \
                        'let a_0=false;' \
                        'let a_1=\'hmggf\';' \
                        'let a_2=null;' \
                        'try {' \
                            'test_function_1(a_0,a_1,a_2);' \
                        '} catch (e) {' \
                            'expect(e.name).toBe("Error");' \
                        '}' \
                    '});'
    # print("")
    # print(content_drain)
    assert content_drain[file_path] == expected_data


def test_test_generator_generate_exception_message_test(
        mock_os_make_dirs,
        mocker_open
):
    content_drain = {}
    mocker_open(
        'api.test_generator.test_generator.open',
        file_mocks=MOCKED_FILES,
        content_drain=content_drain
    )
    generate_tests([TEST_INFO_DATA["argument_exception_test_message"]])
    file_path = '/home/jobe/tidab3/exjobb/react_test_project/src/shared' \
                '/utils/file1.urang.spec.js'

    expected_data = 'test("exception message", () =>  {' \
                        'let a_0=false;' \
                        'let a_1=\'hmggf\';' \
                        'let a_2=null;' \
                        'try {' \
                            'test_function_1(a_0,a_1,a_2);' \
                        '} catch (e) {' \
                            'expect(e.name).toBe("Error");' \
                            'expect(e.message).toBe("This is a message");' \
                        '}' \
                    '});'
    #print("")
    #print(content_drain)
    assert content_drain[file_path] == expected_data


def test_test_generator_not_generate_exception_test(
        mock_os_make_dirs,
        mocker_open
):
    content_drain = {}
    mocker_open(
        'api.test_generator.test_generator.open',
        file_mocks=MOCKED_FILES,
        content_drain=content_drain
    )
    generate_tests([TEST_INFO_DATA["argument_exception_not_equal_test"]])
    file_path = '/home/jobe/tidab3/exjobb/react_test_project/src/shared' \
                '/utils/file1.urang.spec.js'

    expected_data = 'test("exception message", () =>  {' \
                        'let a_0=false;' \
                        'let a_1=\'hmggf\';' \
                        'let a_2=null;' \
                        'try {' \
                            'test_function_1(a_0,a_1,a_2);' \
                        '} catch (e) {' \
                            'expect(e.name).not.toBe("Error");' \
                            'expect(e.message).not.toBe("This is a message");' \
                        '}' \
                    '});'
    #print("")
    #print(content_drain)
    assert content_drain[file_path] == expected_data
