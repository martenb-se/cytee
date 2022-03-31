from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import ConnectionFailure
from pprint import pprint


# Todo: Add error handler that can revert changes and such if error occurs.
# Todo: Check if the object is connected to a database, and disconnect it if
#  that's the case.
# Todo: Set the client, database values to None.
# Todo: Raise another exception.
class TestDatabase:
    """
    Test database class
    """

    client = None
    database = None
    db_url = None

    def __init__(self, url: str):
        """
        Creates an instance of the TestDatabase class.

        :param url: url where the database is located.
        """
        if not isinstance(url, str):
            raise TypeError("url should be a string.")
        if len(url) <= 0:
            raise ValueError("Can't send empty string.")
        self.db_url = url
        return

    def connect_to_db(self) -> None:
        """
        Connects to the mongoDB database

        :return:
        """
        if self.client is not None or self.database is not None:
            raise RuntimeError('Try to connect while already connected')
        try:
            self.client = MongoClient(self.db_url)
            self.client.admin.command('ismaster')
        except ConnectionFailure as exc:
            raise RuntimeError('Failed to open database') from exc
        self.database = self.client.urangutest
        return

    def disconnect_from_db(self) -> None:
        """
        Disconnects from database if it's running.
        :return:
        """
        if self.client is None or self.database is None:
            raise RuntimeError('Try to close non existing connection')

        self.client.close()
        self.client = None
        self.database = None
        return

    def __app_to_db_string_conv(self, in_string: str) -> str:
        """
        Returns a string copy of the given string that can be stored in the
        database. "/" characters are converted to "|" and "." is converted to
        ":".

        :param in_string: given string to be converted.
        :return: string suitable for mongoDB.
        """
        in_string = in_string.replace('/', '|')
        in_string = in_string.replace('.', ':')
        return in_string

    def __db_to_app_string_conv(self, in_string: str) -> str:
        """
        converts a string that has been stored in the database (and therefore
        conforms to mongoDBs naming restrictions) to a string that can be used
        in the application.

        :param in_string: given string to be converted.
        :return: string suitable for the application.
        """

        in_string = in_string.replace('|', '/')
        in_string = in_string.replace(':', '.')
        return in_string

    # Todo: Maybe include hash in the list.
    def __func_info_app_to_db_data_conv(self, function_info):
        """
        Converts certain strings in the function_info object to conform to
        the mongoDB naming restrictions.

        :param function_info:
        :return:
        """
        for item in ['pathToProject', 'pathToFile', 'fileName', 'pathToCache']:
            function_info[item] = self.__app_to_db_string_conv(
                function_info[item])
        return function_info

    # Todo: Maybe include hash in the list.
    def __func_info_db_to_app_data_conv(self, function_info):
        """
        Converts certain strings in the function_info object so they can be
        used in the rest of the application.

        :param function_info: object containing information about a function.
        :return: no return value.
        """
        for item in ['pathToProject', 'pathToFile', 'fileName', 'pathToCache']:
            function_info[item] = self.__app_to_db_string_conv(
                function_info[item])
        return function_info

    # Todo: Check that the function_info is valid.
    # Todo: Check that the function was added successfully to the database.
    def add_function_info(self, function_info):
        """
        Adds function data to the database
        :return:
        """
        db_function_info = self.__func_info_app_to_db_data_conv(function_info)
        self.database.function_info.insert_one(db_function_info)
        return

    def get_function_info(self, id):
        db_function_info = self.database.function_info.find_one({"_id":id})
        return self.__func_info_db_to_app_data_conv(db_function_info)
