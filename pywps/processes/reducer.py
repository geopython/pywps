"""
GeoTiff reducer

Author: Jorge de Jesus (jmdj@pml.ac.uk) WPS/Script
        Stephane Saux-Picart (stux@pml.ac.uk) interpolation script

"""
import types

from numpy import *
import numpy as np
from numpy import ma
#from functionASCII import loadtxtfile as ltf
#import shelve as S
import os
#from matplotlib.numerix.ma import *

from osgeo import gdal

#from matplotlib.numerix.ma import *
#from RandomArray import *
#from pylab import *
import tempfile

def Bin(array_in, size_out, bin_map=None,method=None):
   """ Resize an array from high resolution to low resolution
         array    : input 2D array (can be a masked array)
         size_out : [x, y] where x and y are the dimension of the output array
                          must be smaller than the original dimensions
         method   : default is averaging (No others for the moment).
         bin_map  : [string] should refer to a map of indices for binning.
                         if the file exists then it will use this map rather than recalculate
                         if it does not then it will save the map to the filename given
   """
   
   # Get the size of the input array
   in_size = array_in.shape

   # Test the dimension of arrays
   if ((in_size[0] < size_out[0]) or (in_size[1] < size_out[1])):
      raise ValueError, "Size of the input array is greater than "+str(in_size)+" : "+str(size_out)
   
   # Create 2 vectors containing indices of the input array
   x_in = array(range(in_size[0]))
   y_in = array(range(in_size[1]))
   
   
   x_fac = float(in_size[0])/float(size_out[0])
   y_fac = float(in_size[1])/float(size_out[1])

   # Initialize an empty array with wanted size and a count array used for 
   # averaging
   array_out = zeros([size_out[0],size_out[1]])
   aout_count = zeros([size_out[0],size_out[1]])
   
   #print "Reducing size from "+str(in_size)+" to "+str(size_out)
   
   # Check for existence of binning map and whether it is useable
   use_map=False
   if bin_map and os.path.exists(bin_map):
      map=ltf(bin_map,dtype='int')
      try:
         map=map.reshape(in_size[0],in_size[1],2)
         use_map=True
      except:
         raise 'Warning: Binning map incorrect shape: Ignoring it'
         
    
   # Bin input array, using map if possible.  Using map is ugly, ugly code.
   # Could use changing.
   if use_map:
      # Loop over input array to build up output array
      for i in range(in_size[0]):
         for j in range(in_size[1]):
            if array_in.mask.shape == ():
               array_out[map[i,j,0],map[i,j,1]]=array_out[map[i,j,0],map[i,j,1]]+\
                                                array_in[i,j]
               aout_count[map[i,j,0],map[i,j,1]]=aout_count[map[i,j,0],map[i,j,1]]+1
            else:
               if not array_in.mask[i,j]:
                  array_out[map[i,j,0],map[i,j,1]]=array_out[map[i,j,0],map[i,j,1]]+\
                                                   array_in[i,j]
                  aout_count[map[i,j,0],map[i,j,1]]=aout_count[map[i,j,0],map[i,j,1]]+1
      # Loop finished, now mean array
      array_out=array_out/aout_count
      array_out=ma.masked_where(aout_count==0,array_out)
   else: 
      # Create binning map if file specified
      if  bin_map:
         map=zeros([in_size[0],in_size[1],2])
      # Loop through every element of the output array
      for i in range(size_out[0]):
         for j in range(size_out[1]):
            xbin1 = i*x_fac
            xbin2 = (i+1)*x_fac
            ybin1 = j*y_fac
            ybin2 = (j+1)*y_fac
            indx = nonzero((x_in >= xbin1)*(x_in < xbin2))
            indy = nonzero((y_in >= ybin1)*(y_in < ybin2))
            indx = x_in[indx]
            indy = y_in[indy]
            
            # Extract bin value and average them
            extract = array_in[indx[0]:indx[-1]+1,indy[0]:indy[-1]+1]
            temp_mean = extract.mean()
            if bin_map:
               map[indx[0]:indx[-1]+1,indy[0]:indy[-1]+1,:]=[i,j]

            if method == "mask":
               if extract.mean() == 1:
                  array_out[i,j] = 1
               else:
                  array_out[i,j] = 0
            else:
               if extract.mean() > 0: # problems here for respiration binning
                  array_out[i,j] = temp_mean
               else:
                  array_out[i,j] = -999
            # end if
         #end of j loop
      # end of i loop
      
      # Mask non-valid value
      #array_out = ma.masked_values(array_out,-999)
      
      #Changed so that it is returned a normall array and not masked
      array_out=array_out
      
