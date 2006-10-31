#!/usr/bin/python

import os,urllib,time,string

class Process:
    def __init__(self):
        self.Identifier = "justadd"
        self.processVersion = "0.1"
        self.storeSupported = "true"
        self.Title="Add some value to number"
        self.Inputs = [
                 {
                    'Identifier': 'value',
                    'Title': 'Value to be added',
                    'Abstract': ' "value + 1" ',
                    'LiteralValue': {"values":[250,245]},
                    'value': 10,
                    #'dataType': type(0),
                 }
                ]
        self.Outputs = [
                {
                'Identifier': 'output',
                'Title': 'Resulting output value (value + 1)',
                'LiteralValue': {'UOMs':["meters"]}
                },
        ]
        
    def execute(self):
        self.Outputs[0]['value'] = string.atof(self.Inputs[0]['value']) + 1
        return 
