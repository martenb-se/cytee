import time
from api.analyzer.analyzer import analyze_files
from api.api import *
from flask import Flask, request, jsonify
from pprint import pprint
from flask_sock import Sock
from threading import Thread

server = Flask(__name__, static_folder='../build', static_url_path='/')
socket = Sock(server)
shared_socket_handlers = {}

# TODO: Move all of the below to a common file to be imported where it's
#  needed.
WEBSOCKET_STATUS_URL = "sock_choose_files"
WEBSOCKET_ERR_FILE_EMPTY = "ERR_FILE_EMPTY"
WEBSOCKET_ERR_FILE_MISSING = "ERR_FILE_MISSING"
WEBSOCKET_ERR_PARSE_FAILURE = "ERR_PARSE_FAILURE"
WEBSOCKET_ERR_UNEXPECTED = "ERR_UNEXPECTED"


@server.route('/')
def index():
    return "Hello, World!"


@server.route('/test-socket/<socket_name>')
def test_socket(socket_name):
    """Page used for debugging WebSockets.

    TODO: Remove as this is only a test.

    :param socket_name: The name of the socket endpoint to debug.
    :return: The HTML source.
    """
    return """<!doctype html>
<html>
  <head>
    """ + \
           f"<title>Socket: {socket_name}</title>" + \
           """<script src="https://code.jquery.com/jquery-3.6.0.min.js" 
    integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" 
    crossorigin="anonymous"></script>
  </head>
  <body>
    """ + \
           f"<h1>Socket: {socket_name}</h1>" + \
           """    <div id="log"></div>
    <br>
    <form id="form">
      <label for="text">Input: </label>
      <input type="text" id="text" autofocus>
    </form>
    <script>
$( document ).ready(function() {
    const log = (text, color) => {
        document.getElementById('log').innerHTML += 
        `<span style="color: ${color}">${text}</span><br>`;
    };
    
    """ + \
           f"const socket = " \
           f"new WebSocket('ws://' + location.host + '/{socket_name}');" + \
           """
    
    socket.addEventListener('message', ev => {
        log('<<< ' + ev.data, 'blue');
    });
    document.getElementById('form').onsubmit = ev => {
        ev.preventDefault();
        const textField = document.getElementById('text');
        log('>>> ' + textField.value, 'red');
        socket.send(textField.value);
        textField.value = '';
    };
});
    </script>
  </body>
</html>"""


@server.route('/api/list_files', methods=['POST'])
def post_list_files():
    """List files in the standard directory or from the specified sub
    directory.

    :return: The file list in JSON.
    """
    content = request.json
    file_list = list_files(content['sub_dir'])

    if 'sock_list_files' in shared_socket_handlers:
        shared_socket_handlers["sock_list_files"].\
            send("All the files were read!")

    return jsonify(file_list)


@server.route('/api/choose_files', methods=['POST'])
def post_choose_files():
    """Chose the selected files and begin the process of analyzing the files.

    :return: The number of files to analyze in JSON.
    """
    content = request.json
    file_list = content["chosenFiles"]
    project_root = content["pathToProject"]

    thread = Thread(
        target=analyze_files,
        args=(file_list, project_root, shared_socket_handlers))

    thread.start()

    return_data = {
        "status": "OK",
        "numberOfFiles": len(file_list)
    }

    return jsonify(return_data)


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
    :return: Nothing
    """
    shared_socket_handlers["sock_list_files"] = sock
    while True:
        data = sock.receive()
        sock.send(data)


@socket.route(f'/{WEBSOCKET_STATUS_URL}')
def sock_choose_files(sock):
    """WebSocket for 'choose_files' api. Listeners to this sockets will know
    about events during the analysis of the selected files.

    :param sock: The instantiated socket to communicate over.
    :return: Nothing
    """
    shared_socket_handlers[WEBSOCKET_STATUS_URL] = sock
    while True:
        # TODO: Should not act as an echo server later..
        data = sock.receive()
        sock.send(data)
