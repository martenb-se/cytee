import os
from api.instances.database_main import database_handler
import pathlib
from contextlib import contextmanager
from pprint import pprint
import re


# TODO: Add describe at the top of every test files that mention something
#  about which function is being tested and such.
# TODO: support NaN number


# TODO: Nename to something related to javascript
def number_var_formatter(number_arg):
    return f"""{number_arg}"""


# TODO: Nename to something related to javascript
def string_var_formatter(string_arg):
    return f"""\"{string_arg}\""""


# TODO: Nename to something related to javascript
def boolean_var_formatter(bool_arg):
    if bool_arg:
        return "true"
    return "false"


# TODO: Nename to something related to javascript
# TODO: Remove the dependency on type_matcher_dict
def object_var_formatter(object_arg, type_matcher_dict):
    var_string = ""
    var_string += __object_var_formatter_recur(
        {'value': object_arg},
        type_matcher_dict,
        "{")
    var_string += "}"
    return var_string


def __object_var_formatter_recur(
        object_arg,
        type_matcher_dict,
        var_string):
    first = True
    for item in object_arg['value']:
        if first:
            first = False
        else:
            var_string += ","

        var_string += item['argument'] + ":"

        if item['type'] is 'object':
            var_string += '{'
            var_string += __object_var_formatter_recur(
                {'value': item['value']},
                type_matcher_dict,
                "")
            var_string += '}'
        elif isinstance(type_matcher_dict[item['type']]['var_formatter'], str):
            var_string += type_matcher_dict[item['type']]['var_formatter']
        else:
            var_string += type_matcher_dict[
                item['type']][
                'var_formatter'](
                item['value'])
    return var_string


def array_var_formatter(array_arg):
    pprint(array_arg)
    var_string = ""

    return var_string

def __array_var_formatter_recur(array_arg):

    pass



# check the number of arguemnts a function takes
# https://stackoverflow.com/questions/847936/how-can-i-find-the-number-of-arguments-of-a-python-function


