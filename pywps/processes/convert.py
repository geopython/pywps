#!/usr/bin/python
"""
pywps process example:

conversion: Convert a shape file to GML
"""
# Author:       Luca Casagrande (luca.casagrande@gmail.com)
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
    def __init__(self):
        self.Identifier = "conversion"
        self.processVersion = "0.1"
        self.storeSupport = "true"
        self.statusSupported = "true"
	self.Title="Conversion from shp to gml"
        self.Abstract="Convert a shape file in GML"
        self.Inputs = [
                    # 0
                    {
   			'Identifier': 'shp',
   			'Title': 'Input vector',
   			'ComplexValueReference': {
       			'Formats':["application/octet-stream"],
       				},
		    },
                    # 1
                    {
   			'Identifier': 'shx',
   			'Title': 'Input vector',
   			'ComplexValueReference': {
       			'Formats':["application/octet-stream"],
       				},
		    },
 
                    # 2
                    {
   			'Identifier': 'dbf',
   			'Title': 'Input vector',
   			'ComplexValueReference': {
       			'Formats':["application/octet-stream"],
       				},
		    },
 
 
                     ]
 
	self.Outputs = [
        	#0    
		{
                'Identifier': 'output',
                'Title': 'Resulting output map',
                'ComplexValueReference': {
                'Formats':["text/xml"]
                }
            },
        ]
 
    def execute(self):
        try:
            os.rename(self.DataInputs['shp'],"input.shp")
            os.rename(self.DataInputs['dbf'],"input.dbf")
            os.rename(self.DataInputs['shx'],"input.shx")
        except:
            return "Could not rename input files"

        if os.system("ogr2ogr -f gml out.xml input.shp 1>&2"):
            return "Could not convert vector file"
 
        if "out.xml" in os.listdir(os.curdir):
            self.Outputs[0]['value'] = "out.xml"
            return
        else:
            return "Output file not created"

if __name__ == "__main__":
    proc = Process()
    proc.DataInputs = {}
    proc.DataInputs['vector'] = "shape.shp"
    proc.execute()
