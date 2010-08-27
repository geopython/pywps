from pywps.Process import WPSProcess

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from osgeo import gdal 

def subPlotNumber(nBands):
    nCols=3
    nRows=float(nBands)/float(nCols)
    nRows=int(np.ceil(nRows))
    pos=str(nRows)+str(nCols)
    for nGraph in range(1,(nCols*nRows)+1):
        yield int(pos+str(nGraph))
        

def histOutline(dataIn, *args, **kwargs):
        (histIn, binsIn) = np.histogram(dataIn, *args, **kwargs)
        stepSize = binsIn[1] - binsIn[0]
        bins = np.zeros(len(binsIn)*2 + 2, dtype=np.float)
        data = np.zeros(len(binsIn)*2 + 2, dtype=np.float)#
        for bb in range(len(binsIn)):
                bins[2*bb + 1] = binsIn[bb]
                bins[2*bb + 2] = binsIn[bb] + stepSize
                if bb < len(histIn):
                    data[2*bb + 1] = histIn[bb]
                    data[2*bb + 2] = histIn[bb]

        bins[0] = bins[1]
        bins[-1] = bins[-2]
        data[0] = 0
        data[-1] = 0 
        return (bins, data)



class Process(WPSProcess):
      def __init__(self):
           WPSProcess.__init__(self,
           identifier = "histogramprocess",
           title="Sat image histogram generator",
           version = "0.1",
           abstract="Histogram generator from Sat image",
           storeSupported = "true",
           statusSupported = "true")
           
           self.imageIn=self.addComplexInput(identifier="imageInput",
                                              title="Geotiff input",
                                              abstract="Image that will be reduced",
                                              formats=[{"mimeType": "image/tiff"}]
                                            )
           
           self.imageOut=self.addComplexOutput(identifier="histogramOutput",
                                               title="Histogram image",
                                               abstract="PNG image with histogram",
                                               formats=[{"mimeType": "image/png"}]
                                               )
                                                     
      
      
      def execute(self):
      
      		#http://localhost/wps.cgi?request=Execute&service=wps&version=1.0.0&identifier=histogramprocess&datainputs=[imageInput=http://localhost/tmp2.tif]&responsedocument=imageOutput=@asreference=true
      
           	####config####
           	nCols=3
           	Xsize=12
           	wspa=0.4
           	hspa=0.4
           	#############
           	
      		imageInPath=self.imageIn.getValue()
      		imageIn=gdal.Open(imageInPath)
      		nRows=np.ceil(float(imageIn.RasterCount)/float(nCols))
    		Ysize=(3*nRows)+2
    		plt.figure(figsize=(Xsize,Ysize))
    		plt.subplots_adjust(wspace=wspa)
    		plt.subplots_adjust(hspace=hspa)
    		
    		subPlotNumberGen=subPlotNumber(imageIn.RasterCount)
    		for idx,nBand in enumerate(xrange(1,imageIn.RasterCount+1)):
        		dataArray=imageIn.GetRasterBand(nBand).ReadAsArray()
        		nullValueGDAL=imageIn.GetRasterBand(nBand).GetNoDataValue()
        		dataArray=dataArray.ravel() #flatten array
        		dataArray=dataArray[dataArray!=nullValueGDAL] #remove nulls
        		subplot=subPlotNumberGen.next()
        		plt.subplot(subplot)
        		plt.hist(dataArray,bins=100,normed=True)
        		plt.title("Band number:%s" % str(idx+1))
        	 
        	plt.suptitle('Band histogram of %s' % imageInPath)
        	plt.savefig("/tmp/histo.png")
        	
        	self.imageOut.setValue("/tmp/histo.png")
      		
		
			
			