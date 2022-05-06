import hashlib
import os
import esprima
import re
from api.instances.logging_standard import logging


class AnalyzeJS:
    """Static code analyzer for JavaScript project files.
    The analyzer can identify possible test surfaces and dependencies.

    :param path_target_file: The target file to analyze.
    :type path_target_file: str
    :param path_project_root: The absolute path to the root directory for
    the whole project.
    :type path_project_root: str

    :rtype: None
    """
    def __init__(self, path_target_file, path_project_root) -> None:
        self.ast_analyzed = False

        self.path_target_file = path_target_file
        self.path_project_root = path_project_root
        self.code_target_file = None
        self.ast_target_file = None
        self.js_target_file_import_path = None

        self.analyze_exported = []
        self.analyze_imported = []

        # AST Information Caching
        self.cache_declarations = {}
        self.cache_functions = {}
        self.cache_classes = {}
        self.cache_method_calls = []
        self.cache_declarations_exported_object = {}

        # Processed
        self.exported_test_surfaces = []
        self.imported_dependencies = []

        # Setup Process
        self.__validate_constructor_arguments()
        self.__clean_env_path_variables()
        self.__load_code_target_file()
        self.__load_ast_target_file()
        self.__set_js_target_file_import_path()

    # ~~~~~( Initiation ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __validate_constructor_arguments(self) -> None:
        """Validate the constructor arguments.

        :return: None
        """
        if not isinstance(self.path_target_file, str):
            raise TypeError("'path_target_file' must be a STRING")
        elif len(self.path_target_file) < 1:
            raise ValueError("'path_target_file' cannot be empty")

        if not isinstance(self.path_project_root, str):
            raise TypeError("'path_project_root' must be a STRING")
        elif len(self.path_project_root) < 1:
            raise ValueError("'path_project_root' cannot be empty")

    def __clean_env_path_variables(self) -> None:
        """Clean the variables containing paths

        :return: None
        """
        self.path_target_file = os.path.abspath(self.path_target_file)
        self.path_project_root = os.path.abspath(self.path_project_root)

    def __load_code_target_file(self) -> None:
        """Load the code for the selected target file.

        :return: None
        """
        try:
            with open(self.path_target_file, 'r') as file:
                self.code_target_file = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                "File at "
                f"'{self.path_target_file}' cannot be found and analyzed.")

    def __load_ast_target_file(self) -> None:
        """Load the AST for the selected target file using Esprima.

        :return: None
        """
        try:
            self.ast_target_file = \
                esprima.parseModule(
                    self.code_target_file,
                    {"range": True, "jsx": True})
        except esprima.Error as e:
            raise SyntaxError(
                f"Contents in file at '{self.path_target_file}' string could "
                f"not be parsed.\nInformation from esprima:\n{e}")

    def __set_js_target_file_import_path(self) -> None:
        """Set the absolute import path variable for the loaded target file

        :return: None
        """
        self.js_target_file_import_path = \
            re.sub(r"^" + re.escape(self.path_project_root) + r"/|\.jsx?$",
                   "",
                   self.path_target_file)

    # ~~~~~( Debugging ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __debug_node_in_code(self, node):
        node_code = self.code_target_file[node.range[0]:node.range[1]]
        new_lines = self.code_target_file[:node.range[0]].count("\n") + 1

        return f"\n" \
               f" >>> File: {self.path_target_file}\n" \
               f" >>> Line {new_lines}: {node_code}"

    def __debug_print_location(self, scope, path):
        path_in_program = '/'.join(path)
        scope_in_program = \
            ', '.join(
                [f"{scope_tuple[0]}[{scope_tuple[1]}]"
                 for scope_tuple in scope])

        print(f"path({path_in_program}), scope({scope_in_program})")

    def __debug_print_info(self):
        win_size = 140
        title_name = win_size - 40
        value_size = 119
        name_size = 14
        print()
        print(f"{'=== [ cache_declarations ]':=<{win_size}}")
        for dec_name in self.cache_declarations:
            print(f" > {dec_name}")
            for index, dec_inst in \
                    enumerate(self.cache_declarations[dec_name]):
                print(f" {(index + 1):0>4}.")
                print(f"   - {'scope': >{name_size}}: "
                      f"{' ' + str(dec_inst['scope']):.>{value_size}}")

                print(f"   - {'node_type': >{name_size}}: "
                      f"{' ' + str(dec_inst['node_type']):.>{value_size}}")

                # print(dec_inst['node'])

                print(f"   - {'path': >{name_size}}: "
                      f"{' ' + '/'.join(dec_inst['path']):.>{value_size}}")

                print(f"   - {'kind': >{name_size}}: "
                      f"{' ' + dec_inst['kind']:.>{value_size}}")

            print()
        print()
        print(f"{'=== [ cache_declarations_exported_object ]':=<{win_size}}")
        for dec_name in self.cache_declarations_exported_object:
            print(f" > {dec_name}")
            for index, dec_inst in \
                    enumerate(
                        self.cache_declarations_exported_object[dec_name]):
                print(f" {(index + 1):0>4}.")
                print(f"   - {'scope': >{name_size}}: "
                      f"{' ' + str(dec_inst['scope']):.>{value_size}}")

                print(f"   - {'node_type': >{name_size}}: "
                      f"{' ' + str(dec_inst['node_type']):.>{value_size}}")

                # print(dec_inst['node'])

                print(f"   - {'path': >{name_size}}: "
                      f"{' ' + '/'.join(dec_inst['path']):.>{value_size}}")

            print()

        print(f"{'=== [ cache_functions ]':=<{win_size}}")
        for dec_name in self.cache_functions:
            print(f" > {dec_name}")
            for index, dec_inst in \
                    enumerate(self.cache_functions[dec_name]):
                print(f" {(index + 1):0>4}.")
                print(f"   - {'scope': >{name_size}}: "
                      f"{' ' + str(dec_inst['scope']):.>{value_size}}")

                # print(dec_inst['node'])

                print(f"   - {'path': >{name_size}}: "
                      f"{' ' + '/'.join(dec_inst['path']):.>{value_size}}")

            print()

        print(f"{'=== [ cache_classes ]':=<{win_size}}")
        for dec_name in self.cache_classes:
            print(f" > {dec_name}")
            for index, dec_inst in \
                    enumerate(self.cache_classes[dec_name]):
                print(f" {(index + 1):0>4}.")
                print(f"   - {'constructor': >{name_size}}: "
                      f"{' ' + str(dec_inst['constructor'] is not None):.>{value_size}}")

                print(f"   - {'static': >{name_size}}: "
                      f"{' ' + str(dec_inst['static']):.>{value_size}}")

                print(f"   - {'name': >{name_size}}: "
                      f"{' ' + str(dec_inst['name']):.>{value_size}}")

                print(f"   - {'scope': >{name_size}}: "
                      f"{' ' + str(dec_inst['scope']):.>{value_size}}")

                # print(dec_inst['node'])

                print(f"   - {'path': >{name_size}}: "
                      f"{' ' + '/'.join(dec_inst['path']):.>{value_size}}")

            print()

        print(f"{'=== [ cache_method_calls ]':=<{win_size}}")
        for index, dec_inst in enumerate(self.cache_method_calls):
            print(f" {(index + 1):0>4}.")
            print(f"   - {'name': >{name_size}}: "
                  f"{' ' + str(dec_inst['name']):.>{value_size}}")

            print(f"   - {'scope': >{name_size}}: "
                  f"{' ' + str(dec_inst['scope']):.>{value_size}}")

            # print(dec_inst['node'])

            print(f"   - {'path': >{name_size}}: "
                  f"{' ' + '/'.join(dec_inst['path']):.>{value_size}}")

            print(f"   - {'property_chain': >{name_size}}: "
                  f"{' ' + str(dec_inst['property_chain']):.>{value_size}}")

        print()

        print(f"{'=== [ analyze_exported ]':=<{win_size}}")
        for index, dec_inst in enumerate(self.analyze_exported):
            print(f" {(index + 1):0>4}.")
            print(f"   - {'export': >{name_size}}: "
                  f"{' ' + str(dec_inst['export']):.>{value_size}}")

            print(f"   - {'local_name': >{name_size}}: "
                  f"{' ' + str(dec_inst['local_name']):.>{value_size}}")

            print(f"   - {'export_name': >{name_size}}: "
                  f"{' ' + str(dec_inst['export_name']):.>{value_size}}")

            print(f"   - {'object_type': >{name_size}}: "
                  f"{' ' + str(dec_inst['object_type']):.>{value_size}}")

            # print(dec_inst['node'])

        print()

        print(f"{'=== [ analyze_imported ]':=<{win_size}}")
        for index, dec_inst in enumerate(self.analyze_imported):
            print(f" {(index + 1):0>4}.")
            print(f"   - {'local_name': >{name_size}}: "
                  f"{' ' + str(dec_inst['local_name']):.>{value_size}}")

            print(f"   - {'external_name': >{name_size}}: "
                  f"{' ' + str(dec_inst['external_name']):.>{value_size}}")

            print(f"   - {'absolute_import_path': >{name_size}}: "
                  f"{' ' + str(dec_inst['absolute_import_path']):.>{value_size}}")

            # print(dec_inst['node'])

        print()

    # ~~~~~( Cache Handling ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __cache_function(self, name, scope, node, node_type, path: list):
        cache_content = {
            "scope": scope,
            "node": node,
            "node_type": node_type,
            "path": path
        }

        if name not in self.cache_functions:
            self.cache_functions[name] = [cache_content]
        else:
            self.cache_functions[name].append(cache_content)

    def __cache_class_method(
            self, classname, constructor, static, name, scope, node,
            path: list):
        cache_content = {
            "constructor": constructor,
            "static": static,
            "name": name,
            "scope": scope,
            "node": node,
            "path": path
        }

        if classname not in self.cache_classes:
            self.cache_classes[classname] = [cache_content]
        else:
            self.cache_classes[classname].append(cache_content)

    def __cache_declaration(
            self, name, declaration, scope, path: list, kind=None):
        if name not in self.cache_declarations and \
                (kind is None or kind == "var"):
            kind = "window"
        elif name in self.cache_declarations and kind is None:
            kind = "redeclare"

        if declaration is None:
            declaration_type = None
        else:
            declaration_type = declaration.type

        cache_content = {
            "scope": scope,
            "node": declaration,
            "node_type": declaration_type,
            "path": path,
            "kind": kind
        }

        if name not in self.cache_declarations:
            self.cache_declarations[name] = [cache_content]
        else:
            self.cache_declarations[name].append(cache_content)

    def __cache_declaration_exported_object(
            self, name, declaration, scope, path: list):
        if declaration is None:
            declaration_type = None
        else:
            declaration_type = declaration.type

        cache_content = {
            "scope": scope,
            "node": declaration,
            "node_type": declaration_type,
            "path": path
        }

        if name not in self.cache_declarations_exported_object:
            self.cache_declarations_exported_object[name] = [cache_content]
        else:
            self.cache_declarations_exported_object[name].append(cache_content)

    def __cache_method_call(
            self, name, scope, node, path: list, property_chain=None):
        if property_chain is None:
            property_chain = []

        cache_content = {
            "name": name,
            "scope": scope,
            "node": node,
            "path": path,
            "property_chain": property_chain
        }

        self.cache_method_calls.append(cache_content)

    # ~~~~~( Analysis ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __make_js_absolute_import_path(self, import_path: str) -> str:
        """Convert import path found in JavaScript import statement to an
        absolute path starting from the project root directory.

        :param import_path: The import path to convert.
        :type import_path: str

        :return: An absolute path starting from the project root directory.
        :rtype: str
        """
        abs_import_path = import_path
        is_path_relative = re.match(r"[.]{1,2}/", import_path)
        if is_path_relative:
            combined_paths = \
                os.path.abspath(
                    os.path.dirname(self.path_target_file) + "/" + import_path)

            abs_import_path = \
                re.sub("^" + re.escape(self.path_project_root) + "/",
                       "",
                       combined_paths)

        return abs_import_path

    def __convert_esprima_ast_to_object(
            self,
            node: esprima.nodes.Node | list = None) -> dict | list:
        """Convert an Esprima Abstract Syntax Tree (AST) to native objects
        and lists. The converted data is easily serialized.

        :param node: The Esprima node (or list within a node) to convert.
        :type node: esprima.nodes.Node|list

        :return: The converted AST.
        :rtype: dict|list
        """
        if node is None:
            node = []

        object_data = ""
        if isinstance(node, list):
            object_data = []
            for node_index, sub_node in enumerate(node):
                object_data.append(
                    self.__convert_esprima_ast_to_object(
                        sub_node))

        elif hasattr(node, '__dict__'):
            object_data = {}
            for sub_node_key in node.__dict__:
                object_data[sub_node_key] = \
                    self.__convert_esprima_ast_to_object(
                        node.__dict__[sub_node_key])

        elif isinstance(node, str) or isinstance(node, int):
            object_data = node

        else:
            logging.warning(
                "Object not complete because of unknown data could not be "
                f"handled in parameter tree: {type(node)}. "
                "[W-ONCBODCNBHIPTN]" +
                self.__debug_node_in_code(node))

        return object_data

    def __make_info_export_default(
            self,
            local_name: str,
            object_type: str = None,
            node: esprima.nodes.Node | list = None) -> dict:
        """Make an object that can be used for EXPORT DEFAULT information
        found in JavaScript.

        :param local_name: The exported asset's local name.
        :type local_name: str
        :param object_type: The exported asset's type. (NOT IN USE)
        :type: object_type: str
        :param node: The AST node for the exported asset. (NOT IN USE)
        :type node: esprima.nodes.Node|list

        :return: The EXPORT DEFAULT information object.
        :rtype: dict
        """
        return {
            "export": "export default",
            "local_name": local_name,
            "export_name": local_name,
            "object_type": object_type,
            "node": node
        }

    def __make_info_export_named(
            self,
            local_name: str,
            export_name: str,
            object_type: str = None,
            node: esprima.nodes.Node | list = None) -> dict:
        """Make an object that can be used for EXPORT NAMED information
        found in JavaScript.

        :param local_name: The exported asset's local name.
        :type local_name: str
        :param export_name: The exported asset's name.
        :type export_name: str
        :param object_type: The exported asset's type. (NOT IN USE)
        :type: object_type: str
        :param node: The AST node for the exported asset. (NOT IN USE)
        :type node: esprima.nodes.Node|list

        :return: The EXPORT NAMED information object.
        :rtype: dict
        """
        return {
            "export": "export",
            "local_name": local_name,
            "export_name": export_name,
            "object_type": object_type,
            "node": node
        }

    def __handle_node_export_default(
            self,
            node: esprima.nodes.ExportDefaultDeclaration) -> list:
        """Handler for AST node containing EXPORT DEFAULT information
        (ExportDefaultDeclaration). Collects and returns a list of EXPORT
        DEFAULT information objects.

        :param node: The AST node to handle.
        :type node: esprima.nodes.ExportDefaultDeclaration

        :return: A list of EXPORT DEFAULT information objects.
        :rtype: list
        """
        exported = []
        match node.declaration.type:
            case "Identifier":
                exported.append(
                    self.__make_info_export_default(
                        node.declaration.name))

            case "ObjectExpression":
                for node_prop in node.declaration.properties:
                    exported.append(
                        self.__make_info_export_default(
                            node_prop.key.name))

            case "FunctionDeclaration":
                exported.append(
                    self.__make_info_export_default(
                        node.declaration.id.name))

            case "ClassDeclaration":
                exported.append(
                    self.__make_info_export_default(
                        node.declaration.id.name))

            case _:
                logging.warning(
                    "Export information for 'export default' not yet "
                    f"supported: {node.declaration.type}. "
                    "[W-EIFEDNYSNDT]" +
                    self.__debug_node_in_code(node.declaration))

        return exported

    def __handle_node_export_named(
            self,
            node: esprima.nodes.ExportNamedDeclaration) -> list:
        """Handler for AST node containing EXPORT NAMED information
        (ExportDefaultDeclaration). Collects and returns a list of EXPORT
        NAMED information objects.

        :param node: The AST node to handle.
        :type node: esprima.nodes.ExportNamedDeclaration

        :return: A list of EXPORT NAMED information objects.
        :rtype: list
        """
        exported = []
        if len(node.specifiers) > 0:
            for export_specifier in node.specifiers:
                match export_specifier.type:
                    case "ExportSpecifier":
                        if export_specifier.exported.type != "Identifier":
                            logging.warning(
                                "Export specifier export type not supported: "
                                f"{export_specifier.exported.type}. "
                                "[W-ESETNSEETA]" +
                                self.__debug_node_in_code(
                                    export_specifier.exported))

                        if export_specifier.local.type != "Identifier":
                            logging.warning(
                                "Export specifier export type not supported: "
                                f"{export_specifier.exported.type}. "
                                "[W-ESETNSEETB]" +
                                self.__debug_node_in_code(
                                    export_specifier.exported))

                        if export_specifier.exported.type == "Identifier" and \
                                export_specifier.local.type == "Identifier":
                            exported.append(
                                self.__make_info_export_named(
                                    export_specifier.local.name,
                                    export_specifier.exported.name))

                    case _:
                        logging.warning(
                            "Export specifier type not supported: "
                            f"{export_specifier.type}. "
                            "[W-ESTNSET]" +
                            self.__debug_node_in_code(export_specifier))

        if node.declaration is not None:
            match node.declaration.type:
                case "VariableDeclaration":
                    for declared in node.declaration.declarations:
                        match declared.type:
                            case "VariableDeclarator":
                                if declared.id.type == "Identifier":
                                    exported.append(
                                        self.__make_info_export_named(
                                            declared.id.name,
                                            declared.id.name,
                                            "VariableDeclarator",
                                            declared))

                                else:
                                    logging.warning(
                                        "Exported variable declaration with "
                                        "id of type: "
                                        f"{declared.id.type} not yet "
                                        "supported. "
                                        "[W-EVDWIOTNDITNYS]" +
                                        self.__debug_node_in_code(
                                            declared.id))

                case "FunctionDeclaration":
                    if node.declaration.id.type == "Identifier":
                        exported.append(
                            self.__make_info_export_named(
                                node.declaration.id.name,
                                node.declaration.id.name,
                                "FunctionDeclaration",
                                node.declaration))

                    else:
                        logging.warning(
                            "Exported function declaration with id of type: "
                            f"{node.declaration.id.type} not yet supported. "
                            "[W-EFDWIOTNDITNYS]" +
                            self.__debug_node_in_code(node.declaration))

                case "ClassDeclaration":
                    if node.declaration.id.type == "Identifier":
                        exported.append(
                            self.__make_info_export_named(
                                node.declaration.id.name,
                                node.declaration.id.name,
                                "ClassDeclaration",
                                node.declaration))

                    else:
                        logging.warning(
                            "Exported class declaration with id of type: "
                            f"{node.declaration.id.type} not yet supported. "
                            "[W-ECDWIOTNDITNYS]" +
                            self.__debug_node_in_code(node.declaration))

                case _:
                    logging.warning(
                        "Export information support for type: "
                        f"{node.declaration.type}"
                        " not yet added. "
                        "[W-EISFTNDTNYS]" +
                        self.__debug_node_in_code(node.declaration))

        return exported

    def __process_find_exported_objects(self) -> None:
        """Process to find all exported assets in the AST for the loaded
        target file. The assets are saved into the exported assets instance
        attribute.

        :return: None
        """
        exported = []
        if not isinstance(self.ast_target_file, esprima.nodes.Module):
            ValueError("Can only start process from esprima.nodes.Module")

        for node in self.ast_target_file.body:
            match node.type:
                case "ExportDefaultDeclaration":
                    exported += self.__handle_node_export_default(node)
                case "ExportNamedDeclaration":
                    exported += self.__handle_node_export_named(node)

        self.analyze_exported = exported

    def __make_info_import(
            self,
            local_name: str,
            external_name: str,
            absolute_import_path: str) -> dict:
        """Make an object that can be used for IMPORT information found in
        JavaScript.

        :param local_name: The imported dependency's local name.
        :type local_name: str
        :param external_name: The imported dependency's external name.
        :type external_name: str
        :param absolute_import_path: The absolute import path starting from the
        project root directory.
        :type absolute_import_path:

        :return: The IMPORT information object.
        :rtype: dict
        """
        return {
            "local_name": local_name,
            "external_name": external_name,
            "absolute_import_path": absolute_import_path
        }

    def __process_find_imported_objects(self):
        """Process to find all imported assets in the AST for the loaded
        target file. The assets are saved into the imported assets instance
        attribute.

        :return: None
        """
        imported = []
        if not isinstance(self.ast_target_file, esprima.nodes.Module):
            ValueError("Can only start process from esprima.nodes.Module")

        for node in self.ast_target_file.body:
            if node.type == "ImportDeclaration":

                absolute_import_path = \
                    self.__make_js_absolute_import_path(node.source.value)

                for import_specifier in node.specifiers:
                    match import_specifier.type:
                        case "ImportSpecifier":
                            imported += [
                                self.__make_info_import(
                                    import_specifier.local.name,
                                    import_specifier.imported.name,
                                    absolute_import_path)]

                        case "ImportDefaultSpecifier":
                            imported += [
                                self.__make_info_import(
                                    import_specifier.local.name,
                                    import_specifier.local.name,
                                    absolute_import_path)]

                        case _:
                            logging.warning(
                                f"Import specifier of type {node.type} not "
                                "yet supported.")

        self.analyze_imported = imported

    # ~~~~~( AST Nodes - Information Extraction ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __node_handler_get_name(
            self,
            node_property: esprima.nodes.Node) -> str:
        """Handle AST property node and get name if possible.

        :param node_property: The node property of a node to get the name for.
        :type node_property: esprima.nodes.Node

        :return: The name if found, otherwise 'UNKNOWN'
        :rtype: str
        """
        property_name = "UNKNOWN"
        if node_property.type == "Identifier":
            property_name = node_property.name

        elif node_property.type == "Literal":
            property_name = node_property.value
        else:
            logging.warning(
                "Node handling to get name for type: "
                f"{node_property.type} not yet supported.")

        return property_name

    # ~~~~~( AST Walk - Cache Handling ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __cache_handle_method_call(
            self,
            scope: list,
            node: (esprima.nodes.CallExpression |
                   esprima.nodes.StaticMemberExpression |
                   esprima.nodes.NewExpression),
            path: list) -> None:
        """Handle caching of method calls of the following kinds:
            - aa.bb.cc.dd()
            - ff()
            - (new ClassF()).kk()
            - this.kk()

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.CallExpression |
                    esprima.nodes.StaticMemberExpression |
                    esprima.nodes.NewExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        property_chain = []
        node_walk = node
        last_node = node
        while node_walk.type == "MemberExpression" or \
                node_walk.type == "CallExpression" or \
                node_walk.type == "NewExpression":
            if node_walk.type == "CallExpression" or \
                    node_walk.type == "NewExpression":
                # Walk after method return is difficult to follow and
                # test, so we reset the walk here. In:
                #   aa.bb.cc().ee.ff()
                # only aa.bb.cc() is cached, and in:
                #   aa().bb.cc().ee.ff()
                # only aa() is cached.
                if node_walk.callee.type == "MemberExpression" or \
                        node_walk.callee.type == "CallExpression" or \
                        node_walk.callee.type == "NewExpression":
                    last_node = node_walk

                property_chain = []
                node_walk = node_walk.callee

            else:
                property_chain.append(
                    (node_walk.type,
                     self.__node_handler_get_name(node_walk.property))
                )

                if node_walk.object.type == "MemberExpression" or \
                        node_walk.object.type == "CallExpression" or \
                        node_walk.object.type == "NewExpression":
                    last_node = node_walk

                node_walk = node_walk.object

        match node_walk.type:
            case "Identifier":
                property_chain.append((last_node.type, node_walk.name))

            case "ThisExpression":
                property_chain.append((last_node.type, "this"))

            case "ArrowFunctionExpression" | "FunctionExpression":
                if node_walk.id is None:
                    # Call to anonymous function, don't save to method
                    # call cache.
                    return

            case "Super":
                return

            case _:
                logging.warning(
                    "Handling of caching of method call for final callee of "
                    f"type: {node_walk.type} not yet supported. "
                    "[W-HOCOMCFFCOTNTNYS]" +
                    self.__debug_node_in_code(node_walk))
                return

        property_chain.reverse()

        self.__cache_method_call(
            property_chain[-1][1], scope, node, path, property_chain)

    def __cache_handle_declaration_arrayexpression(
            self,
            scope: list,
            node: esprima.nodes.ArrayExpression,
            path: list,
            nested_declaration_name: list = None) -> None:
        """Handle caching of variable declarators with objects.
        The following:
            - aa = [() => {}, () => {}]
        Will save declarations for aa[0] and aa[1]

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.ArrayExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        if nested_declaration_name is None:
            nested_declaration_name = []

        nested_declaration_name_item = nested_declaration_name

        if node.elements is not None:
            for index, current_element in enumerate(node.elements):
                if len(nested_declaration_name) >= 1:
                    nested_declaration_name_item = \
                        nested_declaration_name[:-1] + \
                        [nested_declaration_name[-1] + f"[{index}]"]

                self.__cache_declaration(
                    '.'.join(nested_declaration_name_item),
                    current_element,
                    scope,
                    path + ["elements", str(index)],
                    "item"
                )

                match current_element.type:
                    case "CallExpression":
                        self.__cache_handle_method_call(
                            scope + [("array-item", str(index))],
                            current_element,
                            path + ["elements", str(index)])

                    case "ObjectExpression":
                        self.__cache_handle_declaration_objectexpression(
                            scope + [("array-item", str(index))],
                            current_element,
                            path + ["elements", str(index)],
                            nested_declaration_name_item)

                    case "ArrayExpression":
                        self.__cache_handle_declaration_arrayexpression(
                            scope + [("array-item", str(index))],
                            current_element,
                            path + ["elements", str(index)],
                            nested_declaration_name_item)

                    case "Literal" | \
                         "ArrowFunctionExpression" | \
                         "FunctionExpression" \
                         "NewExpression" | "MemberExpression":
                        continue

                    case _:
                        logging.warning(
                            "Cache handling for variable declaration "
                            "of type ArrayExpression cannot yet "
                            "handle item of type: "
                            f"{current_element.type}. "
                            "[W-CHFVDOTOCYHPVOTOVT]" +
                            self.__debug_node_in_code(current_element))

    def __cache_handle_declaration_objectexpression(
            self,
            scope: list,
            node: esprima.nodes.ObjectExpression,
            path: list,
            nested_declaration_name: list = None) -> None:
        """Handle caching of variable declarators with objects.
        The following:
            - ff = {
                gg: {
                  hh: () => {}
                }
              }
        Will save declarations for ff, ff.gg and ff.gg.hh

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.ObjectExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        if nested_declaration_name is None:
            nested_declaration_name = []

        if node.properties is not None:
            for index, obj_property in enumerate(node.properties):

                if obj_property.type != "Property":
                    logging.warning(
                        "Cache handling of variable declaration of "
                        "type ObjectExpression cannot yet handle "
                        "object properties of type "
                        f"{obj_property.type} not yet supported. "
                        "[W-CHOVDOTOCYHOPOTOKTNYS]" +
                        self.__debug_node_in_code(obj_property))
                    continue

                if obj_property.key.type == "Identifier":
                    property_name = obj_property.key.name
                elif obj_property.key.type == "Literal":
                    property_name = obj_property.key.value
                else:
                    logging.warning(
                        "Cache handling of variable declaration of "
                        "type ObjectExpression cannot yet handle "
                        "object property keys of type "
                        f"{obj_property.key.type} not yet supported. "
                        "[W-CHOVDOTOCYHOPKOTOKTNYS]" +
                        self.__debug_node_in_code(obj_property.key))
                    continue

                self.__cache_declaration(
                    '.'.join(nested_declaration_name + [property_name]),
                    obj_property.value,
                    scope,
                    path + ["properties", str(index), "value"],
                    "property"
                )

                match obj_property.value.type:
                    case "CallExpression":
                        self.__cache_handle_method_call(
                            scope + [("object-variable", property_name)],
                            obj_property.value,
                            path + ["properties", str(index), "value"])

                    case "ObjectExpression":
                        self.__cache_handle_declaration_objectexpression(
                            scope + [("object-variable", property_name)],
                            obj_property.value,
                            path + ["properties", str(index), "value"],
                            nested_declaration_name + [property_name])

                    case "ArrayExpression":
                        self.__cache_handle_declaration_arrayexpression(
                            scope + [("object-variable", property_name)],
                            obj_property.value,
                            path + ["properties", str(index), "value"],
                            nested_declaration_name + [property_name])

                    case "Literal" | \
                         "ArrowFunctionExpression" | \
                         "FunctionExpression" \
                         "NewExpression" | "MemberExpression":
                        continue

                    case _:
                        logging.warning(
                            "Cache handling for variable declaration "
                            "of type ObjectExpression cannot yet "
                            "handle property value of type: "
                            f"{obj_property.value.type}. "
                            "[W-CHFVDOTOCYHPVOTOVT]" +
                            self.__debug_node_in_code(obj_property.value))

    def __cache_handle_anonymous_objectexpression(
            self,
            scope: list,
            node: esprima.nodes.ObjectExpression,
            path: list) -> None:
        """Handle caching of anonymous objects (passed as arguments)
        The following:
            - aa({bb: cc()})
        Will save the call to cc()

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.ObjectExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        if node.properties is not None:
            for index, obj_property in enumerate(node.properties):
                if obj_property.type != "Property":
                    logging.warning(
                        "Cache handling for anonymous ObjectExpression "
                        "cannot yet handle properties of type: "
                        f"{obj_property.type}. "
                        "[W-CHFAOCYHPOTOT]" +
                        self.__debug_node_in_code(obj_property))
                    continue

                match obj_property.value.type:
                    case "CallExpression":
                        self.__cache_handle_method_call(
                            scope,
                            obj_property.value,
                            path + ["properties", str(index), "value"])

                    case "ObjectExpression":
                        self.__cache_handle_anonymous_objectexpression(
                            scope,
                            obj_property.value,
                            path + ["properties", str(index), "value"])

                    case "Literal" | \
                         "ArrowFunctionExpression" | \
                         "FunctionExpression" \
                         "NewExpression" | "MemberExpression":
                        continue

                    case _:
                        logging.warning(
                            "Cache handling for anonymous ObjectExpression "
                            "cannot yet handle property value of type: "
                            f"{obj_property.value.type}. "
                            "[W-CHFOCYPVOTOVT]" +
                            self.__debug_node_in_code(obj_property.value))

    def __cache_handle_declaration_variabledeclarator(
            self,
            scope: list,
            parent_node: esprima.nodes.VariableDeclaration,
            node: esprima.nodes.VariableDeclarator,
            path: list) -> None:
        """Handle caching of variable declarators of type:
            - const foo = /* Anything here */
            - let bar = /* Anything here */
            - var baz = /* Anything here */
            - const [qux, quux] = [/* Anything here */, /* Anything here */]

        Caching of only class initiation (NewExpression) or class
        prop (MemberExpression) usage is not interesting currently:
            - new ClassA()
            - new ClassA().propK

        Further, caching of direct method calls (CallExpression) after
        assignments are cached, and both method calls and declarations in
        objects (ObjectExpression) are also cached.

        :param scope: The current scope in the AST.
        :type scope: list
        :param parent_node: The parent node of the variable declarator node.
        :type parent_node: esprima.nodes.VariableDeclaration
        :param node: The variable declarator node to handle.
        :type node: esprima.nodes.VariableDeclarator
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        if node.id.type == "Identifier":
            self.__cache_declaration(
                node.id.name,
                node.init,
                scope,
                path + ["init"],
                parent_node.kind
            )

            if node.init is None:
                # Nothing to walk into, stop here.
                return

            match node.init.type:
                case "CallExpression":
                    self.__cache_handle_method_call(
                        scope,
                        node.init,
                        path + ["init"])

                case "ObjectExpression":
                    self.__cache_handle_declaration_objectexpression(
                        scope + [("object-variable", node.id.name)],
                        node.init,
                        path + ["init"],
                        [node.id.name])

                case "Literal" | \
                     "ArrowFunctionExpression" | "FunctionExpression" | \
                     "NewExpression" | "MemberExpression" | \
                     "BinaryExpression":
                    return

                case _:
                    logging.warning(
                        "Cache handling for variable declaration call of "
                        f"type: {node.init.type} not yet supported. "
                        "[W-CHFVDCOTDITNYS]" +
                        self.__debug_node_in_code(node.init))

        elif node.id.type == "ArrayPattern":
            if node.init.type == "ArrayExpression" and \
                    len(node.id.elements) == \
                    len(node.init.elements):
                for index, declaration_item in \
                        enumerate(node.id.elements):

                    self.__cache_declaration(
                        declaration_item.name,
                        node.init.elements[index],
                        scope,
                        path + ["init", "elements", str(index)],
                        parent_node.kind
                    )

                    match node.init.elements[index].type:
                        case "ArrowFunctionExpression" | "FunctionExpression":
                            if node.init.elements[index].body.type \
                                    == "BlockStatement":
                                self.__process_ast_walk(
                                    scope + [
                                        ("function", declaration_item.name)],
                                    node.init.elements[index].body.body,
                                    path + ["init", "elements", str(index),
                                            "body", "body"])
                            else:
                                self.__process_ast_walk(
                                    scope + [
                                        ("function", declaration_item.name)],
                                    node.init.elements[index].body,
                                    path + ["init", "elements", str(index),
                                            "body"])

                        case "CallExpression":
                            self.__cache_handle_method_call(
                                scope,
                                node.init.elements[index],
                                path + ["init", "elements", str(index)])

                        case "ObjectExpression":
                            self.__cache_handle_declaration_objectexpression(
                                scope + [
                                    ("object-variable",
                                     declaration_item.name)],
                                node.init.elements[index],
                                path + ["init", "elements", str(index)],
                                [declaration_item.name])

                        case "Literal" | \
                             "ArrowFunctionExpression" | \
                             "FunctionExpression" | \
                             "NewExpression" | "MemberExpression":
                            return

                        case _:
                            logging.warning(
                                "Cache handling for variable declaration "
                                "call with array pattern and array expression "
                                "of type: "
                                f"{node.init.elements[index].type} "
                                "not yet supported. "
                                "[W-CHFVDCWAPAAEOTNIEITNYS]" +
                                self.__debug_node_in_code(
                                    node.init.elements[index]))

            else:
                match node.init.type:
                    case "CallExpression":
                        # TODO: How to tell user that the variable is
                        #  dependent on only a part of the called method...
                        #  const [aa, bb] = call_method()
                        #  How to show that aa depends on call_method()[0]?

                        self.__cache_handle_method_call(
                            scope,
                            node.init,
                            path + ["init"])

                    case "Literal":
                        return

                    case _:
                        logging.warning(
                            "Cache handling for variable declarator with "
                            "id of an array pattern and initiator of type: "
                            f"{node.init.type} not yet supported. "
                            "[W-CHFVDWIOAAPAIOTNITNYS]" +
                            self.__debug_node_in_code(node.init))

        else:
            logging.warning(
                "Cache handling for variable declaration call with id of "
                f"type {node.id.type} not yet supported. "
                "[W-CHFVDCWIOTNITNYS]" +
                self.__debug_node_in_code(node.id))

    def __cache_handle_exported_object_declaration(
            self,
            node: esprima.nodes.ObjectExpression,
            path: list):
        """Handle caching of special declaration taking place inside an
        exported object.

        Example code:
        .. code-block:: JavaScript
            export default {
              foo: () => {/* ... */}
            };

        'foo' will be cached.

        :param node: The variable declarator node to handle.
        :type node: esprima.nodes.ObjectExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        if node is None or node.type != "ObjectExpression":
            return

        scope = [("special", "export")]

        if node.properties is not None:
            for index, obj_property in enumerate(node.properties):

                if obj_property.type != "Property":
                    logging.warning(
                        "Cache handling of special declaration in exported "
                        f"object with property of type {obj_property.type} "
                        "not yet supported. "
                        "[W-CHOSDIEOWPOTOTNYS]" +
                        self.__debug_node_in_code(obj_property))
                    continue

                if obj_property.key.type == "Identifier":
                    property_name = obj_property.key.name
                elif obj_property.key.type == "Literal":
                    property_name = obj_property.key.value
                else:
                    logging.warning(
                        "Cache handling of special declaration in exported "
                        f"object with property keys of type "
                        f"{obj_property.key.type} not yet supported. "
                        "[W-CHOSDIEOWPKOTOKTNYS]" +
                        self.__debug_node_in_code(obj_property.key))
                    continue

                self.__cache_declaration_exported_object(
                    property_name,
                    obj_property.value,
                    scope,
                    path + ["properties", str(index), "value"]
                )

                match obj_property.value.type:
                    case "CallExpression":
                        self.__cache_handle_method_call(
                            scope + [("object-variable", property_name)],
                            obj_property.value,
                            path + ["properties", str(index), "value"])

                    case "ObjectExpression":
                        self.__cache_handle_declaration_objectexpression(
                            scope + [("object-variable", property_name)],
                            obj_property.value,
                            path + ["properties", str(index), "value"],
                            property_name)

                    case "Literal" | \
                         "ArrowFunctionExpression" | \
                         "FunctionExpression" \
                         "NewExpression" | "MemberExpression":
                        continue

                    case _:
                        logging.warning(
                            "Cache handling of special declaration in "
                            "exported object cannot yet handle property "
                            f"value of type: {obj_property.value.type}. "
                            "[W-CHOSDIEOCYHPVOTOVT]" +
                            self.__debug_node_in_code(obj_property.value))

    # ~~~~~( AST Walk - Tree Exploration ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __ast_walk_handle_method_call(
            self,
            scope: list,
            node: (esprima.nodes.CallExpression |
                   esprima.nodes.StaticMemberExpression |
                   esprima.nodes.NewExpression),
            path: list) -> None:
        """Handle AST walk into a method call (CallExpression,
        StaticMemberExpression or NewExpression). Will continue walking into
        the arguments as they might contain interesting code. In:
            - aa.bb.cc(() => {/* Walk here */})
        The walk will continue into arguments of cc().
        In:
            - aa.bb.cc(() => {/* Walk here */}).dd(() => {/* Walk here */})
        The walk will continue into arguments of cc() and dd().

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.CallExpression |
                    esprima.nodes.StaticMemberExpression |
                    esprima.nodes.NewExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        node_walk = node
        call_chain = []
        call_path = path
        while node_walk.type == "MemberExpression" or \
                node_walk.type == "CallExpression" or \
                node_walk.type == "NewExpression":
            if node_walk.type == "CallExpression" or \
                    node_walk.type == "NewExpression":

                if node_walk.callee.type == "Identifier":
                    call_chain.append(
                        (node_walk.type,
                         node_walk.callee.name,
                         call_path + ["arguments"],
                         node_walk.arguments)
                    )

                    node_walk = node_walk.callee
                    call_path += ["callee"]

                elif node_walk.callee.type == "MemberExpression":
                    call_chain.append(
                        (node_walk.type,
                         self.__node_handler_get_name(
                             node_walk.callee.property),
                         call_path,
                         node_walk.arguments)
                    )

                    node_walk = node_walk.callee.object
                    call_path += ["callee", "object"]

                elif node_walk.callee.type == "Super":
                    call_chain.append(
                        (node_walk.type,
                         "super",
                         call_path + ["arguments"],
                         node_walk.arguments)
                    )

                    node_walk = node_walk.callee
                    call_path += ["callee"]

                elif node_walk.callee.type == "CallExpression" or \
                        node_walk.callee.type == "ArrowFunctionExpression":
                    node_walk = node_walk.callee
                    call_path += ["callee"]

                else:
                    logging.warning(
                        "AST walk handling of method call node walk callee "
                        f"type: {node_walk.callee.type} not yet supported. "
                        "[W-AWHOMCNWCTNCTNYS]" +
                        self.__debug_node_in_code(node_walk.callee))
                    return

            else:
                call_chain.append(
                    (node_walk.type,
                     self.__node_handler_get_name(node_walk.property),
                     call_path)
                )

                if node_walk.object.type == "Identifier":
                    call_chain.append(
                        (node_walk.type,
                         node_walk.object.name,
                         call_path)
                    )

                node_walk = node_walk.object
                call_path += ["object"]

        call_chain.reverse()

        if node_walk.type == "ArrowFunctionExpression":
            if node_walk.body.type == "BlockStatement":
                self.__process_ast_walk(
                    scope + [("anonymous-function", "")],
                    node_walk.body.body,
                    call_path + ["body", "body"])
            else:
                self.__process_ast_walk(
                    scope + [("anonymous-function", "")],
                    node_walk.body,
                    call_path + ["body"])

        elif node_walk.type != "Identifier" and \
                node_walk.type != "ThisExpression" and \
                node_walk.type != "Super":
            logging.warning(
                "AST walk handling of method call for final callee of type: "
                f"{node_walk.type} not yet supported. "
                "[W-AWHOMCFFCOTNTNYS]" +
                self.__debug_node_in_code(node_walk))

        call_identity = []
        for call in call_chain:
            call_args = None

            if call[0] == "CallExpression" or call[0] == "NewExpression":
                call_type, call_name, call_path, call_args = call
            else:
                call_type, call_name, call_path = call

            call_identity.append((call_type, call_name))

            if call_type == "CallExpression" or call_type == "NewExpression":
                self.__process_ast_walk(
                    scope + [("call", call_identity)],
                    call_args,
                    call_path)

    def __ast_walk_handle_objectexpression(
            self,
            scope: list,
            node: esprima.nodes.ObjectExpression,
            path: list) -> None:
        """Handle AST walk into an object expression (ObjectExpression).
        Will continue walking into the objects properties. Example:
        .. code-block:: JavaScript
            const aa = {
                bb: 123,
                cc: () => {/* Walk here */}
            }

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.ObjectExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        if node.properties is None:
            return

        for index, obj_property in enumerate(node.properties):
            if obj_property.type != "Property":
                logging.warning(
                    "AST walk handling of object expression property of type "
                    f"{obj_property.type} not yet supported. "
                    "[W-AWHOOEPOTOTNYS]" +
                    self.__debug_node_in_code(obj_property))
                continue

            if obj_property.key.type == "Identifier":
                property_name = obj_property.key.name
            elif obj_property.key.type == "Literal":
                property_name = obj_property.key.value
            else:
                logging.warning(
                    "AST walk handling of object expression property with "
                    f"key of type {obj_property.key.type} not yet supported. "
                    "[W-AWHOOEPWKOTOKTNYS]" +
                    self.__debug_node_in_code(obj_property.key))
                continue

            match obj_property.value.type:
                case "ArrowFunctionExpression" | "FunctionExpression":
                    if obj_property.value.body.type == "BlockStatement":
                        self.__process_ast_walk(
                            scope + [("function", property_name)],
                            obj_property.value.body.body,
                            path + ["properties", str(index), "value", "body",
                                    "body"])
                    else:
                        self.__process_ast_walk(
                            scope + [("function", property_name)],
                            obj_property.value.body,
                            path + ["properties", str(index), "value", "body"])

                case "CallExpression" | "NewExpression" | "MemberExpression":
                    self.__ast_walk_handle_method_call(
                        scope,
                        obj_property.value,
                        path + ["properties", str(index), "value"])

                case "ObjectExpression":
                    self.__ast_walk_handle_objectexpression(
                        scope + [("object-variable", property_name)],
                        obj_property.value,
                        path + ["properties", str(index), "value"])

                case "ArrayExpression":
                    self.__process_ast_walk(
                        scope + [("object-variable", property_name)],
                        obj_property.value,
                        path + ["properties", str(index), "value"])

                case "Literal":
                    continue

                case _:
                    logging.warning(
                        "AST walk handling of object expression property "
                        f"value of type: {obj_property.value.type} not yet "
                        "supported. "
                        "[W-AWHOOEPVOTOVTNYS]" +
                        self.__debug_node_in_code(obj_property.value))

    def __ast_walk_handle_functiondeclaration(
            self,
            scope: list,
            node: esprima.nodes.FunctionDeclaration,
            path: list) -> None:
        """Handle AST walk into a function declaration (FunctionDeclaration).
        Will continue walking into the function bodies. Example:
        .. code-block:: JavaScript
            function quuz() {
                /* Walk here */
            }

        Further, the function will be saved to the function cache.

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.FunctionDeclaration
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        self.__cache_function(
            node.id.name, scope, node, node.type, path)

        if node.body.type == "BlockStatement" and \
                node.body.body is not None:
            self.__process_ast_walk(
                scope + [("function", node.id.name)],
                node.body.body,
                path + ["body", "body"])

        else:
            logging.warning(
                "AST walk handling of function declaration of type "
                f"{node.type} cannot yet handle function body of "
                f"type {node.body.type}"
                "[W-AWHOFDOTNTCYHFBOTNBT]" +
                self.__debug_node_in_code(node.body))

    def __ast_walk_handle_classdeclaration(
            self,
            scope: list,
            node: esprima.nodes.ClassDeclaration,
            path: list) -> None:
        """Handle AST walk into a class declaration (ClassDeclaration).
        Will continue walking into a class' methods. Example:
        .. code-block:: JavaScript
            class Corge {
                grault() {
                    /* Walk here */
                }
                garply() {
                    /* Also walk here */
                }
            }

        Further, all found methods will be saved to the class method cache
        where it will be noted if they are static, if the class have a
        constructor and more.

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.ClassDeclaration
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        found_methods = []
        constructor_method = None
        if node.body.type != "ClassBody":
            logging.warning(
                "AST walk handling of class declaration cannot yet handle "
                f"class body of type {node.body.type}")
            return

        if node.body.body is not None:
            for index, class_node in enumerate(node.body.body):
                match class_node.type:
                    case "MethodDefinition":
                        if class_node.key.name == "constructor":
                            self.__process_ast_walk(
                                scope + [("class", node.id.name),
                                         ("class-constructor",
                                          "constructor")],
                                class_node.value.body.body,
                                path + ["body", "body", str(index),
                                        "value", "body", "body"])

                            constructor_method = class_node.value

                        else:
                            found_methods.append(
                                (class_node.key.name,
                                 class_node.value,
                                 path + ["body", "body", str(index), "value"],
                                 class_node.static))

                    case _:
                        logging.warning(
                            "AST walk handling of class declaration cannot "
                            "yet handle internal node of type "
                            f"{class_node.type}. "
                            "[W-AWHOCDCYHINOTCT]" +
                            self.__debug_node_in_code(class_node))

        for found_method in found_methods:
            method_name, method_value, method_path, method_static = \
                found_method

            self.__cache_class_method(
                node.id.name,
                constructor_method,
                method_static,
                method_name,
                scope + [("class", node.id.name)],
                method_value,
                method_path)

            self.__process_ast_walk(
                scope + [("class", node.id.name),
                         ("function", method_name)],
                method_value.body.body,
                method_path + ["body", "body"])

    def __ast_walk_handle_binaryexpression(
            self,
            scope: list,
            node: esprima.nodes.BinaryExpression,
            path: list) -> None:
        """Handle AST walk into a binary expression (BinaryExpression).
        Will continue walking into method calls used in a binary expression.
        Example:
        .. code-block:: JavaScript
            foo(/* Walk here */) !== bar(/* Walk here */)

        Further, all found methods calls used in the expressions will be
        saved to the method call cache, and all property declarations in
        any object expressions will be saved.

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.BinaryExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        possible_paths = ["left", "right"]
        for current_path in possible_paths:
            match node.__dict__[current_path].type:
                case "CallExpression" | "NewExpression":
                    self.__cache_handle_method_call(
                        scope,
                        node.__dict__[current_path],
                        path + [current_path])

                    self.__ast_walk_handle_method_call(
                        scope,
                        node.__dict__[current_path],
                        path + [current_path])

                case "ObjectExpression":
                    self.__cache_handle_declaration_objectexpression(
                        scope,
                        node.__dict__[current_path],
                        path + [current_path])

                    self.__ast_walk_handle_objectexpression(
                        scope,
                        node.__dict__[current_path],
                        path + [current_path])

                case "BinaryExpression":
                    self.__ast_walk_handle_binaryexpression(
                        scope,
                        node.__dict__[current_path],
                        path + [current_path])

                case "Literal" | "Identifier" | \
                     "MemberExpression" | \
                     "UnaryExpression":
                    # Nothing more to enter here.
                    return

                case _:
                    logging.warning(
                        "AST walk handling of binary expression "
                        f"{current_path} hand type: "
                        f"{node.__dict__[current_path].type} "
                        f"not yet supported. "
                        "[W-AWHOBERHTNRTNYS]" +
                        self.__debug_node_in_code(node.__dict__[current_path]))

    def __ast_walk_handle_logicalexpression(
            self,
            scope: list,
            node: esprima.nodes.BinaryExpression,
            path: list) -> None:
        """Handle AST walk into a logical expression (BinaryExpression).
        Will continue walking into method calls used in a logical expression.
        Example:
        .. code-block:: JavaScript
            waldo(/* Walk here */) !== fred(/* Walk here */) ||
            plugh(/* Walk here */) > foo

        Further, all found methods used in the expressions will be saved to
        the method call cache.

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.BinaryExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        match node.left.type:
            case "LogicalExpression":
                self.__ast_walk_handle_logicalexpression(
                    scope,
                    node.left,
                    path + ["left"])

            case "BinaryExpression":
                self.__ast_walk_handle_binaryexpression(
                    scope,
                    node.left,
                    path + ["left"])

            case "CallExpression":
                self.__ast_walk_handle_method_call(
                    scope,
                    node.left,
                    path + ["left"])

            case "JSXElement":
                self.__ast_walk_handle_jsxelement(
                    scope,
                    node.left,
                    path + ["left"])

            case "Literal" | "MemberExpression":
                pass

            case _:
                logging.warning(
                    "AST walk handling of logical expression left hand type: "
                    f"{node.left.type} not yet supported. "
                    "[W-AWHOLELHTNLTNYS]" +
                    self.__debug_node_in_code(node.left))

        match node.right.type:
            case "BinaryExpression":
                self.__ast_walk_handle_binaryexpression(
                    scope,
                    node.right,
                    path + ["right"])

            case "CallExpression":
                self.__cache_handle_method_call(
                    scope,
                    node.right,
                    path + ["right"])

                self.__ast_walk_handle_method_call(
                    scope,
                    node.right,
                    path + ["right"])

            case "JSXElement":
                self.__ast_walk_handle_jsxelement(
                    scope,
                    node.right,
                    path + ["right"])

            case "Identifier":
                pass

            case _:
                logging.warning(
                    "AST walk handling of logical expression right hand type: "
                    f"{node.right.type} not yet supported. "
                    "[W-AWHOLERHTDRTNYS]" +
                    self.__debug_node_in_code(node.right))

    def __ast_walk_handle_ifstatement(
            self,
            scope: list,
            node: esprima.nodes.IfStatement,
            path: list,
            pre_condition: list = None) -> None:
        """Handle AST walk into if statements (IfStatement). Will continue
        walking into the body of all alternate paths, and also into method
        calls used in the conditions.

        Example:
        .. code-block:: JavaScript
            if (baz === foo(/* Walk here */)) {
                /* Walk here */
            } else if (global_gazonk = bar(/* Walk here */)) {
                /* Walk here */
            } else {
                /* Walk here */
            }

        Further, all found methods used in the conditions will be saved to
        the method call cache.

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.IfStatement
        :param path: The current path taken in the AST.
        :type path: list
        :param pre_condition: Existing preconditions that must match alongside
        current conditions.
        :type pre_condition: list

        :return: None
        """
        if pre_condition is None:
            pre_condition = []

        match node.test.type:
            case "AssignmentExpression":
                self.__ast_walk_handle_assignmentexpression(
                    scope,
                    node.test,
                    path + ["test"])

            case "LogicalExpression":
                self.__ast_walk_handle_logicalexpression(
                    scope,
                    node.test,
                    path + ["test"])

            case "BinaryExpression":
                self.__ast_walk_handle_binaryexpression(
                    scope,
                    node.test,
                    path + ["test"])

            case "CallExpression":
                self.__cache_handle_method_call(
                    scope,
                    node.test,
                    path + ["test"])

                self.__ast_walk_handle_method_call(
                    scope, node.test, path + ["test"])

            case "Literal":
                pass

            case _:
                logging.warning(
                    "AST walk handling of if statement with test of type: "
                    f"{node.test.type} not yet supported. "
                    "[W-AWHOISWTOTNTTNYS]" +
                    self.__debug_node_in_code(node.test))

        condition_range = node.test.range
        condition_text = \
            self.code_target_file[condition_range[0]:condition_range[1]]

        if len(pre_condition) > 0:
            combined_condition_text = \
                f"{' && '.join(pre_condition)} && {condition_text}"
            combined_condition_text_alternate = \
                f"{' && '.join(pre_condition)} && NOT({condition_text})"
        else:
            combined_condition_text = condition_text
            combined_condition_text_alternate = f"NOT({condition_text})"

        self.__process_ast_walk(
            scope + [("condition", combined_condition_text)],
            node.consequent.body,
            path + ["consequent", "body"])

        if node.alternate is not None:
            match node.alternate.type:
                case "BlockStatement":
                    self.__process_ast_walk(
                        scope + [("condition",
                                  combined_condition_text_alternate)],
                        node.alternate.body,
                        path + ["alternate", "body"])

                case "IfStatement":
                    self.__ast_walk_handle_ifstatement(
                        scope,
                        node.alternate,
                        path + ["alternate"],
                        pre_condition + [f"NOT({condition_text})"])

                case _:
                    logging.warning(
                        "AST walk handling of if statement alternate type "
                        f"{node.alternate.type} not yet supported. "
                        "[W-AWHOISATNATNYS]" +
                        self.__debug_node_in_code(node.alternate))

    def __ast_walk_handle_switchstatement(
            self,
            scope: list,
            node: esprima.nodes.SwitchStatement,
            path: list) -> None:
        """Handle AST walk into switch statements (SwitchStatement). Will
        continue walking into the body of all cases, and also into method
        calls used in the conditions.

        Example:
        .. code-block:: JavaScript
            switch(expression) {
              case foo(/* Walk here */):
                /* Walk here */
                break;
              case bar(/* Walk here */):
                /* Walk here */
                break;
              default:
                /* Walk here */
            }

        Further, all found methods used in the conditions will be saved to
        the method call cache.

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.SwitchStatement
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        discriminant_range = node.discriminant.range
        discriminant_text = \
            self.code_target_file[discriminant_range[0]:discriminant_range[1]]

        # TODO: Add support to walk into the node.discriminant (and cache any
        #  calls)!
        #  ...
        #  switch(/* Walk here */) {
        #  ...

        for index, switch_case in enumerate(node.cases):
            if switch_case.type != "SwitchCase":
                logging.warning(
                    "AST walk handling of switch statement switch case of "
                    f"type: {switch_case.type} not yet supported. "
                    "[W-AWHOSSSCOTSTNYS]" +
                    self.__debug_node_in_code(switch_case))
                continue

            if switch_case.test is not None:
                match switch_case.test.type:
                    case "AssignmentExpression":
                        self.__ast_walk_handle_assignmentexpression(
                            scope,
                            switch_case.test,
                            path + ["cases", str(index), "test"])

                    case "LogicalExpression":
                        self.__ast_walk_handle_logicalexpression(
                            scope,
                            switch_case.test,
                            path + ["cases", str(index), "test"])

                    case "BinaryExpression":
                        self.__ast_walk_handle_binaryexpression(
                            scope,
                            switch_case.test,
                            path + ["cases", str(index), "test"])

                    case "CallExpression":
                        self.__cache_handle_method_call(
                            scope,
                            switch_case.test,
                            path + ["cases", str(index), "test"])

                        self.__ast_walk_handle_method_call(
                            scope,
                            switch_case.test,
                            path + ["cases", str(index), "test"])

                    case "ArrowFunctionExpression":
                        logging.warning(
                            "AST walk handling of switch statement found "
                            "anonymous function expression in a case. There "
                            "should be no way for the contents of it to be "
                            "executed, but it's best to inspect the actual "
                            f"code between {switch_case.test.range[0]} and "
                            f"{switch_case.test.range[1]}. "
                            "[W-AWHOSSFAFEIACTSBNWFTCOITBEBIBTITACBSTRASTR]" +
                            self.__debug_node_in_code(switch_case))
                        # Uncomment to read code
                        # print(
                        #    self.code_target_file[
                        #        declaration.test.range[0],
                        #        declaration.test.range[1]])

                    case "Literal":
                        # Nothing to walk into.
                        pass

                    case _:
                        logging.warning(
                            "AST walk handling of switch statement and switch "
                            f"case with test of type: {switch_case.test.type} "
                            "not yet supported. "
                            "[W-AWHOSSASCWTOTSTTNYS]" +
                            self.__debug_node_in_code(switch_case.test))

            if switch_case.test is not None:
                switch_case_range = switch_case.test.range
                switch_case_text = \
                    self.code_target_file[
                        switch_case_range[0]:switch_case_range[1]]
            else:
                switch_case_text = "default"

            self.__process_ast_walk(
                scope + [("switch-statement", discriminant_text),
                         ("switch-case", switch_case_text)],
                switch_case.consequent,
                path + ["cases", str(index), "consequent"])

    def __ast_walk_handle_variabledeclarator(
            self,
            scope: list,
            node: esprima.nodes.VariableDeclarator,
            path: list) -> None:
        """Handle AST walk into a variable declarator. Will continue walking
        into function bodies of variables declared as functions and method
        call arguments of variables declared as calls.

        Example:
        .. code-block:: JavaScript
            const foo = () => {
                /* Walk here */
            }

            let bar = baz(/* Walk here */);

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.VariableDeclarator
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        if node.init is None:
            # Nothing to walk into.
            return

        if node.id.type == "Identifier":
            match node.init.type:
                case "ArrowFunctionExpression" | "FunctionExpression":
                    if node.init.body.type == "BlockStatement":
                        self.__process_ast_walk(
                            scope + [("function", node.id.name)],
                            node.init.body.body,
                            path + ["init", "body", "body"])
                    else:
                        self.__process_ast_walk(
                            scope + [("function", node.id.name)],
                            node.init.body,
                            path + ["init", "body"])

                case "CallExpression" | "NewExpression" | "MemberExpression":
                    self.__ast_walk_handle_method_call(
                        scope, node.init, path + ["init"])

                case "ObjectExpression":
                    self.__ast_walk_handle_objectexpression(
                        scope + [("object-variable", node.id.name)],
                        node.init,
                        path + ["init"])

                case "BinaryExpression":
                    self.__ast_walk_handle_binaryexpression(
                        scope, node.init, path + ["init"])

                case "Literal":
                    return

                case _:
                    logging.warning(
                        "AST walk handling of variable declarator type: "
                        f"{node.init.type} not yet supported. "
                        "[W-AWHOVDTNITNYS]" +
                        self.__debug_node_in_code(node.init))

        elif node.id.type == "ArrayPattern":
            if node.init.type == "ArrayExpression" and \
                    len(node.id.elements) == \
                    len(node.init.elements):
                for index, declaration_item in \
                        enumerate(node.id.elements):
                    match node.init.elements[index].type:
                        case "ArrowFunctionExpression" | "FunctionExpression":
                            if node.init.elements[index].body.type == \
                                    "BlockStatement":
                                self.__process_ast_walk(
                                    scope + [
                                        ("function", declaration_item.name)],
                                    node.init.elements[index].body.body,
                                    path + ["init", "elements", str(index),
                                            "body", "body"])
                            else:
                                self.__process_ast_walk(
                                    scope + [
                                        ("function", declaration_item.name)],
                                    node.init.elements[index].body,
                                    path + ["init", "elements", str(index),
                                            "body"])

                        case "CallExpression" | "NewExpression" | \
                             "MemberExpression":
                            self.__ast_walk_handle_method_call(
                                scope,
                                node.init.elements[index],
                                path + ["init", "elements", str(index)])

                        case "ObjectExpression":
                            self.__ast_walk_handle_objectexpression(
                                scope + [
                                    ("object-variable",
                                     declaration_item.name)],
                                node.init.elements[index],
                                path + ["init", "elements", str(index)])

                        case "Literal":
                            return

                        case _:
                            logging.warning(
                                "AST walk handling of variable declarator "
                                "array pattern with array expression type: "
                                f"{node.init.elements[index].type} "
                                f"not yet supported. "
                                "[W-AWHOVDAPWAETNIEITNYS]" +
                                self.__debug_node_in_code(
                                    node.init.elements[index]))

            else:
                match node.init.type:
                    case "CallExpression" | "NewExpression" | \
                         "MemberExpression":
                        self.__ast_walk_handle_method_call(
                            scope, node.init, path + ["init"])

                    case "Literal":
                        return

                    case _:
                        logging.warning(
                            "AST walk handling of variable declarator with "
                            "id of an array pattern and initiator of type: "
                            f"{node.init.type} not yet supported. "
                            "[W-AWHOVDWIOAAPAIOTNITNYS]" +
                            self.__debug_node_in_code(node.init))

        else:
            logging.warning(
                "AST walk handling of variable declaration with id of type "
                f"{node.id.type} not yet supported")

    def __ast_walk_handle_variabledeclaration(
            self,
            scope: list,
            node: esprima.nodes.VariableDeclaration,
            path: list) -> None:
        """Handle AST walk into a variable declarator. Will continue walking
        into function bodies of variables declared as functions and method
        call arguments of variables declared as calls.

        Example:
        .. code-block:: JavaScript
            const foo = () => {/* Walk here */},
                  bar = baz(/* Walk here */),
                  gazonk = [qux(/* Walk here */), quux(/* Walk here */)];

        Further, all individual declarations will be cached and all method
        calls used in the declarations will be cached.

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.VariableDeclaration
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        for index, declaration in enumerate(node.declarations):
            if declaration.id.type != "Identifier" and \
                    declaration.id.type != "ArrayPattern":
                logging.warning(
                    "Variable declarator with identifier of type: "
                    f"{declaration.id.type} cannot yet be "
                    f"handled. "
                    "[W-VDWIOTDITCYBH]" +
                    self.__debug_node_in_code(declaration))
                return

            self.__cache_handle_declaration_variabledeclarator(
                scope, node, declaration,
                path + ["declarations", str(index)])

            self.__ast_walk_handle_variabledeclarator(
                scope, declaration,
                path + ["declarations", str(index)])

    def __ast_walk_handle_assignmentexpression(
            self,
            scope: list,
            node: esprima.nodes.AssignmentExpression,
            path: list) -> None:
        """Handle AST walk into an assignment expression. Will continue walking
        into function bodies of variables (re)declared as functions and method
        call arguments of variables (re)declared as calls.

        Example:
        .. code-block:: JavaScript
            foo = () => {
                /* Walk here */
            };

            bar = baz(/* Walk here */);

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.AssignmentExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        call_chain = []
        call_scope = []

        # TODO: Add support for [aa, bb] = [123, 555]

        match node.left.type:
            case "Identifier":
                call_chain.append(node.left.name)
                call_scope.append(("variable",
                                   node.left.name))

            case "MemberExpression":
                node_walk = node.left
                while node_walk.type == "MemberExpression":

                    node_walk_name = \
                        self.__node_handler_get_name(node_walk.property)

                    call_chain.append(node_walk_name)
                    call_scope.append(("object-variable", node_walk_name))

                    if node_walk.object.type == "Identifier":
                        call_chain.append(node_walk.object.name)
                        call_scope.append(("object-variable",
                                           node_walk.object.name))

                    elif node_walk.object.type == "ThisExpression":
                        call_chain.append("this")
                        call_scope.append(("class-this",
                                           "this"))

                    else:
                        logging.warning(
                            "AST walk handling of assignment expression left "
                            "hand member expression object of type: "
                            f"{node_walk.object.type} not yet supported. "
                            "[W-AWHOAELHMEOOTNOTNYS]" +
                            self.__debug_node_in_code(node_walk.object))

                    node_walk = node_walk.object

            case _:
                logging.warning(
                    "AST walk handling of assignment expression left hand "
                    f"type: {node.left.type} not yet supported. "
                    "[W-AWHOAELHTNLTNYS]" +
                    self.__debug_node_in_code(node.left))
                return

        call_chain.reverse()
        call_scope.reverse()
        call_name = '.'.join(call_chain)

        self.__cache_declaration(
            call_name,
            node.right,
            scope,
            path + ["right"]
        )

        match node.right.type:
            case "CallExpression" | "NewExpression":
                self.__cache_handle_method_call(
                    scope,
                    node.right,
                    path + ["right"])

                self.__ast_walk_handle_method_call(
                    scope, node.right, path + ["right"])

            case "ObjectExpression":
                self.__cache_handle_declaration_objectexpression(
                    scope + call_scope,
                    node.right,
                    path + ["right"],
                    call_chain)

                self.__ast_walk_handle_objectexpression(
                    scope + call_scope,
                    node.right,
                    path + ["right"])

            case "ArrayExpression":
                # TODO: Adapt when [aa, bb] = [123, 555] is supported
                self.__cache_handle_declaration_arrayexpression(
                    scope,
                    node.right,
                    path + ["right"],
                    call_chain)

                self.__process_ast_walk(
                    scope,
                    node.right.elements,
                    path + ["right", "elements"])

            case "ArrowFunctionExpression" | "FunctionExpression":
                if node.right.body.type == "BlockStatement":
                    self.__process_ast_walk(
                        scope + call_scope[:-1] +
                        [("function", call_scope[-1][1])],
                        node.right.body.body,
                        path + ["right", "body", "body"])
                else:
                    self.__process_ast_walk(
                        scope + call_scope[:-1] +
                        [("function", call_scope[-1][1])],
                        node.right.body,
                        path + ["right", "body"])

            case "Literal" | \
                 "MemberExpression" | \
                 "Identifier":
                # Nothing more to enter here.
                return

            case _:
                logging.warning(
                    "AST walk handling of assignment expression "
                    f"right hand type: {node.right.type} not yet "
                    "supported. "
                    "[W-AWHOAERHTNRTNYS]" +
                    self.__debug_node_in_code(node.right))

    def __ast_walk_handle_sequenceexpression(
            self,
            scope: list,
            node: esprima.nodes.SequenceExpression,
            path: list) -> None:
        """Handle AST walk into a sequence expression. Will continue walking
        into function bodies of variables (re)declared as functions and method
        call arguments of variables (re)declared as calls.

        Example:
        .. code-block:: JavaScript
            foo = () => {/* Walk here */},
            bar = baz(/* Walk here */);

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.SequenceExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        for index, assignment in enumerate(node.expressions):
            match assignment.type:
                case "AssignmentExpression":
                    self.__ast_walk_handle_assignmentexpression(
                        scope, assignment, path + [str(index)])

                case "Identifier":
                    continue

                case _:
                    logging.warning(
                        "AST walk handling of sequence expression assignment "
                        f"of type: {assignment.type} is not yet supported. "
                        "[W-AWHOSEAOTATINYS]" +
                        self.__debug_node_in_code(assignment))

    def __ast_walk_handle_expressionstatement(
            self,
            scope: list,
            node: esprima.nodes.ExpressionStatement,
            path: list) -> None:
        """Handle AST walk into expression statements (ExpressionStatement).
        Will continue walking into expressions containing calls, function
        definitions or JSX elements.

        Example:
        .. code-block:: JavaScript
            aa(() => {/* Walk here */});

            (new Class(/* Walk here */));

            bb.cc(/* Walk here */

            foo = () => {/* Walk here */}, bar = baz(/* Walk here */);

            (<div>
                {gazonk(/* Walk here */).forEach(() => {/* Walk here */})}
            </div>)

        Further, all found methods used in the expressions will be saved to
        the method call cache.

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.ExpressionStatement
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        match node.expression.type:
            case "CallExpression" | "NewExpression" | "MemberExpression":
                self.__cache_handle_method_call(
                    scope,
                    node.expression,
                    path + ["expression"])

                self.__ast_walk_handle_method_call(
                    scope,
                    node.expression,
                    path + ["expression"])

            case "ArrowFunctionExpression" | "FunctionExpression":
                self.__ast_walk_handle_functionexpression(
                    scope,
                    node.expression,
                    path + ["expression"])

            case "AssignmentExpression":
                self.__ast_walk_handle_assignmentexpression(
                    scope,
                    node.expression,
                    path + ["expression"])

            case "SequenceExpression":
                self.__ast_walk_handle_sequenceexpression(
                    scope,
                    node.expression,
                    path + ["expression"])

            case "JSXElement":
                self.__ast_walk_handle_jsxelement(
                    scope,
                    node.expression,
                    path + ["expression"])

            case _:
                logging.warning(
                    "AST walk handling of expression statement type: "
                    f"{node.expression.type} not yet supported. "
                    "[W-AWHOESTNETNYS]" +
                    self.__debug_node_in_code(node.expression))

    def __ast_walk_handle_functionexpression(
            self,
            scope: list,
            node: (esprima.nodes.ArrowFunctionExpression |
                   esprima.nodes.FunctionExpression),
            path: list) -> None:
        """Handle AST walk into anonymous function expressions
        (ArrowFunctionExpression or FunctionExpression). Will only walk into
        expressions not directly used in body, but those used in arguments.

        Example:
        .. code-block:: JavaScript
            aa(() => {
                /* Will walk here */
            });

            () => {
                /* Will NOT walk here */
            };

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.ArrowFunctionExpression |
                    esprima.nodes.FunctionExpression
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        match node.type:
            case "ArrowFunctionExpression" | "FunctionExpression":
                # Expression is in body or arguments, so it's anonymous.
                # TODO: Verify assumption about anonymous functions:
                #  Expression in body is never called, so it's not interesting?
                #  Code example:
                #  ...
                #  () => {/* Walk here? */}
                #  ...
                #  Can "/* Walk here? */" be executed UNLESS it's
                #  assigned to a variable or inside a call argument?
                #  If it's immediately called:
                #  (() => {/* Walk here? */})();
                #  It becomes a CallExpression.
                if len(path) > 2 and path[-2] == "body":
                    logging.warning(
                        "AST walk handling of expression statement found "
                        "anonymous function expression in a body node. There "
                        "should be no way for the contents of it to be "
                        "executed, but it's best to inspect the actual code "
                        f"between {node.range[0]} and {node.range[1]}. "
                        "[W-AWHOESFAFEIABNTSBNWFTCOITBEBIBTITACBNRANR]" +
                        self.__debug_node_in_code(node))
                    # Uncomment to read code
                    # print(
                    #    self.code_target_file[
                    #        node.range[0], node.range[1]])
                    return

                else:

                    if node.body.type == "BlockStatement" and \
                            node.body.body is not None:
                        self.__process_ast_walk(
                            scope + [("anonymous-function", "")],
                            node.body.body,
                            path + ["body", "body"])

                    elif node.body.type == "JSXElement":
                        self.__ast_walk_handle_jsxelement(
                            scope + [("anonymous-function", "")],
                            node.body,
                            path + ["body"])

                    elif node.body.type == "BinaryExpression":
                        self.__ast_walk_handle_binaryexpression(
                            scope + [("anonymous-function", "")],
                            node.body,
                            path + ["body"])

                    elif node.body.type == "LogicalExpression":
                        self.__ast_walk_handle_logicalexpression(
                            scope + [("anonymous-function", "")],
                            node.body,
                            path + ["body"])

                    else:
                        logging.warning(
                            "AST walk handling of function expression of type "
                            f"{node.type} cannot yet handle function body of "
                            f"type {node.body.type}. "
                            "[W-AWHOFEOTNTCYHFBOTNBT]" +
                            self.__debug_node_in_code(node.body))

            case _:
                logging.warning(
                    "AST walk handling of function expression type: "
                    f"{node.type} not yet supported. "
                    "[W-AWHOFETNTNYS]" +
                    self.__debug_node_in_code(node))

    def __ast_walk_handle_returnstatement(
            self,
            scope: list,
            node: esprima.nodes.ReturnStatement,
            path: list) -> None:
        """Handle AST walk into a return statements (ReturnStatement). Will
        continue walking into returns containing calls, function definitions
        or JSX elements.

        Example:
        .. code-block:: JavaScript
            function foo() {
                return () => {
                    /* Will walk here */
                }
            }

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.ReturnStatement
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        match node.argument.type:
            case "JSXElement":
                self.__ast_walk_handle_jsxelement(
                    scope,
                    node.argument,
                    path + ["argument"])

            case "CallExpression" | "NewExpression" | "MemberExpression":
                self.__ast_walk_handle_method_call(
                    scope,
                    node.argument,
                    path + ["argument"])

            case "ArrowFunctionExpression" | "FunctionExpression":
                if node.argument.body.type == "BlockStatement":
                    self.__process_ast_walk(
                        scope + [("returned-function", "")],
                        node.argument.body.body,
                        path + ["argument", "body", "body"])
                else:
                    self.__process_ast_walk(
                        scope + [("returned-function", "")],
                        node.argument.body,
                        path + ["argument", "body"])

            case "BinaryExpression":
                self.__ast_walk_handle_binaryexpression(
                    scope + [("returned-function", "")],
                    node.argument,
                    path + ["argument"])

            case "Identifier":
                return

            case _:
                logging.warning(
                    "AST walk handling for return statement argument of "
                    f"type: {node.argument.type} not yet supported. "
                    "[W-AWHFRSAOTNATNYS]" +
                    self.__debug_node_in_code(node.argument))

    def __ast_walk_handle_throwstatement(
            self,
            scope: list,
            node: esprima.nodes.ThrowStatement,
            path: list) -> None:
        """Handle AST walk into a throw statements (ThrowStatement). Will
        continue walking into the arguments of the error.

        Example:
        .. code-block:: JavaScript
            throw new Error(/* Walk here */);

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.ThrowStatement
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        if node.argument.type == "NewExpression" or \
                node.argument.type == "CallExpression":
            self.__process_ast_walk(
                scope,
                node.argument,
                path + ["argument"])

        else:
            logging.warning(
                "AST walk handling for throw statement argument of "
                f"type: {node.argument.type} not yet supported. "
                "[W-AWHFTSAOTNATNYS]" +
                self.__debug_node_in_code(node.argument))


    def __ast_walk_handle_jsxelement(
            self,
            scope: list,
            node: (esprima.jsx_nodes.JSXElement |
                   esprima.jsx_nodes.JSXExpressionContainer),
            path: list) -> None:
        """Handle AST walk into a JSX elements (JSXElement). Will continue
        walking into the contents of JSXExpressionContainer or
        BinaryExpression.

        Example:
        .. code-block:: JavaScript
            const App = () => {
                return (<>
                    {bar(/* Will walk here */) && foo(() => {
                        /* Will walk here */
                    })}
                </>)
            };

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.jsx_nodes.JSXElement |
                    esprima.jsx_nodes.JSXExpressionContainer
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        match node.type:
            case "JSXElement":
                for index, jsx_child in enumerate(node.children):
                    self.__ast_walk_handle_jsxelement(
                        scope,
                        jsx_child,
                        path + ["children", str(index)])

            case "JSXExpressionContainer":
                match node.expression.type:
                    case "CallExpression" | "NewExpression" | \
                         "MemberExpression":
                        self.__cache_handle_method_call(
                            scope,
                            node.expression,
                            path + ["expression"])

                        self.__ast_walk_handle_method_call(
                            scope,
                            node.expression,
                            path + ["expression"])

                    case "ArrowFunctionExpression" | "FunctionExpression":
                        self.__ast_walk_handle_functionexpression(
                            scope,
                            node.expression,
                            path + ["expression"])

                    case "AssignmentExpression":
                        self.__ast_walk_handle_assignmentexpression(
                            scope,
                            node.expression,
                            path + ["expression"])

                    case "SequenceExpression":
                        self.__ast_walk_handle_sequenceexpression(
                            scope,
                            node.expression,
                            path + ["expression"])

                    case "LogicalExpression":
                        self.__ast_walk_handle_logicalexpression(
                            scope,
                            node.expression,
                            path + ["expression"])

                    case _:
                        logging.warning(
                            "AST walk handling of expression statement type: "
                            f"{node.expression.type} not yet supported. "
                            "[W-AWHOESTNETNYSA]" +
                            self.__debug_node_in_code(node.expression))

            case "JSXText":
                pass

            case _:
                logging.warning(
                    f"Cache handling for JSX elements of type: {node.type} "
                    "not yet supported. "
                    "[W-CHFJEOTNTNYS]" +
                    self.__debug_node_in_code(node))

    def __process_ast_walk(
            self,
            scope: list = None,
            node: esprima.nodes.Node | list = None,
            path: list = None) -> None:
        """Begin process of walking down the AST tree from the utmost scope
        or continue walk from a function body, argument list or other general
        node.

        Will save method calls, variable declarations, function definitions
        and class method definitions to their respective cache when found.

        :param scope: The current scope in the AST.
        :type scope: list
        :param node: The node to handle.
        :type node: esprima.nodes.Node | list
        :param path: The current path taken in the AST.
        :type path: list

        :return: None
        """
        if scope is None and node is None and path is None:
            scope = [("global", "window")]
            node = self.ast_target_file
            path = []

        # Debug help
        # self.__debug_print_location(scope, path)

        if isinstance(node, list):
            for index, same_level_node in enumerate(node):
                self.__process_ast_walk(
                    scope, same_level_node, path + [str(index)])

        elif hasattr(node, '__dict__') and 'type' in node.__dict__:
            match node.type:
                case "Program":
                    self.__process_ast_walk(scope, node.body, path + ["body"])

                case "FunctionDeclaration":
                    self.__ast_walk_handle_functiondeclaration(
                        scope, node, path)

                case "ClassDeclaration":
                    self.__ast_walk_handle_classdeclaration(
                        scope, node, path)

                case "IfStatement":
                    self.__ast_walk_handle_ifstatement(
                        scope, node, path)

                case "SwitchStatement":
                    self.__ast_walk_handle_switchstatement(
                        scope, node, path)

                case "VariableDeclaration":
                    self.__ast_walk_handle_variabledeclaration(
                        scope, node, path)

                case "ExpressionStatement":
                    self.__ast_walk_handle_expressionstatement(
                        scope, node, path)

                case "BinaryExpression":
                    self.__ast_walk_handle_binaryexpression(
                        scope, node, path)

                case "CallExpression" | "NewExpression":
                    # Single call
                    self.__cache_handle_method_call(
                        scope, node, path)
                    self.__ast_walk_handle_method_call(
                        scope, node, path)

                case "ReturnStatement":
                    self.__ast_walk_handle_returnstatement(
                        scope, node, path)

                case "ThrowStatement":
                    self.__ast_walk_handle_throwstatement(
                        scope, node, path)

                case "JSXElement":
                    self.__ast_walk_handle_jsxelement(
                        scope, node, path)

                case "ObjectExpression":
                    # Expression is in body or arguments, so it's anonymous.
                    self.__cache_handle_anonymous_objectexpression(
                        scope, node, path)
                    self.__ast_walk_handle_objectexpression(
                        scope, node, path)

                case "ArrayExpression":
                    # Expression is in body or arguments, so it's anonymous.
                    # It's just a normal array
                    self.__process_ast_walk(
                        scope, node.elements, path + ["elements"])

                case "ArrowFunctionExpression" | "FunctionExpression":
                    # Expression is in body or arguments, so it's anonymous.
                    # It's most likely in arguments as it would be wrapped in
                    # "ExpressionStatement" if it's in a body, but it's handled
                    # the same anyway.
                    self.__ast_walk_handle_functionexpression(
                        scope, node, path)

                case "ExportNamedDeclaration" | "ExportDefaultDeclaration":
                    # Statement is in most outer scope, so ignore export
                    # information here and just continue walking into
                    # declaration. Export information is logged separately.
                    self.__cache_handle_exported_object_declaration(
                        node.declaration, path + ["declaration"])
                    self.__process_ast_walk(
                        scope, node.declaration, path + ["declaration"])

                case "ImportDeclaration" | "Literal" | "BreakStatement" | \
                     "Identifier" | "MemberExpression":
                    # Nothing interesting in these statements (for now) so
                    # ignore.
                    # TODO: When nested imports are to be supported, allow
                    #  handling and caching of these statements here.
                    # TODO: If usage o literals may help in writing tests,
                    #  (maybe) add more handling here.
                    # TODO: If usage o break in switch cases may help in
                    #  writing tests, (maybe) add more handling here.
                    # TODO: If Identifier passed as argument is helpful,
                    #  (maybe) add more handling here.
                    return

                case _:
                    logging.warning(
                        "AST walk process cannot yet handle node of type: "
                        f"{node.type}. "
                        "[W-AWPCYHNOTNT]" +
                        self.__debug_node_in_code(node))

    # ~~~~~( Analysis - Post Process ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __validate_declaration_candidate(
            self,
            declaration: dict,
            first_declaration: dict = None) -> bool:
        """Validate a variable declaration candidate for it to be eligible
        as a function definition for an exported asset.

        A variable is only eligible if:
            - It's first declared in the utmost scope (global), or..
            - (Alt ^) It's declared under window object explicitly.
            - It's declared as a function.
            - It's not redeclared when initially declared as const.
            - It's not redeclared with let or const in the same scope.

        :param declaration: The variable declaration to validate.
        :type declaration: dict
        :param first_declaration:
        :type first_declaration: dict

        :return: True it declaration is a possible candidate, False otherwise.
        :rtype: bool
        """
        # Declaration is a function
        if declaration["node_type"] != "ArrowFunctionExpression" and \
                declaration["node_type"] != "FunctionExpression":
            return False

        # Explicit declaration in window can always be exported no matter
        # the scope
        if declaration["kind"] == "window-explicit":
            return True

        # First declaration
        if first_declaration is None:

            # Only candidate if scope is global when first declared
            if len(declaration["scope"]) > 1 or \
                    declaration["scope"] != [("global", "window")]:
                return False

            # Not allowed to implicitly declare variable in 'window'
            if declaration["kind"] == "window":
                new_lines = \
                    self.code_target_file[
                        :declaration['node'].range[0]].count("\n") + 1
                logging.warning(
                    f"Variable name first used but never previously declared "
                    f"in file {self.js_target_file_import_path}, on line "
                    f"{new_lines}. Ignoring variable contents. If a global "
                    f"variable should be used then it should be defined under "
                    f"the 'window' object.")
                return False

            return True

        # Redeclaration
        else:
            # Same scope
            if len(declaration["scope"]) == 1 and \
                    declaration["scope"] == [("global", "window")]:

                # Not allowed to redeclare let or const
                if declaration["kind"] == "const" or \
                        declaration["kind"] == "let":
                    return False

                # Only allowed to redeclare if first declaration was not const
                if first_declaration["kind"] == "const":
                    return False

                # Only allowed to redeclare if first declaration was let
                # and redeclaration is in implicit window.
                if first_declaration["kind"] == "let" and \
                        declaration["kind"] != "window":
                    return True

            # Different scope
            else:
                # Declaration with same name in different scope is not
                # a redeclaration, it's a different variable.
                if declaration["kind"] == "const" or \
                        declaration["kind"] == "let":
                    return False

            return True

    def __validate_object_candidate(
            self,
            object_prop: dict) -> bool:
        """Validate an object property declaration candidate for it to be
        eligible as a function definition for an exported asset.

        A property is only eligible if:
            - It's declared as a function.

        :param object_prop: The object property to validate.
        :type object_prop: dict

        :return: True it declaration is a possible candidate, False otherwise.
        :rtype: bool
        """
        # Declaration is a function
        if object_prop["node_type"] != "ArrowFunctionExpression" and \
                object_prop["node_type"] != "FunctionExpression":
            return False

        # Only candidate if object is in exported variable
        # TODO: If there's a need to limit scope.

        return True

    def __validate_function_candidate(
            self,
            function: dict) -> bool:
        """Validate a function declaration candidate for it to be eligible
        as a definition for an exported asset.

        A property is only eligible if:
            - It's declared in the utmost scope (global)

        :param function: The function to validate.
        :type function: dict

        :return: True it declaration is a possible candidate, False otherwise.
        :rtype: bool
        """
        # Only candidate if scope is global
        if len(function["scope"]) > 1 or \
                function["scope"] != [("global", "window")]:
            return False

        return True

    def __process_find_exported_test_surfaces(self) -> None:
        """Process to find all exported test surfaces. Any found test surface
        is saved to the post process instance attribute for exported
        test surfaces.

        :return: None
        """
        for exported_asset in self.analyze_exported:
            local_name = exported_asset["local_name"]
            export_name = exported_asset["export_name"]

            found_export = False
            first_declaration = None
            matching_declaration = None
            matching_name = ""
            matching_type = ""
            non_valid_declarations = []

            for decl_name, decl_alt in \
                    [(decl_name, decl_alt) for decl_name in
                     self.cache_declarations for decl_alt in
                     self.cache_declarations[decl_name]]:

                if re.match(r"window\." + re.escape(local_name) + "$",
                            decl_name):
                    decl_alt["kind"] = "window-explicit"
                    decl_name = local_name

                if decl_name == local_name:
                    if self.__validate_declaration_candidate(
                            decl_alt, first_declaration):
                        if first_declaration is None:
                            first_declaration = decl_alt

                        matching_declaration = decl_alt
                        matching_name = decl_name
                        matching_type = "function"
                    else:
                        non_valid_declarations.append(decl_alt)

                elif re.match(re.escape(local_name), decl_name):
                    if self.__validate_object_candidate(decl_alt):
                        matching_declaration = decl_alt
                        matching_name = decl_name
                        matching_type = "function"
                    else:
                        non_valid_declarations.append(decl_alt)

            if matching_declaration is None:
                for func_name, func_alt in \
                        [(func_name, func_alt) for func_name in
                         self.cache_functions for func_alt in
                         self.cache_functions[func_name]]:
                    if func_name == local_name:
                        if self.__validate_function_candidate(func_alt):
                            matching_declaration = func_alt
                            matching_name = func_name
                            matching_type = "function"
                        else:
                            non_valid_declarations.append(func_alt)

            if matching_declaration is None:
                for decl_name, decl_alt in \
                        [(decl_name, decl_alt) for decl_name in
                         self.cache_declarations_exported_object
                         for decl_alt in
                         self.cache_declarations_exported_object[decl_name]]:
                    if decl_name == local_name:
                        if self.__validate_object_candidate(decl_alt):
                            matching_declaration = decl_alt
                            matching_name = decl_name
                            matching_type = "function"
                        else:
                            non_valid_declarations.append(decl_alt)

            if matching_declaration is not None:
                found_export = True
                test_surface_object = {
                    **exported_asset,
                    "declaration": matching_declaration,
                    "full_name": matching_name,
                    "asset_type": matching_type
                }
                self.exported_test_surfaces.append(test_surface_object)

            if matching_declaration is None:
                for class_name, class_method in \
                        [(class_name, class_method) for class_name in
                         self.cache_classes for class_method in
                         self.cache_classes[class_name]]:
                    if class_name == local_name:
                        found_export = True
                        test_surface_object = {
                            **exported_asset,
                            "declaration": class_method,
                            "full_name": class_name,
                            "asset_type": "class"
                        }
                        self.exported_test_surfaces.append(test_surface_object)

            if found_export is not True:
                if len(non_valid_declarations) == 0:
                    logging.warning(
                        f"Did not find any declaration for "
                        f"export: {export_name}. " 
                        "[W-DNFADFEE]")
                else:
                    string_decl = f" >>> File: {self.path_target_file}\n"
                    for index, decl in enumerate(non_valid_declarations):
                        string_decl += \
                            " >>> Line " + \
                            str(self.code_target_file[
                                :decl['node'].range[0]].count('\n') + 1) + \
                            f" >>> Declaration #{str(index+1):0>3}: " + \
                            self.code_target_file[
                                decl['node'].range[0]:
                                decl['node'].range[1]] + \
                            "\n"

                    logging.warning(
                        f"Did not find any function declaration for "
                        f"export: {export_name}. "
                        "[W-DNFAFDFEE]\n"
                        f"Only found it being declared as the "
                        f"following statement(s):\n{string_decl}")

    def __process_find_imported_dependencies(self) -> None:
        """Process to find all imported and used dependencies. Any found
        dependency is saved to the post process instance attribute for imported
        dependencies.

        :return: None
        """
        for imported_asset in self.analyze_imported:
            local_name = imported_asset["local_name"]

            for method_call in self.cache_method_calls:
                if local_name == method_call["property_chain"][0][1] or \
                        local_name == method_call["name"]:
                    test_surface_object = {
                        **imported_asset,
                        "method_call": method_call
                    }
                    self.imported_dependencies.append(test_surface_object)

    def __make_info_exported_test_surfaces(self) -> list:
        """Make test surface information objects compatible with the database
        naming conventions for all found test surfaces and put them in a list
        that is returned.

        :return: The list of test surface information objects.
        :rtype: list
        """
        info_exported_test_surfaces = []

        for test_surface in self.exported_test_surfaces:
            function_id = "!UNKNOWN"
            arguments = []

            if test_surface["asset_type"] == "class":
                # functionId
                if test_surface["declaration"]["static"]:
                    function_id = f"{test_surface['full_name']}"
                else:
                    function_id = f"(new {test_surface['full_name']}())"
                function_id = f"{function_id}." \
                              f"{test_surface['declaration']['name']}"

                # arguments
                if test_surface["declaration"]["constructor"] is not None:
                    arguments.append(
                        [{test_surface['full_name']:
                            self.__convert_esprima_ast_to_object(
                                test_surface["declaration"][
                                    "constructor"].params)}])

                arguments.append(
                    [{test_surface['declaration']['name']:
                        self.__convert_esprima_ast_to_object(
                            test_surface["declaration"][
                                "node"].params)}])

            elif test_surface["asset_type"] == "function":
                # functionId
                function_id = test_surface["full_name"]

                # arguments
                arguments.append(
                    [{test_surface['full_name']:
                        self.__convert_esprima_ast_to_object(
                            test_surface["declaration"][
                                "node"].params)}])

            else:
                logging.warning(
                    "Unable to create test surface for asset of not yet "
                    f"supported type: {test_surface['asset_type']} "
                    "[W-UTCTSFAONYSTTA]")

            # functionHash
            function_range = test_surface["declaration"]["node"].range
            function_source = \
                self.code_target_file[function_range[0]:function_range[1]]
            function_hash = \
                hashlib.sha256(str.encode(function_source)).hexdigest()

            info_exported_test_surfaces.append({
                "pathToProject": self.path_project_root,
                "fileId": self.js_target_file_import_path,
                "arguments": arguments,
                "functionRange":
                    (test_surface["declaration"]["node"].range[0],
                     test_surface["declaration"]["node"].range[1]),
                "functionHash": function_hash,
                "exportInfo": test_surface["export"],
                "exportName": test_surface["export_name"],
                "functionId": function_id,
            })

        return info_exported_test_surfaces

    def __make_info_imported_dependencies(self) -> list:
        """Make imported dependency information objects compatible with the
        database naming conventions for all found used dependencies and put
        them in a list that is returned.

        :return: The list of imported dependency information objects.
        :rtype: list
        """
        info_imported_dependencies = []

        for dependency in self.imported_dependencies:
            call_range = dependency["method_call"]["node"].range

            dependent = "!OUTSIDE_TEST_SURFACE"

            for test_surface in self.exported_test_surfaces:
                surface_range = test_surface["declaration"]["node"].range
                if call_range[0] >= surface_range[0] and \
                        call_range[1] <= surface_range[1]:
                    dependent = test_surface["full_name"]
                    break

            info_imported_dependencies.append({
                "pathToProject": self.path_project_root,
                "fileId": self.js_target_file_import_path,
                "functionId": dependent,
                "calledFileId": dependency["absolute_import_path"],
                "calledFunctionId":
                    '.'.join([prop for (prop_type, prop) in
                              dependency["method_call"]["property_chain"]])
            })

        return info_imported_dependencies

    def __process_ast(self) -> None:
        """Process to analyze the complete AST and process the data in order
        to find all available test surfaces and used imported dependencies.

        :return: None
        """
        # Exported (and testable) objects
        self.__process_find_exported_objects()

        # Imported (unconditional and global)
        self.__process_find_imported_objects()

        # Walk the AST and cache information
        self.__process_ast_walk()

        # Find Testable Surfaces
        self.__process_find_exported_test_surfaces()

        # Find Imported and Used Dependencies
        self.__process_find_imported_dependencies()

        # Debug help
        # self.__debug_print_info()

        # Done
        self.ast_analyzed = True

    # ~~~~~( Public Interface ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~( Public Interface - Process ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def begin_analyze(self):
        """Begin the process of analyzing the loaded source file. Once complete
        it will be possible to retrieve all test surfaces (get_test_surfaces())
        or all dependency usages (get_dependency_usages()).

        :return: None
        """
        self.__process_ast()

    # ~~~~~( Public Interface - Information Extraction ) ~~~~~~~~~~~~~~~~~~~~~~
    def get_file_identity(self) -> str:
        """Get the file identity for the loaded source file. The file identity
        is the absolute path to the file starting from the project root
        directory.

        :return: The file identity.
        """
        return self.js_target_file_import_path

    # ~~~~~( Public Interface - Post Process Information Extraction ) ~~~~~~~~~
    def get_test_surfaces(self) -> list:
        """Get all found test surfaces as a list of test surface information
        objects compatible with the database naming conventions.

        :return: The list of test surface information objects.
        :rtype: list
        """
        if self.ast_analyzed is False:
            raise Exception(
                "Cannot get test surfaces before analysis is complete. "
                "Call begin_analyze() first!")

        return self.__make_info_exported_test_surfaces()

    def get_dependency_usages(self) -> list:
        """Get all found dependency usages as a list of imported dependency
        information objects compatible with the database naming conventions.

        :return: The list of imported dependency information objects.
        :rtype: list
        """
        if self.ast_analyzed is False:
            raise Exception(
                "Cannot get dependency usages before analysis is complete. "
                "Call begin_analyze() first!")

        return self.__make_info_imported_dependencies()
