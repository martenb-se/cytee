import esprima
from copy import deepcopy

from api.analyzer.coupling import calculate_dependencies
from api.analyzer.logging_analyzer import logging
from enum import Enum


class IdentifierTypes(Enum):
    VARIABLE = 1
    CLASS = 2
    STATIC_METHOD = 3


class EsprimaAnalyze:
    """Esprima handler for analyzing file contents

    :param file_source: The file source code to use.
    :type file_source: str
    """

    def __init__(self, file_source):
        if not isinstance(file_source, str):
            raise TypeError("'file_source' must be a STRING")
        elif len(file_source) < 1:
            raise ValueError("'file_source' cannot be empty")

        try:
            self.esprima_tree = esprima.parseModule(file_source, {"range": True})
        except Exception:
            raise ValueError("'file_source' string could not be parsed.")

        self.file_source = file_source
        self.processed_functions = []

    def __append_to_identifier_chain(self, identifier_type, identifier_name, **old_kwargs):
        if identifier_type is not IdentifierTypes.VARIABLE and \
                identifier_type is not IdentifierTypes.CLASS and \
                identifier_type is not IdentifierTypes.STATIC_METHOD:
            raise ValueError("Unknown 'identifier_type': " + str(identifier_type))

        kwargs_pass = deepcopy(old_kwargs)
        identifier_chain = kwargs_pass.get('identifier_chain', [])
        identifier_chain.append({
            'type': identifier_type,
            'name': identifier_name
        })
        kwargs_pass['identifier_chain'] = identifier_chain
        return kwargs_pass

    def __append_to_class_arguments(self, current_node, **old_kwargs):
        kwargs_pass = deepcopy(old_kwargs)
        class_arguments = kwargs_pass.get('class_arguments', [])

        found_arguments = []
        if hasattr(current_node, 'body') and hasattr(current_node.body, 'body') and \
                isinstance(current_node.body.body, list):
            for decl_in_class in current_node.body.body:
                if isinstance(decl_in_class, esprima.nodes.MethodDefinition) and \
                        decl_in_class.key.name == 'constructor':
                    for param in decl_in_class.value.params:
                        self.__handle_argument_types(found_arguments, param)

        class_arguments.append({
            'identifier': self.__handle_found_function_get_identifier(**kwargs_pass),
            'arguments': found_arguments
        })

        kwargs_pass['class_arguments'] = class_arguments

        return kwargs_pass

    def __handle_found_function_add(self, current_node, **kwargs):
        self.processed_functions.append({
            "declaration_kind": self.__handle_found_function_get_declaration_kind(**kwargs),
            "identifier": self.__handle_found_function_get_identifier(**kwargs),
            "function_definition": self.__handle_found_function_get_definition(current_node),
            "arguments": self.__handle_function_get_arguments(current_node),
            "class_arguments": self.__handle_function_get_class_arguments(**kwargs),
            "source_code_range": self.__handle_function_get_source_code_range(current_node),
            "identifier_chain": kwargs.get('identifier_chain', []),
            "function_ast": current_node
        })

    def __handle_found_function_get_declaration_kind(self, **kwargs):
        return kwargs.get('current_declaration_kind', "")

    def __handle_found_function_get_identifier(self, **kwargs):
        identifier_string = ""

        identifier_chain = kwargs.get('identifier_chain', [])
        for chain_index, current_identifier in enumerate(identifier_chain):
            if current_identifier['type'] is IdentifierTypes.VARIABLE or \
                    current_identifier['type'] is IdentifierTypes.STATIC_METHOD:
                if len(identifier_string) > 0:
                    identifier_string += "." + current_identifier['name']
                else:
                    identifier_string += current_identifier['name']
            elif current_identifier['type'] is IdentifierTypes.CLASS:
                if len(identifier_string) > 0:
                    if (chain_index + 1) < len(identifier_chain) and \
                            identifier_chain[chain_index + 1]['type'] is IdentifierTypes.STATIC_METHOD:
                        identifier_string += "." + current_identifier['name']
                    else:
                        identifier_string += "(new " + identifier_string + "." + current_identifier['name'] + "())"
                else:
                    if (chain_index + 1) < len(identifier_chain) and \
                            identifier_chain[chain_index + 1]['type'] is IdentifierTypes.STATIC_METHOD:
                        identifier_string += current_identifier['name']
                    else:
                        identifier_string += "(new " + current_identifier['name'] + "())"

        return identifier_string

    def __handle_found_function_get_definition(self, current_node):
        return self.file_source[current_node.range[0]:current_node.range[1]]

    def __handle_argument_types(self, arguments, current_parameter):
        if isinstance(current_parameter, esprima.nodes.Identifier):
            self.__handle_argument_type_identifier(arguments, current_parameter)
        elif isinstance(current_parameter, esprima.nodes.Property):
            self.__handle_argument_type_property(arguments, current_parameter)
        elif isinstance(current_parameter, esprima.nodes.ObjectExpression):
            self.__handle_argument_type_objectexpression(arguments, current_parameter)
        elif isinstance(current_parameter, esprima.nodes.RestElement):
            self.__handle_argument_type_restelement(arguments, current_parameter)
        else:
            logging.warning("Argument type not yet implemented and cannot be analyzed: " + str(type(current_parameter)))

    def __handle_argument_type_identifier(self, arguments, current_parameter):
        arguments.append(current_parameter.name)

    def __handle_argument_type_property(self, arguments, current_parameter):
        self.__handle_argument_types(arguments, current_parameter.key)

    def __handle_argument_type_objectexpression(self, arguments, current_parameter):
        object_argument = []
        for current_property in current_parameter.properties:
            self.__handle_argument_types(object_argument, current_property)

        arguments.append(object_argument)

    def __handle_argument_type_restelement(self, arguments, current_parameter):
        arguments.append(['...'])

    def __handle_function_get_arguments(self, current_node):
        arguments = []
        if isinstance(current_node.params, list):
            for param in current_node.params:
                self.__handle_argument_types(arguments, param)

        return arguments

    def __handle_function_get_class_arguments(self, **kwargs):
        return kwargs.get('class_arguments', [])

    def __handle_function_get_source_code_range(self, current_node):
        return current_node.range

    def __handle_estree_list(self, path, current_node, **kwargs):
        for index, node_in_list in enumerate(current_node):
            self.__find_all_functions(path + str(index + 1) + "/", node_in_list, **kwargs)

    def __handle_estree_esprima_nodes_module(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_all_functions(path + "body/", current_node.body, **kwargs)

    def __handle_estree_esprima_nodes_variabledeclaration(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        kwargs_pass = deepcopy(kwargs)
        kwargs_pass['current_declaration_kind'] = current_node.kind
        self.__find_all_functions(path + "declarations/", current_node.declarations, **kwargs_pass)

    def __handle_estree_esprima_nodes_variabledeclarator(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        kwargs_pass = self.__append_to_identifier_chain(IdentifierTypes.VARIABLE, current_node.id.name, **kwargs)
        self.__find_all_functions(path + "init/", current_node.init, **kwargs_pass)

    def __handle_estree_esprima_nodes_objectexpression(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_all_functions(path + "properties/", current_node.properties, **kwargs)

    def __handle_estree_esprima_nodes_property(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        kwargs_pass = self.__append_to_identifier_chain(IdentifierTypes.VARIABLE, current_node.key.name, **kwargs)
        self.__find_all_functions(path + "value/", current_node.value, **kwargs_pass)

    def __handle_estree_esprima_nodes_classdeclaration(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        kwargs_pass = self.__append_to_identifier_chain(IdentifierTypes.CLASS, current_node.id.name, **kwargs)
        kwargs_pass = self.__append_to_class_arguments(current_node, **kwargs_pass)
        self.__find_all_functions(path + "class_body/", current_node.body, **kwargs_pass)

    def __handle_estree_esprima_nodes_classbody(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_all_functions(path + "body/", current_node.body, **kwargs)

    def __handle_estree_esprima_nodes_methoddefinition(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)

        if current_node.static:
            kwargs_pass = self.__append_to_identifier_chain(IdentifierTypes.STATIC_METHOD, current_node.key.name,
                                                            **kwargs)
        else:
            kwargs_pass = self.__append_to_identifier_chain(IdentifierTypes.VARIABLE, current_node.key.name, **kwargs)

        if current_node.key.name != 'constructor':
            self.__handle_found_function_add(current_node, **kwargs_pass)

    def __handle_estree_esprima_nodes_arrowfunctionexpression(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__handle_found_function_add(current_node, **kwargs)

    def __handle_estree_esprima_nodes_asyncarrowfunctionexpression(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__handle_found_function_add(current_node, **kwargs)

    def __handle_estree_esprima_nodes_exportdefaultdeclaration(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_all_functions(path + "declaration/", current_node.declaration, **kwargs)

    def __handle_estree_esprima_nodes_exportnameddeclaration(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_all_functions(path + "declaration/", current_node.declaration, **kwargs)

    def __find_all_functions(self, path, current_node, **kwargs):
        if isinstance(current_node, list):
            self.__handle_estree_list(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.Module):
            self.__handle_estree_esprima_nodes_module(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.VariableDeclaration):
            self.__handle_estree_esprima_nodes_variabledeclaration(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.VariableDeclarator):
            self.__handle_estree_esprima_nodes_variabledeclarator(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ObjectExpression):
            self.__handle_estree_esprima_nodes_objectexpression(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.Property):
            self.__handle_estree_esprima_nodes_property(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ClassDeclaration):
            self.__handle_estree_esprima_nodes_classdeclaration(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ClassBody):
            self.__handle_estree_esprima_nodes_classbody(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.MethodDefinition):
            self.__handle_estree_esprima_nodes_methoddefinition(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ArrowFunctionExpression):
            self.__handle_estree_esprima_nodes_arrowfunctionexpression(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.AsyncArrowFunctionExpression):
            self.__handle_estree_esprima_nodes_asyncarrowfunctionexpression(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ExportDefaultDeclaration):
            self.__handle_estree_esprima_nodes_exportdefaultdeclaration(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ExportNamedDeclaration):
            self.__handle_estree_esprima_nodes_exportnameddeclaration(path, current_node, **kwargs)
        elif not isinstance(current_node, esprima.nodes.ImportDeclaration) and\
                not isinstance(current_node, esprima.nodes.Literal) and \
                not isinstance(current_node, esprima.nodes.BinaryExpression) and \
                not isinstance(current_node, esprima.nodes.Identifier):
            logging.warning("Type not yet implemented and cannot be analyzed: " + str(type(current_node)))
            return

    def process_functions(self):
        """ Will walk through the AST and process all found functions.

        :return: A list of all the found functions and their meta data.
        :rtype: list
        """
        self.__find_all_functions("/", self.esprima_tree)
        return self.processed_functions


def analyze_files(list_of_files):
    """Analyze list of files

    :param list_of_files: The list of files to analyze
    :type list_of_files: list

    :raises:
        TypeError: If the passed 'list_of_files' is of the wrong type.
        ValueError: If the passed 'list_of_files' is empty.

    :return:
    """
    if not isinstance(list_of_files, list):
        raise TypeError("'list_of_files' must be a LIST")
    elif len(list_of_files) < 1:
        raise ValueError("'list_of_files' cannot be empty")

    processed_files = []

    for current_file in list_of_files:
        if not isinstance(current_file, str):
            raise ValueError("'list_of_files' must only contain paths to files as STRINGS")
        elif len(current_file) < 1:
            raise ValueError("Paths in 'list_of_files' cannot be empty strings")

        with open(current_file, 'r') as file:
            analyze_handler = EsprimaAnalyze(file.read())
            processed_functions = analyze_handler.process_functions()

            processed_files.append({
                'filename': current_file,
                'processed_functions': processed_functions
            })

    # TODO: Remove debug print
    for processed_file in processed_files:
        for processed_function in processed_file['processed_functions']:
            print(processed_file['filename'], processed_function['identifier'], processed_function['arguments'])

    calculate_dependencies(processed_files)

    return 0
