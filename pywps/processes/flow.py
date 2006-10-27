#!/usr/bin/python
"""
pywps process example:

flow:   analysis of flowing water
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
        self.Identifier = "flow"
        
        # processVersion - version of this process
        self.processVersion = "0.1"
        
        # Title - title for this process
        self.Title="Flow analysis"
        self.Abstract="GRASS processed r.flow analysis."
        self.grassLocation="/home/bnhelp/grassdata/mylocation/"
        
        #
        # Inputs
        # Inputs is an array of input structure
        # Inputs = [ {input1},{input2},{...} ]
        #
        self.Inputs = [
                # 0
                    {
                        'Identifier': 'x1',
                        'Title': 'X coordinate',
                        'LiteralValue': {
        		    'values':["*"],
                        },
        		'dataType': type(0.0),
                    },
        
                # 1
        	    {
                        'Identifier': 'y1',
                        'Title': 'Y coordinate',
                        'LiteralValue': {
        		    'values':["*"],
                        },
        		'dataType': type(0.0),
                    },
        	    
                # 2
        	    {
                        'Identifier':'x2',
                        'Title': 'X coordinate',
                        'LiteralValue': {
        		    'values':["*"],
                        },
        		'dataType': type(0.0),
                    },
        
        	# 3
        	    {
                        'Identifier':'y2',
                        'Title': 'Y coordinate',
                        'LiteralValue': {
        		    'values':["*"],
                        },
        		'dataType': type(0.0),
                    }
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
                    },
        ]
        
        #
        # Optional attributes
        #
        #
        # storeSuport = "true" or "false" - should the resulting map be stored on our disk?
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
        os.system("g.region -d")
        os.system("g.region w=%s s=%s e=%s n=%s align=dem_cr" % \
                (self.Inputs[0]['value'],
                    self.Inputs[1]['value'],
                    self.Inputs[2]['value'],
                    self.Inputs[3]['value']))
        os.system("r.flow elevin=dem_cr dsout=accum")
        os.system("r.out.tiff -t input=accum output=output0")
        os.system("/usr/local/bin/gdal_translate -of GTiff output0.tif output.tif >> /dev/null")

        # check the resulting file or any other variable, which interrests you
        if "output.tif" in os.listdir(os.curdir):
            self.Outputs[0]['value'] = "output.tif"
            return
        else:
            return "Output file not created"

