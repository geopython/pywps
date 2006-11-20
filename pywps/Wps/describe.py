#!/usr/bin/python
"""
This module generates XML file with DescribeProcess response of WPS
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

# TODO: 
#   * BoundingBoxData not implemented



from xml.dom.minidom import Document
from ogc import processdescription
import append

class Describe:
    def __init__(self,serverSettings,processes,formValues):
        """
        By initalization creates ProcessDescriptions XML response.

        Inputs:
            serverSettings      - file with server settings structure (etc/settings.py)
            describeProcesses   - array of processes, which should be described
        """

        self.document = Document()
        self.settings = serverSettings
        self.WPS = processdescription.WPS()
        self.pd = self.WPS.pd['response'] # structure, where part of OGC 05-007r4 is hold
        self.Append = append.Append() # siple appending of some "standard" nodes

        # creattin array for all processes
        describeProcesses = []
        for process in formValues['identifier']:
            describeProcesses.append(eval("processes.%s.Process()" % (process)))

        # ProcessDescriptions
        self.ProcessDescriptions = self.document.createElementNS(self.WPS.namespaces['ows'],"ProcessDescriptions")
        self.ProcessDescriptions.setAttribute("xmlns",self.WPS.namespaces['wps'])
        self.ProcessDescriptions.setAttribute("xmlns:xlink",self.WPS.namespaces['xlink'])
        self.ProcessDescriptions.setAttribute("xmlns:ows",self.WPS.namespaces['ows'])
        self.ProcessDescriptions.setAttribute("xmlns:xsi",self.WPS.namespaces['xsi'])
        self.ProcessDescriptions.setAttribute("xsi:schemaLocation",self.WPS.namespaces['wps']+' '+self.WPS.schemalocation['wps'])
        self.document.appendChild(self.ProcessDescriptions)

        # for each process, the user wants to describe
        for process in describeProcesses:
            ProcessDescription = self.document.createElement("ProcessDescription")
            self.ProcessDescriptions.appendChild(ProcessDescription)

            # process description attributes
            for attribute in self.pd['attributes']:
                self.Append.Attribute(
                        self.document,
                        attribute, 
                        ProcessDescription,
                        self.pd['attributes'],
                        process
                        )
        
            # for each element in describeProcess structure
            for key in self.pd['order']:
                # For each ProcessInputs
                if key == "DataInputs":
                    datainputs = self.document.createElement("%s%s" %\
                            (self.pd['elements']['DataInputs']['ns'],"DataInputs"))
                    self.dataInputsNode(process,datainputs)
                    ProcessDescription.appendChild(datainputs)
                    # compile each input in process

                elif key == "ProcessOutputs":
                    processOutputs = self.document.createElement("%s%s" %\
                            (self.pd['elements']['ProcessOutputs']['ns'],"ProcessOutputs"))
                    try:
                        self.processOutputsNode(process,processOutputs)
                        ProcessDescription.appendChild(processOutputs)
                    except AttributeError, e:
                        if e == "Outputs":
                            processOutputs.appendChild(self.document.createComment(
                                "===== This process defined no outputs ====="
                                ))
                elif key == "Metadata":
                    # does input have any metadata?
                    try:
                        for metadata in process.Metadata:
                            Metadata = self.document.createElement("%s%s" %\
                                    (self.pd['elements']['Metadata']['ns'],"Metadata"))
                            for metattr in metadata.keys():
                                if metattr.lower() == "textcontent":
                                    pass
                                else:
                                    Metadata.setAttribute(metattr,metadata[metattr])
                            if metadata.has_key("textContent"):
                                Metadata.appendChild(self.document.createTextNode(metadata["textContent"]))
                            ProcessDescription.appendChild(Metadata)
                    except AttributeError,e:
                        ProcessDescription.appendChild(self.document.createComment(
                                "===== This process defined no Metadata =====" 
                                ))
                else: # key != ProcessInputs or != ProcessOutputs -> key is something "normal"
                    self.Append.Node(
                            self.document, key, ProcessDescription,
                            self.pd['elements'], process
                            )
        return

    def dataInputsNode(self,process,parent):
        """
        Creates DataInputs XML Node

        Inputs:
            parent  - node to which the DataInputs node should be appended
            process - process, for which will be the data inputs described
        """

        inputSett = self.pd['elements']['DataInputs']['Input'] # settings after OGC

        # for each input
        for input in process.Inputs:

            # default value
            if input.has_key('value') and \
                input['value'] != None:

                if input.has_key("Abstract"):
                    input['Abstract'] += "\n\nDefault value: %s" %\
                    (str(input['value']))
                else:
                    input['Abstract'] = "\n\nDefault value: %s" %\
                    (str(input['value']))


            # create input node
            dataInput = self.document.createElement("%s%s" %\
                    (self.pd['elements']['DataInputs']['Input']['ns'],"Input"))
            parent.appendChild(dataInput)
            
            # for each input from conf file
            dataStructureDefined = 0
            for inputParam in inputSett['order']:
                if inputParam in [ "ComplexData", "LiteralData", "BoundingBoxData" ]:
                    dataStructureDefined = 1
                    if inputParam == "ComplexData":
                        inputType = "ComplexValue"
                        if input.has_key("ComplexValueReference"):
                            inputType = "ComplexValueReference"
                    elif inputParam == "LiteralData":
                        inputType = "LiteralValue"
                        if input.has_key("LiteralData"):
                            inputType = "LiteralData"
                    elif inputParam == "BoundingBoxData":
                        inputType = "BoundingBoxValue"
                    try:
                        # create the InputData Structure
                        self.inputDataStructure(\
                                inputStruct = inputSett['elements'][inputParam],\
                                processInput = input[inputType],\
                                parent=dataInput,
                                inputtype=inputType,\
                                input=input        
                                )
                        dataStructureDefined = 1
                    except KeyError, what:
                        #print "KeyError: ",what
                        pass
                    continue

                # minimum occures/maximum occures
                if inputParam == "MinimumOccurs":
                    if input.has_key("MinimumOccurs"):
                        occursTag=self.document.createElement("MinimumOccurs")
                        occursTag.appendChild(
                                self.document.createTextNode(str(input['MinimumOccurs'])))
                        dataInput.appendChild(occursTag)
                        continue
                    elif input.has_key('value') and input['value']:
                        occursTag=self.document.createElement("MinimumOccurs")
                        occursTag.appendChild(
                                self.document.createTextNode("0"))
                        dataInput.appendChild(occursTag)
                        continue

                self.Append.Node(
                        document=self.document, 
                        childNode=inputParam, 
                        parentNode=dataInput,
                        Elements=inputSett['elements'], 
                        Values=input
                        )

            # It is not usual, that operation has no input
            if not dataStructureDefined:
                dataInput.appendChild(self.document.createComment(\
                        "===== At least one input should be defined, but none found ===="))
        return

    def processOutputsNode(self,process,parent):
        """
        Creates ProcessOutputs XML Node

        Inputs:
            parent  - node to which the DataInputs node should be appended
            process - process, for which will be the data inputs described
        """

        outputSett = self.pd['elements']['ProcessOutputs']['Output']

        # for each output from output array
        for output in process.Outputs:
            outputNode = self.document.createElement("%s%s" % (outputSett['ns'],"Output"))
            parent.appendChild(outputNode)
            # for each output parameter
            for outputParam in outputSett['order']:

                # special handling
                if outputParam in [ "ComplexOutput", "LiteralOutput", "BoundingBoxOutput" ]:

                    try:
                        if (output.has_key("LiteralValue") and\
                            outputParam=="LiteralOutput") or\
                            \
                            (output.has_key("ComplexValueReference") and\
                            outputParam=="ComplexOutput") or\
                            \
                            (output.has_key("ComplexValue") and\
                            outputParam=="ComplexOutput") or \
                            \
                            (output.has_key("BoundingBoxValue") and\
                            outputParam=="BoundingBoxOutput"):

                            if output.has_key("ComplexValue"):
                                key = "ComplexValue"
                            elif output.has_key("ComplexValueReference"):
                                key = "ComplexValueReference"
                            elif output.has_key("LiteralValue"):
                                key = "LiteralValue"
                            elif output.has_key("BoundingBoxValue"):
                                key = "BoundingBoxValue"
                            self.outputDataStructure(
                                    outputSett['elements'][outputParam],
                                    output[key],
                                    outputNode,key,
                                    )
                    except KeyError, what:
                        #print "KeyError: ",what
                        pass
                else: # append 'normal' node
                    self.Append.Node(
                            document=self.document, 
                            childNode=outputParam, 
                            parentNode=outputNode,
                            Elements=outputSett['elements'], 
                            Values=output
                            )
        return 

    def inputDataStructure(self,inputStruct,processInput,parent,inputtype,input):
        """
        Creates the "ComplexData" structure - see table 19 in WPS 0.4.0

        inputStruct         one of ProcessInputs structure (LiteralData, BBoxData or ComplexData)
        processInput        configuration structure
        parrent             parrent node, to which is everything appended
        inputtype           one of 'LiteralData', 'BoundingBoxData', 'ComplexData' text string
        input               the whole intpu structure
        """
        # <ComplexData>
        if inputtype == "ComplexValue" or \
                inputtype == "ComplexValueReference":
            complexdata = self.document.createElement("ComplexData")

            # <ComplexData defaultFormat="?" >
            try:
                complexdata.setAttribute("%s%s" %\
                        (inputStruct['ns'],"defaultFormat"), \
                        processInput['Formats'][0])
            except IndexError:
                complexdata.setAttribute("%s%s" %\
                        (inputStruct['ns'],"defaultFormat",
                        inputStruct['attributes']['defaultFormat']['default']
                        ))
            parent.appendChild(complexdata)

            # compile every format in configuration structure, append
            for format in processInput['Formats']:
                supportedComData = self.document.createElement("%s%s" %\
                        (inputStruct['elements']['SupportedComplexData']['ns'],
                        "SupportedComplexData"))
                node = self.document.createElement("%s%s" %\
                        (inputStruct['elements']['SupportedComplexData']['elements']['Format']['ns'],\
                        "Format"))
                text = self.document.createTextNode(format)
                node.appendChild(text)
                supportedComData.appendChild(node)
            complexdata.appendChild(supportedComData)

        # <LiteralData>
        elif inputtype == "LiteralValue":
            literaldata = self.document.createElement("%s%s" %\
                    (inputStruct['ns'],"LiteralData"))

            parent.appendChild(literaldata)

            # for each Node in LiteralData structure
            for litData in inputStruct['order']:
                if litData == "LiteralValues":

                    # anyvalue
                    if not processInput.has_key('values') or "*" in processInput['values']:
                        valueNode = self.document.createElement("%s%s" %\
                            (inputStruct['elements']['LiteralValues']['elements']['AnyValue']['ns'],
                            "AnyValue"))
                        literaldata.appendChild(valueNode)

                    # allowed values
                    else:
                        valueNode = self.document.createElement("%s%s" %\
                            (inputStruct['elements']['LiteralValues']['elements']['AllowedValues']['ns'],
                            "AllowedValues"))
                        literaldata.appendChild(valueNode)
                        # allowed values
                        if not type(processInput['values'][0]) == type([]):
                            for val in processInput['values']:
                                value = self.document.createElement("Value")
                                value.appendChild(self.document.createTextNode(str(val)))
                                valueNode.appendChild(value)
                        # ranges
                        # NOTE: only basic suport - just min and max values
                        else:
                            for vals in processInput['values']:
                                rangenode = self.document.createElement("Range")
                                minnode = self.document.createElement("MinimumValue")
                                minnode.appendChild(self.document.createTextNode(str(min(vals))))
                                maxnode = self.document.createElement("MaximumValue")
                                maxnode.appendChild(self.document.createTextNode(str(max(vals))))
                                rangenode.appendChild(minnode)
                                rangenode.appendChild(maxnode)
                                valueNode.appendChild(rangenode)



                    continue

                # append supported values
                elif litData == "SupportedUOMs":
                    self.supportedUOMsElement(literaldata, processInput,
                                inputStruct)
                    continue

                # default values
                if litData == "DefaultValue":
                    if input.has_key('value') and \
                            input['value'] != None:

                        defaultValue = self.document.createElement("%s%s" %\
                            (inputStruct['elements']['DefaultValue']['ns'],
                            "DefaultValue"))
                        defaultValue.appendChild(
                                self.document.createTextNode(str(input['value'])))
                        literaldata.appendChild(defaultValue)
                    continue

                else: # other 'normal' node will be appended
                    self.Append.Node(
                            document=self.document, 
                            childNode=litData, 
                            parentNode=literaldata,
                            Elements=inputStruct['elements'],
                            Values=processInput
                            )

        # <BoundingBoxData> not implemented
        elif inputtype == "BoundingBoxValue":
            bboxNode = self.document.createElement("%s%s" %\
                    (inputStruct['ns'],"BoundingBoxData"))
            bboxNode.setAttribute("defaultCRS","")
            crsNode = self.document.createElement("CRS")
            bboxNode.appendChild(crsNode)

            parent.appendChild(bboxNode)

            pass

        return

    def outputDataStructure(self,outputStructure,processOutput,parent,outputtype):
        """
        Creates the "ComplexData" structure - see table 19 in WPS 0.4.0
        
        outputStructure     one of ProcessInputs structure (LiteralData, BBoxData or ComplexData)
        processOutput       structure with process output from conf. file
        parent              parent node, to which is everything appended
        outputtype          one of 'LiteralData', 'BoundingBoxData', 'ComplexData' text string
        """

        # <ComplexData>
        if outputtype == "ComplexValue" or \
           outputtype == "ComplexValueReference":

            complexdata = self.document.createElement("%s%s" %\
                    (outputStructure['ns'],"ComplexOutput"))
            parent.appendChild(complexdata)
            
            # <ComplexData defaultFormat="?" >
            try:
                complexdata.setAttribute("%s%s" %\
                        (outputStructure['ns'],"defaultFormat"), processOutput['Formats'][0])
            except (IndexError,AttributeError):
                complexdata.setAttribute("defaultFormat", "text/XML")

            # compile every format in configuration structure, append
            supportedComData = self.document.createElement("SupportedComplexData")
            for format in processOutput['Formats']:
                node = self.document.createElement("Format")
                text = self.document.createTextNode(format)
                node.appendChild(text)
                supportedComData.appendChild(node)
            complexdata.appendChild(supportedComData)

        ## LiteralData
        elif outputtype == "LiteralValue":
            literaldata = self.document.createElement("LiteralOutput")
            parent.appendChild(literaldata)

            # for each 'LiteralOutput':{'UOMs':["meters","hectars","kilograms"]}
            self.supportedUOMsElement(literaldata, processOutput,
                    outputStructure)

 
        ## BoundingBoxData not implemented
        elif outputtype == "BoundingBoxValue":
            bboxNode = self.document.createElement("BoundingBoxOutput")
            bboxNode.setAttribute("defaultCRS","")
            crsNode = self.document.createElement("CRS")
            bboxNode.appendChild(crsNode)
            parent.appendChild(bboxNode)
        return

    def supportedUOMsElement(self, parent, litvalue, outputStructure):
        """
        Creates <SuppotedUOMs> tag with it's subelements
        
        parent  - parent xml tag
        litvalue - literaloutput process structure 
        outputStructure  - definition of literaloutput structure (from  ogc/describeprocess.py)
        """

        supportedUOMs = self.document.createElement("%s%s" % \
                (outputStructure['elements']['SupportedUOMs']['ns'],"SupportedUOMs"))
        
        # uoms here?
        if litvalue.has_key('UOMs'):

            supportedUOMs.setAttribute("%s%s" % \
                    (outputStructure['elements']['SupportedUOMs']['attributes']['defaultUOM']['ns'],\
                    "defaultUOM"), litvalue['UOMs'][0])

            # for each UOM, make tag
            for uom in litvalue['UOMs']:
                UOM = self.document.createElement("%s%s" % \
                        (outputStructure['elements']['SupportedUOMs']['elements']['UOM']['ns'],\
                        "UOM"))
                supportedUOMs.appendChild(UOM)
                UOM.appendChild(self.document.createTextNode(uom))

                
        # no uoms, take the default value
        else:
            supportedUOMs.setAttribute("%s%s" % \
                    (outputStructure['elements']['SupportedUOMs']['attributes']['defaultUOM']['ns'],\
                    "defaultUOM"),
                    outputStructure['elements']['SupportedUOMs']['attributes']['defaultUOM']['default'])
        parent.appendChild(supportedUOMs)

