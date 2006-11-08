#!/usr/bin/python

import os,time,string,sys,shutil

class Process:
    def __init__(self):
        self.Identifier = "spearpath"
        self.processVersion = "0.1"
        self.storeSupported = "true"
        self.Title="Find the shortes path on the roads map on Spearfish dataset"
        self.grassLocation="/var/www/wps/spearfish61/"
        self.Inputs = [
                    {
                        'Identifier': 'x1',
                        'Title': 'Start x coordinate',
                        'LiteralData': {
                            'values':["*"],
                            },
                        'dataType': type(0.0),
                        'value': None
                    },
                    {
                        'Identifier': 'y1',
                        'Title': 'Start y coordinate',
                        'LiteralData': {
                            'values':["*"],
                        },
                        'dataType': type(0.0),
                        'value': None
                    },
                    {
                        'Identifier': 'x2',
                        'Title': 'End x coordinate',
                        'LiteralData': {
                            'values':["*"],
                        },
                        'dataType': type(0.0),
                        'value': None
                    },
                    {
                        'Identifier': 'y2',
                        'Title': 'End y coordinate',
                        'LiteralData': {
                            'values':["*"],
                        },
                        'dataType': type(0.0),
                        'value': None
                    }
                ]
        self.Outputs = [
                    {
                        'Identifier': 'outputReference',
                        'Title': 'Resulting output map',
                        'ComplexValueReference': {'Formats':["text/xml"]},
                        'value': None
                    },
                    {
                        'Identifier': 'outputData',
                        'Title': 'Resulting output map',
                        'ComplexValue': {'Formats':["text/xml"]},
                        'value': None
                    },
                ]

    # --------------------------------------------------------------------
    def execute(self):
        """
        This function serves like simple GRASS - python script

        It returns None, if process succeed or String if process failed
        """

        os.system("g.region -d")
        # FIXME: the program does print "Building topology to STDOUT!!
        print  "echo '0 %s %s %s %s' | v.net.path in=roads out=path 1>&2" % \
                (self.Inputs[0]['value'],
                self.Inputs[1]['value'],
                self.Inputs[2]['value'],
                self.Inputs[3]['value'])

        os.system(
            "echo '0 %s %s %s %s' | v.net.path in=roads out=path 1>&2" % \
            (self.Inputs[0]['value'],
                self.Inputs[1]['value'],
                self.Inputs[2]['value'],
                self.Inputs[3]['value']))
        os.system("v.out.ogr format=GML input=path dsn=out.xml  olayer=path.xml 1>&2")

        if "out.xml" in os.listdir(os.curdir):
            shutil.copy("out.xml","out2.xml")
            self.Outputs[0]['value'] = "out.xml"
            self.Outputs[1]['value'] = "out2.xml"
            return
        else:
            return "Ouput file not created!"
