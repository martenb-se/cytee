import os
from api.instances.database_main import database_handler
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


def __argument_formatter(argument):
    argument_var_formatter = TYPE_MATCHER_DICT[
                                argument['type']]['var_formatter']
    if argument['type'] == 'object':
        arg_string = argument_var_formatter(argument['value'], TYPE_MATCHER_DICT)
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


# TODO: Find a way to handle both exports and default exports.
# TODO: Find out what it it's necessary to import an object like
#   defaults.headers or is it ok to just import defaults.
# TODO: may have to detect whether a function or object should be imported or
#   just remove everything after the first . could work as it indicates that
#   it's a object kind of.
def __generate_imports(test_file_path, test_info):
    # What is export default used for
    # https://www.geeksforgeeks.org/what-is-export-default-in-javascript/

    # get the function info from database to find out if it is exported or
    # default export.



    func_inf_docs = database_handler.get_function_info({
        'pathToProject': test_info['pathToProject'],
        'functionId': test_info['functionId'],
        'fileId': test_info['fileId']
    })

    if func_inf_docs is None:
        raise RuntimeError('')

    func_inf = func_inf_docs[0]

    pprint(func_inf)

    if func_inf['exportInfo'] == 'export default':
        exported_function_name = "{" + func_inf['exportName'] + "}"
    else:
        exported_function_name = func_inf['exportName']

    tested_file_path = test_info['pathToProject'] + test_info['fileId']

    relative_path = os.path.relpath(tested_file_path, test_file_path)

    import_string = (f"import {exported_function_name} from" +
                     f" \'{relative_path}\';")

    return import_string


# TODO: Write some description for each tests that say something about what
#  is being tested.
def __generate_test_start(test_info):

    return ("""test("", () =>  {""")


def __generate_test_end(file_handler):
    file_handler.write("""});""")


def __variable_assignment_standard(variable_name, variable_value):
    return f"""let {variable_name}={variable_value};"""


# TODO: Handle situations with no arguments
def __generate_setup(test_info):
    # Returns a string and dictionary with variables.
    argument_declaration_string = ""
    func_arg_var_map = {}

    # get function info arguments

    # for each argument, place the corresponding variable


    for argument_dict in test_info['moduleData']['argumentList']:

        argument_name = f"{argument_dict['argument']}_arg"
        argument_value = __argument_formatter(argument_dict)
        argument_assignment = f"""let {argument_name} = {argument_value};"""
        func_arg_var_map[argument_dict['argument']] = argument_name
        argument_declaration_string += argument_assignment

    return argument_declaration_string, func_arg_var_map


def __generate_function_call_2(function_name, arguemnts, return_variable):
    pass

# TODO: Handle cases with no arguments and cases with no return values maybe
# TODO: Have to detect when () is necessary after a object or function.
def __generate_function_call(test_info, func_arg_var_map):

    function_call_string = ""
    function_call_return_var = {}

    function_info = {
        'functionId': "db:util",
        'args': [
            {'db': ['arg1', 'arg2']},
            {'util': ['hehe', 'ojoj']}
        ]
    }

    if True:
        ret_val = "123"
        function_call_string += f"let {ret_val}="

    # deveide up the function into it's components.
    sub_instance_list = test_info['function_info'].split('.')

    first = True
    for inst in sub_instance_list:
        # Check if it's a class, object or function maybe
        if first:
            first = False
        else:
            function_call_string += '.'

        function_call_string += inst

        # check if the functions has any arguments
        if inst in func_arg_var_map:

            function_call_string += '('
            first_arg = True
            for arg in function_info['args'][inst]:

                if first_arg:
                    first_arg = False
                else:
                    function_call_string += ','

                function_call_string += func_arg_var_map[inst][arg]

            function_call_string += '('

        if inst:  # is class
            # create an instance of that class
            # who dafuq uses classes in JS fr!
            pass

    return function_call_string, function_call_return_var


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
    import_string = __generate_imports(test_file_path, test_info)
    pprint(import_string)

    #test_code_string = ""
    #test_code_string += __generate_imports(test_file_path, test_info)
    #test_code_string += __generate_test_start(test_info)
    #variable_string, variable_dict = __generate_setup(test_info)
    #test_code_string += variable_string
    #string_bing, ret_val = __generate_function_call(test_info, variable_dict)
    #test_code_string += string_bing

    #with open(test_file_path, 'w') as f:
        # __generate_meta_data(f)
        #__generate_imports(f, test_file_path, test_info)

        #__generate_test_start(f, test_info)

        #__generate_setup(f, test_info)

        #__generate_test_end(f)
        #f.write(test_code_string)
