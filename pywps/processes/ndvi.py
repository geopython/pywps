#!/usr/bin/python
"""
pywps process example:

ndvi
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
# the Free Software Foundation; either version 2 of the License.
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

class Process:
#####################################################################
#
# Configuration part of the process
#
#####################################################################
    def __init__(self):
        # 
        # Mandatory parameters
        # 
        # Identifier - name of this process
        self.Identifier = "ndvi"
        # processVersion - version of this process
        self.processVersion = "0.1"
        # Title - title for this process
        self.Title="NDVI"
        self.Abstract = """
        Calculates normalized vegetation index: NDVI =(LANDSAT.4 - LANDSAT.3) / (LANDSAT.4 + LANDSAT.3)" or
        NDVI =(nir - red) / (nir + red)"

        """
        
        #
        # Inputs
        #
        self.Inputs = [
        
                # 0 input
                    {
                        'Identifier': 'landsat3',
                        'Title': 'Landsat 3',
                        'Abstract':'Channel 3 of LANDSAT TM (RED)',
                        'ComplexValueReference': {
                            'Formats':['image/tif','image/png'], # AllowedValues, AnyValue, ValuesReference
                        },
                        'dataType' : type(''), # you should set this for input params controll
                        'value':None,
                    },
                # 1 input
                    {
                        'Identifier': 'landsat4',
                        'Title': 'Landsat 4',
                        'Abstract':'Channel 4 of LANDSAT TM (NIR)',
                        'ComplexValueReference': {
                            'Formats':['image/tif','image/png'], # AllowedValues, AnyValue, ValuesReference
                        },
                        'dataType' : type(''), # you should set this for input params controll
                        'value':None,
                    },

                ]
        
        #
        # Output
        #
        self.Outputs = [
            {
               'Identifier': 'ndvi',
               'Title': 'NDVI',
               'ComplexValueReference': {'Formats':["image/tif"]},
               'value': 'ndvi.tif',
           },
        ]
        
        #
        # Optional attributes
        #
        #
        # storeSuport = "true" or "false" - should the resulting map be stored on our disk?
        self.storeSupport = "true"
        
        #
        # statusSupport = "true" or "false" - if statusLocation is set, the server 
        # will not wait for the end of the operation and will return the 
        # ExectuceResponce XML file immediately, without the ProcessOutput section
        # but with the statusLocation parameter
        self.statusSupport = "true"
        # and many others

    #####################################################################
    #
    # Execute part of the process
    #
    #####################################################################
    def execute(self):
        """
        NDVI
        """

        # import
        if os.system("r.in.gdal in=%s out=red >&2" % (self.Inputs[0]['value'])):
            return "Could not import <%s>" % (self.Inputs[0]['value'])
        if os.system("r.in.gdal in=%s out=nir >&2" % (self.Inputs[1]['value'])):
            return "Could not import <%s>" % (self.Inputs[2]['value'])
        
        # ndvi
        if os.system("""r.mapcalc ndvi"="float(nir-red)/float(nir+red)" >&2"""):
            return   """Could not r.mapcalc ndvi"="float(nir-red)/float(nir+red)" """
        
        # export
        if os.system("""r.out.gdal in=ndvi out=ndvi.tif type=Int32 >&2"""):
            return   """Could r.out.gdal in=ndvi out=ndvi.tif type=Int32 """
        
if __name__ == "__main__":
        
    ps = Process()
    ps.Inputs[0]['value'] = "red"
    ps.Inputs[1]['value'] = "nir"

    ps.execute()
    print ps.Outputs[0]
