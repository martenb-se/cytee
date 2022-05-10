import os
from api.instances.database_main import database_handler
from pprint import pprint
import re


def number_var_formatter(number_arg):
    """Formats the given string argument to be used in variable declaration.

    :param number_arg:
    :type number_arg: int
    :return: string representation of string value
    :rtype: str
    """
    return f"""{number_arg}"""


def string_var_formatter(string_arg: str) -> str:
    """Formats the given string argument to be used in variable declaration.

    :param string_arg: string argument
    :type string_arg: str
    :return: string representation of string value
    :rtype: str
    """
    return f"""\'{string_arg}\'"""


def boolean_var_formatter(bool_arg: bool) -> str:
    """Formats the given boolean argument to be used in variable declaration.

    :param bool_arg: boolean argument
    :type bool_arg: bool
    :return: string representation of boolean value
    :rtype: str
    """
    if bool_arg:
        return "true"
    return "false"


def object_var_formatter(object_arg: list) -> str:
    """Formats the given object to a string to be use in variable declarations.

    :param array_arg: object argument
    :type array_arg: list
    :return: string representation of object
    :rtype: str
    """
    object_string = "{"

    if len(object_arg) > 0:

        first = True
        for argument_data in object_arg:
            if first:
                first = False
            else:
                object_string += ","

            object_string += argument_data['argument'] + ":"
            argument_var_formatter = TYPE_MATCHER_DICT[
                argument_data['type']][
                'var_formatter']

            if isinstance(argument_var_formatter, str):
                object_string += argument_var_formatter
            else:
                object_string += argument_var_formatter(argument_data['value'])

    object_string += "}"
    return object_string


def array_var_formatter(array_arg: list) -> str:
    """Formats the given array to a string to be use in variable declarations.

    :param array_arg: array argument
    :type array_arg: list
    :return: string representation of array
    :rtype: str
    """
    array_string = "["

    if len(array_arg) > 0:

        first = True
        for argument_data in array_arg:
            if first:
                first = False
            else:
                array_string += ","

            argument_var_formatter = TYPE_MATCHER_DICT[
                argument_data['type']][
                'var_formatter']

            if isinstance(argument_var_formatter, str):
                array_string += argument_var_formatter
            else:
                array_string += argument_var_formatter(argument_data['value'])

    array_string += "]"

    return array_string


TYPE_MATCHER_DICT = {
    'array': {
        'matcher': 'toEqual',
        'var_formatter': array_var_formatter
    },
    'bigInt': {
        'matcher': 'toEqual',
        'var_formatter': None
    },
    'boolean': {
        'matcher': 'toBeTruthy',
        'var_formatter': boolean_var_formatter
    },
    'float': {
        'matcher': 'toBeCloseTo',
        'var_formatter': number_var_formatter
    },
    'null': {
        'matcher': 'toBeNull',
        'var_formatter': "null"
    },
    'number': {
        'matcher': 'toEqual',
        'var_formatter': number_var_formatter
    },
    'object': {
        'matcher': 'toEqual',
        'var_formatter': object_var_formatter
    },
    'range': {
        'matcher': 'toEqual',
    },
    'string': {
        'matcher': 'toEqual',
        'var_formatter': string_var_formatter
    },
    'undefined': {
        'matcher': 'toBeUndefined',
        'var_formatter': "undefined"
    },

}

UNIQUE_NUMBER = 0


def __argument_formatter(argument: dict) -> str:
    """Turns the argument value into a string representation.

    :param argument: the argument represented as a dictionary.
    :type argument: dict
    :return: string representation of the argument value.
    """

    argument_var_formatter = TYPE_MATCHER_DICT[
        argument['type']]['var_formatter']

    if isinstance(argument_var_formatter, str):
        arg_string = argument_var_formatter
    else:
        arg_string = argument_var_formatter(argument['value'])

    return arg_string


def __generate_test_file_path(test_info: dict) -> str:
    """Generates the file path at which the test will be generated and returns
    it a string.

    :param test_info: test info document.
    :type test_info: dict
    :return: file of test file
    :rtype: str
    """

    # TODO: Check if the path already exist

    path_to_file = os.path.split(test_info['fileId'])[0]
    test_file_path = test_info['pathToProject'] + path_to_file + "/"
    return test_file_path


