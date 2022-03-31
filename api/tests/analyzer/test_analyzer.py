import base64
import pytest
from api.analyzer.analyzer import analyze_files, HandleEsprima


@pytest.fixture()
def mocker_open(mocker):
    class MockOpen:
        FILE_jira_clone_client_src_shared_utils_api = \
            "aW1wb3J0IGF4aW9zIGZyb20gJ2F4aW9zJzsKCmltcG9ydCBoaXN0b3J5IGZyb20gJ2Jyb3dzZXJIaXN0b3J5JzsKaW1wb3J0IHRvYXN0" \
            "IGZyb20gJ3NoYXJlZC91dGlscy90b2FzdCc7CmltcG9ydCB7IG9iamVjdFRvUXVlcnlTdHJpbmcgfSBmcm9tICdzaGFyZWQvdXRpbHMv" \
            "dXJsJzsKaW1wb3J0IHsgZ2V0U3RvcmVkQXV0aFRva2VuLCByZW1vdmVTdG9yZWRBdXRoVG9rZW4gfSBmcm9tICdzaGFyZWQvdXRpbHMv" \
            "YXV0aFRva2VuJzsKCmNvbnN0IGRlZmF1bHRzID0gewogIGJhc2VVUkw6IHByb2Nlc3MuZW52LkFQSV9VUkwgfHwgJ2h0dHA6Ly9sb2Nh" \
            "bGhvc3Q6MzAwMCcsCiAgaGVhZGVyczogKCkgPT4gKHsKICAgICdDb250ZW50LVR5cGUnOiAnYXBwbGljYXRpb24vanNvbicsCiAgICBB" \
            "dXRob3JpemF0aW9uOiBnZXRTdG9yZWRBdXRoVG9rZW4oKSA/IGBCZWFyZXIgJHtnZXRTdG9yZWRBdXRoVG9rZW4oKX1gIDogdW5kZWZp" \
            "bmVkLAogIH0pLAogIGVycm9yOiB7CiAgICBjb2RlOiAnSU5URVJOQUxfRVJST1InLAogICAgbWVzc2FnZTogJ1NvbWV0aGluZyB3ZW50" \
            "IHdyb25nLiBQbGVhc2UgY2hlY2sgeW91ciBpbnRlcm5ldCBjb25uZWN0aW9uIG9yIGNvbnRhY3Qgb3VyIHN1cHBvcnQuJywKICAgIHN0" \
            "YXR1czogNTAzLAogICAgZGF0YToge30sCiAgfSwKfTsKCmNvbnN0IGFwaSA9IChtZXRob2QsIHVybCwgdmFyaWFibGVzKSA9PgogIG5l" \
            "dyBQcm9taXNlKChyZXNvbHZlLCByZWplY3QpID0+IHsKICAgIGF4aW9zKHsKICAgICAgdXJsOiBgJHtkZWZhdWx0cy5iYXNlVVJMfSR7" \
            "dXJsfWAsCiAgICAgIG1ldGhvZCwKICAgICAgaGVhZGVyczogZGVmYXVsdHMuaGVhZGVycygpLAogICAgICBwYXJhbXM6IG1ldGhvZCA9" \
            "PT0gJ2dldCcgPyB2YXJpYWJsZXMgOiB1bmRlZmluZWQsCiAgICAgIGRhdGE6IG1ldGhvZCAhPT0gJ2dldCcgPyB2YXJpYWJsZXMgOiB1" \
            "bmRlZmluZWQsCiAgICAgIHBhcmFtc1NlcmlhbGl6ZXI6IG9iamVjdFRvUXVlcnlTdHJpbmcsCiAgICB9KS50aGVuKAogICAgICByZXNw" \
            "b25zZSA9PiB7CiAgICAgICAgcmVzb2x2ZShyZXNwb25zZS5kYXRhKTsKICAgICAgfSwKICAgICAgZXJyb3IgPT4gewogICAgICAgIGlm" \
            "IChlcnJvci5yZXNwb25zZSkgewogICAgICAgICAgaWYgKGVycm9yLnJlc3BvbnNlLmRhdGEuZXJyb3IuY29kZSA9PT0gJ0lOVkFMSURf" \
            "VE9LRU4nKSB7CiAgICAgICAgICAgIHJlbW92ZVN0b3JlZEF1dGhUb2tlbigpOwogICAgICAgICAgICBoaXN0b3J5LnB1c2goJy9hdXRo" \
            "ZW50aWNhdGUnKTsKICAgICAgICAgIH0gZWxzZSB7CiAgICAgICAgICAgIHJlamVjdChlcnJvci5yZXNwb25zZS5kYXRhLmVycm9yKTsK" \
            "ICAgICAgICAgIH0KICAgICAgICB9IGVsc2UgewogICAgICAgICAgcmVqZWN0KGRlZmF1bHRzLmVycm9yKTsKICAgICAgICB9CiAgICAg" \
            "IH0sCiAgICApOwogIH0pOwoKY29uc3Qgb3B0aW1pc3RpY1VwZGF0ZSA9IGFzeW5jICh1cmwsIHsgdXBkYXRlZEZpZWxkcywgY3VycmVu" \
            "dEZpZWxkcywgc2V0TG9jYWxEYXRhIH0pID0+IHsKICB0cnkgewogICAgc2V0TG9jYWxEYXRhKHVwZGF0ZWRGaWVsZHMpOwogICAgYXdh" \
            "aXQgYXBpKCdwdXQnLCB1cmwsIHVwZGF0ZWRGaWVsZHMpOwogIH0gY2F0Y2ggKGVycm9yKSB7CiAgICBzZXRMb2NhbERhdGEoY3VycmVu" \
            "dEZpZWxkcyk7CiAgICB0b2FzdC5lcnJvcihlcnJvcik7CiAgfQp9OwoKZXhwb3J0IGRlZmF1bHQgewogIGdldDogKC4uLmFyZ3MpID0+" \
            "IGFwaSgnZ2V0JywgLi4uYXJncyksCiAgcG9zdDogKC4uLmFyZ3MpID0+IGFwaSgncG9zdCcsIC4uLmFyZ3MpLAogIHB1dDogKC4uLmFy" \
            "Z3MpID0+IGFwaSgncHV0JywgLi4uYXJncyksCiAgcGF0Y2g6ICguLi5hcmdzKSA9PiBhcGkoJ3BhdGNoJywgLi4uYXJncyksCiAgZGVs" \
            "ZXRlOiAoLi4uYXJncykgPT4gYXBpKCdkZWxldGUnLCAuLi5hcmdzKSwKICBvcHRpbWlzdGljVXBkYXRlLAp9Owo="

        FILE_jira_clone_client_src_shared_utils_authToken = \
            "ZXhwb3J0IGNvbnN0IGdldFN0b3JlZEF1dGhUb2tlbiA9ICgpID0+IGxvY2FsU3RvcmFnZS5nZXRJdGVtKCdhdXRoVG9rZW4nKTsKCmV4" \
            "cG9ydCBjb25zdCBzdG9yZUF1dGhUb2tlbiA9IHRva2VuID0+IGxvY2FsU3RvcmFnZS5zZXRJdGVtKCdhdXRoVG9rZW4nLCB0b2tlbik7" \
            "CgpleHBvcnQgY29uc3QgcmVtb3ZlU3RvcmVkQXV0aFRva2VuID0gKCkgPT4gbG9jYWxTdG9yYWdlLnJlbW92ZUl0ZW0oJ2F1dGhUb2tl" \
            "bicpOwo="

        def __init__(self, filename, operation):
            self.filename = filename
            self.operation = operation
            self.status = "open"

        # Used for: "with open(...):"
        def __enter__(self):
            return self

        # Used for: "with open(...):"
        def __exit__(self, arg1, arg2, arg3):
            self.status = "closed"

        def read(self):
            file_contents = ""
            if self.filename == "/jira_clone/client/src/shared/utils/api.js":
                file_contents = base64.b64decode(self.FILE_jira_clone_client_src_shared_utils_api).decode("utf-8")
            elif self.filename == "/jira_clone/client/src/shared/utils/authToken.js":
                file_contents = base64.b64decode(self.FILE_jira_clone_client_src_shared_utils_authToken).decode("utf-8")

            return file_contents

        def close(self):
            self.status = "closed"

    # Function to pass to patcher
    def patcher_open(filename, operation):
        return MockOpen(filename, operation)

    mock_open = mocker.patch('api.analyzer.analyzer.open', side_effect=patcher_open)
    # yield mock_open


