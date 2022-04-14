import os
import pathlib
from contextlib import contextmanager
from pprint import pprint

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
def object_var_formatter(object_arg, type_matcher_dict):
    var_string = "{"
    var_string += __object_var_formatter_recur(
                    {'value': object_arg},
                    type_matcher_dict,
                    var_string)
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
                                var_string)
            var_string += '}'
        elif isinstance(type_matcher_dict[item['type']]['var_formatter'], str):
            var_string += type_matcher_dict[item['type']]['var_formatter']
        else:
            var_string += type_matcher_dict[
                            item['type']][
                            'var_formatter'](
                            item['value'])
    return var_string


def array_var_formatter(array_obj, type_matcher_dict):
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


def __generate_test_file_path(test_info):
    proj_dir = os.path.split(os.path.normpath(test_info['pathToProject']))[0]
    test_directory_path = proj_dir + "/urangutest"
    pprint(test_directory_path)
    os.mkdir(test_directory_path)
    test_file_path = test_directory_path + "/" + test_info['fileId']
    pprint(test_file_path)
    os.makedirs(os.path.dirname(test_file_path))
    return test_file_path + ".urang.spec.js"


def __generate_meta_data(file_handler):
    pass


# TODO: Find a way to handle both exports and default exports.
def __generate_imports(file_handler, test_file_path, test_info):
    # What is export default used for
    # https://www.geeksforgeeks.org/what-is-export-default-in-javascript/

    tested_file_path = test_info['pathToProject'] + "/" + test_info['fileId']
    relative_path = os.path.relpath(tested_file_path, test_file_path)
    import_string = (f"import {test_info['functionId']} from" +
                     f" \'{relative_path}\';")
    pprint(import_string)
    file_handler.write(import_string)

# TODO: Write some description for each tests that say something about what
#  is being tested.
def __generate_test_start(file_handler, test_info):

    file_handler.write("""test("", () =>  {""")


def __generate_test_end(file_handler):
    file_handler.write("""});""")


def __variable_assignment_standard(variable_name, variable_value):
    return f"""let {variable_name}={variable_value};"""


def __generate_setup(f, test_info):
    # Returns a dictionary with variables.

    pass


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
    with open(test_file_path, 'w') as f:
        # __generate_meta_data(f)
        __generate_imports(f, test_file_path, test_info)

        __generate_test_start(f, test_info)

        __generate_setup(f, test_info)

        __generate_test_end(f)