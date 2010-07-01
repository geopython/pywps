"""
SOAP
----
SOAP wrapper 
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# License:
#
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from xml.dom import minidom

soap_env_NS = ["http://www.w3.org/2003/05/soap-envelope","http://schemas.xmlsoap.org/soap/envelope/"]
soap_enc_NS = ["http://www.w3.org/2003/05/soap-encoding","http://schemas.xmlsoap.org/soap/encoding/"]

SOAP_ENVELOPE="""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://www.w3.org/2003/05/soap-envelope
	http://www.w3.org/2003/05/soap-envelope">
	<soap:Body>$SOAPBODY$</soap:Body>
</soap:Envelope>"""

soap = False

def isSoap(document):
    global soap
    if document.localName == "Envelope" and\
            document.namespaceURI in soap_env_NS:
        soap = True
        return True
    else:
        soap = False
        return False

class SOAP:
    """Soap wrapper, used for parsing requests, which are in Soap envelope
    and creating Soap responses from normal XMLs.

    .. note:: This class is very primitive, it does not support advanced
        Soap features, like authorization and so on.

    """

    document = None
    nsIndex = 0

    def __init__(self,document=None):

        if document:
            if type(input) == type(""):
                self.document = minidom.parseString(document)
            else:
                self.document = document
            self.nsIndex = soap_env_NS.index(document.namespaceURI)

    def getNode(self,namespace,nodeName):
        """Get XML nod from DOM of specified name and namespace"""

        elements = self.document.getElementsByTagNameNS(namespace, nodeName)
        if len(elements) > 0:
            return elements[0]
        else:
            return None

    def getResponse(self,document):
        """Wrap document into soap envelope"""
        # very primitive, but works
        document = document.__str__().replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>","")
        return SOAP_ENVELOPE.replace("$SOAPBODY$",document)

