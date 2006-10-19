#!/usr/bin/python
"""
pywps process example:

classify: Classify satellite image
"""
# Author:	Stepan Kafka
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

import os,time,string,sys

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
        self.Identifier = "classify"
        # processVersion - version of this process
        self.processVersion = "0.1"
        # Title - title for this process
        self.Title="Image classification"
        self.Abstract="GRASS processed imagery classification. Only unsupervised is supported at the moment."
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
                        'ComplexValueReference': {
                            'Formats': [ "image/tiff" ]
                        },
                        'value':None,
                    },
        
                # Second input
                    {
                        'Identifier': 'classes',
                        'Title': 'Number of classes',
                        'Abstract':'Unsupervised classification number of classes',
                        'LiteralData': {
                            'values':["*"], # values
                        },
                        'dataType' : type(0), # you should set this for input params controll
                        'value':20,
                    },
                ]
        
        #
        # Output
        # The structure is not much different from the input structure
        #
        self.Outputs = [
            {
                'Identifier': 'output',
                'Title': 'Resulting output map',
                'ComplexValueReference': {
                    'Formats':["image/tiff"],
                },
                'value':None,
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
        This function
            1) Imports the raster map
            2) runs r.mapcalc out=in+value
            3) Exports the raster map
            4) returns the new file name or 'None' if something went wrong
        """
        
        os.system("r.in.gdal -o -k input=%s output=input 1>&2" % (self.Inputs[0]['value']))               
        os.system("g.region -p rast=input.1 1>&2")
        os.system("i.group group=gr subgroup=klas input=`g.mlist type=rast sep=',' pattern='input.*'` 1>&2")
        os.system("i.cluster group=gr subgroup=klas sigfile=sig classes=%s 1>&2" % (self.Inputs[1]['value']))
        os.system("i.maxlik -q group=gr subgroup=klas sigfile=sig class=classif reject=rejected 1>&2")
        os.system("r.out.tiff -t input=classif output=output0 1>&2")
        os.system("/usr/local/bin/gdal_translate -of GTiff output0.tif output.tif  1>&2")
        
        # check the resulting file or any other variable, which interrests you
        if "output.tif" in os.listdir(os.curdir):
            self.Outputs[0]['value'] = "output.tif"
            return
        else:
            return "Output file not created"
        
