import json
from enum import Enum
from json import JSONDecodeError

import simple_websocket
from api.instances.logging_standard import logging
from typing import Callable


class WsIdentity(Enum):
    LIST_FILES = "list_files"
    NEW_PROJECT = "new_project"


class WsCategory(Enum):
    PROGRESS = "progress"
    SUCCESS = "success"
    ERROR = "error"


class WsStatus(Enum):
    OK = "OK"
    ERROR = "ERROR"


class WsCode(Enum):
    DONE = "DONE"
    WELCOME = "WELCOME"

    ANALYZE_ERR_FILE_EMPTY = "ANALYZE_ERR_FILE_EMPTY"
    ANALYZE_ERR_PARSE_FAILURE = "ANALYZE_ERR_PARSE_FAILURE"
    ANALYZE_ERR_UNEXPECTED = "ANALYZE_ERR_UNEXPECTED"
    ANALYZE_ERR_CLIENT_STOP = "ANALYZE_ERR_CLIENT_STOP"

    ANALYZE_PROCESS_FILES = "ANALYZE_PROCESS_FILES"
    ANALYZE_CLEAN_DEPENDENCY = "ANALYZE_CLEAN_DEPENDENCY"
    ANALYZE_COUNT_DEPENDENCY = "ANALYZE_COUNT_DEPENDENCY"

    ANALYZE_COMPLETE = "ANALYZE_COMPLETE"

    # TODO: Remove this constant only used for testing purposes.
    FILE_LIST_LOOP_FILES = "FILE_LIST_LOOP_FILES"
    FILE_LIST_COMPLETE = "FILE_LIST_COMPLETE"
    FILE_LIST_FAILURE = "FILE_LIST_FAILURE"


class WsClientCode(Enum):
    ANALYZE_STOP = "ANALYZE_STOP"


