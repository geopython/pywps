# Author:    Jachym Cepicky
#            http://les-ejk.cz
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
import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.append(pywpsPath)

import pywps
import pywps.Process
import unittest
from xml.dom import minidom
import base64
from osgeo import ogr
import tempfile

class ProcessesTestCase(unittest.TestCase):
    inputs = None
    getcapabilitiesrequest = "service=wps&request=getcapabilities"
    wpsns = "http://www.opengis.net/wps/1.0.0"
    xmldom = None

    def test01PYWPS_CFG(self):
        os.environ["PYWPS_CFG"] = os.path.abspath(os.path.join(pywpsPath,"tests","pywps.cfg"))
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest(self.getcapabilitiesrequest)
        mypywps.performRequest(inputs)
        xmldom = minidom.parseString(mypywps.response)

        self.assertEquals(xmldom.getElementsByTagName("ows:Title")[0].firstChild.nodeValue, "Test")

    def test02PYWPS_PROCESSES(self):
        os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath,"tests","processes")
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest(self.getcapabilitiesrequest)
        mypywps.performRequest(inputs)
        xmldom = minidom.parseString(mypywps.response)
        #print mypywps.response

        self.assertTrue(len(xmldom.getElementsByTagNameNS(self.wpsns,"Process"))>0)

    def test03PYWPS_TEMPLATES(self):
        os.environ["PYWPS_TEMPLATES"] = os.path.join(pywpsPath,"tests","Templates")
        mypywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = mypywps.parseRequest(self.getcapabilitiesrequest)
        mypywps.performRequest(inputs)
        xmldom = minidom.parseString(mypywps.response)

        self.assertTrue(xmldom.getElementsByTagName("Test") > 0)


if __name__ == "__main__":
    unittest.main()
