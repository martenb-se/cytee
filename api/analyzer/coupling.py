import esprima
from api.analyzer.logging_analyzer import logging


class EsprimaCoupling:
    """Esprima handler for coupling calculation

    :param function_ast: The function AST
    :type function_ast: esprima.nodes.*
    """

    def __init__(self, function_ast):
        self.function_ast = function_ast

    def __handle_estree_list(self, path, current_node, **kwargs):
        for index, node_in_list in enumerate(current_node):
            self.__find_method_calls(path + str(index + 1) + "/", node_in_list, **kwargs)

    def __handle_estree_esprima_nodes_module(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_method_calls(path + "body/", current_node.body, **kwargs)

    def __handle_estree_esprima_nodes_variabledeclaration(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_method_calls(path + "declarations/", current_node.declarations, **kwargs)

    def __handle_estree_esprima_nodes_variabledeclarator(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_method_calls(path + "init/", current_node.init, **kwargs)

    def __handle_estree_esprima_nodes_objectexpression(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_method_calls(path + "properties/", current_node.properties, **kwargs)

    def __handle_estree_esprima_nodes_property(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_method_calls(path + "value/", current_node.value, **kwargs)

    def __handle_estree_esprima_nodes_classdeclaration(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_method_calls(path + "class_body/", current_node.body, **kwargs)

    def __handle_estree_esprima_nodes_classbody(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        self.__find_method_calls(path + "body/", current_node.body, **kwargs)

    def __handle_estree_esprima_nodes_methoddefinition(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        # print(type(current_node))  # TODO: Remove line
        # print(current_node.keys())  # TODO: Remove line

    def __handle_estree_esprima_nodes_arrowfunctionexpression(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        # print(type(current_node))  # TODO: Remove line
        # print(current_node.keys())  # TODO: Remove line
        self.__find_method_calls(path + "body/", current_node.body, **kwargs)

    def __handle_estree_esprima_nodes_asyncarrowfunctionexpression(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        print(type(current_node))  # TODO: Remove line
        print(current_node.keys())  # TODO: Remove line

    def __handle_estree_esprima_nodes_binaryexpression(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        print(type(current_node))  # TODO: Remove line
        print(current_node.keys())  # TODO: Remove line

    def __handle_estree_esprima_nodes_conditionalexpression(self, path, current_node, **kwargs):
        logging.debug("AST Path: " + path)
        print(type(current_node))  # TODO: Remove line
        print(current_node.keys())  # TODO: Remove line

    def __find_method_calls(self, path, current_node, **kwargs):
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
        elif isinstance(current_node, esprima.nodes.BinaryExpression):
            self.__handle_estree_esprima_nodes_binaryexpression(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ConditionalExpression):
            self.__handle_estree_esprima_nodes_conditionalexpression(path, current_node, **kwargs)
        elif not isinstance(current_node, esprima.nodes.ImportDeclaration) and\
                not isinstance(current_node, esprima.nodes.Literal) and \
                not isinstance(current_node, esprima.nodes.ExportDefaultDeclaration) and \
                not isinstance(current_node, esprima.nodes.ExportNamedDeclaration):
            logging.warning("Type not yet implemented and cannot be analyzed: " + str(type(current_node)))
            return

    def find_method_calls(self):
        self.__find_method_calls("/", self.function_ast)


def calculate_dependencies(processed_files):
    for processed_file in processed_files:
        for processed_function in processed_file['processed_functions']:

            print(processed_function['identifier'])  # TODO: Remove line

            couple_handler = EsprimaCoupling(processed_function['function_ast'])
            couple_handler.find_method_calls()

            # TODO: Continue with coupling
            #   - After having found all calls (CallExpression), match to processed functions
            #   - Add to dependency list (by their identification)

            print("Work in progress")  # TODO: Remove line
            break  # TODO: Remove line

        break  # TODO: Remove line
