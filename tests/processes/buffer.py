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
              metadata=[{'title':'buffer' ,'href':"http://foo/bar"}],
              abstract="Process demonstrating how to work with OGR inside PyWPS: e.g: http%3A//localhost/wps.cgi%3Frequest%3DExecute%26service%3Dwps%26version%3D1.0.0%26identifier%3Dogrbuffer%26datainputs%3D%5Bdata%3Dhttp%3A//openlayers.org/dev/examples/gml/line.xml%3Bsize%3D0.1%5D%26responsedocument%3D%5Bbuffer%3D%40asreference%3Dtrue%5D")
              
         self.data = self.addComplexInput(identifier = "data",
                                            title = "Input vector file",
                                            formats = [{'mimeType': 'text/xml', 'schema': 'http://schemas.opengis.net/gml/2.1.2/feature.xsd', 'encoding': 'UTF-8'}],
                                            metadata=[{'title':'buffer' ,'href':"http://foo/bar"}])
         self.size = self.addLiteralInput(identifier="size", 
                                           title="Buffer area size",
                                           type=type(0.0),
                                           allowedValues = [[0,10000]],
                                           metadata=[{'title':'number','href':'http://integer'}])
         self.output =self.addComplexOutput(identifier="buffer", 
                                            title="Buffered data",
                                            formats = [{'mimeType': 'text/xml', 'schema': 'http://schemas.opengis.net/gml/2.1.2/feature.xsd', 'encoding': 'UTF-8'}],
                                            metadata=[{'title':'bufferOut','href':'http://buffer/out'}],
                                            useMapscript=True)
     def execute(self):

        ogr.UseExceptions()

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
        try:
            spatialRef = inLayer.GetSpatialRef().Clone()
        except:
            spatialRef = None
        outLayer = outSource.CreateLayer(out,srs=spatialRef,geom_type=ogr.wkbPolygon)

        # for each feature
        featureCount = inLayer.GetFeatureCount()
        index = 0

        while index < featureCount:
            #time.sleep(1) # making things little bit slower
            self.status.set("Calculating buffer for feature %d from %d" % (index+1,featureCount),
                    (100*(index+1)/featureCount*1.0))

            # get the geometry
            inFeature = inLayer.GetNextFeature()
            inGeometry = inFeature.GetGeometryRef()

            # make the buffer
            buff = inGeometry.Buffer(self.size.getValue())
            buff.AssignSpatialReference(spatialRef)

            # create output feature to the file
            outFeature = ogr.Feature(feature_def=outLayer.GetLayerDefn())
            outFeature.SetGeometryDirectly(buff)
            outLayer.CreateFeature(outFeature)

            #buff.Destroy()
            #outFeature.Destroy()
            index = index +1
        outLayer.SyncToDisk()
        self.output.setValue(out)
        return