class SharedWebsockets:
    __MAX_SAVED_MESSAGES = 10

    def __init__(self):
        """Used for sharing of WebSocket instances."""
        self.websockets = {}
        self.receive_history = {}
        self.receive_listener = {}

    def __send_message_to_socket(
            self,
            identifier: WsIdentity,
            socket_index: int,
            socket: simple_websocket.ws.Server,
            message_category: str,
            message_contents: dict):
        try:
            socket.send(json.dumps(message_contents))
            logging.info(
                f"SharedWebsockets: Sent '{message_category}' "
                "message to client: "
                f"{socket.environ['REMOTE_ADDR']}:"
                f"{socket.environ['REMOTE_PORT']}")

        except simple_websocket.ConnectionClosed:
            self.websockets[identifier.value].pop(socket_index)

            logging.info(
                "SharedWebsockets: Connection was closed by client: "
                f"{socket.environ['REMOTE_ADDR']}:"
                f"{socket.environ['REMOTE_PORT']}. "
                "Removed shared socket connection")

    def keep_alive(
            self,
            identifier: WsIdentity,
            socket: simple_websocket.ws.Server):
        """Keep the specified socket alive and log received messages to
        the specified identifier.

        :param identifier: The socket identity.
        :type identifier: WsIdentity
        :param socket: The specific socket instance.
        :type socket: simple_websocket.ws.Server
        :return: Nothing
        """
        self.send_welcome_to_socket(socket)

        while socket.connected:
            received_raw = socket.receive(timeout=10)
            if received_raw is not None:
                try:
                    received = json.loads(received_raw)

                    previous_messages = \
                        self.receive_history[identifier.value][
                         :(self.__MAX_SAVED_MESSAGES - 1)]
                    new_message = {
                        **received,
                        "_clientId":
                            f"{socket.environ['REMOTE_ADDR']}:"
                            f"{socket.environ['REMOTE_PORT']}"}

                    self.receive_history[identifier.value] = \
                        [new_message] + previous_messages

                    if identifier.value in self.receive_listener:
                        for callback in \
                                self.receive_listener[identifier.value]:
                            callback(new_message)

                except JSONDecodeError as e:
                    logging.warning(
                        f"Could not decode JSON from client "
                        f"({socket.environ['REMOTE_ADDR']}:"
                        f"{socket.environ['REMOTE_PORT']}). Received data:\n"
                        f"{received_raw}\nError message from parser:\n{e}")

        logging.info(
            "SharedWebsockets: Connection no longer open to client: "
            f"{socket.environ['REMOTE_ADDR']}:"
            f"{socket.environ['REMOTE_PORT']}. "
            "Will no longer wait for messages")

    def add_listener_message(
            self,
            identifier: WsIdentity,
            callback: Callable[[dict], None]):
        """Add a listener to specified socket identity, multiple listeners
        may be added to the same identity.

        :param identifier: The socket identity.
        :type identifier: WsIdentity
        :param callback: Callback function if data is received.
        :type callback: Callable[[dict], None]

        :return:
        """
        if identifier.value not in self.receive_listener:
            self.receive_listener[identifier.value] = [callback]
        else:
            self.receive_listener[identifier.value].append(callback)

    def add_socket(
            self,
            identifier: WsIdentity,
            socket: simple_websocket.ws.Server
    ) -> None:
        """Add a shared socket to specified identity, multiple sockets
        may be added to the same identity.

        :param identifier: The socket identity.
        :type identifier: WsIdentity
        :param socket: The specific socket instance.
        :type socket: simple_websocket.ws.Server
        :return: Nothing
        """
        if not isinstance(identifier, WsIdentity):
            raise TypeError(
                "'identifier' must be of type WsIdentity, "
                f"not {type(identifier)}")

        if not isinstance(socket, simple_websocket.ws.Server):
            raise TypeError(
                "'socket' must be of type simple_websocket.ws.Server, "
                f"not {type(socket)}")

        if identifier.value not in self.websockets:
            self.websockets[identifier.value] = [socket]
            self.receive_history[identifier.value] = []

            logging.info(
                "SharedWebsockets: Added new socket identifier: "
                f"'{identifier.value}'")

        else:
            self.websockets[identifier.value].append(socket)

        logging.info(
            "SharedWebsockets: Added client: "
            f"{socket.environ['REMOTE_ADDR']}:"
            f"{socket.environ['REMOTE_PORT']} "
            f"to socket identifier '{identifier.value}'")

    def send_welcome_to_socket(
            self,
            socket: simple_websocket.ws.Server
    ) -> None:
        socket.send(json.dumps({
            "status": WsStatus.OK.value,
            "statusCode": WsCode.WELCOME.value,
            "message":
                f"Welcome {socket.environ['REMOTE_ADDR']}:"
                f"{socket.environ['REMOTE_PORT']}"
        }))

    def send_progress(
            self,
            identifier: WsIdentity,
            ws_code: WsCode,
            current_number: int,
            goal_number: int = 100,
            message: str = ""
    ) -> None:
        """Send progress message to socket(s) registered under specified
        identifier.

        :param identifier: WebSocket identifier for socket to send message to.
        :type identifier: WsIdentity
        :param ws_code: WebSocket status code to send with the message.
        :type ws_code: WsCode
        :param current_number: The current progress number to send. If goal
        number is not set, this number should be seen as a percentage.
        :type current_number: int
        :param goal_number: The goal progress number to send. By default this
        is set to 100 meaning the progress is meant to be seen as a percentage.
        :type goal_number: int
        :param message: Extra message info to send whenever necessary.
        :type message: str
        :return:
        """
        if identifier.value in self.websockets:
            for socket_index, current_socket in \
                    enumerate(self.websockets[identifier.value]):
                self.__send_message_to_socket(
                    identifier,
                    socket_index,
                    current_socket,
                    WsCategory.PROGRESS.value,
                    {
                        "status": WsStatus.OK.value,
                        "statusCode": ws_code.value,
                        "currentNumber": current_number,
                        "goalNumber": goal_number,
                        "message": message
                    }
                )

    def send_success(
            self,
            identifier: WsIdentity,
            ws_code: WsCode,
            message: str = ""
    ) -> None:
        """Send success message to socket(s) registered under specified
        identifier.

        :param identifier: WebSocket identifier for socket to send message to.
        :type identifier: WsIdentity
        :param ws_code: WebSocket status code to send with the message.
        :type ws_code: WsCode
        :param message: Extra message info to send whenever necessary.
        :type message: str
        :return:
        """
        if identifier.value in self.websockets:
            for socket_index, current_socket in \
                    enumerate(self.websockets[identifier.value]):
                self.__send_message_to_socket(
                    identifier,
                    socket_index,
                    current_socket,
                    WsCategory.SUCCESS.value,
                    {
                        "status": WsStatus.OK.value,
                        "statusCode": ws_code.value,
                        "message": message
                    }
                )

    def send_error(
            self,
            identifier: WsIdentity,
            ws_code: WsCode,
            message: str = ""
    ) -> None:
        """Send error message to socket(s) registered under specified
        identifier.

        :param identifier: WebSocket identifier for socket to send message to.
        :type identifier: WsIdentity
        :param ws_code: WebSocket status code to send with the message.
        :type ws_code: WsCode
        :param message: Extra message info to send whenever necessary.
        :type message: str
        :return:
        """
        if identifier.value in self.websockets:
            for socket_index, current_socket in \
                    enumerate(self.websockets[identifier.value]):
                self.__send_message_to_socket(
                    identifier,
                    socket_index,
                    current_socket,
                    WsCategory.ERROR.value,
                    {
                        "status": WsStatus.ERROR.value,
                        "statusCode": ws_code.value,
                        "message": message
                    }
                )
