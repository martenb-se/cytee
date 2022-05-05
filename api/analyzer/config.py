import os
import re
import yaml
from os.path import exists


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
