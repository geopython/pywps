"""
Simple implementation of PyWPS based on
https://github.com/jachym/pywps-4/issues/2
"""
import os
import tempfile
import time
import sys
from uuid import uuid4

from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
import lxml.etree
from lxml import etree

from pywps.exceptions import InvalidParameterValue, \
    MissingParameterValue, NoApplicableCode, \
    OperationNotSupported, VersionNegotiationFailed, FileSizeExceeded, StorageNotSupported
from pywps._compat import text_type, StringIO, PY2
from pywps import configuration, E, WPS, OWS, NAMESPACES
from pywps.formats import Format
from pywps.inputs import LiteralInput, ComplexInput
from pywps.outputs import LiteralOutput, ComplexOutput































