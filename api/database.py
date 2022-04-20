from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import ConnectionFailure
from pprint import pprint
from pathlib import Path

import yaml

FUNCTION_INFO_COLLECTION = 'functionInfo'
TEST_INFO_COLLECTION = 'testInfo'
FUNCTION_DEPENDENCY_COLLECTION = 'functionDependency'


def __check_for_valid_string(in_arg: str) -> bool:
    """Checks if a given string is valid for being put in the database.

    :param in_arg: The string to be checked

    :return: Boolean value indicating if the given string is valid
    """
    return len(in_arg) > 0


def __check_for_valid_number(in_arg: int) -> bool:
    """Checks if a given number is valid for being put in the database.

    :param in_arg: tThe int to be checked

    :return: Boolean value indicating if the given int is valid
    """
    return in_arg >= 0


def __check_for_valid_id_string(in_arg: str) -> bool:
    """Checks if a given string id is valid for being put in the database.

    :param in_arg: The id, represented as a string, to be checked

    :return: Boolean value indicating if the given int is valid
    """
    return len(in_arg) == 24


def __check_for_valid_function_range(in_arg: tuple):
    return __check_for_valid_number(in_arg[0]) \
           and __check_for_valid_number(in_arg[1])


def __check_for_valid_export_info(in_arg):
    return in_arg in ['export', 'export default', 'private']


def __check_for_valid_arguments(in_arg: list):
    for func_args in in_arg:
        for args in func_args.items():
            for arg_name in args:
                __check_for_valid_string(arg_name)


def __app_to_db_string_conv(in_string: str) -> str:
    """Returns a string copy of the given string that can be stored in the
    database. "/" characters are converted to "|" and "." is converted to
    ":".

    :param in_string: Given string to be converted.

    :return: String suitable for mongoDB databases.
    """
    in_string = in_string.replace('/', '|')
    in_string = in_string.replace('.', ':')
    return in_string


def __db_to_app_string_conv(db_string: str) -> str:
    """converts a string that has been stored in the database (and
    therefore conforms to mongoDBs naming restrictions) to a string that
    can be used in the application.

    :param db_string: Given string to be converted.

    :return: String suitable for the application.
    """

    app_string = db_string.replace('|', '/')
    app_string = app_string.replace(':', '.')
    return app_string


def app_to_db_doc_conv(app_document, document_attribute_checker):
    db_document = app_document.copy()

    for attribute, value in db_document.items():
        if document_attribute_checker[attribute]['app_to_db_conv']:
            db_document[attribute] = document_attribute_checker[
                attribute]['app_to_db_conv'](value)

    return db_document


def db_to_app_doc_conv(db_document, document_attribute_checker):
    app_document = db_document.copy()

    for attribute, value in app_document.items():
        if document_attribute_checker[attribute]['db_to_app_conv']:
            app_document[attribute] = document_attribute_checker[
                attribute]['db_to_app_conv'](value)

    return app_document


def add_default_values(document, document_attribute_checker):
    for attribute_key in document_attribute_checker:
        if attribute_key not in document:
            if 'standard_value' in document_attribute_checker[attribute_key]:
                if attribute_key not in document:
                    document[attribute_key] = document_attribute_checker[
                        attribute_key][
                        'standard_value']


FUNCTION_INFO_ATTRIBUTE_CHECKER = {
    '_id': {
        'type': str,
        'cond': __check_for_valid_id_string,
        'app_to_db_conv': lambda app_data: ObjectId(app_data),
        'db_to_app_conv': lambda db_data: str(db_data)
    },
    'pathToProject': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'fileId': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'functionId': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'arguments': {
        'type': list,
        'cond': None,
        'app_to_db_conv': None,
        'db_to_app_conv': None
    },
    'functionRange': {
        'type': tuple,
        'cond': __check_for_valid_function_range,
        'app_to_db_conv': lambda app_data: [app_data[0], app_data[1]],
        'db_to_app_conv': lambda db_data: tuple(db_data)
    },
    'functionHash': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': None,
        'db_to_app_conv': None
    },
    'dependents': {
        'type': int,
        'cond': __check_for_valid_number,
        'app_to_db_conv': None,
        'db_to_app_conv': None,
        'standard_value': 0
    },
    'dependencies': {
        'type': int,
        'cond': __check_for_valid_number,
        'app_to_db_conv': None,
        'db_to_app_conv': None,
        'standard_value': 0
    },
    'numberOfTests': {
        'type': int,
        'cond': __check_for_valid_number,
        'app_to_db_conv': None,
        'db_to_app_conv': None,
        'standard_value': 0
    },
    'haveFunctionChanged': {
        'type': bool,
        'cond': None,
        'app_to_db_conv': None,
        'db_to_app_conv': None,
        'standard_value': False
    },
    'exportInfo': {
        'type': str,
        'cond': __check_for_valid_export_info,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'exportName': {
        'type': str,
        'cond': None,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    }
}

