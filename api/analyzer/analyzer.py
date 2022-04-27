import hashlib
import os
from copy import deepcopy
from os.path import exists
import esprima
import re
import yaml
from api.instances.logging_standard import logging
from api.cache import save_file, read_file, clear_cache
from api.instances.database_main import database_handler
from api.instances.shared_websockets_main import shared_websockets_handler
from api.util.paths_helper import full_path_to_correct_sub_directory
from api.websocket import WsIdentity, WsCode, WsClientCode

METHOD_STRING_IDENTITY_UNKNOWN = "!unknown"
METHOD_STRING_IDENTITY_IGNORE = "!ignore"


class AnalyzerConfig:
    __STANDARD_CONFIG_LOCATION = \
        os.path.abspath(
            os.path.dirname(os.path.abspath(__file__)) +
            f"/../../analyze.config.yml")

    def __init__(self, config_location=None):
        if not exists(self.__STANDARD_CONFIG_LOCATION):
            raise FileNotFoundError(
                "AnalyzerConfig could not find standard config file "
                f"'{self.__STANDARD_CONFIG_LOCATION}'.")

        if config_location is not None:
            if not isinstance(config_location, str):
                raise TypeError("'config_location' must be a STRING")
            elif len(config_location) < 1:
                raise ValueError("'config_location' cannot be empty")
            elif not exists(config_location):
                raise FileNotFoundError(
                    f"Alternative config file '{config_location}' "
                    "cannot be found")

        if config_location is None:
            if exists(self.__STANDARD_CONFIG_LOCATION):
                self.config_location = self.__STANDARD_CONFIG_LOCATION

        else:
            self.config_location = config_location

        # Thanks: https://stackoverflow.com/a/29809015
        yaml.SafeLoader.add_constructor(
            u'tag:yaml.org,2002:python/regexp',
            lambda l,
            n: re.compile(l.construct_scalar(n)))

        self.config = yaml.safe_load(open(self.config_location))

    def __regex_list_matcher(self, paths_to_list, string_to_match):
        """Generalized regex matcher for list of regular expressions found
        at defined path in the configuration file.

        :param paths_to_list: The path to the list of regular expressions in
        the configuration file.
        :type paths_to_list: list
        :param string_to_match: String to run regex matcher on.
        :type string_to_match: str
        :return: True if a pattern matches on the provided string,
        False otherwise.
        """
        found_match = False

        cur_node = self.config
        for cur_path in paths_to_list:
            if cur_path in cur_node:
                cur_node = cur_node[cur_path]

        if isinstance(cur_node, list):
            for cur_regex in cur_node:
                matches = cur_regex.findall(string_to_match)
                if len(matches) > 0:
                    found_match = True
                    break

        return found_match

    def whitelist_check(self, file_path):
        """See if a string matches a whitelisted file name.

        :param file_path: The file path to check the whitelist against.
        :type file_path: str
        :return: True if the file path matched against a whitelisted name,
        False otherwise.
        """
        path_to_whitelist_patterns = ['whitelist', 'regex']
        return self.__regex_list_matcher(path_to_whitelist_patterns, file_path)

    def blacklist_check(self, file_path):
        """See if a string matches a blacklisted file name.

        :param file_path: The file path to check the blacklist against.
        :type file_path: str
        :return: True if the file path matched against a blacklisted name,
        False otherwise.
        """
        path_to_blacklist_patterns = ['blacklist', 'regex']
        return self.__regex_list_matcher(path_to_blacklist_patterns, file_path)

    def is_file_allowed(self, file_path):
        """See if a file is okay to be loaded.

        :param file_path: The file path to check if it's allowed to be loaded.
        :type file_path: str
        :return: True if the file is okay to be loaded, False otherwise.
        """
        return \
            self.whitelist_check(file_path) and \
            not self.blacklist_check(file_path)


