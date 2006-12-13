# Author: Luca Casagrande ( luca.casagrande@gmail.com )
 
import os,time,string,sys
 
 
class Process:
    def __init__(self):
        self.Identifier = "conversion"
        self.processVersion = "0.1"
        self.storeSupport = "true"
        self.statusSupported = "true"
	self.Title="Conversion shp to gml"
        self.Abstract="Convert a shape in GML"
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
