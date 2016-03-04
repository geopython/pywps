"""
OGC OWS and WPS Exceptions

Based on OGC OWS, WPS and

http://lists.opengeospatial.org/pipermail/wps-dev/2013-October/000335.html
"""
# Author:    Alex Morega & Calin Ciociu
#            
# License:
#
# Web Processing Service implementation
# Copyright (C) 2015 PyWPS Development Team, represented by Jachym Cepicky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
from werkzeug._compat import text_type
from werkzeug.utils import escape
from werkzeug.http import HTTP_STATUS_CODES

import logging

from pywps import __version__

LOGGER = logging.getLogger(__name__)

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
        msg = 'Exception: code: %s, locator: %s, description: %s' % (self.code, self.description, self.locator)
        LOGGER.exception(msg)

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
            u'<!-- PyWPS %(version)s -->\n'
            u'<ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 http://schemas.opengis.net/ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">'
            u'<ows:Exception exceptionCode="%(name)s" locator="%(locator)s" >'
            u'%(description)s'
            u'</ows:Exception>'
            u'</ows:ExceptionReport>'
        ) % {
            'version': __version__,
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
