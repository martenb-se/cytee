from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.errors import ConnectionFailure
from functools import reduce


def __check_for_valid_string(in_arg):
    return len(in_arg) > 0


def __check_for_valid_number(in_arg):
    return in_arg >= 0


def __check_for_valid_id_string(in_arg):
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
        lambda x, y: x & y, in_arg, True)}
}

FUNCTION_INFO_BAD_ATTRIBUTES = ['pathToProject', 'pathToFile', 'fileName',
                                'pathToCache']
TEST_INFO_BAD_ATTRIBUTES = ['pathToProject', 'fullPath', 'functionName']
FUNCTION_COUPLING_BAD_ATTRIBUTES = ['function', 'dependentFunctions']


# Todo: Add error handler that can revert changes and such if error occurs.
# Todo: Check if the object is connected to a database, and disconnect it if
#  that's the case.
# Todo: Set the client, database values to None.
# Todo: Raise another exception.
class DatabaseHandler:
    """
    Test database class
    """

    client = None
    database = None
    db_url = None

    def __init__(self, url: str) -> None:
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
        Connects to the database.

        :return: No return value.
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

    def __db_to_app_string_conv(self, db_string: str) -> str:
        """
        converts a string that has been stored in the database (and therefore
        conforms to mongoDBs naming restrictions) to a string that can be used
        in the application.

        :param db_string: given string to be converted.
        :return: string suitable for the application.
        """

        app_string = db_string.replace('|', '/')
        app_string = app_string.replace(':', '.')
        return app_string

    def __function_info_app_to_db_conv(self, function_info: any) -> any:
        """
        Converts certain strings in the function_info object to conform to
        the mongoDB naming restrictions.

        :param function_info:
        :return:
        """

        for item in FUNCTION_INFO_BAD_ATTRIBUTES:
            if item in function_info:
                function_info[item] = self.__app_to_db_string_conv(
                    function_info[item])
        if '_id' in function_info:
            function_info['_id'] = ObjectId(function_info['_id'])
        return function_info

    def __test_info_app_to_db_conv(self, test_info: any) -> any:
        """

        :param test_info:
        :return:
        """

        for item in TEST_INFO_BAD_ATTRIBUTES:
            if item in test_info:
                test_info[item] = self.__app_to_db_string_conv(test_info[item])
        if '_id' in test_info:
            test_info['_id'] = ObjectId(test_info['_id'])
        return test_info

    def __function_coupling_app_to_db_conv(
            self,
            function_coupling: any) -> any:
        """

        :param function_coupling:
        :return:
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

    def __function_info_db_to_app_conv(self, function_info: any) -> any:
        """
        Converts certain strings in the function_info object so they can be
        used in the rest of the application.

        :param function_info: object containing information about a function.
        :return: no return value.
        """

        for item in FUNCTION_INFO_BAD_ATTRIBUTES:
            if item in function_info:
                function_info[item] = self.__db_to_app_string_conv(
                    function_info[item])
        function_info['_id'] = str(function_info['_id'])

        return function_info

    def __test_info_db_to_app_conv(self, test_info: any) -> any:
        """

        :param test_info:
        :return:
        """

        for item in TEST_INFO_BAD_ATTRIBUTES:
            if item in test_info:
                test_info[item] = self.__db_to_app_string_conv(test_info[item])
        test_info['_id'] = str(test_info['_id'])
        return test_info

    def __function_coupling_db_to_app_conv(
            self,
            function_coupling: any) -> any:
        """

        :param function_coupling:
        :return:
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

    def __is_connected_to_db(self):
        """

        :return:
        """
        return self.client is not None and self.database is not None

    def __get_query(
            self,
            /, collection: str, attribute_value: any, attribute_dict: dict,
            bad_attribute_list: list, db_to_app_conv: any,
            *, document_attribute: str, query_function: any = None,
            act_on_first_match: bool = False
    ) -> any:
        """

        :param collection:
        :param attribute_value:
        :param attribute_dict:
        :param bad_attribute_list:
        :param db_to_app_conv:
        :param document_attribute:
        :param query_function:
        :param act_on_first_match:
        :return:
        """

        if not self.__is_connected_to_db():
            raise RuntimeError("""
                Tried to send query without connecting to database.
            """)

        if not isinstance(document_attribute, str):
            raise TypeError(f"""
                The document_attribute argument should be a string type but was 
                given a {type(document_attribute)} type instead.""")

        if document_attribute not in attribute_dict:
            raise ValueError(f"""
            The given document attribute {document_attribute} is not an valid
            attribute in the {collection} documents.""")

        if not isinstance(
                attribute_value, attribute_dict[document_attribute]['type']):
            raise TypeError(f"""
             The {document_attribute} attribute's value should be {
             attribute_dict[document_attribute]['type']}, but was given a
             {type(attribute_value)} type.""")

        if attribute_dict[document_attribute]['cond'] and not attribute_dict[
                document_attribute]['cond'](attribute_value):
            raise ValueError(f"""
            The value {attribute_value} of attribute {document_attribute} does 
            not conform to the constraints of the attribute.""")

        if document_attribute == '_id':
            db_attribute_value = ObjectId(attribute_value)
        elif document_attribute in bad_attribute_list:
            db_attribute_value = self.__app_to_db_string_conv(attribute_value)
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
        """

        :param collection:
        :param document:
        :param attribute_dict:
        :param app_to_db_conv:
        :param query_function:
        :return:
        """
        if not self.__is_connected_to_db():
            raise RuntimeError("""
                Tried to send query without connecting to database.
            """)

        for attribute, attribute_value in document.items():
            if attribute not in attribute_dict:
                raise ValueError(f"""
                The given document attribute {attribute} is not an valid
                attribute in the {collection} documents.""")

            if not isinstance(
                    attribute_value,
                    attribute_dict[attribute]['type']):
                raise TypeError(f"""
                 The {attribute} attribute's value should be {
                attribute_dict[attribute]['type']}, but was given a
                 {type(attribute_value)} type.""")

            if attribute_dict[attribute]['cond'] and not attribute_dict[
                    attribute]['cond'](attribute_value):
                raise ValueError(f"""
                The value {attribute_value} of attribute {attribute} does 
                not conform to the constraints of the attribute.""")

        db_document = app_to_db_conv(document)

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
        """

        :param collection:
        :param updated_document_data:
        :param filter_attribute:
        :param attribute_dict:
        :param bad_attribute_list:
        :param query_function:
        :param filter_attribute_value:
        :return:
        """
        if not self.__is_connected_to_db():
            raise RuntimeError("""
                Tried to send query without connecting to database.
            """)

        if not isinstance(filter_attribute, str):
            raise TypeError(f"""
            Filter attribute has to be a string but was given argument of
            type {filter_attribute}.""")

        if filter_attribute not in attribute_dict:
            raise ValueError(f"""
            Given filter attribute {filter_attribute} is not a valid attribute
            of the {collection} document.""")

        for attribute, attribute_value in updated_document_data.items():
            if attribute not in attribute_dict:
                raise ValueError(f"""
                The given document attribute {attribute} is not an valid
                attribute in the {collection} documents.""")

            if not isinstance(
                    attribute_value,
                    attribute_dict[attribute]['type']):
                raise TypeError(f"""
                 The {attribute} attribute's value should be {
                attribute_dict[attribute]['type']}, but was given a
                 {type(attribute_value)} type.""")

            if attribute_dict[attribute]['cond'] and not attribute_dict[
                    attribute]['cond'](attribute_value):
                raise ValueError(f"""
                The value {attribute_value} of attribute {attribute} does 
                not conform to the constraints of the attribute.""")

        db_document = app_to_db_conv(updated_document_data)

        if not filter_attribute_value:
            db_document_filter = db_document[filter_attribute]
        else:
            if not isinstance(filter_attribute, attribute_dict[
                    filter_attribute]['type']):
                raise TypeError(f"""
                filter_attribute_value should be of type {
                attribute_dict[filter_attribute]['type']}""")

            if attribute_dict[filter_attribute]['cond'] and not attribute_dict[
                    filter_attribute]['cond'](filter_attribute_value):
                raise ValueError(f"""
                The value {filter_attribute_value} of the filter attribute 
                {filter_attribute} does not conform to the constraints of the 
                attribute.""")

            if filter_attribute in bad_attribute_list:
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
        """

        :param collection:
        :param filter_attribute:
        :param attribute_dict:
        :param bad_attribute_list:
        :param query_function:
        :param act_on_first_match:
        :return:
        """

        if not self.__is_connected_to_db():
            raise RuntimeError("""
                Tried to send query without connecting to database.
            """)

        if not isinstance(filter_attribute, str):
            raise TypeError(f"""
            Filter attribute has to be a string but was given argument of
            type {filter_attribute}.""")

        if filter_attribute not in attribute_dict:
            raise ValueError(f"""
            Given filter attribute {filter_attribute} is not a valid attribute
            of the {collection} document.""")

        if filter_attribute not in attribute_dict:
            raise ValueError(f"""
            The given filter attribute {filter_attribute} is not an valid
            attribute in the {collection} documents.""")

        if not isinstance(
                filter_attribute_value, attribute_dict[filter_attribute][
                    'type']):
            raise TypeError(f"""
             The {filter_attribute_value} attribute's value should be {
             attribute_dict[filter_attribute]['type']}, but was given a
             {type(filter_attribute_value)} type.""")

        if attribute_dict[filter_attribute]['cond'] and not attribute_dict[
                filter_attribute]['cond'](filter_attribute_value):
            raise ValueError(f"""
            The value {filter_attribute_value} of attribute {filter_attribute} 
            does not conform to the constraints of the attribute.""")

        if filter_attribute in bad_attribute_list:
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
            query_function(db_attribute_filter)

    def get_function_info(
            self,
            /, attribute_value: any,
            *, document_attribute: str = '_id'
    ) -> any:
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
        return self.__get_query(
            collection='coupling',
            attribute_value=attribute_value,
            attribute_dict=FUNCTION_COUPLING_ATTRIBUTES_CHECKER,
            bad_attribute_list=FUNCTION_COUPLING_BAD_ATTRIBUTES,
            db_to_app_conv=self.__function_coupling_db_to_app_conv,
            document_attribute=document_attribute
        )

    def add_function_info(self, function_info: any) -> str:
        return self.__query_add_one(
            'function_info',
            function_info,
            FUNCTION_INFO_ATTRIBUTE_CHECKER,
            self.__function_info_app_to_db_conv
        )

    def add_test_info(self, test_info: any) -> str:
        return self.__query_add_one(
            'test_info',
            test_info,
            TEST_INFO_ATTRIBUTES_CHECKER,
            self.__test_info_app_to_db_conv
        )

    def add_function_coupling(self, function_coupling: any) -> str:
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
            /, update_function_info: any,
            *, filter_attribute: any = '_id', filter_attribute_value=None
    ) -> None:
        self.__query_set_one(
            collection='test_info',
            updated_document_data=update_function_info,
            filter_attribute=filter_attribute,
            attribute_dict=TEST_INFO_ATTRIBUTES_CHECKER,
            app_to_db_conv=self.__test_info_app_to_db_conv,
            filter_attribute_value=filter_attribute_value,
            bad_attribute_list=TEST_INFO_BAD_ATTRIBUTES
        )

    def set_function_coupling(
            self,
            /, update_function_info: any,
            *, filter_attribute: any = '_id', filter_attribute_value=None
    ) -> None:
        self.__query_set_one(
            collection='coupling',
            updated_document_data=update_function_info,
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
        self.__query_remove_one(
            collection='coupling',
            filter_attribute=filter_attribute,
            filter_attribute_value=filter_attribute_value,
            attribute_dict=FUNCTION_COUPLING_ATTRIBUTES_CHECKER,
            bad_attribute_list=FUNCTION_COUPLING_BAD_ATTRIBUTES,
            act_on_first_match=act_on_first_match
        )
