
import os

from jinja2 import Environment


class RelEnvironment(Environment):
    """Override join_path() to enable relative template paths."""
    def join_path(self, template, parent):
        return os.path.dirname(parent) + '/' + template


def get_response(operation):

    from .capabilities import CapabilitiesResponse
    from .describe import DescribeResponse
    from .execute import ExecuteResponse

    if operation == "capabilities":
        return CapabilitiesResponse
    elif operation == "describe":
        return DescribeResponse
    elif operation == "execute":
        return ExecuteResponse