def __generate_imports(test_info: dict) -> str:
    """ Generates the import statements as a string.

    :param test_info: test info document.
    :type test_info: dict
    :return: import statments
    :rtype: str
    """
    function_info_documents = database_handler.get_function_info({
        'pathToProject': test_info['pathToProject'],
        'functionId': test_info['functionId'],
        'fileId': test_info['fileId']
    })

    if function_info_documents is None:
        raise RuntimeError(
            f"function with functionId {test_info['functionId']} doesn't" +
            "exist in the database."
        )

    function_info = function_info_documents[0]

    match function_info['exportInfo']:
        case 'export':
            exported_function_name = "{" + function_info['exportName'] + "}"
        case 'export default':
            exported_function_name = function_info['exportName']
        case _:
            raise RuntimeError(
                f"{function_info['exportInfo']} is a invalid export type")

    relative_import_path = './' + os.path.basename(
        os.path.normpath(test_info['fileId'])
    )

    import_expression = (f"import {exported_function_name} from "
                         f"\'{relative_import_path}\';")

    return import_expression


def __generate_test_start(test_info: dict) -> str:
    """
    Generates the starting statement of a jest test as a string. The statement
    includes a descriptions of the test followed by a function declaration.

    :param test_info: test info document.
    :type test_info: dict
    :return: starting statement of jest test.
    :rtype: str
    """
    description_string = ""

    if 'returnValue' in test_info['moduleData']:

        var_formatter = (
            TYPE_MATCHER_DICT[
                test_info['moduleData']['returnValue']['type']
            ]['var_formatter']
        )

        if isinstance(var_formatter, str):
            expected_value = var_formatter
        else:
            expected_value = var_formatter(
                test_info['moduleData']['returnValue']['value']
            )

        description_string += ("Function is expected to return " +
                               f"{expected_value}")
    else:

        exception = test_info['moduleData']['exception']['value']
        description_string += f"Function is expected to throw {exception}"

    # Check if arguments exists
    if 'argumentList' in test_info['moduleData']:

        description_string += ", when given the arguments: "
        first = True
        for argument_data in test_info['moduleData']['argumentList']:
            if first:
                first = False
            else:
                description_string += ', '

            argument_name = argument_data['argument']
            if (argument_data['type'] == 'undefined' or
                    argument_data['type'] == 'null'):
                argument_value = argument_data['type']
            else:
                argument_value = argument_data['value']

            description_string += f"{argument_name} = {argument_value}"

    return f"""test("{description_string}", () => """ + """ {"""


def __generate_test_end() -> str:
    """Returns a closing statement of a test.

    :return: Closing statement of test.
    :rtype: str
    """
    return """});"""


def __variable_assignment_standard(
        variable_name: str,
        variable_value: str
) -> str:
    """Generates a standard variable assignment string based on a variable and
    value string.

    :param variable_name: string representation of the variable name.
    :type variable_name: str
    :param variable_value: string representation of the variable value.
    :type variable_value: str
    :return: string of variable assignment.
    :rtype: str
    """
    return f"""let {variable_name}={variable_value};"""


def __generate_variable_declarations(test_info: dict) -> (str, dict):
    """Generate a string with variable declarations specified in the test info
    document and an argument to variable map for the function being tested.

    :param test_info: Test info document.
    :type test_info: dict
    :return: variable declaration string and argument
    :rtype: tuple
    """
    if 'argumentList' not in test_info['moduleData']:
        return "", None

    arguments = test_info['moduleData']['argumentList']

    func_arg_var_map = {}
    argument_declaration_string = ""

    for argument_data in arguments:

        global UNIQUE_NUMBER
        variable_name = f"a_{UNIQUE_NUMBER}"
        UNIQUE_NUMBER += 1

        variable_value = __argument_formatter(argument_data)

        argument_declaration_string += f"let {variable_name}={variable_value};"

        # TODO: Make it so when variable is and object, that the object is
        #  added instead.

        if argument_data['argument'] == '...':
            if '...' not in func_arg_var_map:
                func_arg_var_map['...'] = []

            func_arg_var_map['...'].append(variable_name)
        else:
            func_arg_var_map[argument_data['argument']] = variable_name

    return argument_declaration_string, func_arg_var_map


