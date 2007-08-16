#!/usr/bin/python
"""
Execute definition file

Description:
    This file contains structure describing the ProcessDescriptions response
    and request. See OGC 05-007r4 for details

    For each structure:
        Possible attributes are

        oblig - (m)andatory, (o)ptional, (c)onditional
        ns - namespace
        elements - nested elements (if any)
        attributes - attributes of this element (if any)
        default - default value (if any)
        values - if there are more nearly same structures
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# 
# Lince: 
# 
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


class WPS:
    def __init__(self):
        self.namespaces = {
            "ows":"http://www.opengeospatial.net/ows",
            "wps":"http://www.opengeospatial.net/wps",
            "xsi":"http://www.w3.org/2001/XMLSchema-instance",
            "xlink":"http://www.w3.org/1999/xlink",
        }
        
        self.schemalocation = {
          # "wps":"http://www.bnhelp.cz/schema/wps/0.4.0/wpsDescribeProcess.xsd",
            "wps":"http://www.ogcnetwork.net/schemas/wps/0.4.0/wpsDescribeProcess.xsd",
        }

        self.pd = {
            'request':{
                'elements':{
                    'Identifier': {
                        'oblig':'m',
                        'ns':'ows',
                        }
                    },

                'attributes': {
                    'service': {
                        'oblig':'m',
                        'ns':'ows',
                        'default':'WPS',
                        },
                    'request': {
                        'oblig':'m',
                        'ns':'ows',
                        'default':'GetCapabilities',
                        },
                    'version': {
                        'oblig':'m',
                        'ns':'ows',
                        'default':'0.4.0',
                        },
                    }
                },
            'response': {
                'order': ['Identifier','Title','Abstract',"Metadata",'DataInputs',
                         'ProcessOutputs',],
                'elements':{
                    'Identifier' :{
                        'oblig':'m',
                        'ns':'ows:'
                        },
                    'Title'      :{
                        'oblig':'m',
                        'ns':'ows:'
                        },
                    'Abstract'   :{
                        'oblig':'o',
                        'ns':'ows:'
                    },
                    'Metadata'   :{
                        'oblig':'o',
                        'ns':'ows:'
                        },
                    'DataInputs':{
                        'ns':'',
                        'Input': {
                            "ns":"",
                            'order':['Identifier','Title','Abstract',
                            'ComplexData', 'LiteralData',
                            'BoundingBoxData','MinimumOccurs'],
                            'elements':{
                                'Identifier':{
                                    'oblig': 'm',
                                    'ns':'ows:',
                                    },
                                'Title':{
                                    'oblig': 'm',
                                    'ns':'ows:',
                                    },
                                'Abstract': {
                                    'oblig': 'o',
                                    'ns':'ows:',
                                    },
                                'MinimumOccurs':{
                                    'oblig': 'm',
                                    'default':1,
                                    'ns':'',
                                    },
                                'ComplexData':{
                                    # table 16
                                    'oblig':'c',
                                    'ns':"",
                                    'elements':{
                                        'SupportedComplexData': {
                                            # table 19
                                            'oblig':'o',
                                            'ns':"",
                                            'elements': {
                                                # table 20
                                                'Format': {
                                                    'oblig':'o',
                                                    'ns':"",
                                                    },
                                                'Encoding':{
                                                    'oblig':'o',
                                                    'ns':"",
                                                    },
                                                'Schema':{
                                                    'oblig':'o',
                                                    'ns':"",
                                                    },
                                            },
                                            'attributes': {
                                                'defaultFormat': {
                                                    'oblig':'o',
                                                    'ns':"",
                                                    'default':'text/XML',
                                                    },
                                                'defaultEncoding': {
                                                    'oblig':'o',
                                                    'ns':"",
                                                    'default':'UTF-8',
                                                    },
                                                'defaultSchema': {
                                                    'oblig':'o',
                                                    'ns':"",
                                                    },
                                                }
                                            },#/SupportedComplexData
                                        },# /elements
                                    'attributes':{
                                        'defaultFormat': {
                                            'ns':"",
                                            'oblig':"o",
                                            'default':"text/XML",
                                            },
                                        'defaultEncoding':{
                                            'ns':"",
                                            'oblig':"o",
                                            'default':"UTF-8",
                                            },
                                        'defaultSchema': {
                                            'ns':"",
                                            'oblig':"o",
                                            }
                                        }#/attributes
                                    },
                                'LiteralData':{
                                    'oblig':'o',
                                    'ns':'',
                                    'order':["DataType","SupportedUOMs","LiteralValues","DefaultValue"],
                                    'elements': {
                                        'DataType': {
                                            'oblig': 'o',
                                            'ns':'',
                                            'attributes':{
                                                'reference':{
                                                    'oblig':'o',
                                                    'ns':'ows:',
                                                    },
                                                },
                                            },
                                        'SupportedUOMs': {
                                            'oblig': 'o',
                                            'ns':'',
                                            'elements': {
                                                'UOM': {
                                                    'oblig': 'o',
                                                    'ns':'ows:',
                                                    'elements': {
                                                        'Name':{
                                                            'oblig':'m',
                                                            'ns':'',
                                                            },
                                                        },
                                                    'attributes':{
                                                        'reference': {
                                                            'oblig':'o',
                                                            'ns':'',
                                                            },
                                                        },
                                                    }, #/UOM
                                                },#/elements
                                            'attributes': {
                                                'defaultUOM': {
                                                    'oblig':'o',
                                                    'ns':'',
                                                    'default':'meters',
                                                    },
                                                }#/attributes
                                            }, # /SupportedUOMs

                                        'LiteralValues': {
                                            'oblig':'m',
                                            'ns':'',
                                            'elements':{
                                                'AllowedValues':  {
                                                    'ns':'',
                                                    'oblig':'c',
                                                    'elements': {
                                                        'Value': {
                                                            'oblig': 'o',
                                                            'ns':'',
                                                            },
                                                        'Range': {
                                                            'oblig': 'o',
                                                            'ns':'',
                                                            },
                                                        },
                                                    },
                                                'AnyValue'     :  {
                                                    'oblig':'c',
                                                    'ns':'ows:',
                                                    # table d.7
                                                    #'elements': {
                                                    #    'Name': {'oblig':'m'},
                                                    #},
                                                    #'attributes':{
                                                    #    'reference':{ 'oblig':'o'},
                                                    #},
                                                    },#/AnyValue
                                                'ValuesReference':{
                                                    'oblig':'c',
                                                    'ns':'',
                                                    # table d.7
                                                    # 'elements': {
                                                    #     'Name': {'oblig':'m',}
                                                    # },
                                                    # 'attributes':{
                                                    #     'reference': {'oblig':'o'},
                                                    # },
                                                    }, #/ValuesReference
                                                }
                                            },
                                        'DefaultValue':  {
                                            'ns':"ows:",
                                            'oblig':'o',
                                            },
                                        } #/elements
                                    }, # /LiteralData
                                'BoundingBoxData':{
                                    'oblig':'m',
                                    'ns':"",
                                    },
                                } #/elements
                            }, #/Input
                        }, #/DataInputs
                    'ProcessOutputs'    :{
                        'ns':'',
                        'Output': {
                            'ns':'',
                            'order': ['Identifier','Title','Abstract',
                            'ComplexOutput', 'LiteralOutput',
                            'BoundingBoxOutput'],
                            'elements':{
                                'Identifier':{
                                    'oblig':'m',
                                    'ns':'ows:',
                                    },
                                'Title':{
                                    'oblig':'m',
                                    'ns':'ows:',
                                    },
                                'Abstract':{
                                    'oblig':'o',
                                    'ns':'ows:',
                                    },
                                'ComplexOutput': {
                                    'oblig':'o',
                                    'ns':'',
                                    'elements': {
                                        'SupportComplexData': {
                                            'oblig': 'o',
                                            'ns':'',
                                            'elements': {
                                                'Formats': {
                                                    'ns':'',
                                                    },
                                                'Encoding':{
                                                    'ns':'',
                                                    },
                                                'Schema'  :{
                                                    'ns':'',
                                                    },
                                                },
                                            'attributes': {
                                                'defaultFormats':   {
                                                    'oblig':'o',
                                                    'ns':'',
                                                    },
                                                'defaultEncoding':  {
                                                    'oblig':'o',
                                                    'ns':'',
                                                    },
                                                'defaultSchema'  :  {
                                                    'oblig':'o',
                                                    'ns':'',
                                                    },
                                                }
                                            }, #/SupportComplexData
                                        },
                                    'attributes': {
                                        'defaultFormat': {
                                            'oblig': 'o',
                                            'default':'text/XML',
                                            'ns':''
                                            },
                                        'defaultEncoding': {
                                            'oblig': 'o',
                                            'default':'',
                                            'ns':''
                                            },
                                        'defaultSchema': {
                                            'oblig': 'o',
                                            'ns': '',
                                            },
                                        }
                                    },#/ComplexOutput
                                'LiteralOutput': {
                                    'oblig':'o',
                                    'ns':'',
                                    'elements': {
                                        'DataType': {
                                            'oblig': 'o',
                                            'ns':'',
                                            'elements': {
                                                'Name': {
                                                    'oblig':'m',
                                                    'ns':'',
                                                    },
                                                },
                                            'attributes':{
                                                'reference':{
                                                    'oblig':'o',
                                                    'ns':'ows:',
                                                    },
                                                },
                                            },
                                        'SupportedUOMs': {
                                            'oblig': 'o',
                                            'ns':'',
                                            'elements': {
                                                'UOM': {
                                                    'oblig': 'o',
                                                    'ns':'ows:',
                                                    'elements': {
                                                        'Name':{
                                                            'oblig':'m',
                                                            'ns':'',
                                                            },
                                                        },
                                                    'attributes':{
                                                        'reference': {
                                                            'oblig':'o',
                                                            'ns':'',
                                                            },
                                                        },
                                                    }, #/UOM
                                                },#/elements
                                            'attributes': {
                                                'defaultUOM': {
                                                    'oblig':'o',
                                                    'ns':'',
                                                    'default':'meters',
                                                    },
                                                }#/attributes
                                            } # /SupportedUOMs
                                        }#/elements
                                    },#/LiteralOutput
                                'BoundingBoxOutput': {
                                    'oblig':'o',
                                    'ns':'',
                                    'elements': {
                                        'CRS':{},
                                    },
                                    'attributes': {
                                        'defaultCRS': {}
                                        }
                                    } #/BoundingBoxOutput
                                }, #/elements
                            },#/Output
                        }, # /processoutput
                    },# /elements
                'attributes':{
                    'processVersion' : {
                        'oblig':'m',
                        'ns':'',
                        },
                    'storeSupported' : {
                        'oblig':'o',
                        'default': "false",
                        'ns':'',
                        },
                    'statusSupported': {
                        'oblig':'o',
                        'default': "false",
                        'ns':'',
                        },
                    }
                }
        }
        return
