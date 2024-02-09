from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pywps import WPSRequest

from pywps.dblog import store_status
from pywps.response.status import WPS_STATUS
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


class WPSResponse(object):

    def __init__(self, wps_request: 'WPSRequest', uuid=None, version="1.0.0"):

        self.wps_request = wps_request
        self.uuid = uuid
        self.message = ''
        self.status = WPS_STATUS.ACCEPTED
        self.status_percentage = 0
        self.doc = None
        self.content_type = None
        self.version = version
        self.template_env = TEMPLATE_ENV

    def _update_status(self, status, message, status_percentage):
        """
        Update status report of currently running process instance

        :param str message: Message you need to share with the client
        :param int status_percentage: Percent done (number between <0-100>)
        :param pywps.response.status.WPS_STATUS status: process status - user should usually
            omit this parameter
        """
        self.message = message
        self.status = status
        self.status_percentage = status_percentage
        store_status(self.uuid, self.status, self.message, self.status_percentage)

    @abstractmethod
    def _construct_doc(self):
        ...

    def get_response_doc(self):
        try:
            self.doc, self.content_type = self._construct_doc()
        except Exception as e:
            if hasattr(e, "description"):
                msg = e.description
            else:
                msg = e
            self._update_status(WPS_STATUS.FAILED, msg, 100)
            raise e

        else:
            self._update_status(WPS_STATUS.SUCCEEDED, "Response generated", 100)

            return self.doc, self.content_type