TYPE_MATCHER_DICT = {
    'array': {
        'matcher': 'toBeEqual',
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


def __argument_formatter(argument):
    argument_var_formatter = TYPE_MATCHER_DICT[
        argument['type']]['var_formatter']
    if argument['type'] == 'object':
        arg_string = argument_var_formatter(argument['value'],
                                            TYPE_MATCHER_DICT)
    elif isinstance(argument_var_formatter, str):
        arg_string = argument_var_formatter
    else:
        arg_string = argument_var_formatter(argument['value'])

    return arg_string


def __generate_test_file_path(test_info):
    proj_dir = os.path.split(os.path.normpath(test_info['pathToProject']))[0]
    test_directory_path = proj_dir + "/urangutest"
    os.mkdir(test_directory_path)
    test_file_path = test_directory_path + "/" + test_info['fileId']
    os.makedirs(os.path.dirname(test_file_path))
    return test_file_path + ".urang.spec.js"


def __generate_meta_data(file_handler):
    pass


def __generate_imports(test_file_path, test_info):
    # Get the corresponding function info
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

    # Determine the export type and generate the corresponding name
    match function_info['exportInfo']:
        case 'export default':
            exported_function_name = "{" + function_info['exportName'] + "}"
        case 'export':
            exported_function_name = function_info['exportName']
        case _:
            raise RuntimeError(
                f"{function_info['exportInfo']} is a invalid export type")

    # Generate the path used to import the file being tested
    path_to_function = test_info['pathToProject'] + test_info['fileId']
    relative_import_path = os.path.relpath(path_to_function,
                                           test_file_path)

    # Generate the import string
    import_expression = (f"import {exported_function_name} from" +
                         f"\'{relative_import_path}\'")

    return import_expression


# TODO: Write some description for each tests that say something about what
#  is being tested.
def __generate_test_start(test_info):
    return ("""test("", () =>  {""")


def __generate_test_end(file_handler):
    file_handler.write("""});""")


def __variable_assignment_standard(variable_name, variable_value):
    return f"""let {variable_name}={variable_value};"""


def __generate_variable_declarations(test_info):
    # Check if there is any defined arguments
    if 'argumentList' not in test_info['moduleData']:
        return "", None

    # Get the argument data
    arguments = test_info['moduleData']['argumentList']

    # Declare func_var_arg_map and string
    argument_declaration_string = ""
    func_arg_var_map = {}

    uniqunes_number = 0
    # Iterate over the arguments
    for argument_data in arguments:
        # TODO: have global unique variable number

        # Generate the variable name
        variable_name = f"a_{uniqunes_number}"
        uniqunes_number += 1

        # Format variable value
        variable_value = __argument_formatter(argument_data)

        # update argument declaration string and func_var_arg_map
        argument_declaration_string += f"let {variable_name}={variable_value};"
        # TODO: Make it so when variable is and object, that the object is
        #  added instead.
        func_arg_var_map[argument_data['argument']] = variable_name

    return argument_declaration_string, func_arg_var_map


def __generate_arguments(arg_list, expression_name, func_arg_var_map):
    first_arg = True
    argument_string = ""

    # make a copy of the relevant func_arg_var_map list and pop
    func_arg_var_map_copy = func_arg_var_map.copy()

    for arg in arg_list:

        if first_arg:
            first_arg = False
        else:
            argument_string += ','

        if isinstance(arg, list):

            ## Determine if it's an object or '...'
            if arg[0] == "...":

                ## Add the remaining of the args in the arg list
                rem_arg_first = True
                for rem_arg in func_arg_var_map_copy:

                    if rem_arg_first:
                        rem_arg_first = False
                    else:
                        argument_string += ','

                    argument_string += rem_arg

            else:

                ## call this function again with arg as new argument list
                argument_string += "{"
                argument_string += __generate_arguments(arg, expression_name,
                                                        func_arg_var_map_copy)
                argument_string += "}"
        else:

            ## variable isn't a list
            argument_string += func_arg_var_map_copy[expression_name].pop(arg)

    return argument_string


def __generate_function_call(test_info, func_arg_var_map):
    # Get function info
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

    # Divide the functionId into sub expressions
    sub_expression_list = test_info['functionId'].split('.')
    expression_arg_list = function_info['arguments']

    # create the aggregation variable
    function_call_string = ""

    # Iterate over each element
    first_expr = True
    for expr in sub_expression_list:

        expression_string = ""

        if first_expr:
            first_expr = False
        else:
            expression_string += '.'

        # Check if the expression is a class
        regex_result = re.search(r"^(?:\(new )(.*)(?:\(\)\))", expr)

        if regex_result is not None:
            expression_name = regex_result.group(1)
            expression_string += f"(new {expression_name}("

            # Iterate over the function info arguments and ad corresponding arguments from the test_info

            arg_list = expression_arg_list.pop(0)[expression_name]

            # Generate the arguments
            expression_string += "("
            expression_string += __generate_arguments(
                arg_list,
                expression_name,
                func_arg_var_map)
            expression_string += ")"
        else:

            # Look if expr is has a function info document in db
            expr_func_info = database_handler.get_function_info({
                'pathToProject': test_info['pathToProject'],
                'functionId': expr,
                'fileId': test_info['fileId']
            })

            # Check if the expr is an object
            if expr_func_info is None:
                expression_string += expr
            else:
                arg_list = expression_arg_list.pop(0)[expr]

                # Generate the arguments
                expression_string += "("
                expression_string += __generate_arguments(
                    arg_list,
                    expr,
                    func_arg_var_map)
                expression_string += ")"

        function_call_string += expression_string

    func_return_variable = "r_1"

    # TODO: Format the string

    result_string = f"let {func_return_variable}={function_call_string}"

    return result_string, func_return_variable


def __generate_assert(f, test_info):
    # toBe is used to test exact equality
    # ToEqual recursively checks every field of an object or array.
    # For float points, use toBeCloseTo instead fo to equal
    # Regular expressions can be checked wit toMatch
    # Check an item in a array or iterable with toContain
    # For exception, use toThrow
    # For null, use toBeNull
    # For undefined, used toBeUndefined, or
    pass


# TODO: Create the test file
# TODO: Import the right function
def generate_test(test_info):
    # Create Directory
    # https://www.geeksforgeeks.org/create-a-directory-in-python/
    # Create File https://www.w3schools.com/python/python_file_write.asp
    # returning from within a with statement
    # https://stackoverflow.com/questions/64469248/is-returning-inside-a-with
    # -statement-dangerous
    # determine the directory of the src
    # absolut path aär project path
    # create directory if it doesn't exist
    # create the jest file, end with .urangu.sepc.js

    """
    test_dir = os.path.dirname(
        test_info['pathToProject'] +
        "../urangutest" +
        test_info['fileId']
    )
    test_file = test_dir + f'/{test_info["functionId"]}.urangu.spec.js'
    pprint(test_file)
    os.makedirs(test_dir, exist_ok=True)
    """

    test_file_path = __generate_test_file_path(test_info)
    #pprint(f"test_file_path: {test_file_path}")
    import_string = __generate_imports(test_file_path, test_info)
    #pprint(f"import_string: {import_string}")
    variable_declaration_string, func_var_arg_map = \
        __generate_variable_declarations(test_info)
    #pprint(f"variable_declaration_string: {variable_declaration_string}")
    #pprint(f"func_var_arg_map: {func_var_arg_map}")

    # test_code_string = ""
    # test_code_string += __generate_imports(test_file_path, test_info)
    # test_code_string += __generate_test_start(test_info)
    # variable_string, variable_dict = __generate_setup(test_info)
    # test_code_string += variable_string
    # string_bing, ret_val = __generate_function_call(test_info, variable_dict)
    # test_code_string += string_bing

    #with open(test_file_path, 'w') as f:
    # __generate_meta_data(f)
    # __generate_imports(f, test_file_path, test_info)

    # __generate_test_start(f, test_info)

    # __generate_setup(f, test_info)

    # __generate_test_end(f)
     #f.write(test_code_string)
