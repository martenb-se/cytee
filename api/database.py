from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import ConnectionFailure
from functools import reduce


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


FUNCTION_INFO_ATTRIBUTE_CHECKER = {
    '_id': {'type': str, 'cond': __check_for_valid_id_string},
    'pathToProject': {'type': str, 'cond': __check_for_valid_string},
    'pathToFile': {'type': str, 'cond': __check_for_valid_string},
    'fileName': {'type': str, 'cond': __check_for_valid_string},
    'functionName': {'type': str, 'cond': __check_for_valid_string},
    'functionHash': {'type': str, 'cond': __check_for_valid_string},
    'pathToCache': {'type': str, 'cond': __check_for_valid_string},
    'dependents': {'type': int, 'cond': __check_for_valid_number},
    'dependencies': {'type': int, 'cond': __check_for_valid_number},
    'numberOfTests': {'type': int, 'cond': __check_for_valid_number},
    'haveFunctionChanged': {'type': bool, 'cond': None}
}
TEST_INFO_ATTRIBUTES_CHECKER = {
    '_id': {'type': str, 'cond': __check_for_valid_id_string},
    'pathToProject': {'type': str, 'cond': __check_for_valid_string},
    'fullPath': {'type': str, 'cond': __check_for_valid_string},
    'functionName': {'type': str, 'cond': __check_for_valid_string},
    'customName': {'type': str, 'cond': None},
    'moduleData': {'type': dict, 'cond': None}
}

FUNCTION_COUPLING_ATTRIBUTES_CHECKER = {
    '_id': {'type': str, 'cond': __check_for_valid_string},
    'function': {'type': str, 'cond': __check_for_valid_string},
    'dependentFunctions': {'type': list, 'cond': lambda in_arg: reduce(
        lambda x, y: x and y, in_arg, True)}
}

FUNCTION_INFO_BAD_ATTRIBUTES = ['pathToProject', 'pathToFile', 'fileName',
                                'pathToCache']
TEST_INFO_BAD_ATTRIBUTES = ['pathToProject', 'fullPath', 'functionName']
FUNCTION_COUPLING_BAD_ATTRIBUTES = ['function', 'dependentFunctions']


def check_valid_document_attribute(
        attribute: str,
        attribute_value: any,
        document_attribute_checker: dict
) -> None:
    """Checks is a given attribute is a valid attribute of a document.

    :param attribute: The attribute, represented as a string, that is being
        checked
    :param attribute_value: The value of the attribute
    :param document_attribute_checker: The dictionary that contains information
        about the type and condition that the attributes should conform to

    :return: No return value

    :raises ValueError: If given attribute isn't an attribute in the document
        specified by the document_attribute_checker, or if the value of the
        attribute_value doesn't conform to the condition specified by the
        document_attribute_checker
    :raises TypeError: If given attribute_value isn't the type that is
        specified in the document_attribute_checker
    """
    if attribute not in document_attribute_checker:
        raise ValueError(f"""
        The given document attribute {attribute} is not an valid
        attribute.""")

    if not isinstance(
            attribute_value,
            document_attribute_checker[attribute]['type']
    ):
        raise TypeError(f"""
         The {attribute} attribute's value should be {
        document_attribute_checker[attribute]['type']}, but was given a
         {type(attribute_value)} type.""")

    if document_attribute_checker[attribute]['cond'] and \
            not document_attribute_checker[attribute]['cond'](attribute_value):
        raise ValueError(f"""
        The value {attribute_value} of attribute {attribute} does 
        not conform to the constraints of the attribute.""")


def check_valid_document(
        document: dict,
        document_attribute_checker: dict
) -> None:
    """Checks that the document, specified by the document_attribute_checker is
    valid.

    :param document: The document to be checked
    :param document_attribute_checker: The dictionary that contains information
        about the type and condition that the attributes should conform to

    :return: No return value

    :raises TypeError: If document doesn't conform to
        document_attribute_checker
    :raises ValueError: If the value of any attribute in the document doesn't
        conform to document_attribute_checker
    """
    for attribute, attribute_value in document.items():
        check_valid_document_attribute(
            attribute,
            attribute_value,
            document_attribute_checker
        )