def __generate_arguments(
        arg_list: list,
        expression_name: str,
        func_arg_var_map: dict
) -> str:
    """Formats the variables as a string to be used as arguments in a function
    call.

    :param arg_list: List of the argument dictionaries.
    :type arg_list: list
    :param expression_name: Name of the expression that is being called.
    :type expression_name: str
    :param func_arg_var_map: Dictionary that maps the function arguments to
    variables in the test function.
    :type  func_arg_var_map: dict
    :return: string containing the varaibles used to call the expression.
    :rtype: str
    """

    first_arg = True
    argument_string = ""

    for argument_data in arg_list:

        if first_arg:
            first_arg = False
        else:
            argument_string += ','

        argument_type = argument_data['type']

        # TODO: Handle default values, how to handle cases where the argument
        #  isn't specified
        match argument_type:
            case 'Identifier':
                argument_string += (
                    func_arg_var_map
                    [argument_data['name']])
            case 'Property':
                argument_string += (
                    func_arg_var_map
                    [argument_data['key']['name']])
            case 'ObjectPattern':
                obj_string = __generate_arguments(
                    argument_data['properties'],
                    expression_name,
                    func_arg_var_map)
                argument_string += "{" + obj_string + "}"
            case 'ArrayPattern':
                array_string = __generate_arguments(
                    argument_data['elements'],
                    expression_name,
                    func_arg_var_map)
                argument_string += "[" + array_string + "]"
            case 'RestElement':
                rest_string = ""
                rest_first = True
                for rest_arg in func_arg_var_map['...']:
                    if rest_first:
                        rest_first = False
                    else:
                        rest_string += ','
                    rest_string += rest_arg
                argument_string += rest_string
            case 'AssignmentPattern':
                # check if corresponding argument exists in func_arg_var_map
                pass
            case _:
                # log warning message
                pass

    return argument_string


def __generate_function_call(
        test_info: dict,
        func_arg_var_map: dict
) -> (str, str):
    """Generates a string with the function call of the functon being tested.

    :param test_info: Test info document.
    :type test_info: dict
    :param func_arg_var_map: Dictionary that maps the function arguments to
    variables in the test function.
    :type  func_arg_var_map: dict
    :return: A tuple containing the function call as a string and the string
    representation of the return variable.
    """
    function_info_documents = database_handler.get_function_info({
        'pathToProject': test_info['pathToProject'],
        'functionId': test_info['functionId'],
        'fileId': test_info['fileId']
    })

    if function_info_documents is None:
        raise RuntimeError(
            f"function with functionId {test_info['functionId']} doesn't" +
            "exist in the database."
        )

    function_info = function_info_documents[0]

    sub_expression_list = test_info['functionId'].split('.')
    expression_arg_list = function_info['arguments']

    function_call_string = ""

    expression_list_index = 0
    first_expr = True
    db_query_string = ""
    for expr in sub_expression_list:

        expression_string = ""

        if first_expr:
            first_expr = False
        else:
            expression_string += '.'
            db_query_string += '.'

        db_query_string += expr
        regex_result = re.search(r"^(?:\(new )(.*)(?:\(\)\))", expr)

        if regex_result is not None:
            expression_name = regex_result.group(1)
            expression_string += f"(new {expression_name}"

            pprint(expression_name)
            expr_arg_list = expression_arg_list[expression_list_index]
            arg_list = expr_arg_list[expression_name]

            expression_string += "("
            expression_string += __generate_arguments(
                arg_list,
                expression_name,
                func_arg_var_map)
            expression_string += ")"
            expression_list_index += 1
        else:
            # TODO: have to concatenate the previous expression string when
            #  searching.

            expr_func_info = database_handler.get_function_info({
                'pathToProject': test_info['pathToProject'],
                'functionId': db_query_string,
                'fileId': test_info['fileId']
            })

            if expr_func_info is None:
                expression_string += expr
            else:
                arg_list = expression_arg_list[expression_list_index][expr]

                expression_string += expr
                expression_string += "("
                expression_string += __generate_arguments(
                    arg_list,
                    expr,
                    func_arg_var_map)
                expression_string += ")"
                expression_list_index += 1

        function_call_string += expression_string

    func_return_variable = "r_1"

    # TODO: Format the string

    result_string = (f"let {func_return_variable}={function_call_string};")

    return result_string, func_return_variable


