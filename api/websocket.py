from enum import Enum
import simple_websocket
from api.instances.logging_standard import logging


class WsIdentity(Enum):
    LIST_FILES = "sock_list_files"
    CHOOSE_FILES = "sock_choose_files"


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

    ANALYZE_PROCESS_FILES = "ANALYZE_PROCESS_FILES"
    ANALYZE_CLEAN_DEPENDENCY = "ANALYZE_CLEAN_DEPENDENCY"
    ANALYZE_COUNT_DEPENDENCY = "ANALYZE_COUNT_DEPENDENCY"

    ANALYZE_COMPLETE = "ANALYZE_COMPLETE"

    # TODO: Remove this constant only used for testing purposes.
    FILE_LIST_LOOP_FILES = "FILE_LIST_LOOP_FILES"
    FILE_LIST_COMPLETE = "FILE_LIST_COMPLETE"
    FILE_LIST_FAILURE = "FILE_LIST_FAILURE"


class SharedWebsockets:
    def __init__(self):
        """Used for sharing of WebSocket instances."""
        self.websockets = {}

    def __sanity_check_identifier(self, identifier):
        if identifier.value not in self.websockets:
            raise ValueError(
                f"No socket with identifier '{identifier}' is registered")

    def __send_message_to_socket(
            self,
            identifier: WsIdentity,
            socket_index: int,
            socket: simple_websocket.ws.Server,
            message_category: str,
            message_contents: dict):
        try:
            socket.send(message_contents)
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
            socket: simple_websocket.ws.Server):

        self.send_welcome_to_socket(socket)

        while socket.connected:
            socket.receive(timeout=10)

        logging.info(
            "SharedWebsockets: Connection no longer open to client: "
            f"{socket.environ['REMOTE_ADDR']}:"
            f"{socket.environ['REMOTE_PORT']}. "
            "Will no longer wait for messages")

    def add_socket(
            self,
            identifier: WsIdentity,
            socket: simple_websocket.ws.Server
    ) -> None:
        """Add a shared socket to specified identity, multiple sockets
        may be added to the same identity.

        :param identifier:
        :type identifier: WsIdentity
        :param socket:
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
        socket.send({
            "status": WsStatus.OK.value,
            "statusCode": WsCode.WELCOME.value,
            "message":
                f"Welcome {socket.environ['REMOTE_ADDR']}:"
                f"{socket.environ['REMOTE_PORT']}"
        })

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
        # self.__sanity_check_identifier(identifier)

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
        # self.__sanity_check_identifier(identifier)

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
        # self.__sanity_check_identifier(identifier)

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
