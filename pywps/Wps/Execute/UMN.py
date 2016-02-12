# Author:	Jachym Cepicky
#        	http://les-ejk.cz
#               jachym at les-ejk dot cz
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


from pywps import config
import os
import urllib2
import logging

LOGGER = logging.getLogger(__name__)

mapscript=False
gdal=False
try:
    from mapscript import *
    mapscript=True
except Exception,e:
    mapscript=False
    LOGGER.info("MapScript could not be loaded, mapserver not supported: %s" %e)

try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except Exception,e:
    gdal=False
    LOGGER.info("osgeo package could not be loaded, mapserver not supported: %s" %e)




class UMN:
    """
    UMN MapServer Mapscript handler

    :param id: Integer process id

    .. attribute :: mapObj

        mapObject
        
    .. attribute :: mapFileName

        map file name

    .. attribute :: mapFileName

        map file name

    .. attribute :: sessionId

        process id from getSessionId()

    .. attribute :: dataset

        gdal.dataset or ogr.dataset

    .. attribute :: outputs

        associative array of outputs

    .. attribute :: process

        :class:`pywps.Process.WPSProcess`
    """

    mapObj = None
    mapFileName = None
    outputs = None
    process = None
    sessionId = None

    def __init__(self,process,sessId):

        if ((mapscript == False) or (gdal== False)):
            return
        
        self.outputs = {}
        self.process = process
        self.sessionId = sessId
        self.projs=self.getProjs()
        self.mapObj = mapObj()
        self.mapObj.setExtent(-180,-90,180,90)# irrelevant for WCS/WFS
        #self.mapObj.setProjection("+init=%s" % self.projs[0])
        self.mapObj.name = "%s-%s"%(self.process.identifier,self.sessionId)
        self.mapObj.setMetaData("ows_title", config.getConfigValue("wps","title"))
        self.mapObj.setMetaData("wms_abstract", config.getConfigValue("wps","abstract"))
        self.mapObj.setMetaData("wcs_abstract", config.getConfigValue("wps","abstract"))
        self.mapObj.setMetaData("wcs_label", process.title)
        self.mapObj.setMetaData("wfs_abstract", config.getConfigValue("wps","abstract"))
        self.mapObj.setMetaData("ows_keywordlist", config.getConfigValue("wps","keywords"))
        self.mapObj.setMetaData("ows_fees", config.getConfigValue("wps","fees"))
        self.mapObj.setMetaData("ows_accessconstraints", config.getConfigValue("wps","constraints"))
        self.mapObj.setMetaData("ows_contactorganization", config.getConfigValue("provider","providerName"))
        self.mapObj.setMetaData("ows_contactperson", config.getConfigValue("provider","individualName"))
        self.mapObj.setMetaData("ows_contactposition", config.getConfigValue("provider","positionName"))
        self.mapObj.setMetaData("ows_enable_request", "*")
        self.mapObj.debug = 5
        self.mapObj.setConfigOption("MS_ERRORFILE", "stderr")
        
        phone =  config.getConfigValue("provider","phoneVoice")
        if phone:
            self.mapObj.setMetaData("ows_contactvoicetelephone", config.getConfigValue("provider","phoneVoice"))
        phone = config.getConfigValue("provider","phoneFacsimile")
        if phone:
            self.mapObj.setMetaData("ows_contactfacsimiletelephone", config.getConfigValue("provider","phoneFacsimile"))
        self.mapObj.setMetaData("ows_address", config.getConfigValue("provider","deliveryPoint"))
        self.mapObj.setMetaData("ows_city", config.getConfigValue("provider","city"))
        self.mapObj.setMetaData("ows_country", config.getConfigValue("provider","country"))
        self.mapObj.setMetaData("ows_postcode", config.getConfigValue("provider","postalCode"))
        self.mapObj.setMetaData("ows_contactelectronicmailaddress", config.getConfigValue("provider","electronicMailAddress"))
        self.mapObj.setMetaData("ows_role", config.getConfigValue("provider","role"))

        self.mapFileName = os.path.join(config.getConfigValue("server","outputPath"),self.sessionId+".map")
        self.mapObj.setMetaData("wms_onlineresource",config.getConfigValue("mapserver","mapserveraddress")+"?map="+self.mapFileName)

    def getReference(self,output):
        """Get reference URL for given output

        :param output: :class:`pywps.Process.InAndOutputs.ComplexOutput`
        
        :rtype: String
        :returns: URL pointing to OGC OWS (WCS/WFS)
        """
        # try to determine the data type
        #need to silence error like: ERROR 4: `/var/www/html/wpsoutputs/vectorout-24363CH3zxi' not recognised as a supported file format.
        #caused by wrong opendataset from gdal or ogr
        datatype = self.getDataset(output)
        
        if not datatype:
            return None

        # get projection and bounding box
        if  not output.bbox:
            output.bbox = self.getBBox(output,datatype)


        myLayerObj = layerObj(self.mapObj)
        myLayerObj.group = self.process.identifier
        myLayerObj.dump = MS_TRUE

        # raster is no problem
        if datatype == "raster":
            myLayerObj.type = MS_LAYER_RASTER
            myLayerObj.data = output.value
            myLayerObj.setMetaData("wcs_label", output.title)
            myLayerObj.setMetaData("wcs_rangeset_name","Range 1")
            myLayerObj.setMetaData("wcs_rangeset_label","My Label")
        # vector has to be point,line,polygon
        # determine this from the first found feature from the first layer
        else:
            myLayerObj.setConnectionType(MS_OGR,output.value)
            myLayerObj.connection = output.value
            myLayerObj.setMetaData("wfs_title", output.title)
            myClassObj=classObj(myLayerObj)
            myStyleObj=styleObj(myClassObj)
            myLayerObj.setMetaData("wfs_title", output.title)
            myLayerObj.setMetaData("gml_featureid","ID")
            myLayerObj.setMetaData("gml_include_items","all")

            layer = self.dataset.GetLayer()
            feature = layer.GetNextFeature()
            geometry = feature.GetGeometryRef()

            myLayerObj.data = layer.GetName()

            if geometry.GetGeometryName().lower() in ["point","multipoint"]:
                myLayerObj.type = MS_LAYER_POINT
                myStyleObj.color.setRGB(0,0,0)
            else:
                myStyleObj.outlinecolor= colorObj(134,81,0)
                myStyleObj.color= colorObj(238,153,0)
                myStyleObj.size=5
                myStyleObj.width=5
                if geometry.GetGeometryName().lower() in ["linestring","multilinestring"]:
                    myLayerObj.type = MS_LAYER_LINE
                elif geometry.GetGeometryName().lower() in ["polygon", "multipolygon"]:
                    myLayerObj.type = MS_LAYER_POLYGON
                else:
                    myLayerObj.type = MS_LAYER_POINT

            #elif geometry.GetGeometryName().lower() in ["line","linestring"]:
            #    myLayerObj.type = MS_LAYER_LINE
            #    myStyleObj.color.setRGB(0,0,0)
            #elif geometry.GetGeometryName().lower() == "polygon":
            #    myLayerObj.type = MS_LAYER_POLYGON
            #    myStyleObj.outlinecolor.setRGB(0,0,0)

        if self.process.abstract:
            myLayerObj.setMetaData("group_abstract",self.process.abstract)
        if output.abstract:
            myLayerObj.setMetaData("wcs_abstract", output.abstract)
            myLayerObj.setMetaData("wfs_abstract", output.abstract)
        myLayerObj.name = output.identifier

        # either the output has projection already, use it
        
        
        if output.projection:
            #output.projection=epsg:4326,epsg:102067,epsg:3059,epsg:900913 like cfg file
            firstEPSG=output.projection.lower().split(",")[0]
            myLayerObj.setProjection(firstEPSG)
        else:
            #do we have info from self.projs
            if len(self.projs)>0:
                myLayerObj.setProjection(self.projs[0])
            else:
            # try to determine dataset projection using gdal/ogr
                spatialReference = self.getSpatialReference(output,datatype)
                if spatialReference:
                    
                    if spatialReference.IsProjected():
                        authority = spatialReference.GetAuthorityName("PROJCS")
                        code = spatialReference.GetAuthorityCode("PROJCS")
                    else:
                        authority = spatialReference.GetAuthorityName("GEOGCS")
                        code = spatialReference.GetAuthorityCode("GEOGCS")
                        #authority = spatialReference.GetAuthorityName("PROJCS")
                        #code = spatialReference.GetAuthorityCode("PROJCS")

                # we are able to construct something like "epsg:4326"
                    if authority and code:
                        myLayerObj.setProjection("init=%s:%s"% (authority.lower(),code))
                      
                # we will have at least PROJ4 parameters, but no
                # AUTHORITY:CODE, the dataset will obtain projection from
                # the map object
        
        #setting wfs_srs, wms_srs and wcs_srs
        if output.projection:
                epsgList=output.projection.split(",")
                ows_srs=" ".join(epsgList).upper()
                output.projection=epsgList[0]
        else: 
            #check for output.projection
            if len(self.projs)>0:
                ows_srs=" ".join(self.projs).upper()
                output.projection=self.projs[0]
            else:
                #try to get from data otherwise give up on it
                if ("authority" and "code" in locals()) and (authority and code):
                    ows_srs=authority.upper()+":"+code
                    output.projection=authority.upper()+":"+code  
       #if we have ows_srs then set it
        if "ows_srs" in locals():
            myLayerObj.setMetaData("ows_srs",ows_srs)
                  
        if datatype == "raster":
            return self.getMapServerWCS(output)
            myLayerObj.type = MS_LAYER_RASTER
        # make it WFS
        else:
            return self.getMapServerWFS(output)


    def getDataset(self,output):
        """
        :param output: :class:`pywps.Process.InAndOutputs.ComplexOutput`
        :returns: "raster" or "vector"
        """

        LOGGER.debug("Importing given output [%s] using gdal" % output.value)
        #If dataset is XML it will make an error like ERROR 4: `/var/www/html/wpsoutputs/vectorout-26317EUFxeb' not recognised as a supported file format.
        self.dataset = gdal.Open(output.value)

        if self.dataset:
            return "raster"

        if not self.dataset:
            LOGGER.debug("Importing given output [%s] using ogr" % output.value)
            self.dataset = ogr.Open(output.value)

        if self.dataset:
            return "vector"
        else:
            return None

    def getSpatialReference(self,output,datatype):
        """
        :param output: :class:`pywps.Process.InAndOutputs.ComplexOutput`
        :param datatype: String
        :return: projection of the output
        """

        sr = osr.SpatialReference()
        if datatype == "raster":
            wkt = self.dataset.GetProjection()
            res = sr.ImportFromWkt(wkt)
            if res == 0:
                return sr
        elif datatype == "vector":
            layer = self.dataset.GetLayer()
            ref = layer.GetSpatialRef()
            if ref:
                return ref
        return None

    def getBBox(self,output,datatype):
        """
        :param output: :class:`pywps.Process.InAndOutputs.ComplexOutput`
        :param datatype: String raster or vector
        :return: bounding box of the dataset
        """

        if datatype == "raster":
            geotransform = self.dataset.GetGeoTransform()
            if not output.height:
                output.height = self.dataset.RasterYSize
                output.width = self.dataset.RasterXSize
            return (geotransform[0],
                    geotransform[3]+geotransform[5]*self.dataset.RasterYSize,
                    geotransform[0]+geotransform[1]*self.dataset.RasterXSize,
                    geotransform[3])
        else:
            layer = self.dataset.GetLayer()
            return layer.GetExtent()

 
    def save(self):
        """Save the mapfile to disc"""
        if self.mapObj:
            self.mapObj.save(self.mapFileName)
    
    def getProjs(self):
        """Gets projections from config file and it returns a len=0 list if no projs present"""
        projs=config.getConfigValue("mapserver","projs").lower().split(",") #List with projs
        projs=[item for item in projs if 'epsg' in item] #cleaning a bit (specially from '')
        return projs

    def getMapServerWCS(self,output):
        """Get the URL for mapserver WCS request of the output"""
        return urllib2.quote(config.getConfigValue("mapserver","mapserveraddress")+
                "?map="+self.mapFileName+
                "&SERVICE=WCS"+ "&REQUEST=GetCoverage"+ "&VERSION=1.0.0"+
                "&COVERAGE="+output.identifier+"&CRS="+output.projection.replace("+init=","")+
                "&BBOX=%s,%s,%s,%s"%(output.bbox[0],output.bbox[1],output.bbox[2],output.bbox[3])+
                "&HEIGHT=%s" %(output.height)+"&WIDTH=%s"%(output.width)+"&FORMAT=%s"%output.format["mimetype"])

    def getMapServerWFS(self,output):
        """Get the URL for mapserver WFS request of the output"""
        return urllib2.quote(config.getConfigValue("mapserver","mapserveraddress")+
                "?map="+self.mapFileName+
                "&SERVICE=WFS"+ "&REQUEST=GetFeature"+ "&VERSION=1.0.0"+
                "&TYPENAME="+output.identifier)
