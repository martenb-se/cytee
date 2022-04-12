from copy import deepcopy
import esprima
import re
from api.analyzer.logging_analyzer import logging


class AnalyzeJS:
    __METHOD_STRING_IDENTITY_UNKNOWN = "!unknown"
    __METHOD_STRING_IDENTITY_IGNORE = "!ignore"

    def __init__(self, file_location, project_root=""):
        """Analyzer for JavaScript project files.

        :param file_location: The JS file to analyze.
        :type file_location: str
        :param project_root: The root directory for the whole project.
        :type project_root: str
        """
        if not isinstance(file_location, str):
            raise TypeError("'file_location' must be a STRING")
        elif len(file_location) < 1:
            raise ValueError("'file_location' cannot be empty")

        if not isinstance(project_root, str):
            raise TypeError("'project_root' must be a STRING")

        try:
            with open(file_location, 'r') as file:
                self.file_source = file.read()
                self.esprima_tree = esprima.parseModule(self.file_source, {"range": True})

        except Exception:
            raise ValueError("Contents in file at 'file_location' string could not be parsed.")

        self.file_location = file_location
        self.project_root = project_root
        self.file_identity = re.sub(r'' + re.escape(self.project_root) + r'|\.jsx?$', '', self.file_location)
        self.created_functions = {}
        self.class_information = {}

    def __find_scope_method_identity(self, path, method):
        """Find possible dependency on method starting from current scope inside the AST (path).

        :param path: Path to the start the search backwards up the AST from.
        :type path: list
        :param method: The method to search for.
        :type method: str

        :return: Tuple with the current found file identity and '!unknown' if the method definition cannot be found,
        the found file identity and '!ignore' if the found method definition isn't an actual dependency and the
        the found file identity and the method string identity if the method might be a dependency.
        :rtype: tuple
        """
        file_identity = self.file_identity
        string_identity = self.__METHOD_STRING_IDENTITY_UNKNOWN
        pre_call_chain = []

        path_search = path
        while len(path_search) > 0:
            search_results = self.__find_all_by_prop_value("name", method, path_search)
            for search_result in search_results:
                is_search_result_a_method_call = search_result[-1] == 'callee' or \
                                                 search_result[-1] == 'property' and search_result[-2] == 'callee'

                parent_parent_node = self.__go_to_absolute_path(search_result[:-2])
                is_search_result_property_of_member_expression = \
                    not isinstance(parent_parent_node, list) and \
                    'callee' in parent_parent_node.__dict__ and \
                    isinstance(parent_parent_node.callee, esprima.nodes.StaticMemberExpression)

                if is_search_result_property_of_member_expression and not is_search_result_a_method_call:
                    if isinstance(parent_parent_node.callee.object, esprima.nodes.Identifier):
                        method = parent_parent_node.callee.object.name
                        current_node = parent_parent_node.callee
                        pre_call_chain = [{'node_search': current_node,
                                           'path_search': search_result[:-2] + ['callee'],
                                           'node_key': 'property'}]
                    elif isinstance(parent_parent_node.callee.object, esprima.nodes.CallExpression):
                        method = parent_parent_node.callee.object.callee.name
                        current_node = parent_parent_node.callee
                        pre_call_chain = [{'node_search': current_node,
                                           'path_search': search_result[:-2] + ['callee'],
                                           'node_key': 'property'}]
                    else:
                        logging.warning(
                            "Unknown member expression object: " + str(type(parent_parent_node.callee.object)))

                elif not is_search_result_a_method_call:
                    is_search_result_a_method_parameter = 'params' in search_result
                    if is_search_result_a_method_parameter:
                        string_identity = self.__METHOD_STRING_IDENTITY_IGNORE
                    else:
                        file_identity, string_identity = self.__create_identity_from_call_chain(
                            self.__create_call_chain(search_result, pre_call_chain))

                    return file_identity, string_identity

            path_search = path_search[:-1]

        return file_identity, string_identity

    def __find_method_calls(self, path):
        """Find all method calls searching the AST from current 'path'.

        :param path: The path to the AST node where the search will begin.
        :type path: list
        :return: All found method calls first labeled by their file identity and then by their method string identity.
        :rtype: dict
        """
        method_calls = {}
        for method_call_path in self.__find_all_by_prop_value("type", "CallExpression", path):
            if 'callee' in self.__go_to_absolute_path(method_call_path).__dict__:
                string_identity = self.__METHOD_STRING_IDENTITY_UNKNOWN
                file_identity = self.file_identity
                callee_node = self.__go_to_absolute_path(method_call_path).callee
                if isinstance(callee_node, esprima.nodes.Identifier):
                    file_identity, string_identity = \
                        self.__find_scope_method_identity(method_call_path, callee_node.name)
                elif isinstance(callee_node, esprima.nodes.StaticMemberExpression):
                    file_identity, string_identity = \
                        self.__find_scope_method_identity(method_call_path, callee_node.property.name)
                else:
                    logging.warning("Method call has unknown callee type: " + str(type(callee_node)))

                if file_identity not in method_calls:
                    method_calls[file_identity] = {}

                if string_identity in method_calls[file_identity]:
                    method_calls[file_identity][string_identity] += 1
                else:
                    method_calls[file_identity][string_identity] = 1

            else:
                logging.warning("No callee in CallExpression found at: " + self.__get_path_string(method_call_path))

        return method_calls

    def __handle_and_append_argument(self, arguments, current_parameter):
        """Handle specific argument types when creating an ordered list of arguments, alters the 'arguments' list
        to include the handled arguments.

        :param arguments: The handled arguments.
        :type arguments: list
        :param current_parameter: The current method parameter to handle.
        :type current_parameter: esprima.nodes.Property|esprima.nodes.ObjectExpression|esprima.nodes.RestElement

        :return: Nothing
        """
        if isinstance(current_parameter, esprima.nodes.Identifier):
            arguments.append(current_parameter.name)

        elif isinstance(current_parameter, esprima.nodes.Property):
            self.__handle_and_append_argument(arguments, current_parameter.key)

        elif isinstance(current_parameter, esprima.nodes.ObjectExpression):
            object_argument = []
            for current_property in current_parameter.properties:
                self.__handle_and_append_argument(object_argument, current_property)
            arguments.append(object_argument)

        elif isinstance(current_parameter, esprima.nodes.RestElement):
            arguments.append(['...'])

        # TODO: Must be expanded to handle the crazy arguments like:
        #   https://github.com/oldboyxx/jira_clone/blob/26a9e77b1789fef9cb43edb5d6018cf1663cf035/client/src/shared/utils/styles.js#L140
        #   What this is: https://stackoverflow.com/questions/26578167/es6-object-destructuring-default-parameters
        #   To implement:
        #     - Must support: left hand <class 'esprima.nodes.ObjectExpression'>
        #     - Must support: right hand right <class 'esprima.nodes.StaticMemberExpression'>
        #   Code should be moved to own method...
        #
        elif isinstance(current_parameter, esprima.nodes.AssignmentExpression):
            if 'left' in current_parameter.__dict__ and 'right' in current_parameter.__dict__:
                if isinstance(current_parameter.__dict__['left'], esprima.nodes.Identifier):
                    if isinstance(current_parameter.__dict__['right'], esprima.nodes.Literal):
                        arguments.append({
                            current_parameter.__dict__['left'].__dict__['name']:
                                current_parameter.__dict__['right'].__dict__['value']})
                    else:
                        logging.warning("AssignmentExpression right hand assignment typ not understood: " +
                                        str(type(current_parameter.__dict__['right'])))
                else:
                    logging.warning("AssignmentExpression left hand assignment typ not understood: " +
                                    str(type(current_parameter.__dict__['left'])))
            else:
                logging.warning("AssignmentExpression variant not yet implemented and cannot be analyzed: " +
                                str(type(current_parameter)))
        else:
            logging.warning("Argument type not yet implemented and cannot be analyzed: " + str(type(current_parameter)))

    def __make_argument_list(self, argument_node_list):
        """Create a simple ordered argument list from an argument list containing AST nodes.

        :param argument_node_list: A list of the method arguments as AST nodes.
        :type argument_node_list: list
        :return: The ordered argument list.
        """
        arguments = []
        if isinstance(argument_node_list, list):
            for current_node_argument in argument_node_list:
                self.__handle_and_append_argument(arguments, current_node_argument)
        return arguments

    def __find_method_arguments(self, current_node):
        """Find all AST node arguments under the 'current_node'.

        :param current_node: The node to find the arguments under.
        :type current_node: esprima.nodes.VariableDeclarator|esprima.nodes.Property

        :return: An ordered list of method arguments.
        """
        if not (isinstance(current_node, esprima.nodes.VariableDeclarator) or
                isinstance(current_node, esprima.nodes.Property)):
            logging.warning("Called __find_method_arguments() with unknown node type: " + str(type(current_node)))

        function_arguments = []
        if 'value' in current_node.__dict__ and 'params' in current_node.__dict__['value'].__dict__:
            function_arguments = self.__make_argument_list(current_node.__dict__['value'].__dict__['params'])
        elif 'init' in current_node.__dict__ and 'params' in current_node.__dict__['init'].__dict__:
            function_arguments = self.__make_argument_list(current_node.__dict__['init'].__dict__['params'])
        return function_arguments

    def __call_chain_entry_handle_import(self, chain_entry, current_node, current_path):
        """Handle the current node if it is an import statement, alters the 'chain_entry' dict to include information
        about an imported method name and the original name.

        :param chain_entry: The chain entry to handle a possible esprima.nodes.ImportSpecifier for.
        :type chain_entry: dict
        :param current_node: The node to handle.
        :type current_node: esprima.nodes.*
        :param current_path: Path to the node to handle.
        :type current_path: list
        :return: Nothing
        """
        if isinstance(current_node, esprima.nodes.ImportSpecifier) or \
                isinstance(current_node, esprima.nodes.ImportDefaultSpecifier):
            import_declaration = self.__go_to_absolute_path(current_path[:-2])
            if 'source' in import_declaration.__dict__:
                if isinstance(import_declaration.__dict__['source'], esprima.nodes.Literal):
                    chain_entry['file_identity'] = import_declaration.__dict__['source'].__dict__['value']
                else:
                    logging.warning("Call chain entry: Import type not yet supported: ",
                                    str(type(import_declaration.__dict__['source'])))
            else:
                logging.warning("'Call chain entry: Source not found in import at: ",
                                self.__get_path_string(current_path[:-2]))

            if isinstance(current_node, esprima.nodes.ImportSpecifier):
                chain_entry['name'] = current_node.__dict__['local'].__dict__['name']
                chain_entry['external_name'] = current_node.__dict__['imported'].__dict__['name']
            elif isinstance(current_node, esprima.nodes.ImportDefaultSpecifier):
                chain_entry['name'] = current_node.__dict__['local'].__dict__['name']
                chain_entry['external_name'] = current_node.__dict__['local'].__dict__['name']

    def __call_chain_entry_handle_arguments(self, chain_entry, current_node, current_path):
        """Handle the current node's arguments, whether it's a normal method or a class' instantiation arguments, alters
        the 'chain_entry' dict to include the argument information.

        For classes, it will use self.class_information cache in order to find instantiation arguments, and whenever
        cache is nonexistent, it will be created once arguments have been found for quicker chain entry creation.

        :param chain_entry: The chain entry to handle arguments for.
        :type chain_entry: dict
        :param current_node: The node to handle.
        :type current_node: esprima.nodes.*
        :param current_path: Path to the node to handle.
        :type current_path: list
        :return: Nothing
        """
        if isinstance(current_node, esprima.nodes.ClassDeclaration):
            if chain_entry['name'] in self.class_information:
                chain_entry['arguments'] = self.class_information[chain_entry['name']]['arguments']
            else:
                node_class_constructor = \
                    self.__go_to_absolute_path(self.__find_by_prop_value("name", "constructor", current_path)[:-1])
                chain_entry['arguments'] = self.__find_method_arguments(node_class_constructor)
                self.class_information[chain_entry['name']] = {'arguments': chain_entry['arguments']}
        elif (isinstance(current_node, esprima.nodes.VariableDeclarator) or
              isinstance(current_node, esprima.nodes.Property)):
            chain_entry['arguments'] = self.__find_method_arguments(current_node)

        elif not (isinstance(current_node, esprima.nodes.ImportSpecifier) or
                  isinstance(current_node, esprima.nodes.ImportDefaultSpecifier) or
                  isinstance(current_node, esprima.nodes.CallExpression) or
                  isinstance(current_node, esprima.nodes.StaticMemberExpression)):
            logging.warning("__call_chain_entry_handle_arguments: not yet checked type: " + str(type(current_node)))
            logging.warning(str(current_node))

    def __create_call_chain_entry(self, current_node, current_path, current_node_property):
        """Create a call chain entry base from the current AST node and node property.

        :param current_node: The AST node to create the call chain entry for.
        :type current_node: esprima.nodes.*
        :param current_node_property: The name of the current node property to create the chain entry for.
        :type current_node_property: str

        :return: The call chain entry.
        :rtype: dict
        """
        chain_entry = {'name': current_node.__dict__[current_node_property].__dict__['name'],
                       'external_name': current_node.__dict__[current_node_property].__dict__['name'],
                       'path': current_path,
                       'type': None,
                       'static': True,
                       'file_identity': self.file_identity,
                       'arguments': []}

        if 'type' in current_node.__dict__:
            chain_entry['type'] = type(current_node)

        if 'static' in current_node.__dict__:
            chain_entry['static'] = current_node.__dict__['static']

        self.__call_chain_entry_handle_import(chain_entry, current_node, current_path)
        self.__call_chain_entry_handle_arguments(chain_entry, current_node, current_path)

        return chain_entry

    def __create_call_chain(self, path, existing_call_chain=None):
        """Create a method call chain to the current path in the AST.

        :param path: The path to create the method call chain for.
        :type path: list

        :return: The method call chain.
        :rtype: list
        """
        if existing_call_chain is None:
            existing_call_chain = []

        call_chain = []
        path_search = path
        node_search = self.__go_to_absolute_path(path_search)

        for call_chain_prep in existing_call_chain:
            prep_call = self.__create_call_chain_entry(call_chain_prep['node_search'], call_chain_prep['path_search'],
                                                       call_chain_prep['node_key'])
            call_chain.append(prep_call)

        while len(path_search) > 0:
            if hasattr(node_search, '__dict__'):
                for node_key in node_search.__dict__:
                    if isinstance(node_search.__dict__[node_key], esprima.nodes.Identifier):
                        is_node_inside_promise = node_search.__dict__[node_key].__dict__['name'] == 'Promise' and \
                                                 isinstance(node_search, esprima.nodes.NewExpression)
                        if is_node_inside_promise:
                            call_chain = []
                        else:
                            current_call = self.__create_call_chain_entry(node_search, path_search, node_key)
                            call_chain.append(current_call)

                            # Only add one call at current level
                            break

            path_search = path_search[:-1]
            node_search = self.__go_to_absolute_path(path_search)

        call_chain.reverse()

        return call_chain

    def __create_identity_from_call_chain(self, call_chain):
        """Create a string identity tuple from the given call chain.

        :param call_chain: The call chain to create the identity for.
        :type call_chain: list

        :return: A tuple containing the string identity for the filename and a string identity for the method call.
        :rtype: tuple
        """
        file_identity = self.file_identity
        identity = []

        for chain_index, current_call in enumerate(call_chain):
            if current_call['type'] is esprima.nodes.ClassDeclaration:
                if len(call_chain) <= chain_index + 1:
                    logging.warning("Cannot create unique identity for a complete class, the call chain must end at "
                                    "some method, not a full class.")
                    break

                if call_chain[chain_index + 1]['static']:
                    identity.append(current_call['name'])
                elif not call_chain[chain_index + 1]['static']:
                    identity.append("(new " + current_call['name'] + "())")

            elif current_call['type'] is esprima.nodes.MethodDefinition or \
                    current_call['type'] is esprima.nodes.Property or \
                    current_call['type'] is esprima.nodes.VariableDeclarator or \
                    current_call['type'] is esprima.nodes.CatchClause or \
                    current_call['type'] is esprima.nodes.StaticMemberExpression:
                identity.append(current_call['name'])

            elif current_call['type'] is esprima.nodes.ImportSpecifier:
                identity.append(current_call['external_name'])
                file_identity = current_call['file_identity']

            elif current_call['type'] is esprima.nodes.ImportDefaultSpecifier:
                identity.append(current_call['name'])
                file_identity = current_call['file_identity']

            else:
                logging.warning("Identity type not yet implemented: " + str(current_call['type']))

        return file_identity, '.'.join(identity)

    def __save_created_method(self, string_identity, current_node, call_chain):
        """Save found method creation in the AST to the cache of all found method creations.

        :param string_identity: The string identity for the method to save.
        :type string_identity: str
        :param current_node: The method AST node.
        :type current_node: esprima.nodes.*
        :param call_chain: The call chain to the method.
        :type call_chain: list

        :return: Nothing
        """
        if string_identity in self.created_functions and \
                current_node.__dict__['range'][0] <= \
                self.created_functions[string_identity]['current_node'].__dict__['range'][0] and \
                current_node.__dict__['range'][1] >= \
                self.created_functions[string_identity]['current_node'].__dict__['range'][1] or \
                string_identity not in self.created_functions:
            self.created_functions[string_identity] = {
                'current_node': current_node,
                'call_chain': call_chain
            }

    def __handle_node_method_declaration(self, path, current_node):
        """Handle an AST node method declaration and save found method declarations to cache.

        :param path: The path to the AST node.
        :type path: list
        :param current_node: The current AST node.
        :type current_node: esprima.nodes.MethodDefinition|esprima.nodes.ArrowFunctionExpression|
        esprima.nodes.AsyncArrowFunctionExpression|esprima.nodes.AsyncFunctionDeclaration|
        esprima.nodes.AsyncFunctionExpression|esprima.nodes.FunctionDeclaration|esprima.nodes.FunctionExpression

        :return: Nothing
        """
        if isinstance(current_node, esprima.nodes.MethodDefinition) or \
                isinstance(current_node, esprima.nodes.ArrowFunctionExpression) or \
                isinstance(current_node, esprima.nodes.AsyncArrowFunctionExpression) or \
                isinstance(current_node, esprima.nodes.AsyncFunctionDeclaration) or \
                isinstance(current_node, esprima.nodes.AsyncFunctionExpression) or \
                isinstance(current_node, esprima.nodes.FunctionDeclaration) or \
                isinstance(current_node, esprima.nodes.FunctionExpression):
            call_chain = self.__create_call_chain(path)
            file_identity, string_identity = self.__create_identity_from_call_chain(call_chain)

            if not (len(call_chain) >= 2 and
                    call_chain[-1]['type'] is esprima.nodes.MethodDefinition and
                    call_chain[-1]['name'] == 'constructor' and
                    call_chain[-2]['type'] is esprima.nodes.ClassDeclaration):
                self.__save_created_method(string_identity, current_node, call_chain)

    def __get_path_string(self, path):
        """Convert the given AST path to a string.

        :param path: The path to convert to a string.
        :type path: list

        :return: The string path.
        """
        return '/'.join(path)

    def __handle_node(self, path, current_node):
        """Handle current AST node of any type.

        At current state of static analysis only handles method declarations.

        :param path: The path to the AST node.
        :type path: list
        :param current_node: The current AST node.
        :type current_node: esprima.nodes.*

        :return: Nothing
        """
        self.__handle_node_method_declaration(path, current_node)

    def __get_sub_paths(self, current_path=None):
        """Find all possible sub-paths from the given path.

        :param current_path: The path to find all sub-paths from.
        :type current_path: list|None

        :return: A list of all found paths.
        :rtype: list
        """
        if current_path is None:
            current_path = []

        possible_paths = []
        current_node = self.__go_to_absolute_path(current_path)

        if hasattr(current_node, '__dict__'):
            for node_key in current_node.__dict__:
                if not isinstance(current_node.__dict__[node_key], str) and \
                        not isinstance(current_node.__dict__[node_key], int) and \
                        not re.match(r"^(range)$", node_key):
                    possible_paths.append(current_path + [node_key])

        elif isinstance(current_node, list):
            for node_index, node_alt in enumerate(current_node):
                possible_paths.append(current_path + [str(node_index)])

        elif current_node is not None and not isinstance(current_node, re.Pattern):
            logging.warning("Type not yet implemented and cannot be analyzed: " + str(type(current_node)))

        return possible_paths

    def __analyze_ast(self, path, current_node):
        """Recursively walk down the complete AST and analyze each node by calling the general AST node handler.

        :param path: The current path in the AST.
        :type path: list
        :param current_node: The current AST node.
        :type current_node: esprima.nodes.*|list

        :return: Nothing.
        """
        self.__handle_node(path, current_node)

        for sub_path in self.__get_sub_paths(path):
            sub_node = self.__go_to_absolute_path(sub_path)
            self.__analyze_ast(sub_path, sub_node)

    def __find_by_prop_value(self, prop, value, current_path=None):
        """Find AST node by given property name holding the specified value.

        :param prop: The property name to look for.
        :type prop: str
        :param value: The value for the property.
        :type value: str
        :param current_path: The path to start searching from.
        :type current_path: list

        :return: Return the path to the AST node if found, otherwise False is returned.
        :rtype: list|bool
        """
        if current_path is None:
            current_path = []

        current_node = self.__go_to_absolute_path(current_path)
        if hasattr(current_node, '__dict__') and \
                prop in current_node.__dict__ and current_node.__dict__[prop] == value:
            return current_path

        for sub_path in self.__get_sub_paths(current_path):
            sub_path_result = self.__find_by_prop_value(prop, value, sub_path)
            if sub_path_result is not False:
                return sub_path_result

        return False

    def __find_all_by_prop_value(self, prop, value, current_path=None):
        """Find AST nodes by given property name holding the specified value.

        :param prop: The property name to look for.
        :type prop: str
        :param value: The value for the property.
        :type value: str
        :param current_path: The path to start searching from.
        :type current_path: list

        :return: Return the path to all found AST nodes in a list, if nothing is found an empty list is returned.
        :rtype: list
        """
        if current_path is None:
            current_path = []

        current_node = self.__go_to_absolute_path(current_path)
        results = []

        if hasattr(current_node, '__dict__') and \
                prop in current_node.__dict__ and current_node.__dict__[prop] == value:
            results += [current_path]

        for sub_path in self.__get_sub_paths(current_path):
            results += self.__find_all_by_prop_value(prop, value, sub_path)

        return results

    def __go_to_absolute_path(self, path):
        """Go to an retrieve an AST node from an absolute AST path either as a string or an array.

        :param path: The path to the AST node to get.
        :type path: str|list

        :return: The AST node
        :rtype: esprima.nodes.*|list
        """
        current_node = self.esprima_tree

        walk_path = []
        if isinstance(path, str):
            walk_path = path.split("/")
        elif isinstance(path, list):
            walk_path = deepcopy(path)

        while len(walk_path) > 0:
            cur_path = walk_path.pop(0)

            if cur_path.isdecimal():
                cur_path = int(cur_path)

            if callable(getattr(current_node, "keys", None)):
                current_node = current_node.__dict__[cur_path]
            elif isinstance(current_node, list):
                current_node = current_node[cur_path]

        return current_node

    def begin_analyze(self):
        """Start analyzing  the loaded file.

        :return:
        """
        self.__analyze_ast([], self.esprima_tree)

    def get_file_identity(self):
        return self.file_identity

    def get_functions(self):
        return self.created_functions

    def get_method_calls(self, function_identity):
        path_to_function = self.created_functions[function_identity]['call_chain'][-1]['path']
        return self.__find_method_calls(path_to_function)


def analyze_files(list_of_files, project_root=""):
    """Analyze list of files

    :param list_of_files: The list of files to analyze
    :type list_of_files: list
    :param project_root: The project root directory
    :type project_root: str

    :raises:
        TypeError: If the passed 'list_of_files' is of the wrong type.
        ValueError: If the passed 'list_of_files' is empty.

    :return: ?
    TODO: Specify return
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

        print("Current file: ", current_file)

        analyzer = AnalyzeJS(current_file, project_root=project_root)

        # TODO: Announce to callback or something that file X of Y is being analyzed (needed for loading info)
        analyzer.begin_analyze()

        # TODO: Add ability to save analyzed data to database
        # TODO: Add caching of analyzed files.

    return
