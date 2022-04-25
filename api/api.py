import logging
import os
import re
from enum import Enum
from api.analyzer.analyzer import analyze_files
from threading import Thread
from api.cache import read_file as cache_read_file
from api.instances.database_main import database_handler
from api.instances.shared_websockets_main import shared_websockets_handler
from api.websocket import WsIdentity, WsCode
from api.instances.config_urang import config_urang


class APIStatus(Enum):
    OK = "OK"
    ERROR = "ERROR"


class APICode(Enum):
    ERROR_BAD_REQUEST = "BAD_REQUEST"

    ERROR_NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    ERROR_UNKNOWN = "UNKNOWN"

    ERROR_PROJECT_NOT_EXISTING = "PROJECT_NOT_EXISTING"
    ERROR_PROJECT_FILE_NOT_EXISTING = "PROJECT_FILE_NOT_EXISTING"
    ERROR_PROJECT_FUNCTION_NOT_EXISTING = "PROJECT_FUNCTION_NOT_EXISTING"

    ERROR_PROJECT_CACHE_FILE_NOT_EXISTING = "PROJECT_CACHE_FILE_NOT_EXISTING"

    ERROR_PROJECT_TEST_NOT_EXISTING = "PROJECT_TEST_NOT_EXISTING"


def list_files(sub_dir: str) -> dict:
    """List files in the given sub directory.

    :param sub_dir: The sub directory to list files from.
    :type sub_dir: str
    :return: Operation status data and the list of files.
    :rtype: dict
    """
    if 'directory' in config_urang and 'base' in config_urang['directory']:
        base_directory = config_urang['directory']['base']
    else:
        base_directory = os.path.dirname(os.path.abspath(__file__))

    try:
        path_to_dir = base_directory + "/" + sub_dir

        if not re.match(
                re.escape(base_directory), os.path.abspath(path_to_dir)):
            sub_dir = ""
            path_to_dir = base_directory

        files = os.listdir(path_to_dir)

        sub_dir_fixed = \
            re.sub(
                re.escape(os.path.abspath(base_directory)),
                '',
                os.path.abspath(path_to_dir))

        file_list = [
            {
                "fileName":
                    f,
                "subDir":
                    sub_dir_fixed,
                "isDirectory":
                    os.path.isdir(path_to_dir + "/" + f),
                "isFile":
                    os.path.isfile(path_to_dir + "/" + f)
            } for f in files]

        # TODO: Remove this loop only used for testing purposes.
        for file_index, file in enumerate(file_list):
            shared_websockets_handler.send_progress(
                WsIdentity.LIST_FILES,
                WsCode.FILE_LIST_LOOP_FILES,
                file_index,
                len(file_list),
                "Progress is being made"
            )

        # TODO: Remove this only used for testing purposes.
        shared_websockets_handler.send_success(
            WsIdentity.LIST_FILES,
            WsCode.FILE_LIST_COMPLETE,
            "Listing files was complete!"
        )

        return_message = {
            "status": APIStatus.OK.value,
            "curDir": sub_dir_fixed,
            "fileList": file_list
        }

    except Exception as e:
        logging.critical(
            "During api.api:list_files() an unknown exception was raised: "
            f"{e}")

        return_message = {
            "status": APIStatus.ERROR.value,
            "statusCode": APICode.ERROR_UNKNOWN.value
        }

    return return_message


def new_project(path_to_project: str) -> dict:
    """Create a new project from the specified path.

    :param path_to_project:
    :type path_to_project: str
    :return: Operation status data.
    :rtype: dict
    """
    if 'directory' in config_urang and 'base' in config_urang['directory']:
        base_directory = config_urang['directory']['base']
    else:
        base_directory = os.path.dirname(os.path.abspath(__file__))

    full_path_to_project = \
        os.path.abspath(base_directory + "/" + path_to_project)

    thread = Thread(
        target=analyze_files,
        args=(full_path_to_project, ))

    thread.start()

    return {
        "status": APIStatus.OK.value
    }


def choose_project(path_to_project: str) -> dict:
    """Choose and reopen an existing project.

    :param path_to_project: Path to existing project.
    :type path_to_project: str

    :return: Operation status data.
    :rtype: dict
    """
    return {
        "status": APIStatus.ERROR.value,
        "statusCode": APICode.ERROR_NOT_IMPLEMENTED.value
    }


def __get_function_info_project(path_to_project: str):
    return database_handler.get_function_info({
        'pathToProject': path_to_project
    })


