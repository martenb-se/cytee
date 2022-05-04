import hashlib
import os
from api.analyzer.client_actions import CACode
from api.analyzer.config import AnalyzerConfig
from api.instances.analyzer_client_action import client_action
from api.instances.logging_standard import logging
from api.analyzer.analyzer import AnalyzeJS
from api.cache import clear_cache, read_file, save_file, debug_get_cache_info
from api.instances.database_main import database_handler
from api.instances.shared_websockets_main import shared_websockets_handler
from api.util.paths_helper import full_path_to_correct_sub_directory
from api.websocket import WsIdentity, WsCode, WsClientCode


class ProjectDataHandler:
    """Project data handler for handling and saving data returned by an
    AnalyzeJS object.

    :param path_project_root: The absolute path to the root directory for
    the whole project.
    :type path_project_root: str

    :rtype: None
    """

    def __init__(self, path_project_root: str):
        self.__is_project_existing = False
        self.path_project_root = path_project_root
        self.code_target_file = None

        # Analyzer
        self.analyzer_instance = None

        # Data Handling
        self.added_function_dependencies = []
        self.existing_function_dependencies = []
        self.dead_function_dependencies = []

        self.added_function_info = []
        self.existing_function_info = []
        self.dead_function_info = []

        # Setup Process
        self.__validate_constructor_arguments()
        self.__clean_env_path_variables()
        self.__project_backup()

    # ~~~~~( Initiation ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __validate_constructor_arguments(self) -> None:
        """Validate the constructor arguments.

        :return: None
        """
        if not isinstance(self.path_project_root, str):
            raise TypeError("'path_project_root' must be a STRING")
        elif len(self.path_project_root) < 1:
            raise ValueError("'path_project_root' cannot be empty")

    def __clean_env_path_variables(self) -> None:
        """Clean the variables containing paths

        :return: None
        """
        self.path_project_root = os.path.abspath(self.path_project_root)

    # ~~~~~( Debugging ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~( General ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __compare_dict_prop_values(
            self,
            old_dict: dict,
            new_dict: dict) -> list:
        """Compare differences of property values between two dictionaries
        with the same set of properties and get a list of all the names of all
        properties with found changes.

        :param old_dict: The old dictionary to compare to.
        :type old_dict: dict
        :param new_dict: The new dictionary with potential changes.
        :type new_dict: dict

        :return: A list with names of all changed properties.
        :rtype: list
        """
        change_list = []
        for function_info_prop in new_dict:
            if new_dict[function_info_prop] != \
                    old_dict[function_info_prop]:
                change_list.append(function_info_prop)

        return change_list

    # ~~~~~( Backup Management ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __project_backup_remove(self) -> None:
        """Remove backup of the current project from the database.
        Will remove all backups for entries in: function_info,
        function_dependency and test_info.

        :return: None
        """
        path_project_root_backup = "/BACKUP" + self.path_project_root
        backup_info = {"pathToProject": path_project_root_backup}

        database_handler.remove_function_info(backup_info)
        database_handler.remove_function_dependency(backup_info)
        database_handler.remove_test_info(backup_info)

    def __project_backup(self):
        """Create a backup of the current project in the database.
        Will back up all entries in found in: function_info,
        function_dependency and test_info.

        :return:
        """
        path_project_root_backup = "/BACKUP" + self.path_project_root
        original_info = {"pathToProject": self.path_project_root}
        backup_info = {"pathToProject": path_project_root_backup}

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
                    self.existing_function_info. \
                        append(existing_function_info_id)

                database_handler.add_function_info({
                    **function_info,
                    **backup_info
                })

        if orig_function_dependency is not None:
            for function_dependency in orig_function_dependency:
                if '_id' in function_dependency:
                    existing_dependency_id = function_dependency.pop("_id")
                    self.existing_function_dependencies. \
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

    def __project_restore(self) -> None:
        """Restore project from the created backup.
        Will restore all entries in found in the backups for: function_info,
        function_dependency and test_info.
        If project was not previously existing, it will also clear the
        created cache.
        Once restoration done the backup will be removed.

        :return: None
        """
        path_project_root_backup = "/BACKUP" + self.path_project_root
        original_info = {"pathToProject": self.path_project_root}
        backup_info = {"pathToProject": path_project_root_backup}

        if not self.__is_project_existing:
            database_handler.remove_function_info(original_info)
            database_handler.remove_function_dependency(original_info)
            database_handler.remove_test_info(original_info)
            clear_cache(self.path_project_root)

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

    def __backup_get_project_function_info(
            self,
            file_id: str,
            function_id: str) -> dict:
        """Get specified project test surface function info from the database
        backup.

        :param file_id: The function's file ID.
        :type file_id: str
        :param function_id: The project function ID.
        :type function_id: str

        :return: The specified test surface's function info.
        :rtype: dict
        """
        path_project_root_backup = "/BACKUP" + self.path_project_root
        function_info = None
        db_function_info = \
            database_handler.get_function_info({
                "pathToProject": path_project_root_backup,
                "fileId": file_id,
                "functionId": function_id
            })

        if db_function_info is not None:
            function_info = db_function_info[0]

        return function_info

    # ~~~~~( Database Management ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __db_get_project_function_dependencies(self) -> list:
        """Get all project function dependencies from the database.

        :return: All function dependencies.
        :rtype: list
        """
        function_dependencies = []
        db_function_dependencies = \
            database_handler.get_function_dependency({
                "pathToProject": self.path_project_root
            })

        if db_function_dependencies is not None:
            function_dependencies = db_function_dependencies

        return function_dependencies

    def __db_get_project_function_info(self) -> list:
        """Get all project test surfaces and their function info from the
        database.

        :return: All test surfaces function info.
        :rtype: list
        """
        function_info = []
        db_function_info = \
            database_handler.get_function_info({
                "pathToProject": self.path_project_root
            })

        if db_function_info is not None:
            function_info = db_function_info

        return function_info

    def __db_get_dead_project_function_dependencies_id(self) -> list:
        """Get a list of the IDs of all function dependencies stored in the
        database that were never found during the most recent analysis.
        These dependencies are considered dead as they no longer exist in the
        project files.

        :return: All dead function dependencies.
        :rtype: list
        """
        saved_dependencies = \
            [dependency["_id"] for dependency in
             self.__db_get_project_function_dependencies()]
        found_dependencies = \
            self.added_function_dependencies + \
            self.existing_function_dependencies
        dead_dependencies = \
            list(set(saved_dependencies).difference(found_dependencies))

        return dead_dependencies

    def __db_get_dead_project_function_info_id(self) -> list:
        """Get a list of the IDs of all test surfaces stored in the database
        that were never found during the most recent analysis. These test
        surfaces are considered dead as they no longer exist in the project
        files.

        :return: All dead test surfaces.
        :rtype: list
        """
        saved_functions = \
            [dependency["_id"] for dependency in
             self.__db_get_project_function_info()]
        found_functions = \
            self.added_function_info + \
            self.existing_function_info
        dead_functions = \
            list(set(saved_functions).difference(found_functions))

        return dead_functions

    def __db_delete_dead_project_function_dependencies(self) -> None:
        """Remove all function dependencies previously stored in the
        database that were never found during the most recent analysis.

        :return: None
        """
        dead_dependencies = \
            self.__db_get_dead_project_function_dependencies_id()

        if len(dead_dependencies) > 0:
            for dead_dependency in dead_dependencies:
                database_handler.remove_function_dependency({
                    '_id': dead_dependency
                })

            logging.info(
                f"Removed {len(dead_dependencies)} dead dependencies from "
                f"project at: {self.path_project_root}")

    def __db_delete_dead_project_function_info(self) -> None:
        """Remove all test surfaces previously stored in the database that
        were never found during the most recent analysis.

        :return: None
        """
        dead_functions = \
            self.__db_get_dead_project_function_info_id()

        if len(dead_functions) > 0:
            for dead_function in dead_functions:
                database_handler.remove_function_info({
                    '_id': dead_function
                })

            logging.info(
                f"Removed {len(dead_functions)} dead test surfaces from "
                f"project at: {self.path_project_root}")

    def __db_get_function_dependency_id(
            self,
            function_id: str,
            called_file_id: str,
            called_function_id: str) -> str:
        """Get the database ID for the specified function dependency.

        :param function_id: The callee function ID (the dependent).
        :type function_id: str
        :param called_file_id: The called function's file ID (file dependency).
        :type called_file_id: str
        :param called_function_id: The called function ID
        (function dependency).
        :type called_function_id: str

        :return: The database ID of the saved dependency if found, otherwise
        None is returned.
        :rtype: str
        """
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file information")

        function_dependency_id = None

        db_function_dependencies = \
            database_handler.get_function_dependency({
                "pathToProject": self.path_project_root,
                "fileId": self.analyzer_instance.get_file_identity(),
                "functionId": function_id,
                "calledFileId": called_file_id,
                "calledFunctionId": called_function_id
            })

        if db_function_dependencies is not None:
            if len(db_function_dependencies) > 1:
                logging.warning(
                    "Multiple dependency definitions in database for "
                    f"{self.path_project_root} : "
                    f"{self.analyzer_instance.get_file_identity()} : "
                    f"{function_id} ->"
                    f"{called_file_id} : "
                    f"{called_function_id}.")

            function_dependency_id = db_function_dependencies[0]["_id"]

        return function_dependency_id

    def __db_get_function_info(self, function_id: str) -> dict:
        """Get the database ID for the specified test surface function.

        :param function_id: The test surface function ID.
        :type function_id: str

        :return: The database entry of the saved test surface if found,
        otherwise None is returned.
        :rtype: str
        """
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file information")

        function_info = None

        db_function_info = \
            database_handler.get_function_info({
                "pathToProject": self.path_project_root,
                "fileId": self.analyzer_instance.get_file_identity(),
                "functionId": function_id
            })

        if db_function_info is not None:
            if len(db_function_info) > 1:
                logging.warning(
                    "Multiple function definitions in database "
                    "for "
                    f"{self.path_project_root} : "
                    f"{self.analyzer_instance.get_file_identity()} : "
                    f"{function_id}")

            function_info = db_function_info[0]

        return function_info

    def __db_save_function_info_test_surfaces(self) -> None:
        """Save all function info for all test surfaces found by the current A
        nalyzeJS instance into the database.

        :return: None
        """
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        test_surfaces = self.analyzer_instance.get_test_surfaces()
        for test_surface in test_surfaces:

            new_function_info = {
                "arguments": test_surface["arguments"],
                "functionRange": test_surface["functionRange"],
                "functionHash": test_surface["functionHash"],
                "exportInfo": test_surface["exportInfo"],
                "exportName": test_surface["exportName"]
            }

            existing_function_info = \
                self.__db_get_function_info(test_surface['functionId'])

            if existing_function_info is not None:
                self.existing_function_info. \
                    append(existing_function_info["_id"])

                change_list = \
                    self.__compare_dict_prop_values(
                        existing_function_info, new_function_info)

                previous_change_list = existing_function_info['changeList']

                if len(change_list) > 0:
                    logging.info(
                        f"Detected changes were: {', '.join(change_list)}")

                    database_handler.set_function_info(
                        {
                            **new_function_info,
                            "haveFunctionChanged": True,
                            "changeList": previous_change_list + change_list
                        },
                        {'_id': existing_function_info["_id"]}
                    )

            else:
                added_test_surface_id = \
                    database_handler.add_function_info(test_surface)
                self.added_function_info.append(added_test_surface_id)

    def __db_save_function_dependencies(self) -> None:
        """Save all function dependencies found by the current AnalyzeJS
        instance into the database.

        :return:
        """
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        function_dependencies = self.analyzer_instance.get_dependency_usages()
        for function_dependency in function_dependencies:

            existing_dependency_id = \
                self.__db_get_function_dependency_id(
                    function_dependency["functionId"],
                    function_dependency["calledFileId"],
                    function_dependency["calledFunctionId"])

            if existing_dependency_id is not None:
                self.existing_function_dependencies. \
                    append(existing_dependency_id)

            else:
                added_dependency_id = \
                    database_handler.add_function_dependency(
                        function_dependency)
                self.added_function_dependencies.append(added_dependency_id)

    def __db_cleanup_project_function_dependencies(self) -> None:
        """Remove all dependencies on functions not defined in the current
        project as they are not part of the possible test surfaces. This will
        remove dependencies on external libraries.

        :return: None
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
                    'pathToProject': self.path_project_root,
                    'fileId': project_dependency['calledFileId'],
                    'functionId': project_dependency['calledFunctionId']
                })

            if dependency_defined_in_project is None:
                database_handler.remove_function_dependency({
                    '_id': project_dependency["_id"]
                })

    def __db_save_project_function_dependencies_count(self) -> None:
        """For all saved test surfaces, count the number of dependents that
        rely on the current function, and count the number of test functions
        the current function depends upon. Once done, save this information
        to the test surface's function info entry in the database.

        :return:
        """
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
                    'pathToProject': self.path_project_root,
                    'fileId': project_function['fileId'],
                    'functionId': project_function['functionId']
                })

            depends_on_function = \
                database_handler.get_function_dependency({
                    'pathToProject': self.path_project_root,
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

            project_function_backup = \
                self.__backup_get_project_function_info(
                    project_function['fileId'], project_function['functionId'])

            if project_function_backup is not None:
                change_list = \
                    self.__compare_dict_prop_values(
                        project_function_backup, new_function_info)

                previous_change_list = project_function['changeList']

                if len(change_list) > 0:
                    logging.info(
                        f"Detected changes were: {', '.join(change_list)}")

                    database_handler.set_function_info(
                        {
                            **new_function_info,
                            "haveFunctionChanged": True,
                            "changeList": previous_change_list + change_list
                        },
                        {'_id': project_function["_id"]}
                    )

            else:
                database_handler.set_function_info(
                    new_function_info,
                    {'_id': project_function["_id"]}
                )

    # ~~~~~( Public Interface ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~( Public Interface - Analyzer Management ) ~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_analyzer(self, analyzer_instance: AnalyzeJS) -> None:
        """Set the current AnalyzeJS instance in order to handle information
        from a completed analysis.

        :param analyzer_instance: The AnalyzeJS instance.
        :type analyzer_instance: AnalyzeJS

        :return: None
        """
        if not isinstance(analyzer_instance, AnalyzeJS):
            raise TypeError("'analyzer_instance' must be a AnalyzeJS object")

        self.analyzer_instance = analyzer_instance
        self.code_target_file = analyzer_instance.code_target_file

    def unset_analyzer(self) -> None:
        """Unset the current AnalyzeJS instance in order to prevent any
        further unwanted handling of (probably) already handled information.

        :return: None
        """
        self.analyzer_instance = None
        self.code_target_file = None

    # ~~~~~( Public Interface - Cache Management ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def cache_check(self) -> bool:
        """Check if the current AnalyzeJS instance's target file is actually
        different from the file already stored in cache. If the files are
        the same, there should be no need for a new analysis.

        :return: True if the cache is the same as the current target file,
        False otherwise, meaning the curren target file has changed.
        :rtype: bool
        """
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        new_contents_hash = \
            hashlib.sha256(str.encode(self.code_target_file)).hexdigest()

        try:
            cache_contents_hash = \
                hashlib.sha256(str.encode(read_file(
                    self.path_project_root,
                    self.analyzer_instance.get_file_identity()))).hexdigest()

        except FileNotFoundError:
            cache_contents_hash = ""

        return cache_contents_hash == new_contents_hash

    def cache_save(self) -> None:
        """Save the current AnalyzeJS instance's target file to the cache.

        :return: None
        """
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        save_file(
            self.path_project_root,
            self.analyzer_instance.get_file_identity(),
            self.code_target_file)

    # ~~~~~( Public Interface - Database Management ) ~~~~~~~~~~~~~~~~~~~~~~~~~
    def database_save(self) -> None:
        """Save all function info for all test surfaces and all function
        dependencies found by the current AnalyzeJS instance into the
        database.

        :return: None
        """
        if self.analyzer_instance is None:
            raise ValueError(
                "No 'analyzer_instance' is set! Cannot handle individual "
                "project file management")

        self.__db_save_function_info_test_surfaces()
        self.__db_save_function_dependencies()

    def database_cleanup(self) -> None:
        """Clean the database from dependencies on non-testable functions,
        count the number of dependencies and dependents a test surface have
        and delete all dead test surfaces and dependencies no longer existing
        in the project at the current state.

        :return: None
        """
        self.__db_cleanup_project_function_dependencies()
        self.__db_save_project_function_dependencies_count()
        self.__db_delete_dead_project_function_dependencies()
        self.__db_delete_dead_project_function_info()

    # ~~~~~( Public Interface - Cleanup ) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def process_cleanup(self) -> None:
        """Cleanup process after a successful project analysis.

        :return: None
        """
        self.__project_backup_remove()

    def restore_backup(self) -> None:
        """Restore analysis backup if current project analysis process have to
        be cancelled.

        :return: None
        """
        self.__project_restore()


def point_client_action_cancel(project_data: ProjectDataHandler):
    if client_action.pop_state() == CACode.ACTION_CANCEL:
        project_data.restore_backup()
        shared_websockets_handler.send_error(
            WsIdentity.NEW_PROJECT,
            WsCode.ANALYZE_ERR_CLIENT_STOP,
            f"Process cancelled by client"
        )
        return True

    else:
        return False


def analyze_files(project_root):
    """Analyze all eligible files in the provided project root.

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

    def callback_client_messages(message: dict):
        if 'userAction' in message and message['userAction'] == \
                WsClientCode.ANALYZE_STOP.value:
            logging.info(
                "Analyzer received cancellation action from client "
                f"({message['_clientId']})")
            client_action.dispatch(CACode.ACTION_CANCEL)

    shared_websockets_handler.add_listener_message(
        WsIdentity.NEW_PROJECT, callback_client_messages)

    list_of_files = []
    for path, currentDirectory, files in os.walk(project_root):
        for file in files:
            file_location = os.path.abspath(os.path.join(path, file))
            if analyzer_config.is_file_allowed(file_location):
                list_of_files.append(file_location)

    for file_num, current_file in enumerate(list_of_files):
        # Client Cancellation Point
        if point_client_action_cancel(project_data):
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
            analyzer = AnalyzeJS(current_file, project_root)

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

        # Uncomment to enable helpful debugging info
        # __debug_info_print_project_info(
        #    project_root, file_num, current_file, analyzer)
        # debug_get_cache_info(
        #    project_root, analyzer.js_target_file_import_path)

        # Client Cancellation Point
        if point_client_action_cancel(project_data):
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
            analyzer.begin_analyze()

            # Client Cancellation Point
            if point_client_action_cancel(project_data):
                return

            project_data.cache_save()
            project_data.database_save()

        project_data.unset_analyzer()

    project_data.database_cleanup()
    project_data.process_cleanup()

    # Client Cancellation Point
    if point_client_action_cancel(project_data):
        return

    shared_websockets_handler.send_success(
        WsIdentity.NEW_PROJECT,
        WsCode.ANALYZE_COMPLETE,
        "Project analysis complete!"
    )


# Debugging Help
def __debug_info_print_project_info(
        project_root: str = "",
        file_num: int = 0,
        current_file: str = "",
        analyzer: AnalyzeJS = None) -> None:
    win_size = 120
    name_size = 20
    print("")
    print(f"{'project_root': <{name_size}}: "
          f"{' ' + project_root:.>{win_size}}")
    print(f"{'current_file (num)': <{name_size}}: "
          f"{f' {current_file} ({file_num})':.>{win_size}}")
    print(f"{'file_identity': <{name_size}}: "
          f"{f' {analyzer.js_target_file_import_path}':.>{win_size}}")