class AnalyzeJS:
    def __init__(self, file_location, project_root):
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
        elif len(project_root) < 1:
            raise ValueError("'project_root' cannot be empty")

        try:
            with open(file_location, 'r') as file:
                self.file_source = file.read()

        except FileNotFoundError:
            raise FileNotFoundError(
                f"File at '{file_location}' cannot be found and analyzed.")

        try:
            self.esprima_tree = esprima.parseModule(self.file_source,
                                                    {"range": True,
                                                     "jsx": True})

        except esprima.Error as e:
            raise SyntaxError(
                "Contents in file at 'file_location' string could not be "
                "parsed.\n"
                "Information from esprima:\n"
                f"{e}")

        self.file_location = os.path.abspath(file_location)
        self.project_root = os.path.abspath(project_root)

        # TODO: Fix better file identity:
        #  - If index.jsx is used in a Component/index.js manner
        self.file_identity = re.sub(r'' + re.escape(self.project_root) +
                                    r'|\.jsx?$', '', self.file_location)
        self.created_functions = {}
        self.class_information = {}

    def __debug_info_print(self):
        win_size = 120
        print(f"file_location : {self.file_location:.>{win_size}}")
        print(f"project_root  : {self.project_root:.>{win_size}}")
        print(f"file_identity : {self.file_identity:.>{win_size}}")

    def __find_scope_method_identity(self, path, method):
        """Find possible dependency on method starting from current scope
        inside the AST (path).

        :param path: Path to the start the search backwards up the AST from.
        :type path: list
        :param method: The method to search for.
        :type method: str

        :return: Tuple with the current found file identity and '!unknown' if
        the method definition cannot be found, the found file identity and
        '!ignore' if the found method definition isn't an actual dependency and
        the found file identity and the method string identity if the method
        might be a dependency.
        :rtype: tuple
        """
        file_identity = self.file_identity
        string_identity = METHOD_STRING_IDENTITY_UNKNOWN
        pre_call_chain = []

        path_search = path
        while len(path_search) > 0:
            search_results = self.__find_all_by_prop_value(
                "name",
                method,
                path_search)
            for search_result in search_results:
                is_search_result_a_method_call = \
                    search_result[-1] == 'callee' or \
                    search_result[-1] == 'property' and \
                    search_result[-2] == 'callee'

                parent_parent_node = \
                    self.__go_to_absolute_path(search_result[:-2])
                is_search_result_property_of_member_expression = \
                    not isinstance(parent_parent_node, list) and \
                    'callee' in parent_parent_node.__dict__ and \
                    isinstance(
                        parent_parent_node.callee,
                        esprima.nodes.StaticMemberExpression)

                if is_search_result_property_of_member_expression and \
                        not is_search_result_a_method_call:
                    if isinstance(
                            parent_parent_node.callee.object,
                            esprima.nodes.Identifier):
                        method = parent_parent_node.callee.object.name
                        current_node = parent_parent_node.callee
                        pre_call_chain = \
                            [{'node_search': current_node,
                              'path_search': search_result[:-2] + ['callee'],
                              'node_key': 'property'}]
                    elif isinstance(
                            parent_parent_node.callee.object,
                            esprima.nodes.CallExpression):
                        method = parent_parent_node.callee.object.callee.name
                        current_node = parent_parent_node.callee
                        pre_call_chain = \
                            [{'node_search': current_node,
                              'path_search': search_result[:-2] + ['callee'],
                              'node_key': 'property'}]
                    else:
                        logging.warning(
                            "Unknown member expression object: " +
                            str(type(parent_parent_node.callee.object)))

                elif not is_search_result_a_method_call:
                    is_search_result_a_method_parameter = \
                        'params' in search_result
                    if is_search_result_a_method_parameter:
                        string_identity = METHOD_STRING_IDENTITY_IGNORE
                    else:
                        file_identity, string_identity = \
                            self.__create_identity_from_call_chain(
                                self.__create_call_chain(
                                    search_result,
                                    pre_call_chain))

                    return file_identity, string_identity

            path_search = path_search[:-1]

        return file_identity, string_identity

    def __find_method_calls(self, path):
        """Find all method calls searching the AST from current 'path'.

        :param path: The path to the AST node where the search will begin.
        :type path: list

        :return: All found method calls first labeled by their file identity
        and then by their method string identity.
        :rtype: dict
        """
        method_calls = {}
        for method_call_path in \
                self.__find_all_by_prop_value("type", "CallExpression", path):
            if 'callee' in \
                    self.__go_to_absolute_path(method_call_path).__dict__:
                string_identity = METHOD_STRING_IDENTITY_UNKNOWN
                file_identity = self.file_identity
                callee_node = \
                    self.__go_to_absolute_path(method_call_path).callee

                if isinstance(callee_node, esprima.nodes.Identifier):
                    file_identity, string_identity = \
                        self.__find_scope_method_identity(
                            method_call_path,
                            callee_node.name)
                elif isinstance(
                        callee_node,
                        esprima.nodes.StaticMemberExpression):
                    file_identity, string_identity = \
                        self.__find_scope_method_identity(
                            method_call_path,
                            callee_node.object.name)
                else:
                    logging.warning("Method call has unknown callee type: " +
                                    str(type(callee_node)))

                if file_identity not in method_calls:
                    method_calls[file_identity] = {}

                if string_identity in method_calls[file_identity]:
                    method_calls[file_identity][string_identity] += 1
                else:
                    method_calls[file_identity][string_identity] = 1

            else:
                logging.warning("No callee in CallExpression found at: " +
                                self.__get_path_string(method_call_path))

        return method_calls

    def __simplify_esprima_ast(self, current_node=None):
        """Convert esprima AST data to a simple AST with objects, arrays,
        strings and numbers. The simple AST will not contain anything of type
        esprima.nodes.* and is compatible with anything supporting objects,
        arrays, strings and numbers.

        :param current_node: The current node to convert from.
        :type current_node: Any
        :return: The simplified AST.
        """
        if current_node is None:
            current_node = []

        object_data = ""
        if isinstance(current_node, list):
            object_data = []
            for node_index, sub_node in enumerate(current_node):
                object_data.append(
                    self.__simplify_esprima_ast(
                        sub_node))

        elif hasattr(current_node, '__dict__'):
            object_data = {}
            for sub_node_key in current_node.__dict__:
                object_data[sub_node_key] = \
                    self.__simplify_esprima_ast(
                        current_node.__dict__[sub_node_key])

        elif isinstance(current_node, str) or isinstance(current_node, int):
            object_data = current_node

        else:
            logging.warning(
                "Object not complete because of unknown data could not be "
                "handled in parameter tree: "
                f"{type(current_node)}")

        return object_data

    def __make_argument_list(self, argument_node_list):
        """Create a simple ordered argument list from an argument list
        containing AST nodes.

        :param argument_node_list: A list of the method arguments as AST nodes.
        :type argument_node_list: list
        :return: The ordered argument list.
        """
        arguments = []

        if isinstance(argument_node_list, list):
            arguments = self.__simplify_esprima_ast(argument_node_list)

        else:
            logging.warning(
                "Cannot create argument list for non list type: "
                f"{type(argument_node_list)}")

        return arguments

    def __find_method_arguments(self, current_node):
        """Find all AST node arguments under the 'current_node'.

        :param current_node: The node to find the arguments under.
        :type current_node: esprima.nodes.VariableDeclarator|
        esprima.nodes.Property|
        esprima.nodes.FunctionDeclaration|
        esprima.nodes.MethodDefinition

        :return: An ordered list of method arguments.
        """
        if not (isinstance(current_node, esprima.nodes.VariableDeclarator) or
                isinstance(current_node, esprima.nodes.Property) or
                isinstance(current_node, esprima.nodes.FunctionDeclaration) or
                isinstance(current_node, esprima.nodes.MethodDefinition)):
            logging.warning(
                "Method arguments cannot be found for unknown node type: "
                f"{type(current_node)}")
            # Uncomment to get more information about unhandled type
            # logging.warning(f"Node information: {current_node}")

        function_arguments = []
        if 'value' in current_node.__dict__ and \
                'params' in current_node.value.__dict__:
            function_arguments = self.__make_argument_list(
                current_node.value.params)
        elif 'init' in current_node.__dict__ and \
                'params' in current_node.init.__dict__:
            function_arguments = self.__make_argument_list(
                current_node.init.params)
        elif 'params' in current_node.__dict__:
            function_arguments = self.__make_argument_list(
                current_node.params)
        return function_arguments

    def __call_chain_entry_handle_import(
            self,
            chain_entry,
            current_node,
            current_path):
        """Handle the current node if it is an import statement, alters the
        'chain_entry' dict to include information about an imported method name
        and the original name.

        :param chain_entry: The chain entry to handle a possible
        esprima.nodes.ImportSpecifier for.
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
                if isinstance(
                        import_declaration.source,
                        esprima.nodes.Literal):
                    chain_entry['file_identity'] = \
                        import_declaration.source.value
                else:
                    logging.warning(
                        "Call chain entry: Import type not yet supported: ",
                        str(type(import_declaration.source)))
            else:
                logging.warning(
                    "'Call chain entry: Source not found in import at: ",
                    self.__get_path_string(current_path[:-2]))

            if isinstance(current_node, esprima.nodes.ImportSpecifier):
                chain_entry['name'] = current_node.local.name
                chain_entry['external_name'] = current_node.imported.name
            elif isinstance(current_node,
                            esprima.nodes.ImportDefaultSpecifier):
                chain_entry['name'] = current_node.local.name
                chain_entry['external_name'] = current_node.local.name

    def __call_chain_entry_handle_arguments(
            self,
            chain_entry,
            current_node,
            current_path):
        """Handle the current node's arguments, whether it's a normal method or
        a class' instantiation arguments, alters the 'chain_entry' dict to
        include the argument information.

        For classes, it will use self.class_information cache in order to find
        instantiation arguments, and whenever cache is nonexistent, it will be
        created once arguments have been found for quicker chain entry
        creation.

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
                chain_entry['arguments'] = \
                    self.class_information[chain_entry['name']]['arguments']
            elif self.__find_by_prop_value(
                    "name",
                    "constructor",
                    current_path):
                node_class_constructor = \
                    self.__go_to_absolute_path(
                        self.__find_by_prop_value(
                            "name",
                            "constructor",
                            current_path)[:-1])
                chain_entry['arguments'] = \
                    self.__find_method_arguments(node_class_constructor)
                self.class_information[chain_entry['name']] = \
                    {'arguments': chain_entry['arguments']}
        elif (isinstance(current_node, esprima.nodes.VariableDeclarator) or
              isinstance(current_node, esprima.nodes.Property) or
              isinstance(current_node, esprima.nodes.FunctionDeclaration) or
              isinstance(current_node, esprima.nodes.MethodDefinition)):
            chain_entry['arguments'] = \
                self.__find_method_arguments(current_node)

        elif not (isinstance(current_node,
                             esprima.nodes.ImportSpecifier) or
                  isinstance(current_node,
                             esprima.nodes.ImportDefaultSpecifier) or
                  isinstance(current_node,
                             esprima.nodes.CallExpression) or
                  isinstance(current_node,
                             esprima.nodes.StaticMemberExpression)):
            logging.warning(
                "Call chain argument handler cannot yet handle type: "
                f"{type(current_node)}")
            # Uncomment to get more information about unhandled type
            # logging.warning(f"Node information: {current_node}")

    def __create_call_chain_entry(
            self,
            current_node,
            current_path,
            current_node_property):
        """Create a call chain entry base from the current AST node and node
        property.

        :param current_node: The AST node to create the call chain entry for.
        :type current_node: esprima.nodes.*
        :param current_node_property: The name of the current node property to
        create the chain entry for.
        :type current_node_property: str

        :return: The call chain entry.
        :rtype: dict
        """
        chain_entry = {
            'name': current_node.__dict__[current_node_property].name,
            'external_name':
                current_node.__dict__[current_node_property].name,
            'path': current_path,
            'type': None,
            'static': True,
            'file_identity': self.file_identity,
            'arguments': []}

        if 'type' in current_node.__dict__:
            chain_entry['type'] = type(current_node)

        if 'static' in current_node.__dict__:
            chain_entry['static'] = current_node.static

        self.__call_chain_entry_handle_import(
            chain_entry,
            current_node,
            current_path)
        self.__call_chain_entry_handle_arguments(
            chain_entry,
            current_node,
            current_path)

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
            prep_call = \
                self.__create_call_chain_entry(
                    call_chain_prep['node_search'],
                    call_chain_prep['path_search'],
                    call_chain_prep['node_key'])
            call_chain.append(prep_call)

        if len(path_search) > 0 and path_search[-1] == 'right':
            left_node = \
                self.__go_to_absolute_path(path_search[:-1] + ['left'])

            if isinstance(left_node, esprima.nodes.StaticMemberExpression):
                prop_dig = left_node
                prop_dig_path = path_search[:-1] + ['left']
                while isinstance(
                        prop_dig,
                        esprima.nodes.StaticMemberExpression):
                    current_call = \
                        self.__create_call_chain_entry(
                            prop_dig,
                            prop_dig_path,
                            'property')
                    call_chain.append(current_call)

                    prop_dig = prop_dig.object
                    prop_dig_path += ['object']

                if isinstance(prop_dig, esprima.nodes.Identifier):
                    current_call = \
                        self.__create_call_chain_entry(
                            self.__go_to_absolute_path(prop_dig_path[:-1]),
                            prop_dig_path[:-1],
                            'object')
                    call_chain.append(current_call)

                else:
                    logging.warning(
                        "Call chain initiation from right hand expression "
                        "cannot handle StaticMember 'object' of type: "
                        f"{type(prop_dig)}")

            else:
                logging.warning(
                    "Call chain initiation from right hand expression "
                    "cannot handle expression of type: "
                    f"{type(left_node)}")

        while len(path_search) > 0:
            if hasattr(node_search, '__dict__'):
                for node_key in node_search.__dict__:
                    if isinstance(
                            node_search.__dict__[node_key],
                            esprima.nodes.Identifier):
                        is_node_inside_promise = \
                            node_search.__dict__[node_key].name == \
                            'Promise' and \
                            isinstance(
                                node_search,
                                esprima.nodes.NewExpression)
                        if is_node_inside_promise:
                            call_chain = []
                        else:
                            current_call = \
                                self.__create_call_chain_entry(
                                    node_search,
                                    path_search,
                                    node_key)
                            call_chain.append(current_call)

                            # Only add one call at current level in order
                            # to not register duplicates
                            break

            path_search = path_search[:-1]
            node_search = self.__go_to_absolute_path(path_search)

        call_chain.reverse()

        return call_chain

    def __create_identity_from_call_chain(self, call_chain):
        """Create a string identity tuple from the given call chain.

        :param call_chain: The call chain to create the identity for.
        :type call_chain: list

        :return: A tuple containing the string identity for the filename and a
        string identity for the method call.
        :rtype: tuple
        """
        file_identity = self.file_identity
        identity = []

        for chain_index, current_call in enumerate(call_chain):
            if current_call['type'] is esprima.nodes.ClassDeclaration:
                if len(call_chain) <= chain_index + 1:
                    logging.warning(
                        "Cannot create unique identity for a complete class, "
                        "the call chain must end at some method, not a full "
                        "class.")
                    break

                if call_chain[chain_index + 1]['static']:
                    identity.append(current_call['name'])
                elif not call_chain[chain_index + 1]['static']:
                    identity.append("(new " + current_call['name'] + "())")

            elif current_call['type'] is \
                    esprima.nodes.MethodDefinition or \
                    current_call['type'] is \
                    esprima.nodes.Property or \
                    current_call['type'] is \
                    esprima.nodes.VariableDeclarator or \
                    current_call['type'] is \
                    esprima.nodes.CatchClause or \
                    current_call['type'] is \
                    esprima.nodes.StaticMemberExpression or \
                    current_call['type'] is \
                    esprima.nodes.FunctionDeclaration:
                identity.append(current_call['name'])

            elif current_call['type'] is \
                    esprima.nodes.ImportSpecifier:
                identity.append(current_call['external_name'])
                file_identity = current_call['file_identity']

            elif current_call['type'] is \
                    esprima.nodes.ImportDefaultSpecifier:
                if len(call_chain) == 1:
                    identity.append(current_call['name'])

                file_identity = current_call['file_identity']

            else:
                logging.warning(
                    "Identity type not yet implemented: " +
                    str(current_call['type']))

        return file_identity, '.'.join(identity)

    def __initiate_export_information(self):
        """Export information tuple initiator with data default.

        :return: The default export information before any information is
        found.
        """
        return "private", ""

    def __make_tuple_export_default(self, method_name):
        """Create a default export tuple for the given method.

        :param method_name: The name of the method to create the tuple for.
        :return: The export information tuple.
        """
        return "export default", method_name

    def __make_tuple_export_named(self, method_name):
        """Create a named export tuple for the given method.

        :param method_name: The name of the method to create the tuple for.
        :return: The export information tuple.
        """
        return "export", method_name

    def __match_export_default_information(self, method_name):
        """Find possible export default declaration information for the given
        method.

        :param method_name: The method to search for and match.
        :return: The export information tuple for the given method.
        """
        export_type, export_name = self.__initiate_export_information()

        export_default_declarations = \
            self.__find_all_by_prop_value("type", "ExportDefaultDeclaration")

        for export_default_path in export_default_declarations:
            export_default_node = \
                self.__go_to_absolute_path(export_default_path)

            is_export_an_identifier = isinstance(
                export_default_node.declaration,
                esprima.nodes.Identifier)

            is_export_an_object = isinstance(
                export_default_node.declaration,
                esprima.nodes.ObjectExpression)

            is_export_a_function = isinstance(
                export_default_node.declaration,
                esprima.nodes.FunctionDeclaration)

            is_export_a_class = isinstance(
                export_default_node.declaration,
                esprima.nodes.ClassDeclaration)

            if is_export_an_identifier:
                if export_default_node.declaration.name == method_name:
                    return self.__make_tuple_export_default(method_name)

            elif is_export_an_object:
                for exported_prop in \
                        export_default_node.declaration.properties:
                    if exported_prop.key.name == method_name:
                        return self.__make_tuple_export_default(method_name)

            elif is_export_a_function or is_export_a_class:
                if export_default_node.declaration.id.name == method_name:
                    return self.__make_tuple_export_default(method_name)

            else:
                logging.warning(
                    "Export information for 'export default' not yet "
                    f"supported: {type(export_default_node.declaration)}")

        return export_type, export_name

    def __handle_previously_declared_asset_export_named(
            self,
            method_name,
            export_named_node):
        """Handle named export for a previously declared asset (const, let,
        function or class) with the given method name.

        :param method_name: The method to search for.
        :return: The export information tuple for the given method.
        """
        export_type, export_name = self.__initiate_export_information()

        for export_named_instance in export_named_node.specifiers:

            is_exported_named_instance_an_identifier = \
                isinstance(
                    export_named_instance.exported,
                    esprima.nodes.Identifier)

            is_local_named_instance_an_identifier = \
                isinstance(
                    export_named_instance.local,
                    esprima.nodes.Identifier)

            if is_exported_named_instance_an_identifier and \
                    is_local_named_instance_an_identifier:
                if export_named_instance.local.name == method_name:
                    return self.__make_tuple_export_named(
                        export_named_instance.exported.name)

            else:
                logging.warning(
                    "Export information for 'export named' not yet "
                    "supported. Exported instance is of type: "
                    f"{type(export_named_instance.exported)} and local "
                    "instance of type: "
                    f"{type(export_named_instance.local)}")

        return export_type, export_name

    def __handle_newly_declared_asset_export_named(
            self,
            method_name,
            export_named_node):
        """Handle named export for a newly declared asset (const, let,
        function or class) with the given method name.

        :param method_name: The method to search for.
        :return: The export information tuple for the given method.
        """
        export_type, export_name = self.__initiate_export_information()

        is_declaration_a_variabledeclaration = \
            isinstance(
                export_named_node.declaration,
                esprima.nodes.VariableDeclaration)

        is_declaration_a_functiondeclaration = \
            isinstance(
                export_named_node.declaration,
                esprima.nodes.FunctionDeclaration)

        is_declaration_a_classdeclaration = \
            isinstance(
                export_named_node.declaration,
                esprima.nodes.ClassDeclaration)

        if is_declaration_a_variabledeclaration:
            for export_named_instance in \
                    export_named_node.declaration.declarations:
                is_exported_named_instance_a_variable_declarator = \
                    isinstance(
                        export_named_instance,
                        esprima.nodes.VariableDeclarator)

                if is_exported_named_instance_a_variable_declarator:
                    is_variable_declarator_id_an_identifier = \
                        isinstance(
                            export_named_instance.id,
                            esprima.nodes.Identifier)

                    if is_variable_declarator_id_an_identifier:
                        if export_named_instance.id.name == method_name:
                            return self.__make_tuple_export_named(
                                export_named_instance.id.name)

                    else:
                        logging.warning(
                            "Support for id of type: "
                            f"'{type(export_named_instance.id)}' for newly "
                            "declared exported variable declaration not yet "
                            "added.")

                else:
                    logging.warning(
                        "Support for newly declared asset export of type: "
                        f"'{type(export_named_instance)}' not yet added.")

        elif is_declaration_a_functiondeclaration:
            is_function_declarator_id_an_identifier = \
                isinstance(
                    export_named_node.declaration.id,
                    esprima.nodes.Identifier)

            if is_function_declarator_id_an_identifier:
                if export_named_node.declaration.id.name == method_name:
                    return self.__make_tuple_export_named(
                        export_named_node.declaration.id.name)

                else:
                    logging.warning(
                        "Support for id of type: "
                        f"'{type(export_named_node.declaration)}' for newly "
                        "declared exported function declaration not yet "
                        "added.")

        elif is_declaration_a_classdeclaration:
            is_class_declarator_id_an_identifier = \
                isinstance(
                    export_named_node.declaration.id,
                    esprima.nodes.Identifier)

            if is_class_declarator_id_an_identifier:
                if export_named_node.declaration.id.name == method_name:
                    return self.__make_tuple_export_named(
                        export_named_node.declaration.id.name)

                else:
                    logging.warning(
                        "Support for id of type: "
                        f"'{type(export_named_node.declaration)}' for newly "
                        "declared exported class declaration not yet "
                        "added.")

        else:
            logging.warning(
                "Called export new declaration handler with unsupported type: "
                f"{type(export_named_node.declaration)}")

        return export_type, export_name

    def __match_export_named_information(self, method_name):
        """Find possible named export declaration information for the given
        method.

        :param method_name: The method to search for and match.
        :return: The export information tuple for the given method.
        """
        export_type, export_name = self.__initiate_export_information()

        export_named_declarations = \
            self.__find_all_by_prop_value("type", "ExportNamedDeclaration")

        for export_named_path in export_named_declarations:
            export_named_node = \
                self.__go_to_absolute_path(export_named_path)

            if len(export_named_node.specifiers) > 0:
                export_type, export_name = \
                    self.__handle_previously_declared_asset_export_named(
                        method_name,
                        export_named_node)

            if self.__was_export_information_found(export_type, export_name):
                break

            if export_named_node.declaration is not None:
                if isinstance(
                        export_named_node.declaration,
                        esprima.nodes.VariableDeclaration) or \
                        isinstance(
                            export_named_node.declaration,
                            esprima.nodes.FunctionDeclaration) or \
                        isinstance(
                            export_named_node.declaration,
                            esprima.nodes.ClassDeclaration):
                    export_type, export_name = \
                        self.__handle_newly_declared_asset_export_named(
                            method_name,
                            export_named_node)

                else:
                    logging.warning(
                        "Export information support for type: "
                        f"{type(export_named_node.declaration)}"
                        " not yet added.")

        return export_type, export_name

    def __was_export_information_found(self, export_type, export_name):
        """Check if given export type and name means that export information
        has been found.

        :param export_type: The export type to check.
        :param export_name: The export name to check.
        :return: True if the export information is different from the defaults.
        """
        default_export_type, default_export_name = \
            self.__initiate_export_information()
        return not (
                export_type == default_export_type and
                export_name == default_export_name)

    def __find_export_information_for_asset(self, method_name):
        """Find any export information for the given method.

        :param method_name: The method to find any export information for.
        :return: The export information tuple for the given method.
        """
        export_type, export_name = \
            self.__match_export_default_information(method_name)

        if not self.__was_export_information_found(export_type, export_name):
            export_type, export_name = \
                self.__match_export_named_information(method_name)

        return export_type, export_name

    def __save_created_method(
            self,
            string_identity,
            current_node,
            call_chain,
            export_info,
            export_name):
        """Save found method creation in the AST to the cache of all found
        method creations.

        :param string_identity: The string identity for the method to save.
        :type string_identity: str
        :param current_node: The method AST node.
        :type current_node: esprima.nodes.*
        :param call_chain: The call chain to the method.
        :type call_chain: list

        :return: Nothing
        """
        if string_identity in self.created_functions and \
                current_node.range[0] <= \
                self.created_functions[
                    string_identity][
                    'current_node'].range[0] and \
                current_node.range[1] >= \
                self.created_functions[
                    string_identity][
                    'current_node'].range[1] or \
                string_identity not in self.created_functions:
            self.created_functions[string_identity] = \
                {
                    'current_node': current_node,
                    'call_chain': call_chain,
                    'export_info': export_info,
                    'export_name': export_name
                }

    def __handle_node_method_declaration(self, path, current_node):
        """Handle an AST node method declaration and save found method
        declarations to cache.

        :param path: The path to the AST node.
        :type path: list
        :param current_node: The current AST node.
        :type current_node: esprima.nodes.MethodDefinition|
        esprima.nodes.ArrowFunctionExpression|
        esprima.nodes.AsyncArrowFunctionExpression|
        esprima.nodes.AsyncFunctionDeclaration|
        esprima.nodes.AsyncFunctionExpression|
        esprima.nodes.FunctionDeclaration|
        esprima.nodes.FunctionExpression

        :return: Nothing
        """
        is_node_a_methoddefinition = \
            isinstance(
                current_node,
                esprima.nodes.MethodDefinition)
        is_node_an_arrowfunctionexpression = \
            isinstance(
                current_node,
                esprima.nodes.ArrowFunctionExpression)
        is_node_an_asyncarrowfunctionexpression = \
            isinstance(
                current_node,
                esprima.nodes.AsyncArrowFunctionExpression)
        is_node_an_asyncfunctiondeclaration = \
            isinstance(
                current_node,
                esprima.nodes.AsyncFunctionDeclaration)
        is_node_an_asyncfunctionexpression = \
            isinstance(
                current_node,
                esprima.nodes.AsyncFunctionExpression)
        is_node_a_functiondeclaration = \
            isinstance(
                current_node,
                esprima.nodes.FunctionDeclaration)
        is_node_a_functionexpression = \
            isinstance(
                current_node,
                esprima.nodes.FunctionExpression)

        is_node_an_anonymous_callback = \
            (is_node_an_arrowfunctionexpression or
             is_node_an_asyncarrowfunctionexpression or
             is_node_an_asyncfunctionexpression or
             is_node_a_functionexpression) and \
            len(path) > 2 and path[-2] == "arguments"

        if (is_node_a_methoddefinition or
            is_node_an_asyncfunctiondeclaration or
            is_node_a_functiondeclaration) or \
                (is_node_an_arrowfunctionexpression or
                 is_node_an_asyncarrowfunctionexpression or
                 is_node_an_asyncfunctionexpression or
                 is_node_a_functionexpression) and \
                not is_node_an_anonymous_callback:

            call_chain = self.__create_call_chain(path)
            file_identity, string_identity = \
                self.__create_identity_from_call_chain(call_chain)

            if len(call_chain) > 0:
                export_info, export_name = \
                    self.__find_export_information_for_asset(
                        call_chain[0]['name'])

                if not (len(call_chain) >= 2 and
                        call_chain[-1][
                            'type'] is esprima.nodes.MethodDefinition and
                        call_chain[-1]['name'] == 'constructor' and
                        call_chain[-2]['type'] is
                        esprima.nodes.ClassDeclaration):
                    self.__save_created_method(
                        string_identity,
                        current_node,
                        call_chain,
                        export_info,
                        export_name)
            else:
                logging.critical(
                    "Cannot create call chain to found method at path: "
                    f"{self.__get_path_string(path)}")

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

    def __get_sub_paths(self, current_path=None, node_type_blacklist=None):
        """Find all possible sub-paths from the given path.

        :param current_path: The path to find all sub-paths from.
        :type current_path: list|None

        :return: A list of all found paths.
        :rtype: list
        """
        if current_path is None:
            current_path = []
        if node_type_blacklist is None:
            node_type_blacklist = []

        possible_paths = []
        current_node = self.__go_to_absolute_path(current_path)

        if hasattr(current_node, '__dict__'):
            for node_key in current_node.__dict__:
                next_node = current_node.__dict__[node_key]

                is_node_blacklisted = False
                for type_blacklist in node_type_blacklist:
                    if isinstance(next_node, type_blacklist):
                        is_node_blacklisted = True
                        break

                if not is_node_blacklisted and \
                        not isinstance(next_node, str) and \
                        not isinstance(next_node, int) and \
                        not re.match(r"^(range)$", node_key):
                    possible_paths.append(current_path + [node_key])

        elif isinstance(current_node, list):
            for node_index, node_alt in enumerate(current_node):
                possible_paths.append(current_path + [str(node_index)])

        elif current_node is not None and \
                not isinstance(current_node, re.Pattern) and \
                not isinstance(current_node, float):
            logging.warning(
                "Type not yet implemented and cannot be analyzed: " +
                str(type(current_node)))

        return possible_paths

    def __analyze_ast(self, path, current_node):
        """Recursively walk down the complete AST and analyze each node by
        calling the general AST node handler.

        :param path: The current path in the AST.
        :type path: list
        :param current_node: The current AST node.
        :type current_node: esprima.nodes.*|list

        :return: Nothing.
        """
        self.__handle_node(path, current_node)

        # Don't enter CallExpression, can't test anything created here..
        # Don't enter JSX, things are not defined there...
        node_type_blacklist = [
            esprima.nodes.CallExpression,
            esprima.jsx_nodes.JSXElement
        ]

        for sub_path in \
                self.__get_sub_paths(
                    current_path=path,
                    node_type_blacklist=node_type_blacklist):
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

        :return: Return the path to the AST node if found, otherwise False is
        returned.
        :rtype: list|bool
        """
        if current_path is None:
            current_path = []

        current_node = self.__go_to_absolute_path(current_path)
        if hasattr(current_node, '__dict__') and \
                prop in current_node.__dict__ and \
                current_node.__dict__[prop] == value:
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

        :return: Return the path to all found AST nodes in a list, if nothing
        is found an empty list is returned.
        :rtype: list
        """
        if current_path is None:
            current_path = []

        current_node = self.__go_to_absolute_path(current_path)
        results = []

        if hasattr(current_node, '__dict__') and \
                prop in current_node.__dict__ and \
                current_node.__dict__[prop] == value:
            results += [current_path]

        for sub_path in self.__get_sub_paths(current_path):
            results += self.__find_all_by_prop_value(prop, value, sub_path)

        return results

    def __go_to_absolute_path(self, path):
        """Go to an retrieve an AST node from an absolute AST path either as a
        string or an array.

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

        :return: Nothing
        """
        self.__analyze_ast([], self.esprima_tree)

    def get_file_identity(self):
        return self.file_identity

    def get_functions(self):
        return self.created_functions

    def get_method_calls(self, function_identity):
        path_to_function = \
            self.created_functions[function_identity]['call_chain'][-1]['path']
        return self.__find_method_calls(path_to_function)