##   if (array_out==array_out2).all():
##      print 'IT WORKED!!!'
##   else:
##      print 'IT FAILED'
      # Write to binning map if file specified
      if  bin_map:
         fid=open(bin_map,'w')
         for i in range(in_size[0]):
            for j in range(in_size[1]):
               fid.write(' %04d %04d' %(map[i,j,0],map[i,j,1]))
            fid.write('\n')
         fid.close()
   return array_out
   
# end of fuction Bin
def resize(imageInPath,imageOutPath,reductionPer):
 
   format = "GTiff"
   driver = gdal.GetDriverByName( format )
   
   
   imageIn=gdal.Open(imageInPath)
   print "Image size Y:%s  X:%s" % (imageIn.RasterYSize,imageIn.RasterXSize)
   #imageIn.RasterXSize


   #Attention that out_size should be (Y,X)
   out_size = (int(floor(float(imageIn.RasterYSize)*reductionPer)),int(floor(float(imageIn.RasterXSize)*reductionPer)))
   
   print "Out size Y:%s X:%s" % out_size
   #map(lambda x: x*0.5,out_size)
   #map(round,out_size)
   
   
   rasterType=imageIn.GetRasterBand(1).DataType
   imageOut = driver.Create(imageOutPath,out_size[1],out_size[0], imageIn.RasterCount, rasterType )
   imageOut.SetProjection(imageIn.GetProjection())
   
   #This is not 100% correct
   GeoTransIn=imageIn.GetGeoTransform()
   GeoTansOut=[GeoTransIn[0],GeoTransIn[1]/reductionPer,GeoTransIn[2],GeoTransIn[3],GeoTransIn[4],GeoTransIn[5]/reductionPer]
   imageOut.SetGeoTransform(GeoTansOut)
   
   for nBand in xrange(1,imageIn.RasterCount+1):
       sample_array=imageIn.GetRasterBand(nBand).ReadAsArray()
       nullValueGDAL=imageIn.GetRasterBand(nBand).GetNoDataValue()
       #sample_array[sample_array==nullValueGDAL]=np.nan
       sample_array[sample_array==nullValueGDAL]=np.nan
       out_sample_array = Bin(sample_array,out_size)
       out_sample_array[out_sample_array==-999.000]=nullValueGDAL
       imageOut.GetRasterBand(nBand).WriteArray(out_sample_array)
       
       imageOut.GetRasterBand(nBand).SetNoDataValue(nullValueGDAL)
   imageOut=None
       
   return None




from pywps.Process import WPSProcess
class Process(WPSProcess):
      def __init__(self):
           WPSProcess.__init__(self,
           identifier = "reducer",
           title="Geotiff sizer reducer",
           version = "0.1",
           abstract="GDAL and Numpy code that will reduze the dimension of a satelite image by using a mean calculation of values",
           storeSupported = "true",
           statusSupported = "true")
           
           self.reductionFactor=self.addLiteralInput(identifier = "reductionFactor",
                                                     title = "Reduction factor (fraction)",
                                                     abstract="Reduction factor between 0 and 1.0 that will be use do reducec the image",
                                                     minOccurs=1,
                                                     type=types.FloatType,
                                                     allowedValues=("*")
                                                     )
                                               #      default=0.5)
           self.imageIn=self.addComplexInput(identifier="imageInput",
                                              title="Geotiff input",
                                              abstract="Image that will be reduced",
                                              formats=[{"mimeType": "image/tiff"}]
                                            )
           
           self.imageOut=self.addComplexOutput(identifier="imageOutput",
                                               title="Geotiff output",
                                               abstract="Reduced image",
                                               formats=[{"mimeType": "image/tiff"}]
                                               )
                                                     
      
      
      def execute(self):
              #Gettint inputs
             #http://localhost/wps.cgi?request=Execute&service=wps&version=1.0.0&identifier=reducer&datainputs=[reductionFactor=0.5;imageInput=http://localhost/tmp2.tif]&responsedocument=imageOutput=@asreference=true
     
         
              imageInPath=self.imageIn.getValue()
 
              tmpFile=tempfile.NamedTemporaryFile(suffix='.tif', prefix='tmp',delete=False)
              
              reductionFactor=self.reductionFactor.getValue()
              
              resize(imageInPath,tmpFile.name,reductionFactor)
              self.imageOut.setValue(tmpFile.name)
              
              
                  