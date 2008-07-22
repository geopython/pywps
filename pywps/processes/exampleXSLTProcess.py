"""Example PyWPS process

Demonstration of XSLT XML transformation, support for internationalization
and BoundingBox output value
"""
# Author: Jachym Cepicky <jachym.cepicky gmail.com>

import os,time,string,sys
from pywps.Process.Process import WPSProcess

class Process(WPSProcess):

    def __init__(self):
        """Process initialization"""

        # initializa the process with minimal inputs
        # in this case, only process identifier is really needed
        WPSProcess.__init__(self,"exampleXSLTProcess")

        # set messages in different languages
        self.lang.strings["eng"]["title"] = "Translator"
        self.lang.strings["ger"]["title"] = "Umwanlder"

        self.lang.strings["eng"]["abstract"] = "Translate given GML file according to given XSLT template"
        self.lang.strings["ger"]["abstract"] = "Leitet input GML nach input XSLT um"

        self.lang.strings["eng"]["gml"] = "Input GML data"
        self.lang.strings["ger"]["gml"] = "Input GML daten"

        self.lang.strings["eng"]["xslt"] = "Input XSLT Template"
        self.lang.strings["ger"]["xslt"] = "Input XSLT Schablone"

        self.lang.strings["eng"]["gmlOut"] = "Output processed GML file"
        self.lang.strings["ger"]["gmlOut"] = "Output verarbeitate GML Datei"

        self.lang.strings["eng"]["error.outputNotCreated"] = "Output file not created"
        self.lang.strings["ger"]["error.outputNotCreated"] = "Output Datei nicht erzeugt worden"

        self.lang.strings["eng"]["bboxOut.abstract"] = "Estimated bounding box of the output fileoutput"
        self.lang.strings["ger"]["bboxOut.abstract"] = "Bounding box fuer Output Daten"

        # call the method for later process initialization with translated
        # strings
        self.initProcess(title= self.i18n("title"),
            version = "0.1",
            storeSupported = "true",
            statusSupported = "true",
            abstract= self.i18n("abstract"))

        # define in- and outputs
        self.gmlIn = self.addComplexInput(identifier="gml",
                             title = self.i18n("gml"))

        self.xsltIn = self.addComplexInput(identifier = "xslt",
                             title = self.i18n("xslt"))

        self.gmlOut = self.addComplexOutput(identifier="gml",
                                title=self.i18n("gmlOut"))

        self.bboxOut = self.addBBoxOutput(identifier="bbox",
                                title=self.i18n("bboxOut"),
                                abstract=self.i18n("bboxOut.abstract"))

    def execute(self):
        """Execute process"""

        # set status
        self.status.set("Processing data",1)

        # call the xslt transformation tool
	self.cmd("/usr/bin/java -jar /usr/local/saxon/saxon9.jar -o output.gml %s %s" %\
	(self.getInputValue("gml"), self.getInputValue("xslt")))

        # set first output
        self.gmlOut.setValue("output.gml")
        
        # get the bounding box of the transformation result using ogr tools
        self.status.set("Estimating bounding box",75)

        # call another method for estimating extent
        extent = self.getBBox("output.gml")
        self.bboxOut.setValue(extent)

    def getBBox(self,file):
        """Get bounding box of given vector file. 
        
        The attributes are mined using python-gdal bindings
        
        """
        # NOTE: this could be done by standard shell functions as well
        # but this is more elegant way
        # see
        # http://trac.osgeo.org/gdal/wiki/GdalOgrInPython
        # and
        # http://trac.osgeo.org/gdal/browser/trunk/gdal/swig/python/samples/val_repl.py
        # example for more details

        import osgeo
        from osgeo import ogr

        ogrdatafile = ogr.Open(file)
        layer = ogrdatafile.GetLayerByIndex(0)
        extent = layer.GetExtent()

        return extent
        
