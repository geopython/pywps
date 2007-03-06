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
        self.Identifier = "visibility"
        
        # processVersion - version of this process
        self.processVersion = "0.1"
        
        # Title - title for this process
        self.Title="Visibility analysis"
        self.Abstract="GRASS processed line of sight analysis."
        self.grassLocation="/var/www/wps/spearfish61/"
        
        #
        # Inputs
        # Inputs is an array of input structure
        # Inputs = [ {input1},{input2},{...} ]
        #
        self.Inputs = [
                # 0
                    {
                        'Identifier': 'x',
                        'Title': 'X coordinate',
                        'LiteralData': {
		            'values':["*"],
                        },
		        'dataType': type(0.0),
                    },
        
                # 1
	            {
                        'Identifier': 'y',
                        'Title': 'Y coordinate',
                        'LiteralData': {
		            'values':["*"],
                        },
		        'dataType': type(0.0),
                    },
	            
                # 2
	            {
                        'Identifier':'maxdist',
                        'Title': 'Maximal distance',
		        'Abstract':'Maximal distance of visibility (meters)',
                        'LiteralData': {
		            'values':["*"],
                        },
		        'dataType': type(0.0),
                    },
        
	        # 3
	            {
                        'Identifier':'observer',
                        'Title': 'Observer elevation',
		        'Abstract':'The height of observer eye over the terrain (meters)',
                        'LiteralData': {
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
                }
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
        dist = int(self.Inputs[2]['value'])
        if dist > 20000:
            return "Visibility Error: maximal distance 2000 exceeded (%d)" % dist
        xmin=int(self.Inputs[0]['value']) - dist
        ymin=int(self.Inputs[1]['value']) - dist
        xmax=int(self.Inputs[0]['value']) + dist
        ymax=int(self.Inputs[1]['value']) + dist
        os.system("g.region w=%i s=%i e=%i n=%i align=dem_cr" % (xmin,ymin,xmax,ymax))
	self.status=["Calculating visibility", ""]
        os.system("r.los input=dem_cr output=output coordinate=%s,%s max_dist=%i obs_elev=%s" % \
                (self.Inputs[0]['value'],self.Inputs[1]['value'],dist, self.Inputs[3]['value']))
	self.status=["Creating output", ""]        
	sys.stderr.write("r.los input=dem_cr output=output coordinate=%s,%s max_dist=%i obs_elev=%s\n"  %\
               (self.Inputs[0]['value'],self.Inputs[1]['value'],dist, self.Inputs[3]['value']))
        os.system("""r.mapcalc "output0=if(output,1,0)" """)
        os.system("r.out.tiff -t -p input=output0 output=output0")
        os.system("/usr/local/bin/gdal_translate -of GTiff output0.tif output.tif 1>&2")

        # check the resulting file or any other variable, which interrests you
        if "output.tif" in os.listdir(os.curdir):
            self.Outputs[0]['value'] = "output.tif"
            return
        else:
            return "Output file not created"
