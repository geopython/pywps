
import os

from jinja2 import Environment, PackageLoader
from pywps.translations import get_translation


class RelEnvironment(Environment):
    """Override join_path() to enable relative template paths."""
    def join_path(self, template, parent):
        return os.path.dirname(parent) + '/' + template


TEMPLATE_ENV = RelEnvironment(
    loader=PackageLoader('pywps', 'templates'),
    trim_blocks=True, lstrip_blocks=True,
    autoescape=True,
)
TEMPLATE_ENV.globals.update(get_translation=get_translation)


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
