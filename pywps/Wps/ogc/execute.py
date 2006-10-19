#!/usr/bin/python
"""
Execute definition file

Description:
    This file contains structure describing the Execute response
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
          "wps":"http://www.bnhelp.cz/schema/wps/0.4.0/wpsExecute.xsd",
        }
        
        self.e = {
            'request': {
                'attributes': {
                    'service':{
                        'oblig':"m"
                        },
                    'request':{
                        'oblig':"m"
                        },
                    'version':{
                        'oblig':"m"
                        },
                    'store': {
                        'oblig':"o", 
                        'defaul':"false"
                        },
                    'status':{
                        'oblig':"o", 
                        'defaul':"false"
                        },
                    },
                'elements': {
                    'Identifier':{
                        'oblig':"m"
                        },
                    'DataInputs':{
                        'Input': {
                            'Identifier': {
                                'oblig':"m"
                                },
                            'Title'     : {
                                'oblig':"m"
                                },
                            'Abstract'  : {
                                'oblig':"o"
                                },
                            'ValueFormChoice' : {
                                'ComplexValueReference': {
                                        'attributes': {
                                            'format': {
                                                'oblig':"o"
                                                },
                                            'encoding': {
                                                'oblig':"o"
                                                },
                                            'schema': {
                                                'oblig':"o"
                                                },
                                            'reference': {
                                                'oblig':"m"
                                                },
                                            }
                                        },#/ComplexValueReference
                                    'ComplexValue': {
                                        'attributes': {
                                            'format': {
                                                'oblig':"o"
                                                },
                                            'encoding': {
                                                'oblig':"o"
                                                },
                                            'schema': {
                                                'oblig':"o"
                                                },
                                            },
                                        'elements': {
                                            'Value': {
                                                'oblig':"m"
                                                },
                                            }
                                        }, #/ComplexValue
                                    'LiteralValue': {
                                            'value': {
                                                'oblig':"m"
                                                },
                                            'dataType': {
                                                'oblig':"o"
                                                },
                                            'uom': {
                                                'oblig':"o"
                                                },

                                        }, #/LiteralValue
                                    'BoundingBoxValue':{
                                        }#/BoundingBoxValue
                                    },
                            }

                        },# DataInputs
                    'OutputDefinitions':{
                        'oblig':"o",
                        'Output': {
                            'ns': '',
                            'elements': {
                                'Identifier': {
                                    'oblig':"m",
                                    'ns': 'ows:',
                                    },
                                'Title'     : {
                                    'oblig':"m",
                                    'ns': 'ows:',
                                    },
                                'Abstract'  : {
                                    'oblig':"o",
                                    'ns': 'ows:',
                                    },
                                },
                            'attributes': {
                                'format':    {
                                    'oblig':"o"
                                    },
                                'encoding':  {
                                    'oblig':"o"
                                    },
                                'schema':    {
                                    'oblig':"o"
                                    },
                                'uom':       {
                                    'oblig':"o"
                                    },
                                }
                            },

                        }, # /OutputDefinitions
                    }, #/ elements
                }, # request
            ##############################################################
            'response': {
                'attributes' : {
                    'version' : {
                        'oblig':"m", 
                        'default':'0.4.0',
                        'ns':"",
                        },
                    'statusLocation': {
                        'oblig':"o",
                        'ns':"",
                        },
                    },
                'order': ['Identifier',"Status",'DataInputs','OutputDefinitions','ProcessOutputs',
                         ],
                'elements': {
                    'Identifier': {
                        'oblig':"m",
                        'ns':"ows:",
                        },
                    'DataInputs': {
                        'oblig':"o",
                        'ns':"",
                        },
                    'Status': { # table 40
                        'oblig':"m",
                        'ns':"",
                        'elements':{
                            'ProcessAccepted':{
                                'ns':"",
                                },
                            'ProcessStarted': {
                                'ns':"",
                                'attributes': {
                                    'message':{
                                        'oblig':"m",
                                        'ns':"",
                                        },
                                    'percentCompleted':{
                                        'oblig':"o",
                                        'ns':"",
                                        },
                                    },
                                },
                            'ProcessSucceeded':{
                                'ns':"",
                                },
                            'ProcessFailed'  :{
                                'ns':"",
                                },
                            }
                        },
                    'OutputDefinitions': { # table 29
                        'ns':"",
                        'elements': {
                            'Output': { # table 30
                                'ns':"",
                                'order': ['Identifier','Title','Abstract'],
                                'elements': {
                                    'Identifier': {
                                        'oblig':"m",
                                        'ns':"ows:",
                                        },
                                    'Title'     : {
                                        'oblig':"m",
                                        'ns':"ows:",
                                        },
                                    'Abstract'  : {
                                        'oblig':"o",
                                        'ns':"ows:",
                                        },
                                    },
                                'attributes': {
                                    'format':    {
                                        'oblig':"o",
                                        'ns':"",
                                        },
                                    'encoding':  {
                                        'oblig':"o",
                                        'ns':"",
                                        },
                                    'schema':    {
                                        'oblig':"o",
                                        'ns':"",
                                        },
                                    'uom':       {
                                        'oblig':"o",
                                        'ns':"",
                                        },
                                    }
                                }
                            }
                        }, # /OutputDefinitions
                    'DataInputs': { # table 28
                        'ns':"",
                        'elements': {
                            'Input': {
                                'order':['Identifier','Title','Abstract','ValueFormChoice'],
                                'elements': {
                                    'Identifier': {
                                        'oblig':"m",
                                        'ns':"ows:",
                                        },
                                    'Title'     : {
                                        'oblig':"m",
                                        'ns':"ows:",
                                        },
                                    'Abstract'  : {
                                        'oblig':"o",
                                        'ns':"ows:",
                                        },
                                    'ValueFormChoice'  : {# table 32
                                        'ComplexValueReference': {
                                                'attributes': {
                                                    'format': {
                                                        'oblig':"o",
                                                        'ns':"",
                                                        },
                                                    'encoding': {
                                                        'oblig':"o",
                                                        'ns':"",
                                                        },
                                                    'schema': {
                                                        'oblig':"o",
                                                        'ns':"",
                                                        },
                                                    'reference': {
                                                        'oblig':"m",
                                                        'ns':"",
                                                        },
                                                }
                                            },#/ComplexValueReference
                                            'ComplexValue': {
                                                'attributes': {
                                                    'format': {
                                                        'oblig':"o",
                                                        'ns':"",
                                                        },
                                                    'encoding': {
                                                        'oblig':"o",
                                                        'ns':"",
                                                        },
                                                    'schema': {
                                                        'oblig':"o",
                                                        'ns':"",
                                                        },
                                                },
                                                'elements': {
                                                    'Value': {
                                                        'oblig':"m",
                                                        'ns':"",
                                                        },
                                                }
                                            }, #/ComplexValue
                                            'LiteralValue': {
                                                'ns':"",
                                                'attributes':{
                                                    'value': {
                                                        'oblig':"m",
                                                        'ns':"",
                                                        },
                                                    'dataType': {
                                                        'oblig':"o",
                                                        'ns':"",
                                                        },
                                                    'uom': {
                                                        'oblig':"o",
                                                        'ns':"",
                                                        },
                                                    },
                                                }, #/LiteralValue
                                            'BoundingBoxValue':{
                                                'ns':'',
                                                'order': ['LowerCorner','UpperCorner'],
                                                'elements': {
                                                    'LowerCorner': {
                                                        'oblig':'m',
                                                        'ns':'ows:',
                                                        },
                                                    'UpperCorner': {
                                                        'oblig':'m',
                                                        'ns':'ows:',
                                                        },
                                                },#/elements
                                                'attributes':{
                                                    'dimensions': {
                                                        'oblig':'o',
                                                        'ns':'ows:',
                                                        'default':2,
                                                        },
                                                    'crs': {
                                                        'oblig':'o',
                                                        'ns':'ows:',
                                                        },
                                                    }#/elements
                                                }#/BoundingBoxValue
                                            },
                                        },
                                    }
                                }
                            }, # /DataInputs
                        'ProcessOutputs': { # table 39
                            'elements' : {
                                'Output': {
                                    'ns':"",
                                    'order': ['Identifier','Title','Abstract','ValueFormChoice'],
                                    'elements': {
                                        'Identifier': {
                                            'oblig':"m",
                                            'ns':"ows:",
                                            },
                                        'Title'     : {
                                            'oblig':"m",
                                            'ns':"ows:",
                                            },
                                        'Abstract'  : {
                                            'oblig':"o",
                                            'ns':"ows:",
                                            },
                                        'ValueFormChoice' : {
                                            'ns':"",
                                            'elements': {
                                                'ComplexValueReference': {
                                                        'ns':"",
                                                        'attributes': {
                                                            'format': {
                                                                'ns':"",
                                                                'oblig':"o",
                                                                },
                                                            'encoding': {
                                                                'oblig':"o",
                                                                'ns':"",
                                                                'default':'utf-8',
                                                                },
                                                            'schema': {
                                                                'oblig':"o",
                                                                'ns':"",
                                                                'default':'',
                                                                },
                                                            'reference': {
                                                                'oblig':"m",
                                                                'ns':"ows:",
                                                                'default':'text/xml',
                                                                },
                                                            }
                                                        },#/ComplexValueReference
                                                    'ComplexValue': {
                                                        'ns':"",
                                                        'attributes': {
                                                            'format': {
                                                                'oblig':"o",
                                                                'ns':"",
                                                                },
                                                            'encoding': {
                                                                'oblig':"o",
                                                                'ns':"",
                                                                },
                                                            'schema': {
                                                                'oblig':"o",
                                                                'ns':"",
                                                                },
                                                            },
                                                        'elements': {
                                                        'Value': {
                                                            'oblig':"m",
                                                                'ns':"",
                                                                },
                                                            }
                                                        }, #/ComplexValue
                                                    'LiteralValue': {
                                                            'ns':"",
                                                            'attributes':{
                                                                'value': {
                                                                    'oblig':"m",
                                                                    'ns':"",
                                                                    },
                                                                'dataType': {
                                                                    'oblig':"o",
                                                                    'ns':"",
                                                                    },
                                                                'uom': {
                                                                    'oblig':"o",
                                                                    'ns':"",
                                                                    },
                                                            }#/attributes
                                                        }, #/LiteralValue
                                                'BoundingBoxValue':{
                                                        'ns':'',
                                                        'order': ['LowerCorner','UpperCorner'],
                                                        'elements': {
                                                            'LowerCorner': {
                                                                'oblig':'m',
                                                                'ns':'ows:',
                                                                },
                                                            'UpperCorner': {
                                                                'oblig':'m',
                                                                'ns':'ows:',
                                                                },
                                                        },#/elements
                                                        'attributes':{
                                                            'dimensions': {
                                                                'oblig':'o',
                                                                'ns':'',
                                                                'default':2,
                                                                },
                                                            'crs': {
                                                                'oblig':'o',
                                                                'ns':'',
                                                                },
                                                            }#/elements
                                                        }#/BoundingBoxValue

                                                }, #/elements
                                            }, # /ValueFormChoice
                                    } # /elements
                                },# /output
                            }, #/elements
                        }, # /ProcessOutputs
                } # / elements
            } # /responce
        } # /e
