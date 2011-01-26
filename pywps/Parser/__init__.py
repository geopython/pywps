"""Parser parses input parameters, send via HTTP Post or HTTP Get method. If
send via HTTP Post, the input is usually XML file.

Each class in the package is resposible for each type of the request.

"""

# Author:    Jachym Cepicky
#            http://les-ejk.cz
# Lince:
#
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

__all__ = [
        "Get",
        "Post",
        "GetCapabilities",
        "DescribeProcess",
        "Execute"
        ]


class Parser:
    """Parent class for all request parsers.
    
    .. attribute:: wps

        instace of :class:`pywps.Pywps`

    .. attribute:: isSoap

        indicates, whether the request is in Soap envelope or not

    .. attribute:: inputs

        object, where results of parsing is stored
    """

    wps = None
    isSoap = False
    soapVersion=None
    isSoapExecute=None
    inputs = None

    def __init__(self,wps):
        self.wps = wps
        self.inputs = {}
    
    def _trueOrFalse(self,str):
        """Return True or False, if input is "true" or "false" 
        :param str: String to be checks and returned
        :returns: bool or str 
        """
        if str.lower() == "false":
            return False
        elif str.lower() == "true":
            return True
        else:
            return str

