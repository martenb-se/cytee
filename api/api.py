import os


def list_files(sub_dir):
    path_to_dir = os.path.dirname(os.path.abspath(__file__)) + "/" + sub_dir
    files = os.listdir(path_to_dir)
    file_list = [path_to_dir + "/" + f for f in files]
    return file_list


def choose_files(path_to_project, list_of_files) -> str:
    """Chose files

    :param path_to_project:
    :type path_to_project: str
    :param list_of_files:
    :type list_of_files: list[str]
    :return: JSON Data
    :rtype: str
    """
    pass


def choose_project(path_to_project) -> str:
    """

    :param path_to_project: path to project
    :type path_to_project: str

    :return: JSON Data
    :rtype: str
    """
    pass