def __get_function_info_project_file(path_to_project: str, file_id: str):
    return database_handler.get_function_info({
        'pathToProject': path_to_project,
        'fileId': file_id
    })


def __get_function_info_project_file_function(
        path_to_project: str,
        file_id: str,
        function_id: str):
    return database_handler.get_function_info({
        'pathToProject': path_to_project,
        'fileId': file_id,
        'functionId': function_id
    })


def get_functions_for_project(path_to_project: str) -> dict:
    """Get all functions created for the project at the given path.

    :param path_to_project: Path to existing project.
    :type path_to_project: str

    :return: Operation status data and the project functions if successful.
    :rtype: dict
    """
    project_functions = __get_function_info_project(path_to_project)

    if project_functions is None:
        return_message = {
            "status": APIStatus.ERROR,
            "statusCode": APICode.ERROR_PROJECT_NOT_EXISTING.value
        }

    else:
        return_message = {
            "status": APIStatus.OK.value,
            "projectFunctions": project_functions
        }

    return return_message


def read_file(
        path_to_project: str,
        file_id: str) -> dict:
    """Read a project file.

    :param path_to_project: Path to existing project.
    :type path_to_project: str
    :param file_id: The id of the file to get.
    :type file_id: str

    :return: Operation status data and the file data if successful.
    :rtype: dict
    """
    project_file_functions = \
        __get_function_info_project_file(path_to_project, file_id)

    if project_file_functions is None:
        if __get_function_info_project(path_to_project) is None:
            return_message = {
                "status": APIStatus.ERROR,
                "statusCode": APICode.ERROR_PROJECT_NOT_EXISTING.value
            }
        else:
            return_message = {
                "status": APIStatus.ERROR,
                "statusCode": APICode.ERROR_PROJECT_FILE_NOT_EXISTING.value
            }

    else:
        try:
            file_contents = cache_read_file(path_to_project, file_id)
            return_message = {
                "status": APIStatus.OK.value,
                "fileContents": file_contents
            }

        except FileNotFoundError:
            return_message = {
                "status":
                    APIStatus.ERROR,
                "statusCode":
                    APICode.ERROR_PROJECT_CACHE_FILE_NOT_EXISTING.value
            }

        except Exception as e:
            logging.critical(
                "During api.api:read_file() an unknown exception was raised: "
                f"{e}")

            return_message = {
                "status": APIStatus.ERROR.value,
                "statusCode": APICode.ERROR_UNKNOWN.value
            }

    return return_message


def get_tests_for_project(path_to_project: str) -> dict:
    """Get all tests for the given project.

    :param path_to_project: Path to existing project.
    :type path_to_project: str
    :return: Operation status data and the project tests.
    :rtype: dict
    """
    project_tests = \
        database_handler.get_test_info({
            'pathToProject': path_to_project
        })

    tests = []

    if project_tests is not None:
        tests = project_tests

    return {
        "status": APIStatus.OK.value,
        "projectTests": tests
    }


def __update_tests_count(
        path_to_project: str,
        file_id: str,
        function_id: str):
    if __get_function_info_project_file_function(
            path_to_project, file_id, function_id) is not None:
        function_tests = \
            database_handler.get_test_info({
                'pathToProject': path_to_project,
                'fileId': file_id,
                'functionId': function_id
            })

        tests_count = 0
        if function_tests is not None:
            tests_count = len(function_tests)

        database_handler.set_function_info(
            {
                "numberOfTests": tests_count
            }, {
                'pathToProject': path_to_project,
                'fileId': file_id,
                'functionId': function_id
            })


def __missing_project_function_return_data(path_to_project, file_id):
    if __get_function_info_project(path_to_project) is None:
        return_message = {
            "status": APIStatus.ERROR,
            "statusCode": APICode.ERROR_PROJECT_NOT_EXISTING.value
        }
    elif __get_function_info_project_file(
            path_to_project, file_id) is None:
        return_message = {
            "status": APIStatus.ERROR,
            "statusCode": APICode.ERROR_PROJECT_FILE_NOT_EXISTING.value
        }
    else:
        return_message = {
            "status": APIStatus.ERROR,
            "statusCode": APICode.ERROR_PROJECT_FUNCTION_NOT_EXISTING.value
        }

    return return_message


