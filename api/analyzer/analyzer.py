import esprima
from copy import deepcopy


class HandleEsprima:
    """Esprima handler

    :param file_source: The file source code to use.
    :type file_source: str
    """

    def __init__(self, file_source):
        if not isinstance(file_source, str):
            raise TypeError("'file_source' must be a STRING")
        elif len(file_source) < 1:
            raise ValueError("'file_source' cannot be empty")

        try:
            self.file_source = file_source
            self.esprima_tree = esprima.parseModule(file_source, {"range": True})
        except Exception:
            raise ValueError("'file_source' string could not be parsed.")

    def __generate_function_declaration(self, current_node, **kwargs):
        declaration_kind = kwargs.get('current_declaration_kind', "")
        variable_chain = kwargs.get('variable_chain', [])
        function_declaration = declaration_kind + " "

        if len(variable_chain) == 0:
            raise ValueError("Keyword arg 'variable_chain' is empty. Cannot create a declaration for an anonymous "
                             "function")

        function_declaration = function_declaration + variable_chain[0]

        for declaration_chain_length in range(1, len(variable_chain)):
            function_declaration = \
                function_declaration + \
                " = {};\n" + \
                '.'.join(variable_chain[:(declaration_chain_length + 1)]) + " "

        function_declaration = \
            function_declaration + \
            " = " + \
            self.file_source[current_node.range[0]:current_node.range[1]] + \
            ";"

        return function_declaration

    def __handle_estree_list(self, path, current_node, **kwargs):
        # [{}, {}, {}, ...] -- TODO: Remove comment when done
        for index, node_in_list in enumerate(current_node):
            self.__find_all_functions(path + str(index + 1) + "/", node_in_list, **kwargs)

    def __handle_estree_esprima_nodes_module(self, path, current_node, **kwargs):
        # 'type', 'sourceType', 'body', 'range' -- TODO: Remove comment when done
        print(path)  # -- TODO: Remove line when done

        # Enter 'body' -- TODO: Remove comment when done
        self.__find_all_functions(path + "body/", current_node.body, **kwargs)

    def __handle_estree_esprima_nodes_importdeclaration(self, path, current_node, **kwargs):
        # print("ImportDeclaration", current_node.keys()) -- TODO: Remove comment when done
        # 'type', 'specifiers', 'source', 'range' -- TODO: Remove comment when done
        # Stop here. Not interesting. -- TODO: Remove comment when done
        return

    def __handle_estree_esprima_nodes_variabledeclaration(self, path, current_node, **kwargs):
        # print("VariableDeclaration", current_node.keys()) -- TODO: Remove comment when done
        # 'type', 'declarations', 'kind', 'range' -- TODO: Remove comment when done
        print(path)  # -- TODO: Remove line when done

        # Enter 'declarations' -- TODO: Remove comment when done
        kwargs['current_declaration_kind'] = current_node.kind
        self.__find_all_functions(path + "declarations/", current_node.declarations, **kwargs)

    def __handle_estree_esprima_nodes_variabledeclarator(self, path, current_node, **kwargs):
        # print("VariableDeclarator", current_node.keys()) -- TODO: Remove comment when done
        # 'type', 'id', 'init', 'range' -- TODO: Remove comment when done
        print(path)  # -- TODO: Remove line when done

        # Set variable chain -- TODO: Remove comment when done
        kwargs_pass = deepcopy(kwargs)
        variable_chain = kwargs_pass.get('variable_chain', [])
        variable_chain.append(current_node.id.name)
        kwargs_pass['variable_chain'] = variable_chain

        # Enter 'init' -- TODO: Remove comment when done
        self.__find_all_functions(path + "init/", current_node.init, **kwargs_pass)

    def __handle_estree_esprima_nodes_objectexpression(self, path, current_node, **kwargs):
        # print("ObjectExpression", current_node.keys()) -- TODO: Remove comment when done
        # 'type', 'properties', 'range' -- TODO: Remove comment when done
        print(path)  # -- TODO: Remove line when done

        # Enter 'properties' -- TODO: Remove comment when done
        self.__find_all_functions(path + "properties/", current_node.properties, **kwargs)

    def __handle_estree_esprima_nodes_property(self, path, current_node, **kwargs):
        # print("Property", current_node.keys()) -- TODO: Remove comment when done
        # 'type', 'key', 'computed', 'value', 'kind', 'method', 'shorthand', 'range' -- TODO: Remove comment when done
        print(path)  # -- TODO: Remove line when done

        # Set variable chain -- TODO: Remove comment when done
        kwargs_pass = deepcopy(kwargs)
        variable_chain = kwargs_pass.get('variable_chain', [])
        variable_chain.append(current_node.key.name)
        kwargs_pass['variable_chain'] = variable_chain

        # Enter 'value' -- TODO: Remove comment when done
        self.__find_all_functions(path + "value/", current_node.value, **kwargs_pass)

    def __handle_estree_esprima_nodes_arrowfunctionexpression(self, path, current_node, **kwargs):
        # print("ArrowFunctionExpression", current_node.keys()) -- TODO: Remove comment when done
        # 'type', 'generator', 'isAsync', 'params', 'body', 'expression', 'range' -- TODO: Remove comment when done
        print(path)  # -- TODO: Remove line when done

        declaration_kind = kwargs.get('current_declaration_kind', "")  # -- TODO: Remove line when done
        print("type:", kwargs.get('current_declaration_kind', ""))  # -- TODO: Remove line when done
        print("variable:", '.'.join((kwargs.get('variable_chain', []))))  # -- TODO: Remove line when done
        print("range:", current_node.range)  # -- TODO: Remove line when done
        print("Variable content")  # -- TODO: Remove line when done
        print(self.__generate_function_declaration(path, current_node, **kwargs))  # -- TODO: Remove line when done
        # TODO: Continue from here with more function extractions
        #   ...
        #   ...
        #   ...

    def __handle_estree_esprima_nodes_binaryexpression(self, path, current_node, **kwargs):
        # print("BinaryExpression", current_node.keys()) -- TODO: Remove comment when done
        # 'type', 'operator', 'left', 'right', 'range' -- TODO: Remove comment when done
        # Stop here. Not interesting.  # -- TODO: Remove line when done
        return

    def __handle_estree_esprima_nodes_exportdefaultdeclaration(self, path, current_node, **kwargs):
        # print("ExportDefaultDeclaration", current_node.keys()) -- TODO: Remove comment when done
        # 'type', 'declaration', 'range' -- TODO: Remove comment when done
        # Stop here. Not interesting. -- TODO: Remove comment when done
        return

    def __handle_estree_esprima_nodes_exportnameddeclaration(self, path, current_node, **kwargs):
        # print("ExportNamedDeclaration", current_node.keys()) -- TODO: Remove comment when done
        # 'type', 'declaration', 'specifiers', 'source', 'range' -- TODO: Remove comment when done
        # Stop here. Not interesting.  # -- TODO: Remove line when done
        return

    def __find_all_functions(self, path, current_node, **kwargs):
        if isinstance(current_node, list):
            self.__handle_estree_list(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.Module):
            self.__handle_estree_esprima_nodes_module(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ImportDeclaration):
            self.__handle_estree_esprima_nodes_importdeclaration(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.VariableDeclaration):
            self.__handle_estree_esprima_nodes_variabledeclaration(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.VariableDeclarator):
            self.__handle_estree_esprima_nodes_variabledeclarator(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ObjectExpression):
            self.__handle_estree_esprima_nodes_objectexpression(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.Property):
            self.__handle_estree_esprima_nodes_property(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ArrowFunctionExpression):
            self.__handle_estree_esprima_nodes_arrowfunctionexpression(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.BinaryExpression):
            self.__handle_estree_esprima_nodes_binaryexpression(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ExportDefaultDeclaration):
            self.__handle_estree_esprima_nodes_exportdefaultdeclaration(path, current_node, **kwargs)
        elif isinstance(current_node, esprima.nodes.ExportNamedDeclaration):
            self.__handle_estree_esprima_nodes_exportnameddeclaration(path, current_node, **kwargs)
        else:
            print("Unknown type:", type(current_node))
            return 1

    def find_all_functions(self):
        # -- TODO: Add documentation and/or change name
        self.__find_all_functions("/", self.esprima_tree)
        return 1


def analyze_files(list_of_files):
    """Analyze list of files

    :param list_of_files: The list of files to analyze
    :type list_of_files: list

    :raises:
        TypeError: Explanation here.
        ValueError: Explanation here.

    :return:
    """
    if not isinstance(list_of_files, list):
        raise TypeError("'list_of_files' must be a LIST")
    elif len(list_of_files) < 1:
        raise ValueError("'list_of_files' cannot be empty")

    for current_file in list_of_files:
        if not isinstance(current_file, str):
            raise ValueError("'list_of_files' must only contain paths to files as STRINGS")
        elif len(current_file) < 1:
            raise ValueError("Paths in 'list_of_files' cannot be empty strings")

        with open(current_file, 'r') as file:
            print("current_file", current_file)
            # print("file", file) -- TODO: Remove comment when done
            # print("file.read()", file.read()) -- TODO: Remove comment when done
            # parsed_source = esprima.parseModule(file.read(), {"range": True}) -- TODO: Remove comment when done

            handler = HandleEsprima(file.read())
            handler.find_all_functions()

            # TODO: Continue from here with..
            #   - cache
            #   - cc
            #   - coupling

            # print(parsed_source) -- TODO: Remove comment when done

    return 0
