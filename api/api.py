import os
from enum import Enum
from api.analyzer.analyzer import analyze_files
from threading import Thread

from api.instances.database_main import database_handler
from api.instances.shared_websockets_main import shared_websockets_handler
from api.websocket import WsIdentity, WsCode


class APIStatus(Enum):
    OK = "OK"
    ERROR = "ERROR"


class APICode(Enum):
    ERROR_UNKNOWN = "ERROR_UNKNOWN"


def list_files(sub_dir):
    try:
        path_to_dir = os.path.dirname(os.path.abspath(__file__)) + "/" + sub_dir
        files = os.listdir(path_to_dir)
        file_list = [path_to_dir + "/" + f for f in files]

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
            "fileList": file_list
        }

    except Exception as e:
        # TODO: Remove this only used for testing purposes.
        shared_websockets_handler.send_error(
            WsIdentity.LIST_FILES,
            WsCode.FILE_LIST_FAILURE,
            f"Listing files failed. More info:\n{e}"
        )

        return_message = {
            "status": APIStatus.ERROR.value,
            "statusCode": APICode.ERROR_UNKNOWN.value
        }

    return return_message


def choose_files(path_to_project, list_of_files) -> dict:
    """Chose files

    :param path_to_project:
    :type path_to_project: str
    :param list_of_files:
    :type list_of_files: list[str]
    :return: JSON Data
    :rtype: dict
    """
    thread = Thread(
        target=analyze_files,
        args=(list_of_files, path_to_project))

    thread.start()

    return {
        "status": APIStatus.OK.value,
        "numberOfFiles": len(list_of_files)
    }


def choose_project(path_to_project) -> dict:
    """

    :param path_to_project: path to project
    :type path_to_project: str

    :return: JSON Data
    :rtype: dict
    """
    pass


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
        return '<!doctype html><html><head><title>Socket: Unavailable</title>'\
           '</head><body>'\
           '<h1>Socket: Unavailable</h1>' + \
           f'<p>Available sockets are: {", ".join(socket_links)}</p>' \
           '</body></html>'

    return '<!doctype html><html><head>'\
           f'<title>Socket: {socket_identifier}</title>'\
           '<script src="https://code.jquery.com/jquery-3.6.0.min.js" ' \
           'integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" ' \
           'crossorigin="anonymous"></script></head><body>'\
           f'<h1>Socket: {socket_identifier}</h1>' + \
           '<div id="log"></div><br><form id="form">' \
           '<label for="text">Input:</label>' \
           '<input type="text" id="text" autofocus></form>' \
           '<script>$( document ).ready(function() {const log = ' \
           '(text, color) => {document.getElementById("log").innerHTML += ' \
           '`<span style="color: ${color}">${text}</span><br>`;};' \
           'const socket = new WebSocket("ws://" + location.host + ' \
           f'"/{socket_identifier}");' + \
           'socket.addEventListener("message", ev => ' \
           '{log("<<< " + ev.data, "blue");});' \
           'document.getElementById("form").onsubmit = ev => ' \
           '{ev.preventDefault();const textField = ' \
           'document.getElementById("text");' \
           'log(">>> " + textField.value, "red");' \
           'socket.send(textField.value);textField.value = "";};});' \
           '</script></body></html>'