def check_valid_attribute_filter(
        attribute_filter: str,
        document_attribute_checker: dict
) -> None:
    """Checks if a given attribute filter conforms to the document attribute
    checker

    :param attribute_filter:  The attribute filter being checked
    :param document_attribute_checker: The dictionary that contains information
        about the type and condition that the attributes should conform to

    :return: No return value

    :raises TypeError: If document doesn't conform to
        document_attribute_checker
    :raises ValueError: If the value of any attribute in the document doesn't
        conform to document_attribute_checker
    """
    if not isinstance(attribute_filter, str):
        raise TypeError(f"""Filter attribute {attribute_filter} is not of type 
        str.""")

    if not __check_for_valid_string(attribute_filter):
        raise ValueError("""Filter attribute cant be an empty string """)

    if attribute_filter not in document_attribute_checker:
        raise ValueError("""Filter attribute is not a valid attribute""")


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
            self.client = MongoClient(self.db_url)
            self.client.admin.command('ismaster')
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

    def __app_to_db_string_conv(self, in_string: str) -> str:
        """Returns a string copy of the given string that can be stored in the
        database. "/" characters are converted to "|" and "." is converted to
        ":".

        :param in_string: Given string to be converted.

        :return: String suitable for mongoDB databases.
        """
        in_string = in_string.replace('/', '|')
        in_string = in_string.replace('.', ':')
        return in_string

    def __db_to_app_string_conv(self, db_string: str) -> str:
        """converts a string that has been stored in the database (and
        therefore conforms to mongoDBs naming restrictions) to a string that
        can be used in the application.

        :param db_string: Given string to be converted.

        :return: String suitable for the application.
        """

        app_string = db_string.replace('|', '/')
        app_string = app_string.replace(':', '.')
        return app_string

    def __function_info_app_to_db_conv(self, function_info: dict) -> dict:
        """Converts strings in the given function info object to conform to
        the mongoDB naming restrictions.

        :param function_info: The function info document representation to be
            converted.

        :return: Function info document suitable for mongoDB databases
        """

        for item in FUNCTION_INFO_BAD_ATTRIBUTES:
            if item in function_info:
                function_info[item] = self.__app_to_db_string_conv(
                    function_info[item])
        if '_id' in function_info:
            function_info['_id'] = ObjectId(function_info['_id'])
        return function_info

    def __test_info_app_to_db_conv(self, test_info: dict) -> dict:
        """Converts strings in the given test info object to conform to
         the mongoDB naming restrictions.

         :param test_info: The test info document representation to be
             converted.

         :return: Test info document suitable for mongoDB databases
         """

        for item in TEST_INFO_BAD_ATTRIBUTES:
            if item in test_info:
                test_info[item] = self.__app_to_db_string_conv(test_info[item])
        if '_id' in test_info:
            test_info['_id'] = ObjectId(test_info['_id'])
        return test_info

    def __function_coupling_app_to_db_conv(
            self,
            function_coupling: dict) -> dict:
        """Converts strings in the given function coupling object to conform to
         the mongoDB naming restrictions.

         :param function_coupling: The test info document representation to be
             converted.

         :return: Function coupling document suitable for mongoDB databases
         """
        if 'function' in function_coupling:
            function_coupling['function'] = self.__app_to_db_string_conv(
                function_coupling['function'])
        if 'dependentFunctions' in function_coupling:
            function_coupling['dependentFunctions'] = [
                self.__app_to_db_string_conv(item) for item in
                function_coupling['dependentFunctions']]
        if '_id' in function_coupling:
            function_coupling['_id'] = ObjectId(function_coupling['_id'])
        return function_coupling

    def __function_info_db_to_app_conv(self, function_info: dict) -> dict:
        """Converts strings in the given function info object in order to
        be used in the rest of the application.

        :param function_info: The function info document representation to be
            converted.

        :return: No return value.
        """

        for item in FUNCTION_INFO_BAD_ATTRIBUTES:
            if item in function_info:
                function_info[item] = self.__db_to_app_string_conv(
                    function_info[item])
        function_info['_id'] = str(function_info['_id'])

        return function_info

    def __test_info_db_to_app_conv(self, test_info: dict) -> dict:
        """Converts strings in the given test info object in order to
        be used in the rest of the application.

        :param test_info: The test info document representation to be
            converted.

        :return: No return value.
        """

        for item in TEST_INFO_BAD_ATTRIBUTES:
            if item in test_info:
                test_info[item] = self.__db_to_app_string_conv(test_info[item])
        test_info['_id'] = str(test_info['_id'])
        return test_info

    def __function_coupling_db_to_app_conv(
            self,
            function_coupling: dict) -> dict:
        """Converts strings in the given function coupling object in order to
         be used in the rest of the application.

         :param function_coupling: The function coupling document
            representation to be converted.

         :return: No return value.
         """
        if 'function' in function_coupling:
            function_coupling['function'] = self.__db_to_app_string_conv(
                function_coupling['function'])
        if 'dependentFunctions' in function_coupling:
            function_coupling['dependentFunctions'] = [
                self.__db_to_app_string_conv(item) for item in
                function_coupling['dependentFunctions']]
        function_coupling['_id'] = str(function_coupling['_id'])
        return function_coupling

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
            /, collection: str, attribute_value: any, attribute_dict: dict,
            bad_attribute_list: list, db_to_app_conv: any,
            *, document_attribute: str, query_function: any = None,
            act_on_first_match: bool = False
    ) -> any:
        """Sends a get query to connected database.

        :param collection:
            The collection from which the document should be
            fetched from.
        :param attribute_value:
            The value of the attribute that is used to
            identify the sought after document in the database.
        :param attribute_dict:
            A dictionary used to check that the given attribute_value and
            document_attribute conforms to the document type specified by the
            collection argument.
        :param bad_attribute_list:
            Contains a list of attribute that need to be
            converted before being used to query the database.
        :param db_to_app_conv:
            Function used to convert the resulting document in order to be used
            in the application.
        :param document_attribute:
            The attribute used to specify which attribute will be used to
            identify the sought after document in the database.
        :param query_function:
            An optional function that can be used to specify a custom query
            to the database.
        :param act_on_first_match:
            An optional argument that can be used to specify if only the first
            document that conforms to the query condition should be returned or
            if all documents that fulfills the query condition should be
            returned.

        :return: An list containing the documents corresponding to the given
            attribute_value and document_attribute value. If no document could
            be found, None is returned.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the given document_attribute isn't a valid string or if
            attribute_dict isn't a valid attribute document specified by the
            attribute_dict dictionary. It's also raised if the given
            attribute_value doesn't conform to the condition of the
            document_attribute which is also specified by the attribute_dict.
        :raises TypeError:
            If the given document_attribute isn't a string or if the given
            document_attribute's typ isn't equal to that specified by the
            attribute_dict for the given document_attribute.
        """

        self.__check_connection()
        check_valid_attribute_filter(document_attribute, attribute_dict)
        check_valid_document_attribute(
            document_attribute,
            attribute_value,
            attribute_dict
        )

        if document_attribute == '_id':
            db_attribute_value = ObjectId(attribute_value)
        elif document_attribute in bad_attribute_list:
            if isinstance(attribute_value, list):
                db_attribute_value = [self.__app_to_db_string_conv(attr_val)
                                      for attr_val in attribute_value]
            else:
                db_attribute_value = self.__app_to_db_string_conv(
                    attribute_value)
        else:
            db_attribute_value = attribute_value

        if not query_function:
            if act_on_first_match or (document_attribute == '_id'):
                db_documents = self.database[collection].find_one({
                    document_attribute: db_attribute_value
                })

                if not db_documents:
                    return None

                db_documents = [db_documents]
            else:
                db_documents = self.database[collection].find({
                    document_attribute: db_attribute_value
                })._compute_results()

            if not db_documents:
                return None

            return [db_to_app_conv(docs) for docs in db_documents]
        else:
            return query_function(db_attribute_value)

    def __query_add_one(
            self,
            /, collection: str, document: any, attribute_dict: dict,
            app_to_db_conv: any,
            *, query_function: any = None
    ) -> str:
        """Query that adds one document to the database.

        :param collection:
            The collection to which the document should be added.
        :param document:
            The document that should be added.
        :param attribute_dict:
            A dictionary used to check that the given document conforms to the
            document type specified by the collection argument.
        :param app_to_db_conv:
            A function used to convert the document in order to be stored in
            the database.
        :param query_function:
            An optional function that can be used to specify a custom query
            to the database.

        :return: The document id is returned as a string.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the document contains attribute that doesn't exist in the
            attribute_dict or if any of the attribute values doesn't
            conform the condition specified in the attribute_dict.
        :raises TypeError:
            If any of the attribute's values in the documents has an incorrect
            type.
        """

        self.__check_connection()
        check_valid_document(document, attribute_dict)

        db_document = app_to_db_conv(document.copy())

        if not query_function:
            db_result = self.database[collection].insert_one(db_document)
            return str(db_result.inserted_id)
        else:
            return query_function(db_document)

    def __query_set_one(
            self,
            /, collection: str, updated_document_data: any,
            filter_attribute: str, attribute_dict: dict, app_to_db_conv: any,
            bad_attribute_list: list,
            *, query_function: any = None, filter_attribute_value: any = None
    ) -> None:
        """Query that updates a document in the database.

        :param collection:
            The collection containing the element that should be updated.
        :param updated_document_data:
            The updated document data.
        :param filter_attribute:
            The document used to specify which document should be updated.
        :param attribute_dict:
            A dictionary used to check that the given updated document and
             filer_attribute conforms to the document type specified by the
             collection argument.
        :param app_to_db_conv:
            Function used to convert the resulting document in order to be used
            in the application.
        :param bad_attribute_list:
            Contains a list of attribute that need to be converted before being
            used to query the database.
        :param query_function:
            An optional function that can be used to specify a custom query
            to the database.
        :param filter_attribute_value:
            An optional value that is used if the data used to search for the
            document isn't included in the updated document data.

        :return: No return value.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises TypeError:
            If the types of the attribute values in the updated document is
            invalid or if the filter_attribute_value is invalid according to
            the attribute_dict.
        : raises ValueError:
            If the values in the updated documents or
            the filter_attribute_value are invalid according to the
            attribute_dict.
        """

        self.__check_connection()
        check_valid_attribute_filter(filter_attribute, attribute_dict)
        check_valid_document(updated_document_data, attribute_dict)

        db_document = app_to_db_conv(updated_document_data.copy())

        if not filter_attribute_value:
            db_document_filter = db_document[filter_attribute]
        else:
            check_valid_document_attribute(
                filter_attribute,
                filter_attribute_value,
                attribute_dict)

            if filter_attribute == '_id':
                db_document_filter = ObjectId(filter_attribute_value)
            elif filter_attribute in bad_attribute_list:
                db_document_filter = self.__app_to_db_string_conv(
                    filter_attribute_value)
            else:
                db_document_filter = filter_attribute_value

        if not query_function:
            self.database[collection].update_one(
                {filter_attribute: db_document_filter},
                {'$set': db_document})
        else:
            query_function(db_document, filter_attribute, db_document_filter)

    def __query_remove_one(
            self,
            /, collection: str, filter_attribute: str,
            filter_attribute_value: any, attribute_dict: dict,
            bad_attribute_list: any,
            *, query_function: any = None, act_on_first_match: bool = True
    ) -> None:
        """Removes one or more documents from the database.

        :param collection:
            The collection in which the document to be removed resides.
        :param filter_attribute:
            The attribute used to indentify the document to be removed.
        :param filter_attribute_value:
            The value of the filter attribute.
        :param attribute_dict:
            A dictionary used to check that the given updated document and
             filer_attribute conforms to the document type specified by the
             collection argument.
        :param bad_attribute_list:
            Contains a list of attribute that need to be converted before being
            used to query the database.
        :param query_function:
            An optional function that can be used to specify a custom query
            to the database.
        :param act_on_first_match:
            An optional argument that, is set to true, will only remove the
            first found document that conforms to the query. If it's set to
            false, then all documents found by the query will be removed.

        :return: No return value

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the filter_attribute isn't in attribute_dict or the
            filter_attribute_value doesn't conform to the attribute_dict.
        :raises TypeError:
            If the type of the filter_attribute or filter_attribute_value are
            invalid.

        """

        self.__check_connection()
        check_valid_attribute_filter(filter_attribute, attribute_dict)
        check_valid_document_attribute(
            filter_attribute,
            filter_attribute_value,
            attribute_dict
        )

        if filter_attribute == '_id':
            db_attribute_filter = ObjectId(filter_attribute_value)
        elif filter_attribute in bad_attribute_list:
            if isinstance(filter_attribute_value, list):
                db_attribute_filter = [self.__app_to_db_string_conv(attr_val)
                                       for attr_val in filter_attribute_value]
            else:
                db_attribute_filter = self.__app_to_db_string_conv(
                    filter_attribute_value)
        else:
            db_attribute_filter = filter_attribute_value

        if not query_function:
            if act_on_first_match:
                self.database[collection].delete_one({
                    filter_attribute: db_attribute_filter})
            else:
                self.database[collection].delete_many({
                    filter_attribute: db_attribute_filter})
        else:
            query_function(filter_attribute, db_attribute_filter)

    def get_function_info(
            self,
            /, attribute_value: any,
            *, document_attribute: str = '_id'
    ) -> any:
        """Returns one or more function info documents from the database based
        on the given attribute value.

        :param attribute_value:
            Value of the document attribute used to identify the document in
            the database
        :param document_attribute:
            The document attribute that used to indentify the document in the
            database.

        :return: An array containing the found documents.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the value of attribute_value is invalid for the corresponding
            document_attribute, or if the document_attribute isn't a string.
        """
        return self.__get_query(
            collection='function_info',
            attribute_value=attribute_value,
            attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
            bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
            db_to_app_conv=self.__function_info_db_to_app_conv,
            document_attribute=document_attribute
        )

    def get_test_info(
            self,
            /, attribute_value: any,
            *, document_attribute: str = '_id'
    ) -> any:
        """Returns one or more test info documents from the database based
        on the given attribute value.

        :param attribute_value:
            Value of the document attribute used to identify the document in
            the database
        :param document_attribute:
            The document attribute that used to indentify the document in the
            database.

        :return: An array containing the found documents.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the value of attribute_value is invalid for the corresponding
            document_attribute, or if the document_attribute isn't a string.
        """
        return self.__get_query(
            collection='test_info',
            attribute_value=attribute_value,
            attribute_dict=TEST_INFO_ATTRIBUTES_CHECKER,
            bad_attribute_list=TEST_INFO_BAD_ATTRIBUTES,
            db_to_app_conv=self.__test_info_db_to_app_conv,
            document_attribute=document_attribute
        )

    def get_function_coupling(
            self,
            /, attribute_value: any,
            *, document_attribute: str = '_id'
    ) -> any:
        """Returns one or more function coupling documents from the database
        based on the given attribute value.

        :param attribute_value:
            Value of the document attribute used to identify the document in
            the database
        :param document_attribute:
            The document attribute that used to indentify the document in the
            database.

        :return: An array containing the found documents.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the value of attribute_value is invalid for the corresponding
            document_attribute, or if the document_attribute isn't a string.
        """
        if document_attribute == 'dependentFunctions':
            def dependent_function_query(db_attribute_value):
                db_documents = self.database['coupling'].find({
                    'dependentFunctions': db_attribute_value[0]
                })
                if not db_documents:
                    return None

                return [self.__db_to_app_string_conv(docs['function']) for docs
                        in db_documents]

            return self.__get_query(
                collection='coupling',
                attribute_value=attribute_value,
                attribute_dict=FUNCTION_COUPLING_ATTRIBUTES_CHECKER,
                bad_attribute_list=FUNCTION_COUPLING_BAD_ATTRIBUTES,
                db_to_app_conv=self.__function_coupling_db_to_app_conv,
                document_attribute=document_attribute,
                query_function=dependent_function_query
            )
        else:
            return self.__get_query(
                collection='coupling',
                attribute_value=attribute_value,
                attribute_dict=FUNCTION_COUPLING_ATTRIBUTES_CHECKER,
                bad_attribute_list=FUNCTION_COUPLING_BAD_ATTRIBUTES,
                db_to_app_conv=self.__function_coupling_db_to_app_conv,
                document_attribute=document_attribute
            )

    def add_function_info(self, function_info: any) -> str:
        """Adds a function info document to the database.

        :param function_info:
            The document that should be added to the database.

        :return:
           The document id represented as a string.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the values of the attributes in the function_info document
            doesn't conform to the document types condition.
        :raises TypeError:
            If the types of the attribute values in the function_info document
            doesn't conform to the document attribute values specifications.
        """
        return self.__query_add_one(
            'function_info',
            function_info,
            FUNCTION_INFO_ATTRIBUTE_CHECKER,
            self.__function_info_app_to_db_conv
        )

    def add_test_info(self, test_info: any) -> str:
        """Adds a test info document to the database.

        :param test_info:
            The document that should be added to the database.

        :return:
            The document id represented as a string.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the values of the attributes in the test_info document
            doesn't conform to the document types condition.
        :raises TypeError:
            If the types of the attribute values in the test_info document
            doesn't conform to the document attribute values specifications.
        """
        return self.__query_add_one(
            'test_info',
            test_info,
            TEST_INFO_ATTRIBUTES_CHECKER,
            self.__test_info_app_to_db_conv
        )

    def add_function_coupling(self, function_coupling: any) -> str:
        """Adds a function coupling document to the database.

        :param function_coupling:
            The document that should be added to the database.

        :return:
            The document id represented as a string.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the values of the attributes in the function_coupling document
            doesn't conform to the document types condition.
        :raises TypeError:
            If the types of the attribute values in the function_coupling
            document doesn't conform to the document attribute values
            specifications.
        """
        return self.__query_add_one(
            'coupling',
            function_coupling,
            FUNCTION_COUPLING_ATTRIBUTES_CHECKER,
            self.__function_coupling_app_to_db_conv
        )

    def set_function_info(
            self,
            /, update_function_info: any,
            *, filter_attribute: any = '_id', filter_attribute_value=None
    ) -> None:
        """Updates the value of a function info document.

        :param update_function_info:
            Contains the updated function info data.
        :param filter_attribute:
            The attribute used to locate the document in the database.
        :param filter_attribute_value:
            The value of filter_attribute.

        :return: No return value.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the value of filter_attribute_value, the values in the
             update_function_info, or the filter_attribute are invalid.
        :raises TypeError:
            If the type of filter_attribute_value, the values in the
             update_function_info, or the filter_attribute are invalid.
        """
        self.__query_set_one(
            collection='function_info',
            updated_document_data=update_function_info,
            filter_attribute=filter_attribute,
            attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
            app_to_db_conv=self.__function_info_app_to_db_conv,
            filter_attribute_value=filter_attribute_value,
            bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES
        )

    def set_test_info(
            self,
            /, update_test_info: any,
            *, filter_attribute: any = '_id', filter_attribute_value=None
    ) -> None:
        """Updates the value of a test info document.

        :param update_test_info:
            Contains the updated test info data.
        :param filter_attribute:
            The attribute used to locate the document in the database.
        :param filter_attribute_value:
            The value of filter_attribute.

        :return: No return value.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the value of filter_attribute_value, the values in the
             update_test_info, or the filter_attribute are invalid.
        :raises TypeError:
            If the type of filter_attribute_value, the values in the
             update_test_info, or the filter_attribute are invalid.
        """
        self.__query_set_one(
            collection='test_info',
            updated_document_data=update_test_info,
            filter_attribute=filter_attribute,
            attribute_dict=TEST_INFO_ATTRIBUTES_CHECKER,
            app_to_db_conv=self.__test_info_app_to_db_conv,
            filter_attribute_value=filter_attribute_value,
            bad_attribute_list=TEST_INFO_BAD_ATTRIBUTES
        )

    def set_function_coupling(
            self,
            /, update_function_coupling: any,
            *, filter_attribute: any = '_id', filter_attribute_value=None
    ) -> None:
        """Updates the value of a function coupling document.

        :param update_function_coupling:
            Contains the updated test info data.
        :param filter_attribute:
            The attribute used to locate the document in the database.
        :param filter_attribute_value:
            The value of filter_attribute.

        :return: No return value.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the value of filter_attribute_value, the values in the
             update_function_coupling, or the filter_attribute are invalid.
        :raises TypeError:
            If the type of filter_attribute_value, the values in the
             update_function_coupling, or the filter_attribute are invalid.
        """
        self.__query_set_one(
            collection='coupling',
            updated_document_data=update_function_coupling,
            filter_attribute=filter_attribute,
            attribute_dict=FUNCTION_COUPLING_ATTRIBUTES_CHECKER,
            app_to_db_conv=self.__function_coupling_app_to_db_conv,
            filter_attribute_value=filter_attribute_value,
            bad_attribute_list=FUNCTION_COUPLING_BAD_ATTRIBUTES
        )

    def delete_function_info(
            self,
            /, filter_attribute_value: any,
            *, filter_attribute: str = '_id', act_on_first_match: bool = True
    ) -> None:
        """Removes a function info document from the database.

        :param filter_attribute_value:
            The value of filter_attribute.
        :param filter_attribute:
            The attribute used to locate the document in the database.
        :param act_on_first_match:
            If this is set to ture, then only the first found document will be
            deleted. If it's set to false, then all fund documents will be
            deleted.

        :return: No return value.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the given filter_attribute_value is invalid or if
            filter_attribute isn̈́'t part of the document type.
        :raises TypeError:
            If the type of filter_attribute_value is invalid or
            if filter_attribute isn't a string.
        """
        self.__query_remove_one(
            collection='function_info',
            filter_attribute=filter_attribute,
            filter_attribute_value=filter_attribute_value,
            attribute_dict=FUNCTION_INFO_ATTRIBUTE_CHECKER,
            bad_attribute_list=FUNCTION_INFO_BAD_ATTRIBUTES,
            act_on_first_match=act_on_first_match
        )

    def delete_test_info(
            self,
            /, filter_attribute_value: any,
            *, filter_attribute: str = '_id', act_on_first_match: bool = True
    ) -> None:
        """Removes a test info document from the database.

        :param filter_attribute_value:
            The value of filter_attribute.
        :param filter_attribute:
            The attribute used to locate the document in the database.
        :param act_on_first_match:
            If this is set to ture, then only the first found document will be
            deleted. If it's set to false, then all fund documents will be
            deleted.

        :return: No return value.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the given filter_attribute_value is invalid or if
            filter_attribute isn̈́'t part of the document type.
        :raises TypeError:
            If the type of filter_attribute_value is invalid or
            if filter_attribute isn't a string.
        """
        self.__query_remove_one(
            collection='test_info',
            filter_attribute=filter_attribute,
            filter_attribute_value=filter_attribute_value,
            attribute_dict=TEST_INFO_ATTRIBUTES_CHECKER,
            bad_attribute_list=TEST_INFO_BAD_ATTRIBUTES,
            act_on_first_match=act_on_first_match
        )

    def delete_function_coupling(
            self,
            /, filter_attribute_value: any,
            *, filter_attribute: str = '_id', act_on_first_match: bool = True
    ) -> None:
        """Removes a function coupling document from the database.

        :param filter_attribute_value:
            The value of filter_attribute.
        :param filter_attribute:
            The attribute used to locate the document in the database.
        :param act_on_first_match:
            If this is set to ture, then only the first found document will be
            deleted. If it's set to false, then all fund documents will be
            deleted.

        :return: No return value.

        :raises RuntimeError:
            If instance is not connected to a database.
        :raises ValueError:
            If the given filter_attribute_value is invalid or if
            filter_attribute isn̈́'t part of the document type.
        :raises TypeError:
            If the type of filter_attribute_value is invalid or
            if filter_attribute isn't a string.
        """

        if filter_attribute == 'dependentFunctions':
            def delete_dependents(filter_attribute_str, db_attribute_filter):
                self.database['coupling'].delete_many({
                    filter_attribute_str: db_attribute_filter[0]
                })

            self.__query_remove_one(
                collection='coupling',
                filter_attribute=filter_attribute,
                filter_attribute_value=filter_attribute_value,
                attribute_dict=FUNCTION_COUPLING_ATTRIBUTES_CHECKER,
                bad_attribute_list=FUNCTION_COUPLING_BAD_ATTRIBUTES,
                act_on_first_match=act_on_first_match,
                query_function=delete_dependents
            )

        else:
            self.__query_remove_one(
                collection='coupling',
                filter_attribute=filter_attribute,
                filter_attribute_value=filter_attribute_value,
                attribute_dict=FUNCTION_COUPLING_ATTRIBUTES_CHECKER,
                bad_attribute_list=FUNCTION_COUPLING_BAD_ATTRIBUTES,
                act_on_first_match=act_on_first_match
            )
