# Author: Luca Casagrande ( luca.casagrande@gmail.com )

import os,time,string,sys


class Process:
    def __init__(self):
        self.Identifier = "buffer"
        self.processVersion = "0.1"
        self.storeSupport = "true"
        self.Title="Create a buffer around a point "
        self.Abstract="Create a buffer around point"
        self.grassLocation="/var/www/wps/spearfish60/"

        self.Metadata = [
                {
                    "Identifier":"point",
                    "type":"point",
                    "textContent":"Click in the map"},
                ]

        self.Inputs = [
                    # 0
                    {
   			'Identifier': 'point',
   			'Title': 'Input points',
   			'ComplexValueReference': {
       			'Formats':["text/plain"],
       				},
		    },

                    # 1
			{
                        'Identifier': 'radius',
                        'Title': 'Value of the buffer',
                        'LiteralValue': {'values':["*"]},
                        'dataType' : type(0.0), 
                        'value':None
                        },

                     ]
        
	self.Outputs = [
        	#0    
		{
                'Identifier': 'output',
                'Title': 'Resulting output map',
                'ComplexValueReference': {
                'Formats':["text/xml"],
                }
            },
        ]
        
    def execute(self):

        if os.system("g.region -d"):
            return "Could not set region to default"
	    	
	if os.system("v.in.ascii input=%s output=punto format=point fs=, skip=0 x=1 y=2 z=0 cat=0 -t 1>&2" %\
                (self.DataInputs['point'])) :
            return "Could run v.in.ascii"
            
	if os.system("v.buffer input=punto output=punto_buff type=point layer=1 buffer=%s scale=1.0 tolerance=0.01 1>&2" %\
                (self.DataInputs['radius'])):
            return "Could not run v.buffer"
            	
	if os.system("v.out.ogr type=area format=GML input=punto_buff dsn=out.xml  olayer=path.xml 1>&2"):
            return "Could not export vector map"

        
        if "out.xml" in os.listdir(os.curdir):
            self.DataOutputs['output'] = "out.xml"
            return
        else:
            return "Output file not created"

