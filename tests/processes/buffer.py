"""
OGR Buffer process

Author: Jachym Cepicky (jachym@les-ejk.cz) 
"""

from pywps.Process import WPSProcess                                
from osgeo import ogr
import os

class Process(WPSProcess):
     def __init__(self):
          # init process
         WPSProcess.__init__(self,
              identifier = "ogrbuffer", # must be same, as filename
              title="Buffer process using OGR",
              version = "0.1",
              storeSupported = "true",
              statusSupported = "true",
              abstract="Process demonstrating how to work with OGR inside PyWPS")
              
         self.data = self.addComplexInput(identifier = "data",
                                            title = "Input vector file")
         self.size = self.addLiteralInput(identifier="size", 
                                           title="Buffer area size",
                                           allowedValues = [[-10000,10000]])
         self.output =self.addComplexOutput(identifier="buffer", 
                                            title="Buffered data",
                                            useMapscript=True)
     def execute(self):


        # open the input file
        try:
            inSource = ogr.Open(self.data.getValue())
        except Exception,e:
            return "Could not open given vector file: %s" % e

        inLayer = inSource.GetLayer()
        out = inLayer.GetName()

        # create output file
        driver = ogr.GetDriverByName('GML')
        outSource = driver.CreateDataSource(out, ["XSISCHEMAURI=http://schemas.opengis.net/gml/2.1.2/feature.xsd"])
        outLayer = outSource.CreateLayer(out,None,ogr.wkbUnknown)

        # for each feature
        featureCount = inLayer.GetFeatureCount()
        index = 0

        while index < featureCount:
            self.status.set("Calculating buffer for feature %d from %d" % (index+1,featureCount),
                    (100*(index+1)/featureCount*1.0))

            # get the geometry
            inFeature = inLayer.GetNextFeature()
            inGeometry = inFeature.GetGeometryRef()

            # make the buffer
            buff = inGeometry.Buffer(10000)

            # create output feature to the file
            outFeature = ogr.Feature(feature_def=outLayer.GetLayerDefn())
            outFeature.SetGeometryDirectly(buff)
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy()
            index = index +1
        
        self.output.setValue(out)
        return