def test_class_handleesprima_init_not_string():
    file_source = False
    try:
        HandleEsprima(file_source)
        assert False
    except TypeError as e:
        assert str(e) == "'file_source' must be a STRING"
    except Exception:
        assert False


def test_class_handleesprima_init_no_content():
    file_source = ""
    try:
        HandleEsprima(file_source)
        assert False
    except ValueError as e:
        assert str(e) == "'file_source' cannot be empty"
    except Exception:
        assert False


def test_analyze_files_arg_not_list():
    list_of_files = ""
    try:
        analyze_files(list_of_files)
        assert False
    except TypeError as e:
        assert str(e) == "'list_of_files' must be a LIST"
    except Exception:
        assert False


def test_analyze_files_arg_empty_list():
    list_of_files = []
    try:
        analyze_files(list_of_files)
        assert False
    except ValueError as e:
        assert str(e) == "'list_of_files' cannot be empty"
    except Exception:
        assert False


def test_analyze_files_arg_list_item_not_string():
    list_of_files = [
        1,
        -7
    ]
    try:
        analyze_files(list_of_files)
        assert False
    except ValueError as e:
        assert str(e) == "'list_of_files' must only contain paths to files as STRINGS"
    except Exception:
        assert False


def test_analyze_files_arg_list_item_empty_string():
    list_of_files = [
        "",
        ""
    ]
    try:
        analyze_files(list_of_files)
        assert False
    except ValueError as e:
        assert str(e) == "Paths in 'list_of_files' cannot be empty strings"
    except Exception:
        assert False


# TODO: Continue with testing
"""
def test_analyze_files_arg_empty_list123(mocker_open):
    list_of_files = [
        "/jira_clone/client/src/shared/utils/api.js",
        "/jira_clone/client/src/shared/utils/authToken.js"
    ]

    analyze_files(list_of_files)

    assert False
"""