class ProjectDataHandler:
    def __init__(self, project_root: str):
        """Project data handler for saving and updating data

        :param project_root: The project root
        :type project_root: str
        """
        if not isinstance(project_root, str):
            raise TypeError("'project_root' must be a STRING")
        elif len(project_root) < 1:
            raise ValueError("'project_root' cannot be empty")

        self.analyzer_instance = None
        self.file_source = None
        self.project_root = os.path.abspath(project_root)

        self.__is_project_existing = False

        self.added_function_dependencies = []
        self.existing_function_dependencies = []
        self.dead_function_dependencies = []

        self.added_function_info = []
        self.existing_function_info = []
        self.dead_function_info = []

        self.__project_backup()

    def __project_backup_remove(self):
        project_root_backup = "/BACKUP" + self.project_root
        backup_info = {"pathToProject": project_root_backup}

        database_handler.remove_function_info(backup_info)
        database_handler.remove_function_dependency(backup_info)
        database_handler.remove_test_info(backup_info)

    def __project_backup(self):
        project_root_backup = "/BACKUP" + self.project_root
        original_info = {"pathToProject": self.project_root}
        backup_info = {"pathToProject": project_root_backup}

        self.__project_backup_remove()

        orig_function_info = \
            database_handler.get_function_info(original_info)
        orig_function_dependency = \
            database_handler.get_function_dependency(original_info)
        orig_test_info = \
            database_handler.get_test_info(original_info)

        if orig_function_info is not None:
            self.__is_project_existing = True
            for function_info in orig_function_info:
                if '_id' in function_info:
                    existing_function_info_id = function_info.pop("_id")
                    self.existing_function_info.\
                        append(existing_function_info_id)

                database_handler.add_function_info({
                    **function_info,
                    **backup_info
                })

        if orig_function_dependency is not None:
            for function_dependency in orig_function_dependency:
                if '_id' in function_dependency:
                    existing_dependency_id = function_dependency.pop("_id")
                    self.existing_function_dependencies.\
                        append(existing_dependency_id)

                database_handler.add_function_dependency({
                    **function_dependency,
                    **backup_info
                })

        if orig_test_info is not None:
            for test_info in orig_test_info:
                if '_id' in test_info:
                    test_info.pop("_id")

                database_handler.add_test_info({
                    **test_info,
                    **backup_info
                })

    def __project_restore(self):
        project_root_backup = "/BACKUP" + self.project_root
        original_info = {"pathToProject": self.project_root}
        backup_info = {"pathToProject": project_root_backup}

        if not self.__is_project_existing:
            database_handler.remove_function_info(original_info)
            database_handler.remove_function_dependency(original_info)
            database_handler.remove_test_info(original_info)
            clear_cache(self.project_root)

        else:
            backup_function_info = \
                database_handler.get_function_info(backup_info)
            backup_function_dependency = \
                database_handler.get_function_dependency(backup_info)
            backup_test_info = \
                database_handler.get_test_info(backup_info)

            if backup_function_info is not None:
                database_handler.remove_function_info(original_info)
                for function_info in backup_function_info:
                    if '_id' in function_info:
                        function_info.pop("_id")
                    database_handler.add_function_info(
                        {**function_info, **original_info})

            if backup_function_dependency is not None:
                database_handler.remove_function_dependency(original_info)
                for function_dependency in backup_function_dependency:
                    if '_id' in function_dependency:
                        function_dependency.pop("_id")
                    database_handler.add_function_dependency(
                        {**function_dependency, **original_info})

            if backup_test_info is not None:
                database_handler.remove_test_info(original_info)
                for test_info in backup_test_info:
                    if '_id' in test_info:
                        test_info.pop("_id")
                    database_handler.add_test_info(
                        {**test_info, **original_info})

        self.__project_backup_remove()

    def set_analyzer(self, analyzer_instance):
        if not isinstance(analyzer_instance, AnalyzeJS):
            raise TypeError("'analyzer_instance' must be a AnalyzeJS object")

        self.analyzer_instance = analyzer_instance
        self.file_source = analyzer_instance.file_source

    def unset_analyzer(self):
        self.analyzer_instance = None
        self.file_source = None

    def __db_get_project_function_dependencies(self):
        function_dependencies = []
        db_function_dependencies = \
            database_handler.get_function_dependency({
                "pathToProject": self.project_root
            })

        if db_function_dependencies is not None:
            function_dependencies = db_function_dependencies

        return function_dependencies

    def __db_get_project_function_info(self):
        function_info = []
        db_function_info = \
            database_handler.get_function_info({
                "pathToProject": self.project_root
            })

        if db_function_info is not None:
            function_info = db_function_info

        return function_info

    def __db_get_dead_project_function_dependencies_id(self):
        saved_dependencies = \
            [dependency["_id"] for dependency in
             self.__db_get_project_function_dependencies()]
        found_dependencies = \
            self.added_function_dependencies + \
            self.existing_function_dependencies
        dead_dependencies = \
            list(set(saved_dependencies).difference(found_dependencies))

        return dead_dependencies

    def __db_get_dead_project_function_info_id(self):
        saved_functions = \
            [dependency["_id"] for dependency in
             self.__db_get_project_function_info()]
        found_functions = \
            self.added_function_info + \
            self.existing_function_info
        dead_functions = \
            list(set(saved_functions).difference(found_functions))

        return dead_functions

    def __db_delete_dead_project_function_dependencies(self):
        dead_dependencies = \
            self.__db_get_dead_project_function_dependencies_id()

        if len(dead_dependencies) > 0:
            for dead_dependency in dead_dependencies:
                database_handler.remove_function_dependency({
                    '_id': dead_dependency
                })

            logging.info(
                f"Removed {len(dead_dependencies)} dead dependencies from "
                f"project at: {self.project_root}")

    def __db_delete_dead_project_function_info(self):
        dead_functions = \
            self.__db_get_dead_project_function_info_id()

        if len(dead_functions) > 0:
            for dead_function in dead_functions:
                database_handler.remove_function_info({
                    '_id': dead_function
                })

            logging.info(
                f"Removed {len(dead_functions)} dead functions from "
                f"project at: {self.project_root}")

    def __db_get_function_dependency_id(
            self,
            function_id,
            called_file_id,
            called_function_id):
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file information")

        function_dependency_id = None

        db_function_dependencies = \
            database_handler.get_function_dependency({
                "pathToProject": self.project_root,
                "fileId": self.analyzer_instance.get_file_identity(),
                "functionId": function_id,
                "calledFileId": called_file_id,
                "calledFunctionId": called_function_id
            })

        if db_function_dependencies is not None:
            if len(db_function_dependencies) > 1:
                logging.warning(
                    "Multiple dependency definitions in database "
                    "for "
                    f"{self.project_root} : "
                    f"{self.analyzer_instance.get_file_identity()} : "
                    f"{function_id} ->"
                    f"{called_file_id} : "
                    f"{called_function_id}")

            function_dependency_id = db_function_dependencies[0]["_id"]

        return function_dependency_id

    def __db_get_function_info(self, function_id):
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file information")

        function_info = None

        db_function_info = \
            database_handler.get_function_info({
                "pathToProject": self.project_root,
                "fileId": self.analyzer_instance.get_file_identity(),
                "functionId": function_id
            })

        if db_function_info is not None:
            if len(db_function_info) > 1:
                logging.warning(
                    "Multiple function definitions in database "
                    "for "
                    f"{self.project_root} : "
                    f"{self.analyzer_instance.get_file_identity()} : "
                    f"{function_id}")

            function_info = db_function_info[0]

        return function_info

    def __db_save_function_dependencies(self, created_function):
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        function_dependencies = \
            self.analyzer_instance.get_method_calls(created_function)

        for file_identity, string_identity in \
                [(file_identity, string_identity)
                 for file_identity in function_dependencies
                 for string_identity in function_dependencies[file_identity]]:

            if string_identity != METHOD_STRING_IDENTITY_UNKNOWN and \
                    string_identity != METHOD_STRING_IDENTITY_IGNORE:

                existing_dependency_id = \
                    self.__db_get_function_dependency_id(
                        created_function, file_identity, string_identity)

                if existing_dependency_id is not None:
                    self.existing_function_dependencies. \
                        append(existing_dependency_id)

                else:
                    added_dependency_id = \
                        database_handler.add_function_dependency({
                            "pathToProject": self.project_root,
                            "fileId":
                                self.analyzer_instance.get_file_identity(),
                            "functionId": created_function,
                            "calledFileId": file_identity,
                            "calledFunctionId": string_identity
                        })

                    self.added_function_dependencies. \
                        append(added_dependency_id)

    def __make_function_info_change_list(
            self,
            old_function_info,
            new_function_info):
        change_list = []
        for function_info_prop in new_function_info:
            if new_function_info[function_info_prop] != \
                    old_function_info[function_info_prop]:
                change_list.append(function_info_prop)

        return change_list

    def __db_make_function_info_arguments(self, created_function):
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        created_functions = self.analyzer_instance.get_functions()
        col_arguments = []
        for call in created_functions[created_function]['call_chain']:
            col_arguments.append({call['name']: call['arguments']})
        return col_arguments

    def __db_make_function_info_functionhash(self, current_node):
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        function_source = \
            self.file_source[current_node.range[0]:current_node.range[1]]
        function_hash = hashlib.sha256(str.encode(function_source))
        return function_hash.hexdigest()

    def __db_save_function_info(self, created_function):
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        created_functions = self.analyzer_instance.get_functions()
        current_node = created_functions[created_function]['current_node']

        new_function_info = {
            "arguments":
                self.__db_make_function_info_arguments(created_function),
            "functionRange":
                (current_node.range[0], current_node.range[1]),
            "functionHash":
                self.__db_make_function_info_functionhash(current_node),
            "exportInfo":
                created_functions[created_function]['export_info'],
            "exportName":
                created_functions[created_function]['export_name']
        }

        existing_function_info = self.__db_get_function_info(created_function)

        if existing_function_info is not None:
            self.existing_function_info. \
                append(existing_function_info["_id"])

            change_list = self.__make_function_info_change_list(
                existing_function_info,
                new_function_info
            )

            if len(change_list) > 0:
                logging.info(
                    f"Detected changes were: {', '.join(change_list)}")

                database_handler.set_function_info(
                    new_function_info,
                    {'_id': existing_function_info["_id"]}
                )

        else:
            added_function_info_id = database_handler.add_function_info({
                "pathToProject": self.project_root,
                "fileId": self.analyzer_instance.get_file_identity(),
                "functionId": created_function,
                **new_function_info
            })

            self.added_function_info. \
                append(added_function_info_id)

    def __db_cleanup_project_function_dependencies(self):
        """Remove all dependencies on function not defined in the current
        project. This will remove dependencies on external libraries.

        :return: Nothing
        """
        project_dependencies = self.__db_get_project_function_dependencies()
        for index, project_dependency in enumerate(project_dependencies):
            shared_websockets_handler.send_progress(
                WsIdentity.NEW_PROJECT,
                WsCode.ANALYZE_CLEAN_DEPENDENCY,
                index + 1,
                len(project_dependencies),
                "Checking dependency: "
                f"{project_dependency['fileId']}:"
                f"{project_dependency['functionId']} -> "
                f"{project_dependency['calledFileId']}:"
                f"{project_dependency['calledFunctionId']}"
            )

            dependency_defined_in_project = \
                database_handler.get_function_info({
                    'pathToProject': self.project_root,
                    'fileId': project_dependency['calledFileId'],
                    'functionId': project_dependency['calledFunctionId']
                })

            if dependency_defined_in_project is None:
                database_handler.remove_function_dependency({
                    '_id': project_dependency["_id"]
                })

    def __db_save_project_function_dependencies_count(self):
        project_functions = self.__db_get_project_function_info()

        for index, project_function in enumerate(project_functions):

            shared_websockets_handler.send_progress(
                WsIdentity.NEW_PROJECT,
                WsCode.ANALYZE_COUNT_DEPENDENCY,
                index + 1,
                len(project_functions),
                "Calculating dependency information for: "
                f"{project_function['fileId']}:"
                f"{project_function['functionId']}"
            )

            function_depends_on = \
                database_handler.get_function_dependency({
                    'pathToProject': self.project_root,
                    'fileId': project_function['fileId'],
                    'functionId': project_function['functionId']
                })

            depends_on_function = \
                database_handler.get_function_dependency({
                    'pathToProject': self.project_root,
                    'calledFileId': project_function['fileId'],
                    'calledFunctionId': project_function['functionId']
                })

            function_depends_on_count = 0
            depends_on_function_count = 0

            if function_depends_on is not None:
                function_depends_on_count = len(function_depends_on)

            if depends_on_function is not None:
                depends_on_function_count = len(depends_on_function)

            new_function_info = {
                'dependencies': function_depends_on_count,
                'dependents': depends_on_function_count
            }

            change_list = \
                self.__make_function_info_change_list(
                    project_function, new_function_info)

            if len(change_list) > 0:
                logging.info(
                    f"Detected changes were: {', '.join(change_list)}")

                database_handler.set_function_info(
                    new_function_info,
                    {'_id': project_function["_id"]}
                )

    def cache_check(self):
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        new_contents_hash = \
            hashlib.sha256(str.encode(self.file_source)).hexdigest()

        try:
            cache_contents_hash = \
                hashlib.sha256(str.encode(read_file(
                    self.project_root,
                    self.analyzer_instance.get_file_identity()))).hexdigest()

        except FileNotFoundError:
            cache_contents_hash = ""

        return cache_contents_hash == new_contents_hash

    def cache_save(self):
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        save_file(
            self.project_root,
            self.analyzer_instance.get_file_identity(),
            self.file_source)

    def database_save(self):
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        created_functions = self.analyzer_instance.get_functions()

        for created_function in created_functions:
            self.__db_save_function_dependencies(created_function)
            self.__db_save_function_info(created_function)

    def database_cleanup(self):
        self.__db_cleanup_project_function_dependencies()
        self.__db_save_project_function_dependencies_count()
        self.__db_delete_dead_project_function_dependencies()
        self.__db_delete_dead_project_function_info()

    def process_cleanup(self):
        self.__project_backup_remove()

    def restore_backup(self):
        self.__project_restore()


