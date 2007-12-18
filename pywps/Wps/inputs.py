"""
This module parses the input for WPS. Input
can be either XML string or comma and = separated string in form 

    name1=value1,name2=value2,name3=value3,value4
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# Lince: 
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


import xml
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces
import sys
import wpsexceptions
from wpsexceptions import *
from debug import PyWPSdebug

#--------------------------------------------------------------------#
# processExecuteXML - for parsing the input xml document using sax   #
#--------------------------------------------------------------------#
class processExecuteXML(xml.sax.handler.ContentHandler):
    """
    processExecuteXML defineds the sax handler for parsing input XML file
    reseved by XML POST
    """
    def __init__(self):
        self.inInput = None
        self.inDataInputs = None
        self.inIdentifier = None
        self.inValue = None

        self.inComplexValue = False

        self.value = ''
        self.ident = ''

        self.values = {} # here will be the input values stored
        self.values['datainputs'] = {}

        self.valueFirstChild = None
        self.inComplexValueInValue = False

    def startElementNS(self,name, qname, attrs):
        if name[1] == "DataInputs":
            self.inDataInputs = True
        elif name[1] == "Identifier":
            self.inIdentifier = True
        elif name[1] == "ComplexValueReference":
            self.inComplexValueReference = True
            # get reference namespace
            for attr in attrs.keys():
                if attr[1] == "reference":
                    self.value = {
                        "type":"ComplexValueReference",
                        "data": attrs[attr]
                    }
        elif name[1] == "ComplexValue":
            self.inComplexValue = True
            self.value = {
                "type":"ComplexValue",
                "data":"!complexvalue!",
            }

        elif name[1] == "BoundingBoxValue":
            self.value = "!bboxvalue!"

        elif name[1] == "LiteralValue":
            self.inValue = True
            self.inLiteralValue = True

        # for embeded xmls in
        # <ComplexValue><Value>...</Value></ComplexValue>
        if self.inComplexValueInValue and not self.valueFirstChild:
            self.valueFirstChild = name

        # for embeded xmls in
        # <ComplexValue><Value>...</Value></ComplexValue>
        # in next step, 
        if name[1] == "Value":
            self.inComplexValueInValue = True

    def endElementNS(self,name, qname):

        if name[1] == "DataInputs":
            self.inDataInputs = False
        if name[1] == "Identifier":
            self.inIdentifier = False
        #if name[1] == "ComplexValue":
        #    self.value["data"] = "!complexvalue!"
        #if name[1] == "BoundingBoxValue":
        #    self.value = "!bboxvalue!"

        if self.value and self.ident:
            
            # if it exists, it will be array
            if self.values['datainputs'].has_key(self.ident):
                
                # "value" -> [value]
                self.values['datainputs'][self.ident] = \
                        [self.values['datainputs'][self.ident]]
                # [value] -> [value1,value2]
                self.values['datainputs'][self.ident].append(self.value)
            # normal value else
            else:
                self.values['datainputs'][self.ident] = self.value
            self.value = self.ident = ''

        if name[1] == "ComplexValue":
            self.inValue = False
        if name[1] == "LiteralValue":
            self.inValue = False
        if name[1] == "ComplexValueReference":
            self.inValue = False

        if name[1] == "Input":
            self.inComplexValue = False
            self.inComplexValueReference = False
            self.inLiteralValue = False

    def characters(self,characters):
        """
        Here are the values taken
        """

        characters = characters.strip()

        # process identifier
        if self.inIdentifier and not self.inDataInputs:
            self.values['identifier'] = [characters]
        # identifier of the input
        elif self.inIdentifier and self.inDataInputs:
            self.ident = characters
        # value of the input
        elif self.inValue and self.inDataInputs:
            self.value = characters


class Inputs:
    """
    This class will store the input structure
    """
    def __init__(self):
        self.values = {}

    #--------------------------------------------------------------------#
    # formvalsPost2dict - convert xml input to dictionary structure      #
    #--------------------------------------------------------------------#
    def formvalsPost2dict(self,file,size):
        """
        stores the input formValues to to input structure. suppose,
        formValues['request'] parameter is xml string
        """
        import xml.dom.minidom

        # read only defined size
        if size:
            inputxml = file.read(size)
        else:
            inputxml = file.read()

        # maximum size exceeded
        if file.read():
            raise FileSizeExceeded()

        try:
            formDocument = xml.dom.minidom.parseString(inputxml)
        except xml.parsers.expat.ExpatError,e:
            PyWPSdebug(inputxml)
            raise NoApplicableCode(e)


        #
        # decribe process request
        #
        if formDocument.firstChild.tagName.find("DescribeProcess")>-1:
            self.values['request'] = "DescribeProcess"
            from ogc import processdescription

            pdrWps = processdescription.WPS()
            requestAttrs = pdrWps.pd['request']

            for identifier in formDocument.getElementsByTagNameNS("*","Identifier"):
                if not 'identifier' in self.values.keys():
                    self.values['identifier'] = []
                self.values['identifier'].append(identifier.firstChild.data)

            # namespace
            ns = formDocument.firstChild.namespaceURI

            for attribute in requestAttrs['attributes']:
                value = None
                value = formDocument.firstChild.getAttributeNS(ns,attribute)
                # if there is no such attribute, exception
                if not value:
                    if attribute.lower() == "request":
                        continue
                    if requestAttrs[attribute]['oblig'] == "m":
                        return "DescribeProcess"
                else:
                    self.values[attribute] =  value

        #
        # execute request
        #
        elif formDocument.firstChild.tagName.find("Execute") > -1:

            from ogc import execute
            exEps = execute.WPS()
            requestExec = exEps.e['request']

            parser=make_parser()

            # Create the handler
            eh = processExecuteXML()

            # Tell the parser we are not interested in XML namespaces
            parser.setFeature(feature_namespaces, 1)

            # Tell the parser to use our handler
            parser.setContentHandler(eh)

            # Parse the input
            parser.feed(inputxml)
            self.values = eh.values
            
            # namespace
            ns = formDocument.firstChild.namespaceURI

            # attributes
            #for attribute in requestExec['attributes'].keys():
                    #value = formDocument.firstChild.getAttributeNS(ns,attribute)
                    #if requestExec["attributes"][attribute]['oblig'] == "m":
                    #    print >>sys.stderr, "#### tadxx"
                    #    return "Execute"
                    #self.values[attribute] =  value

            self.values['request'] = "Execute"
            self.values['service'] = "Wps"
            pass
            

            for input in self.values['datainputs'].keys():
                # complexvalues
                if type(self.values['datainputs'][input]) == type({}) and \
                        self.values['datainputs'][input]["data"] == "!complexvalue!":
                    # for each Input in XML
                    for Input in formDocument.getElementsByTagNameNS("http://www.opengeospatial.net/wps","Input"):
                        cmplxval = Input.getElementsByTagNameNS("http://www.opengeospatial.net/wps","ComplexValue")
                        identifier = Input.getElementsByTagNameNS("http://www.opengeospatial.net/ows","Identifier")[0].firstChild.data
                        print >>sys.stderr, cmplxval
                        # if there is at least one <ComplexValue> Element
                        # in input xml 
                        if len(cmplxval) and identifier == input:
                            # store to ["data"], ["type"] = "ComplexValue"
                            # allready
                            if cmplxval[0].firstChild.nodeType == 3:
                                for node in cmplxval[0].childNodes:
                                    if node.nodeType == 1:
                                            self.values['datainputs'][input]["data"] = node.toxml()
                            else:
                                self.values['datainputs'][input]["data"] = cmplxval[0].firstChild.toxml()

                # bbox values
                if self.values['datainputs'][input] == "!bboxvalue!":
                    for Input in formDocument.getElementsByTagNameNS("http://www.opengeospatial.net/wps","Input"):
                        cmplxval = Input.getElementsByTagNameNS("http://www.opengeospatial.net/wps","BoundingBoxValue")
                        identifier = Input.getElementsByTagNameNS("http://www.opengeospatial.net/ows","Identifier")[0].firstChild.data
                        if len(cmplxval) and identifier == input:
                            self.values['datainputs'][input] = []
                            geom = \
                                    cmplxval[0].getElementsByTagName("LowerCorner")[0].firstChild.data.split()
                            self.values['datainputs'][input].append(geom[0])
                            self.values['datainputs'][input].append(geom[1])

                            geom = \
                                    cmplxval[0].getElementsByTagName("UpperCorner")[0].firstChild.data.split()
                            self.values['datainputs'][input].append(geom[0])
                            self.values['datainputs'][input].append(geom[1])

            # identifier is array
            # self.values['identifier'] = [self.values['identifier']]

            firstNode = formDocument.firstChild
            if (firstNode.getAttributeNS(ns,"store")):
                self.values['store'] = firstNode.getAttributeNS(ns,"store")
            if (firstNode.getAttributeNS(ns,"status")):
                self.values['store'] = firstNode.getAttributeNS(ns,"status")

        # not describeprocess and not execute: exception
        else:
            raise InvalidParameterValue(formDocument.firstChild.tagName)
        return

    def formvalsGet2dict(self,formValues):
        """
        stores the input formValues to to input structure. suppose,
        formValues['request'] parameter is something like 
        
        "describeprocess" or "execute".
        """
        
        for key in formValues.keys():
            self.values[key] = formValues[key]
        if 'identifier' in formValues.keys():
            self.values['identifier'] = formValues['identifier'].split(",")
        if 'datainputs' in formValues.keys():
            self.values['datainputs'] = []
            datainputs = formValues['datainputs'].split(",")
            #
            # DataInputs must be even number
            #
            if len(datainputs) % 2 != 0:
                raise InvalidParameterValue("DataInputs")
            #
            # Array -> Dictionary
            #
            self.values['datainputs'] = dict(zip(datainputs[0::2], datainputs[1::2]))
        return

    def controllProcesses(self,processes,formValues):
        """
        controlls, if there is such process in processes array
        """

        if formValues.has_key('request') and \
           formValues['request'].lower() == "describeprocess" or \
           formValues['request'].lower() == "execute":
            if formValues.has_key('identifier'):
                for process in formValues['identifier']:
                    if not process in processes:
                        return process
            else:
                return "identifier"
        return
