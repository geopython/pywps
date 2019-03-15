##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""
OGC OWS and WPS Exceptions

Based on OGC OWS, WPS and

http://lists.opengeospatial.org/pipermail/wps-dev/2013-October/000335.html
"""


from werkzeug.wrappers import Response
from werkzeug.exceptions import HTTPException
from werkzeug._compat import text_type
from werkzeug.utils import escape

import logging

from pywps import __version__

__author__ = "Alex Morega & Calin Ciociu"

LOGGER = logging.getLogger('PYWPS')


class NoApplicableCode(HTTPException):
    """No applicable code exception implementation

    also

    Base exception class
    """

    code = 500
    locator = ""

    def __init__(self, description, locator="", code=400):
        self.code = code
        self.description = description
        self.locator = locator
        msg = 'Exception: code: {}, description: {}, locator: {}'.format(self.code, self.description, self.locator)
        LOGGER.exception(msg)

        HTTPException.__init__(self)

    @property
    def name(self):
        """The status name."""
        return self.__class__.__name__

    def get_description(self, environ=None):
        """Get the description."""
        if self.description:
            return '''<ows:ExceptionText>{}</ows:ExceptionText>'''.format(escape(self.description))
        else:
            return ''

    def get_response(self, environ=None):
        args = {
            'version': __version__,
            'code': self.code,
            'locator': escape(self.locator),
            'name': escape(self.name),
            'description': self.get_description(environ)
        }
        doc = text_type((
            u'<?xml version="1.0" encoding="UTF-8"?>\n'
            u'<!-- PyWPS {version} -->\n'
            u'<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">\n'  # noqa
            u'  <ows:Exception exceptionCode="{name}" locator="{locator}" >\n'
            u'      {description}\n'
            u'  </ows:Exception>\n'
            u'</ows:ExceptionReport>'
        ).format(**args))

        return Response(doc, self.code, mimetype='text/xml')


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
    code = 400


class OperationNotSupported(NoApplicableCode):
    """Operation not supported exception implementation
    """
    code = 501


class StorageNotSupported(NoApplicableCode):
    """Storage not supported exception implementation
    """
    code = 400


class NotEnoughStorage(NoApplicableCode):
    """Storage not supported exception implementation
    """
    code = 400


class ServerBusy(NoApplicableCode):
    """Max number of operations exceeded
    """

    code = 400
    description = 'Maximum number of processes exceeded'

    def get_body(self, environ=None):
        """Get the XML body."""
        args = {
            'name': escape(self.name),
            'description': self.get_description(environ)
        }
        return text_type((
            u'<?xml version="1.0" encoding="UTF-8"?>\n'
            u'<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 ../../../ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">'  # noqa
            u'<ows:Exception exceptionCode="{name}">'
            u'{description}'
            u'</ows:Exception>'
            u'</ows:ExceptionReport>'
        ).format(**args))


class FileURLNotSupported(NoApplicableCode):
    """File URL not supported exception implementation
    """
    code = 400
    description = 'File URL not supported as input.'

    def __init__(self, description="", locator="", code=400):
        description = description or self.description
        NoApplicableCode.__init__(self, description=description, locator=locator, code=code)


class SchedulerNotAvailable(NoApplicableCode):
    """Job scheduler not available exception implementation
    """
    code = 400
