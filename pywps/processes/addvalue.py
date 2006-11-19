"""
pywps process example:

addvalue: Adds some value to raster map
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

import os,time,string,sys,shutil

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
        # 'Identifier' = 'addvalue'
        self.Identifier = "addvalue"

        # processVersion - version of this process
        # processVersion = "0.1"
        self.processVersion = "0.1"

        # Title - title for this process
        # Title = "Add some value to the raster map"
        self.Title="Add some value to raster map"

        # define GRASS location
        self.grassLocation = None

        #
        # Inputs
        # Inputs is an array of input structure
        # Inputs = [ {input1},{input2},{...} ]
        #
        self.Inputs = [
                # This module has 2 inputs: 
                # 1) Input raster map
                # 2) Value to be added

                # First input
                    {
                        'Identifier':'input',
                        'Title': 'Input raster map',
                        'ComplexValue': {
                            'Formats': [ "image/tiff" ]
                        },
                    },

                # Second input
                    {
                        'Identifier': 'value',
                        'Title': 'Value to be added',
                        'LiteralValue': {'values':["*"]},
                        'dataType' : type(0.0), # you should set this for input params controll
                        'value':None
                    },
                # 2
                    {
                        'Identifier': 'noth',
                        'Title': 'Array',
                        'LiteralValue': {'values':[10,20]},
                        'dataType' : type(0.0), # you should set this for input params controll
                        'value':10,
                        'MinimumOccurs': 3,
                    },
                # 3
                    {
                        'Identifier': 'bbox',
                        'Title': 'Bounding Box',
                        'Abstract': 'Required BoundibgBox',
                        'BoundingBoxValue': {},
                        'value':True
                    },

                ]

        #
        # Output
        # The structure is not much different from the input structure
        #
        self.Outputs = [
                {
                    'Identifier': 'outputVal',
                    'Title': 'Resulting output map',
                    'ComplexValueReference': {
                        'Formats':["image/tiff"],
                        },
                    'value':None
                },
                {
                    'Identifier': 'outputRef',
                    'Title': 'Resulting output map',
                    'ComplexValueReference': {
                        'Formats':["image/tiff"],
                        },
                    'value':None
                },
                {
                    'Identifier': 'bbox',
                    'Title': 'Bounding box of the map',
                    'BoundingBoxValue': {},
                    'value':[]
                },
                {
                    'Identifier': 'litval',
                    'Title': 'literal value',
                    'LiteralValue': {'UOMs':["km"]},
                    'value':" ahoj "
                }



            ]

        #
        # Optional attributes
        #
        #
        # storeSuported = "true" or "false" - should the resulting map be stored on our disk?
        self.storeSupported = "true"

        #
        # statusSupported = "true" or "false" - if statusLocation is set, the server 
        # will not wait for the end of the operation and will return the 
        # ExectuceResponce XML file immediately, without the ProcessOutput section
        # but with the statusLocation parameter
        self.statusSupported = "true"
        # and many others

    #####################################################################
    #
    # Execute part of the process
    #
    #####################################################################
    def execute(self):
        """
        This function
            1) Imports the raster map
            2) runs r.mapcalc out=in+value
            3) Exports the raster map
            4) returns the new file name or 'None' if something went wrong
        """

        os.system("r.in.gdal -o in=%s out=input >&2" %\
                (self.DataInputs['input']))

        self.status = ["Ahoj, svete", 10]

        for gdalinfoln in os.popen("gdalinfo %s" % \
                (self.DataInputs['input'])):
            if gdalinfoln.split()[0] == "Band" and gdalinfoln.split()[1] == "3":
                os.system("""g.region rast=input.red >&2""")
                os.system("r.composite r=input.red b=input.blue g=input.green out=input >&2")
        os.system("""g.region rast=input >&2""")
        os.system("r.mapcalc output=input+%f >&2" % \
                (float(self.DataInputs['value'])))
        os.system("r.out.gdal type=Int32 in=output out=%s 1>&2" % "output.tif")
        self.status = ["Ahoj, svete", 90]

        # boundingbox
        region = {}
        for b in os.popen("g.region -g"):
            b = b.strip()
            key,val = b.split("=")
            region[key] = val

        #time.sleep(10)
        #os.system("r.out.tiff in=output out=output >&2")
        if "output.tif" in os.listdir(os.curdir):
            shutil.copy("output.tif","output2.tif")
            self.DataOutputs['outputVal'] = "output.tif"
            self.DataOutputs['outputRef'] = "output2.tif"
            self.DataOutputs['bbox'] = [region['s'],region['e'],region['n'],region['w']]
            return 
        else:
            return "Output file not created!"
