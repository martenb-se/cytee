import pytest


@pytest.fixture()
def mocker_os_path_isfile(mocker):
    """
    :param mocker: Pytest mocker.
    :return: The custom mocker.
    """

    class MockOpenObject:
        def __init__(self, file_mocks=None):
            if file_mocks is None:
                self.file_mocks = []
            else:
                self.file_mocks = file_mocks

        def patcher_os_path_isfile(self, filename):
            return filename in self.file_mocks

    def mocker_return(to_mock, file_mocks=None):
        """Mocker to send back to test.
        :param to_mock: Variant of os.path.isfile() to mock.
        :type to_mock: str
        :param file_mocks:
        :return: Nothing
        """
        mocked_open = MockOpenObject(file_mocks)
        mocker.patch(to_mock, side_effect=mocked_open.patcher_os_path_isfile)

    yield mocker_return