def __generate_assert(
        test_info: dict,
        return_variable: str
) -> str:
    """generates and assert string based on the given test info document and
    the return value of the executed function.
    
    :param test_info: Test info document.
    :type test_info: dict
    :param return_variable: A string representation of the variable with the
    return value from the executed function.
    :type return_variable: str
    :return: The assertion string.
    :rtype: str
    """

    if 'returnValue' not in test_info['moduleData']:
        raise RuntimeError('test info is missing return value ')

    expected_data = test_info['moduleData']['returnValue']
    match_expression = TYPE_MATCHER_DICT[expected_data['type']]['matcher']
    if expected_data['type'] in ['undefined', 'null']:
        expected_value = (
            TYPE_MATCHER_DICT
            [expected_data['type']]
            ['var_formatter']
        )
    else:
        expected_value = (
            TYPE_MATCHER_DICT
            [expected_data['type']]
            ['var_formatter']
            (expected_data['value'])
        )

    assert_string = (f"expect({return_variable})"
                     f".{match_expression}({expected_value});")

    return assert_string


def __generate_exception(
        test_info: dict,
        function_call_string: str
) -> str:
    """Add a 'toThrow' expression to the end of the given function call string
    with the expression provided in the test info document. The new string is
    then returned.

    :param test_info: Test info document.
    :type test_info: dict
    :param function_call_string: The test code represented as a string of the
    given test info document.
    :type  function_call_string: str
    :return: The function call string with the toThrow expression.
    :rtype: str
    """
    exception = test_info['moduleData']['exception']['value']

    exception_string = function_call_string.replace(
        ";",
        f".toThrow({exception});",
        1
    )
    return exception_string


# TODO: Make it so several tests info instances can be sent int.
# TODO: Make it so several tests are written to the same file.
# TODO: Fix path issue

def generate_test(
        test_info: dict
) -> (str, str):
    """Uses the given test info document to generate a jest test code and the
    necessary import statements as strings

    :param test_info: The test info document used to generate the test.
    :type test_info:
    :return: tuple containing the test as a string and necessary import
    statement.
    :rtype: tuple

    """
    global UNIQUE_NUMBER
    UNIQUE_NUMBER = 0

    import_string = __generate_imports(test_info)

    variable_declaration_string, func_var_arg_map = \
        __generate_variable_declarations(test_info)

    function_call_string, return_var = __generate_function_call(
        test_info,
        func_var_arg_map)

    if 'returnValue' in test_info['moduleData']:
        assert_string = __generate_assert(test_info, return_var)
    else:
        assert_string = __generate_exception(test_info, function_call_string)

    test_string = (
            __generate_test_start(test_info) +
            variable_declaration_string +
            function_call_string +
            assert_string +
            __generate_test_end()
    )
    return test_string, import_string


def generate_tests(test_info_list: list) -> None:
    """ Generates jest tests based on the given test info list. The tests are
    saved in the same folder as the file being tested.s

    :param test_info_list: List of test info documents.
    :type test_info_list: list
    :return: No return value
    :rtype: None
    """

    test_file_dict = {}

    for test_info in test_info_list:

        abs_func_path = test_info['pathToProject'] + "/" + test_info['fileId']

        if abs_func_path not in test_file_dict:
            test_file_dict[abs_func_path] = {}

        if test_info['functionId'] not in test_file_dict[abs_func_path]:
            test_file_dict[abs_func_path][test_info['functionId']] = []

        test_file_dict[abs_func_path][test_info['functionId']].append(
            test_info)

    for file_path, file_test_info_dir in test_file_dict.items():

        urangutest_file = file_path + ".urang.spec.js"
        file_imports = []
        file_tests = []

        for functionId, func_test_info_list in file_test_info_dir.items():
            func_test_strings = ""

            for func_test_info in func_test_info_list:
                test_string, import_string = generate_test(func_test_info)
                func_test_strings += test_string

                if import_string not in file_imports:
                    file_imports.append(import_string)

            file_tests.append(func_test_strings)

        with open(urangutest_file, 'w') as f:

            for import_statement in file_imports:
                f.write(import_statement)

            for function_tests in file_tests:
                f.write(function_tests)
