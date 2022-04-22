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

    :return: The file list in JSON.
    """
    content = request.json

    api_return = list_files(content['sub_dir'])

    return jsonify(api_return)


@server.route('/api/choose_files', methods=['POST'])
def post_choose_files():
    """Chose the selected files and begin the process of analyzing the files.

    :return: The number of files to analyze in JSON.
    """
    content = request.json
    path_to_project = content["pathToProject"]
    list_of_files = content["chosenFiles"]

    api_return = choose_files(path_to_project, list_of_files)

    return jsonify(api_return)


@server.route('/api/time')
def get_current_time():
    """Display the current time.

    TODO: Remove as this is only a test.

    :return: The time.
    """
    return {'time': time.time()}


@socket.route('/sock_list_files')
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


@socket.route('/sock_choose_files')
def sock_choose_files(sock):
    """WebSocket for 'choose_files' api. Listeners to this sockets will know
    about events during the analysis of the selected files.

    :param sock: The instantiated socket to communicate over.
    :return: Nothing
    """
    shared_websockets_handler.add_socket(WsIdentity.CHOOSE_FILES, sock)
    shared_websockets_handler.keep_alive(sock)

    """while True:
        # TODO: Should not act as an echo server later..
        data = sock.receive()
        sock.send(data)"""