TEST_INFO_ATTRIBUTES_CHECKER = {
    '_id': {
        'type': str,
        'cond': __check_for_valid_id_string,
        'app_to_db_conv': lambda app_data: ObjectId(app_data),
        'db_to_app_conv': lambda db_data: str(db_data)
    },
    'pathToProject': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'fileId': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'functionId': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'customName': {
        'type': str,
        'cond': None,
        'app_to_db_conv': None,
        'db_to_app_conv': None
    },
    'moduleData': {
        'type': dict,
        'cond': None,
        'app_to_db_conv': None,
        'db_to_app_conv': None
    }
}

FUNCTION_DEPENDENCY_ATTRIBUTES_CHECKER = {
    '_id': {
        'type': str,
        'cond': __check_for_valid_id_string,
        'app_to_db_conv': lambda app_data: ObjectId(app_data),
        'db_to_app_conv': lambda db_data: str(db_data)
    },
    'pathToProject': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'fileId': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'functionId': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'calledFileId': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    },
    'calledFunctionId': {
        'type': str,
        'cond': __check_for_valid_string,
        'app_to_db_conv': __app_to_db_string_conv,
        'db_to_app_conv': __db_to_app_string_conv
    }
}


def check_valid_document_attributes(
        attribute_filter_value_dict: dict,
        attribute_property_checker: dict,
        *, strict_compare: bool = False
) -> None:
    for attribute_key, attribute_value in attribute_filter_value_dict.items():

        if not isinstance(attribute_key, str):
            raise TypeError(f"""
            All keys in the {attribute_filter_value_dict} should be strings but
            got a key of type {type(attribute_key)} with the corresponding
            value: {attribute_value}.""")

        if not __check_for_valid_string(attribute_key):
            raise ValueError(f"""
            A key in the {attribute_filter_value_dict}, with the corresponding
            value {attribute_value}, is an empty string.""")

        if attribute_key not in attribute_property_checker:
            raise ValueError(f"""
            The attribute key {attribute_key} isn't a valid attribute according
            to the attribute property checker.""")

        if not isinstance(
                attribute_value,
                attribute_property_checker[
                    attribute_key][
                    'type']):
            raise TypeError(f"""The value of the attribute {attribute_key},
                should be a {attribute_property_checker[attribute_key]['type']}
                type, but was given a value of type {
            type(attribute_value)}.""")

        if attribute_property_checker[
                attribute_key]['cond']:
            if not attribute_property_checker[
                    attribute_key][
                    'cond'](
                    attribute_value):
                raise ValueError(f"""
                Attribute {attribute_key} has the value {attribute_value} which 
                doesn't conform to the conditions for that attribute.""")

    if strict_compare:
        for item in attribute_property_checker:
            if item == '_id':
                continue
            if item not in attribute_filter_value_dict:
                raise ValueError(f"""
                The attribute {item} is missing form the given attribute
                attribute dictionary.""")


def _import_auth_info():
    path = Path(__file__).parent / "../db.config.yml"
    config = yaml.safe_load(path.open())
    return config


