"""
OGC OWS and WPS Exceptions

Based on OGC OWS, WPS and

http://lists.opengeospatial.org/pipermail/wps-dev/2013-October/000335.html
"""

from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
from werkzeug._compat import text_type
from werkzeug.utils import escape
from werkzeug.http import HTTP_STATUS_CODES


class NoApplicableCode(HTTPException):
    """No applicable code exception implementation

    also

    Base exception class
    """

    code = 400
    locator = ""

    def __init__(self, description, locator="", code=400):
        self.code = code
        self.description = description
        self.locator = locator

        HTTPException.__init__(self)

    @property
    def name(self):
        """The status name."""
        return self.__class__.__name__

    def get_headers(self, environ=None):
        """Get a list of headers."""
        return [('Content-Type', 'text/xml')]

    def get_description(self, environ=None):
        """Get the description."""
        if self.description:
            return '''<ows:ExceptionText>%s</ows:ExceptionText>''' % escape(self.description)
        else:
            return ''

    def get_body(self, environ=None):
        """Get the XML body."""
        return text_type((
            u'<?xml version="1.0" encoding="UTF-8"?>\n'
            u'<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 ../../../ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">'
            u'<ows:Exception exceptionCode="%(name)s" locator="%(locator)s" >'
            u'%(description)s'
            u'</ows:Exception>'
            u'</ows:ExceptionReport>'
        ) % {
            'code':         self.code,
            'locator':         escape(self.locator),
            'name':         escape(self.name),
            'description':  self.get_description(environ)
        })


class InvalidParameterValue(NoApplicableCode):
    """Invalid parameter value exception implementation
    """
    code = 400


class MissingParameterValue(NoApplicableCode):
    """Missing parameter value exception implementation
    """
    code = 400


class FileSizeExceeded(NoApplicableCode):
    """File size exceeded exception implementation
    """
    code = 400


class VersionNegotiationFailed(NoApplicableCode):
    """Version negotiation exception implementation
    """
    pass


class OperationNotSupported(NoApplicableCode):
    """Operation not supported exception implementation
    """
    code = 501


class StorageNotSupported(NoApplicableCode):
    """Storage not supported exception implementation
    """
    code = 400

