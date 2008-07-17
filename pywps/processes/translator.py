# Author: Jachym Cepicky <jachym.cepicky@gmail.com>

import os,time,string,sys
from pywps.Process import WPSProcess

class Process(WPSProcess):

    def __init__(self):
        WPSProcess.__init__(self,"translator")

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

        self.initProcess(title= self.i18n("title"),
            version = "0.1",
            storeSupported = "true",
            statusSupported = "true",
            abstract= self.i18n("abstract"))


        self.gmlIn = self.addComplexInput(identifier="gml",
                             title = self.i18n("gml"))

        self.xsltIn = self.addComplexInput(identifier = "xslt",
                             title = self.i18n("xslt"))

        self.gmlOut = self.addComplexOutput(identifier="gml",
                                title=self.i18n("gmlOut"),
				asReference=True)

    def execute(self):

        self.status.set("Processing data",1)

	self.cmd("/usr/bin/java -jar /usr/local/saxon/saxon9.jar -o output.gml %s %s" %\
	(self.getInputValue("gml"), self.getInputValue("xslt")))
        
        if "output.gml" in os.listdir(os.curdir):
            self.gmlOut.setValue("output.gml")
            return
        else:
            return self.i18n("error.outputNotCreated")
