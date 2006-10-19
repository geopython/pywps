#!/usr/bin/python

# Author: Stepan Kafka

import os,time,string,sys


class Process:
    def __init__(self):
        self.Identifier = "shortestpath"
        self.processVersion = "0.1"
        self.storeSupport = "true"
        self.Title="Shortest path"
        self.Abstract="Find the shortes path on the roads map on Czech republic road network"
        self.grassLocation="/home/bnhelp/grassdata/mylocation/"
        #self.grassLocation="/var/www/wps/spearfish60/"
        self.Inputs = [
                    # 0
                    {
                        'Identifier': 'x1',
                        'Title': 'Start x coordinate',
                        'LiteralValue': {
                        },
                        'dataType': type(0.0),
                    },
                    # 1
                     {
                        'Identifier': 'y1',
                        'Title': 'Start y coordinate',
                        'LiteralValue': {
                            'AnyValue':None, # AllowedValues, AnyValue, ValuesReference
                        },
                        'dataType': type(0.0),
                    },
                    # 2
                     {
                        'Identifier': 'x2',
                        'Title': 'End x coordinate',
                        'LiteralValue': {
                            'AnyValue':None, # AllowedValues, AnyValue, ValuesReference
                        },
                        'dataType': type(0.0),
                    },
                    # 3
                     {
                        'Identifier': 'y2',
                        'Title': 'End y coordinate',
                        'LiteralValue': {
                            'AnyValue':None, # AllowedValues, AnyValue, ValuesReference
                        },
                        'dataType': type(0.0),
                    },
                    # 4
                     {
                        'Identifier': 'cost',
                        'Title': 'Calculation parameter',
        		'Abstract': 'time or length (default) ',
                        'LiteralValue': {
                            'AnyValue': None, #AllowedValues , #AnyValue, ValuesReference
                        },
                        'dataType': type(0.0),
                    }
        	    #,
                    # {
                #        'Identifier': 'distance',
            #            'Title': 'Search distance',
        #		'Abstract': 'Distance, where roads are searched is XY is not on a rouad.',
        #                'LiteralValue': {
        #                    'AnyValue': None, #AllowedValues , #AnyValue, ValuesReference
        #                },
        #                'dataType': type(0.0),
        #            }
                ]
        self.Outputs = [
            {
            'Identifier': 'output',
            'Title': 'Resulting output map',
            'ComplexValueReference': {
                'Formats':["text/xml"],
                }
            },
        ]
        
    def execute(self):
        os.system("g.region -d")

        if int(self.Inputs[4]['value']) == 1:
            os.system("echo '0 %s %s %s %s ' | v.net.path in=siln out=path afcolumn=COST2 dmax=5000 abcolumn=COST2 1>&2" %\
                            (self.Inputs[0]['value'],self.Inputs[1]['value'],self.Inputs[2]['value'],self.Inputs[3]['value']))
        else:
            os.system("echo '0 %s %s %s %s ' | v.net.path in=siln out=path dmax=5000 1>&2" %\
                            (self.Inputs[0]['value'],self.Inputs[1]['value'],self.Inputs[2]['value'],self.Inputs[3]['value']))
        os.system("v.out.ogr format=GML input=path dsn=out.xml  olayer=path.xml 1>&2")
        
        if "out.xml" in os.listdir(os.curdir):
            self.Outputs[0]['value'] = "out.xml"
            return
        else:
            return "Output file not created"