def save_test(
        path_to_project: str,
        file_id: str,
        function_id: str,
        test_module: dict,
        custom_name: str) -> dict:
    """Save a test for the given function.

    :param path_to_project: Path to existing project.
    :type path_to_project: str
    :param file_id: The id of the file containing the function.
    :type file_id: str
    :param function_id: The id of the function to test.
    :type function_id: str
    :param test_module: The test specification.
    :type test_module: dict
    :param custom_name: Custom test name or description.
    :type custom_name: str
    :return: Operation status data.
    :rtype: dict
    """

    project_function = __get_function_info_project_file_function(
        path_to_project, file_id, function_id)

    if project_function is None:
        return_message = \
            __missing_project_function_return_data(path_to_project, file_id)

    else:
        database_handler.add_test_info({
            'pathToProject': path_to_project,
            'fileId': file_id,
            'functionId': function_id,
            'customName': custom_name,
            'moduleData': test_module
        })

        __update_tests_count(path_to_project, file_id, function_id)

        return_message = {
            "status": APIStatus.OK.value
        }

    return return_message


def edit_test(
        test_id: str,
        test_module: dict,
        custom_name: str) -> dict:
    """Edit a test given by the specified Id.

    :param test_id: The id of the test to edit.
    :type test_id: str
    :param test_module: The test specification.
    :type test_module: dict
    :param custom_name: Custom test name or description.
    :type custom_name: str
    :return: Operation status data.
    :rtype: dict
    """

    project_test = database_handler.get_test_info({
        '_id': test_id
    })

    if project_test is None:
        return_message = {
            "status": APIStatus.ERROR,
            "statusCode": APICode.ERROR_PROJECT_TEST_NOT_EXISTING.value
        }

    else:
        database_handler.set_test_info(
            {
                'customName': custom_name,
                'moduleData': test_module
            },
            {'_id': test_id}
        )

        return_message = {
            "status": APIStatus.OK.value
        }

    return return_message


def delete_test(test_id: str) -> dict:
    """Delete a test given by the specified Id.

    :param test_id: The id of the test to edit.
    :type test_id: str
    :return: Operation status data.
    :rtype: dict
    """
    project_test = database_handler.get_test_info({
        '_id': test_id
    })

    if project_test is None:
        return_message = {
            "status": APIStatus.ERROR,
            "statusCode": APICode.ERROR_PROJECT_TEST_NOT_EXISTING.value
        }

    else:
        database_handler.remove_test_info({
            '_id': test_id
        })

        __update_tests_count(
            project_test[0]["pathToProject"],
            project_test[0]["fileId"],
            project_test[0]["functionId"])

        return_message = {
            "status": APIStatus.OK.value
        }

    return return_message


def test_socket(socket_identifier):
    """Debugging WebSockets.

    TODO: Remove as this is only a test.

    :param socket_identifier: The name of the socket endpoint to debug.
    :return: The HTML source.
    """
    values = set(item.value for item in WsIdentity)
    socket_links = \
        map(lambda socket_id:
            f"<a href='/test-socket/{socket_id}'>{socket_id}</a>", values)

    if socket_identifier not in values:
        return '<!doctype html><html><head><title>Socket: Unavailable</title>' \
               '</head><body>' \
               '<h1>Socket: Unavailable</h1>' + \
               f'<p>Available sockets are: {", ".join(socket_links)}</p>' \
               '</body></html>'

    return '<!doctype html><html><head>' \
           f'<title>Socket: {socket_identifier}</title>' \
           '<script src="https://code.jquery.com/jquery-3.6.0.min.js" ' \
           'integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" ' \
           'crossorigin="anonymous"></script></head><body>' \
           f'<h1>Socket: {socket_identifier}</h1>' + \
           '<div id="log"></div><br><form id="form">' \
           '<label for="text">Input:</label>' \
           '<input type="text" id="text" autofocus></form>' \
           '<script>$( document ).ready(function() {const log = ' \
           '(text, color) => {document.getElementById("log").innerHTML += ' \
           '`<span style="color: ${color}">${text}</span><br>`;};' \
           'const socket = new WebSocket("ws://" + location.host + ' \
           f'"/sock/{socket_identifier}");' + \
           'socket.addEventListener("message", ev => ' \
           '{log("<<< " + ev.data, "blue");});' \
           'document.getElementById("form").onsubmit = ev => ' \
           '{ev.preventDefault();const textField = ' \
           'document.getElementById("text");' \
           'log(">>> " + textField.value, "red");' \
           'socket.send(textField.value);textField.value = "";};});' \
           '</script></body></html>'