# Todo: Add error handler that can revert changes and such if error occurs.
class DatabaseHandler:
    """
    The DatabaseHandler class is used to communicate with the database
    """

    def __init__(self, url: str) -> None:
        """Initiates an instance of the DatabaseHandler class.

        :param url: The url at which the database resides

        :raises TypeError: If the given url isn't a string
        :raises ValueError: If the given url string is empty
        """

        self.client = None
        self.database = None
        self.db_url = None

        if not isinstance(url, str):
            raise TypeError("url should be a string.")
        if len(url) <= 0:
            raise ValueError("Can't send empty string.")
        self.db_url = url

        return

    def connect_to_db(self) -> None:
        """Connects to the database located att the url provided during the
        instantiation of the object.

        :return: No return value

        :raises RuntimeError: If the user tries to connect while already being
            connected. It can also be raised if the connection fails.
        """
        if self.client is not None or self.database is not None:
            raise RuntimeError('Try to connect while already connected')
        try:

            auth_info = _import_auth_info()

            self.client = MongoClient(
                self.db_url,
                username=auth_info['auth']['username'],
                password=auth_info['auth']['password'])

            self.client.admin.command('hello')
        except ConnectionFailure as exc:
            raise RuntimeError('Failed to open database') from exc
        self.database = self.client.urangutest
        return

    def disconnect_from_db(self) -> None:
        """Disconnects the instance from the database.

        :return: No return value

        :raises RuntimeError: If the instance tries to disconnect without
            being connected to a database.
        """
        if self.client is None or self.database is None:
            raise RuntimeError('Try to close non existing connection')

        self.client.close()
        self.client = None
        self.database = None
        return

    def __check_connection(self) -> None:
        """Checks if the instance is connected to a database.

        :return: No return value.

        :raises RuntimeError: If instance is not connected to a database.
        """
        if self.client is None and self.database is None:
            raise RuntimeError("""
                Tried to send query without connecting to database.
            """)

    def __get_query(
            self,
            /, collection: str,
            attribute_filter_dict: dict,
            attribute_property_checker: dict,
            *, query_function: any = None,
            act_on_first_match: bool = False
    ) -> any:

        self.__check_connection()

        check_valid_document_attributes(
            attribute_filter_dict,
            attribute_property_checker)

        db_attribute_filter_dict = app_to_db_doc_conv(
            attribute_filter_dict,
            attribute_property_checker)

        if not query_function:

            # TODO: Fix it so that is _id is only attribute then used find one.
            #   or maybe just change act_on_first_match accrdingly.

            if act_on_first_match or '_id' in attribute_filter_dict:
                db_documents = self.database[
                    collection] \
                    .find_one(
                    db_attribute_filter_dict)

                if not db_documents:
                    return None

                db_documents = [db_documents]
            else:
                db_documents = self.database[
                    collection] \
                    .find(
                    db_attribute_filter_dict)

            if not db_documents:
                return None

            ret_list = [
                db_to_app_doc_conv(docs, attribute_property_checker)
                for docs in db_documents]

            if len(ret_list) == 0:
                return None

            return ret_list
        else:
            return query_function(db_attribute_filter_dict)

    def __add_query(
            self,
            /, collection: str,
            document: any,
            attribute_property_checker: dict,
            *, query_function: any = None
    ) -> str:

        self.__check_connection()

        check_valid_document_attributes(
            document,
            attribute_property_checker,
            strict_compare=False)

        db_document = app_to_db_doc_conv(
            document,
            attribute_property_checker)

        add_default_values(db_document, attribute_property_checker)

        if not query_function:
            db_result = self.database[collection].insert_one(db_document)
            return str(db_result.inserted_id)
        else:
            return query_function(db_document)

    def __set_query(
            self,
            /, collection: str, updated_document_data: any,
            attribute_filter_dict: dict, attribute_property_checker: dict,
            *, query_function: any = None
    ) -> None:

        self.__check_connection()

        check_valid_document_attributes(
            attribute_filter_dict,
            attribute_property_checker)

        check_valid_document_attributes(
            updated_document_data,
            attribute_property_checker)

        db_updated_document = app_to_db_doc_conv(
            updated_document_data,
            attribute_property_checker)

        db_attribute_filter_dict = app_to_db_doc_conv(
            attribute_filter_dict,
            attribute_property_checker)

        if not query_function:
            self.database[collection].update_one(
                db_attribute_filter_dict,
                {'$set': db_updated_document})
        else:
            query_function(db_updated_document, db_attribute_filter_dict)

    def __remove_query(
            self,
            /, collection: str,
            attribute_filter_dict: dict,
            attribute_property_checker: dict,
            *, query_function: any = None,
            act_on_first_match: bool = False
    ) -> None:

        self.__check_connection()

        check_valid_document_attributes(
            attribute_filter_dict,
            attribute_property_checker)

        db_attribute_filter = app_to_db_doc_conv(
            attribute_filter_dict,
            attribute_property_checker)

        # TODO: make it so delete_one is called when attribute is the only
        #   ket in attribute_filter_dict
        if not query_function:
            if act_on_first_match:
                self.database[collection].delete_one(db_attribute_filter)
            else:
                self.database[collection].delete_many(db_attribute_filter)
        else:
            query_function(db_attribute_filter)

    def get_function_info(
            self,
            /, attribute_filter_dict: any,
    ) -> any:
        return self.__get_query(
            collection=FUNCTION_INFO_COLLECTION,
            attribute_filter_dict=attribute_filter_dict,
            attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    def get_test_info(
            self,
            /, attribute_filter_dict
    ) -> any:
        return self.__get_query(
            collection=TEST_INFO_COLLECTION,
            attribute_filter_dict=attribute_filter_dict,
            attribute_property_checker=TEST_INFO_ATTRIBUTES_CHECKER
        )

    def get_function_dependency(
            self,
            /, attribute_filter_dict
    ) -> any:
        return self.__get_query(
            collection=FUNCTION_DEPENDENCY_COLLECTION,
            attribute_filter_dict=attribute_filter_dict,
            attribute_property_checker=FUNCTION_DEPENDENCY_ATTRIBUTES_CHECKER
        )

    def add_function_info(self, function_info: any) -> str:
        return self.__add_query(
            collection=FUNCTION_INFO_COLLECTION,
            document=function_info,
            attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    def add_test_info(self, test_info: any) -> str:
        return self.__add_query(
            collection=TEST_INFO_COLLECTION,
            document=test_info,
            attribute_property_checker=TEST_INFO_ATTRIBUTES_CHECKER)

    def add_function_dependency(self, function_dependency):
        return self.__add_query(
            collection=FUNCTION_DEPENDENCY_COLLECTION,
            document=function_dependency,
            attribute_property_checker=FUNCTION_DEPENDENCY_ATTRIBUTES_CHECKER)

    def set_function_info(
            self,
            /, update_function_info: dict, attribute_filter_dict
    ) -> None:

        self.__set_query(
            collection=FUNCTION_INFO_COLLECTION,
            updated_document_data=update_function_info,
            attribute_filter_dict=attribute_filter_dict,
            attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER
        )

    def set_test_info(
            self,
            /, update_test_info: dict, attribute_filter_dict: dict
    ) -> None:

        self.__set_query(
            collection=TEST_INFO_COLLECTION,
            updated_document_data=update_test_info,
            attribute_filter_dict=attribute_filter_dict,
            attribute_property_checker=TEST_INFO_ATTRIBUTES_CHECKER
        )

    def set_function_dependency(
            self,
            /, update_function_dependency: dict, attribute_filter_dict: dict
    ) -> None:

        self.__set_query(
            collection=FUNCTION_DEPENDENCY_COLLECTION,
            updated_document_data=update_function_dependency,
            attribute_filter_dict=attribute_filter_dict,
            attribute_property_checker=FUNCTION_DEPENDENCY_ATTRIBUTES_CHECKER
        )

    def remove_function_info(
            self,
            /, attribute_filter_dict: dict
    ) -> None:

        self.__remove_query(
            collection=FUNCTION_INFO_COLLECTION,
            attribute_filter_dict=attribute_filter_dict,
            attribute_property_checker=FUNCTION_INFO_ATTRIBUTE_CHECKER)

    def remove_test_info(
            self,
            /, attribute_filter_dict: dict
    ) -> None:

        self.__remove_query(
            collection=TEST_INFO_COLLECTION,
            attribute_filter_dict=attribute_filter_dict,
            attribute_property_checker=TEST_INFO_ATTRIBUTES_CHECKER)

    def remove_function_dependency(
            self,
            /, attribute_filter_dict: dict,
    ) -> None:

        self.__remove_query(
            collection=FUNCTION_DEPENDENCY_COLLECTION,
            attribute_filter_dict=attribute_filter_dict,
            attribute_property_checker=FUNCTION_DEPENDENCY_ATTRIBUTES_CHECKER)
        