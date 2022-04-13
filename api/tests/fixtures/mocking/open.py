import pytest
import base64
from api.tests.analyzer.mock_data_test_analyzer import \
    CONTENTS_FILE_jira_clone_client_src_shared_utils_api, \
    CONTENTS_FILE_jira_clone_client_src_shared_utils_authToken


@pytest.fixture()
def mocker_open(mocker):
    """Pytest mocker for built in function: open(filename, operation)
    :param mocker: Pytest mocker.
    :return: The custom mocker.
    """

    class MockOpenReturnObject:
        def __init__(
                self,
                filename,
                operation,
                file_mocks=None,
                content_drain=None):
            """Mock replacement for built in function returned by
            open(filename, operation).

            :param filename: The filename (with filepath) to open.
            :type filename: str
            :param operation: The operation code to read the file with. This
            option is of no importance to this mocker and its contents will be
            ignored.
            :type filename: str
            """
            if file_mocks is None:
                file_mocks = {
                    "/jira_clone/client/src/shared/utils/api.js":
                        base64.b64decode(
                            CONTENTS_FILE_jira_clone_client_src_shared_utils_api
                        ).decode("utf-8"),
                    "/jira_clone/client/src/shared/utils/authToken.js":
                        base64.b64decode(
                            CONTENTS_FILE_jira_clone_client_src_shared_utils_authToken
                        ).decode("utf-8")
                }

            if content_drain is None:
                content_drain = {}

            self.filename = filename
            self.operation = operation
            self.status = "open"
            self.file_mocks = file_mocks
            self.content_drain = content_drain

        def __enter__(self):
            """Returns the own class instance.
            Note: Method is called when running "with open(...):" and therefore
            must be defined, it's effect is of no importance to the mocker.
            :return: The class instance.
            """
            return self

        def __exit__(self, arg1, arg2, arg3):
            """Sets the internal file status to "closed".
            Note: Method is called when running "with open(...):" and therefore
            must be defined, it's effect is of no importance to the mocker.
            :param arg1: Positional argument 1 is of no importance to the
            mocker.
            :param arg2: Positional argument 2 is of no importance to the
            mocker.
            :param arg3: Positional argument 3 is of no importance to the
            mocker.
            :return: Nothing
            """
            self.status = "closed"

        def read(self):
            file_contents = ""

            if self.filename in self.file_mocks:
                file_contents = self.file_mocks[self.filename]

            return file_contents

        def write(self, data):
            self.content_drain[self.filename] = data

        def close(self):
            self.status = "closed"

    class MockOpenObject:
        def __init__(self, file_mocks=None, content_drain=None):
            self.file_mocks = file_mocks
            self.content_drain = content_drain

        def patcher_open(self, filename, operation):
            """The patcher function to use instead of open().
            :param filename: The filename (with filepath) to open.
            :type filename: str
            :param operation: The operation code to read the file with. This
            option is of no importance to this mocker and
            its contents will be ignored.
            :type filename: str
            :return: The initiated mocker instance.
            """
            return MockOpenReturnObject(
                filename,
                operation,
                file_mocks=self.file_mocks,
                content_drain=self.content_drain)

    def mocker_return(to_mock, file_mocks=None, content_drain=None):
        """Mocker to send back to test.
        :param to_mock: Variant of open() to mock.
        :type to_mock: str
        :param file_mocks:
        :return: Nothing
        """
        mocked_open = MockOpenObject(
            file_mocks=file_mocks,
            content_drain=content_drain)
        mocker.patch(to_mock, side_effect=mocked_open.patcher_open)

    yield mocker_return
