import time
from api.api import *
from flask import Flask, request, jsonify
from flask_sock import Sock
from api.instances.shared_websockets_main import shared_websockets_handler
from api.websocket import WsIdentity
import simple_websocket


server = Flask(__name__, static_folder='../build', static_url_path='/')
socket = Sock(server)


@server.route('/')
def index():
    return "Hello, World!"


@server.route('/test-socket/<socket_identifier>')
def any_test_socket(socket_identifier):
    """Page used for debugging WebSockets.

    TODO: Remove as this is only a test.

    :param socket_identifier: The name of the socket endpoint to debug.
    :return: The HTML source.
    """
    return test_socket(socket_identifier)


@server.route('/api/list_files', methods=['POST'])
def post_list_files():
    """List files in the standard directory or from the specified sub
    directory.

    :return: JSON with status code and a list of files if successful.
    """
    content = request.json

    if 'subDirectory' in content:
        api_return = list_files(content['subDirectory'])

    else:
        api_return = {
            "status": APIStatus.ERROR.value,
            "statusCode": APICode.ERROR_BAD_REQUEST.value,
            "message":
                "Required property 'subDirectory' is missing from request!"
        }

    return jsonify(api_return)


@server.route('/api/new_project', methods=['POST'])
def post_new_project():
    """Create a new project from the specified path.

    :return: JSON with status code.
    """
    content = request.json
    path_to_project = content["pathToProject"]

    api_return = new_project(path_to_project)

    return jsonify(api_return)


@server.route('/api/choose_project', methods=['POST'])
def post_choose_project():
    """Choose and reopen an existing project.

    :return: JSON with status code.
    """
    content = request.json
    path_to_project = content["pathToProject"]

    api_return = choose_project(path_to_project)

    return jsonify(api_return)


@server.route('/api/get_functions_for_project', methods=['POST'])
def post_get_functions_for_project():
    """Get all functions created for a project.

    :return: JSON with status code.
    """
    content = request.json
    path_to_project = content["pathToProject"]

    api_return = get_functions_for_project(path_to_project)

    return jsonify(api_return)


@server.route('/api/read_file', methods=['POST'])
def post_read_file():
    """Read a project file.

    :return: JSON with status code.
    """
    content = request.json
    path_to_project = content["pathToProject"]
    file_id = content["fileId"]

    api_return = read_file(path_to_project, file_id)

    return jsonify(api_return)


@server.route('/api/get_tests_for_project', methods=['POST'])
def post_get_tests_for_project():
    """Get all tests for the given project.

    :return: JSON with status code.
    """
    content = request.json
    path_to_project = content["pathToProject"]

    api_return = get_tests_for_project(path_to_project)

    return jsonify(api_return)


@server.route('/api/save_test', methods=['POST'])
def post_save_test():
    """Save a test for the given function.

    :return: JSON with status code.
    """
    content = request.json
    path_to_project = content["pathToProject"]
    file_id = content["fileId"]
    function_id = content["functionId"]
    test_module = content["testModule"]

    if 'customName' in content:
        custom_name = content["customName"]
    else:
        custom_name = ""

    api_return = \
        save_test(
            path_to_project, file_id, function_id, test_module, custom_name)

    return jsonify(api_return)


@server.route('/api/edit_test', methods=['POST'])
def post_edit_test():
    """Edit a test given by the specified Id.

    :return: JSON with status code.
    """
    content = request.json
    test_id = content["testId"]
    test_module = content["testModule"]
    custom_name = content["customName"]

    api_return = edit_test(test_id, test_module, custom_name)

    return jsonify(api_return)


@server.route('/api/delete_test', methods=['POST'])
def post_delete_test():
    """Delete a test given by the specified Id.

    :return: JSON with status code.
    """
    content = request.json
    test_id = content["testId"]

    api_return = delete_test(test_id)

    return jsonify(api_return)


@server.route('/api/time')
def get_current_time():
    """Display the current time.

    TODO: Remove as this is only a test.

    :return: The time.
    """
    return {'time': time.time()}


@socket.route('/sock/list_files')
def sock_list_files(sock):
    """WebSocket for 'list_files' api. Listeners to this sockets will know
    when the listing of files is done.

    TODO: Remove as this is only a test.

    :param sock: The instantiated socket to communicate over.
    :type sock: simple_websocket.ws.Server
    :return: Nothing
    """
    shared_websockets_handler.add_socket(WsIdentity.LIST_FILES, sock)
    shared_websockets_handler.keep_alive(sock)


@socket.route('/sock/new_project')
def sock_new_project(sock):
    """WebSocket for 'choose_files' api. Listeners to this sockets will know
    about events during the analysis of the selected files.

    :param sock: The instantiated socket to communicate over.
    :return: Nothing
    """
    shared_websockets_handler.add_socket(WsIdentity.NEW_PROJECT, sock)
    shared_websockets_handler.keep_alive(sock)