global CLIENT_ACTION_CANCEL
CLIENT_ACTION_CANCEL = False


def analyze_files(project_root):
    """Analyze list of files

    :param project_root: The project root directory
    :type project_root: str

    :raises:
        TypeError: If the passed 'project_root' is of the wrong type.
        ValueError: If the passed 'project_root' is empty.

    :return: Nothing
    """
    if not isinstance(project_root, str):
        raise ValueError(
            "'project_root' must be a STRING")
    elif len(project_root) < 1:
        raise ValueError(
            "'project_root' must be a path")

    analyzer_config = AnalyzerConfig()
    project_data = ProjectDataHandler(project_root)

    global CLIENT_ACTION_CANCEL

    def callback_client_messages(message: dict):
        if 'userAction' in message and message['userAction'] == \
                WsClientCode.ANALYZE_STOP.value:
            logging.info(
                "Analyzer received cancellation action from client "
                f"({message['_clientId']})")
            global CLIENT_ACTION_CANCEL
            CLIENT_ACTION_CANCEL = True

    shared_websockets_handler.add_listener_message(
        WsIdentity.NEW_PROJECT, callback_client_messages)

    list_of_files = []
    for path, currentDirectory, files in os.walk(project_root):
        for file in files:
            file_location = os.path.abspath(os.path.join(path, file))
            if analyzer_config.is_file_allowed(file_location):
                list_of_files.append(file_location)

    for file_num, current_file in enumerate(list_of_files):
        # TODO: Find better solution for a graceful cancellation event at
        #  specific points..
        if CLIENT_ACTION_CANCEL:
            project_data.restore_backup()
            shared_websockets_handler.send_error(
                WsIdentity.NEW_PROJECT,
                WsCode.ANALYZE_ERR_CLIENT_STOP,
                f"Process cancelled by client"
            )
            CLIENT_ACTION_CANCEL = False
            return

        with open(current_file, 'r') as file:
            file_source = file.read()

        if len(file_source) < 1:
            shared_websockets_handler.send_error(
                WsIdentity.NEW_PROJECT,
                WsCode.ANALYZE_ERR_FILE_EMPTY,
                f"File '{current_file}' is empty, skipping."
            )
            continue

        try:
            analyzer = AnalyzeJS(current_file, project_root=project_root)

        except SyntaxError as e:
            logging.warning(
                f"File '{current_file}' cannot be parsed. More information: "
                f"{e}")

            shared_websockets_handler.send_error(
                WsIdentity.NEW_PROJECT,
                WsCode.ANALYZE_ERR_PARSE_FAILURE,
                f"File '{current_file}' cannot be parsed."
            )
            return

        except Exception as e:
            logging.warning(
                f"Unexpected error when handling file '{current_file}'. "
                f"More information: {e}")

            shared_websockets_handler.send_error(
                WsIdentity.NEW_PROJECT,
                WsCode.ANALYZE_ERR_UNEXPECTED,
                f"An unexpected error occurred while handling "
                f"'{current_file}'."
            )
            return

        # TODO: Find better solution for a graceful cancellation event at
        #  specific points..
        if CLIENT_ACTION_CANCEL:
            project_data.restore_backup()
            shared_websockets_handler.send_error(
                WsIdentity.NEW_PROJECT,
                WsCode.ANALYZE_ERR_CLIENT_STOP,
                f"Process cancelled by client"
            )
            CLIENT_ACTION_CANCEL = False
            return

        analyzed_file_path = full_path_to_correct_sub_directory(current_file)
        shared_websockets_handler.send_progress(
            WsIdentity.NEW_PROJECT,
            WsCode.ANALYZE_PROCESS_FILES,
            file_num,
            len(list_of_files),
            f"Analyzing file: '{analyzed_file_path}'"
        )

        project_data.set_analyzer(analyzer)

        if not project_data.cache_check():
            print(f"{current_file}: {len(analyzer.get_functions())}")
            analyzer.begin_analyze()

            # TODO: Find better solution for a graceful cancellation event at
            #  specific points..
            if CLIENT_ACTION_CANCEL:
                project_data.restore_backup()
                shared_websockets_handler.send_error(
                    WsIdentity.NEW_PROJECT,
                    WsCode.ANALYZE_ERR_CLIENT_STOP,
                    f"Process cancelled by client"
                )
                CLIENT_ACTION_CANCEL = False
                return

            project_data.cache_save()
            project_data.database_save()

        project_data.unset_analyzer()

    project_data.database_cleanup()
    project_data.process_cleanup()

    # TODO: Find better solution for a graceful cancellation event at
    #  specific points..
    if CLIENT_ACTION_CANCEL:
        project_data.restore_backup()
        shared_websockets_handler.send_error(
            WsIdentity.NEW_PROJECT,
            WsCode.ANALYZE_ERR_CLIENT_STOP,
            f"Process cancelled by client"
        )
        CLIENT_ACTION_CANCEL = False
        return

    shared_websockets_handler.send_success(
        WsIdentity.NEW_PROJECT,
        WsCode.ANALYZE_COMPLETE,
        "Project analysis complete!"
    )
