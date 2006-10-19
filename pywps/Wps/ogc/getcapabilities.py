"""
GetCapabilities definition file

Description:
    This file contains structure describing the GetCapabilities response
    and request. See OGC 05-008 for details

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
#       	http://les-ejk.cz
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
# 

class WPS:
    def __init__(self):
        self.namespaces = {
            "ows":"http://www.opengeospatial.net/ows",
            "wps":"http://www.opengeospatial.net/wps",
            "xsi":"http://www.w3.org/2001/XMLSchema-instance",
            "xlink":"http://www.w3.org/1999/xlink",
        }
        
        self.schemalocation = {
          "wps":"http://www.bnhelp.cz/schema/wps/0.4.0/wpsGetCapabilities.xsd",
        }
        
        self.gc = {
            'order': ['ServiceIdentification','ServiceProvider',
                'OperationsMetadata','ProcessOfferings'],
            'elements':{
                'ServiceIdentification':{
                    'ns':'ows:',
                    'order': ['Title','Abstract','Keywords','ServiceType',
                            'ServiceTypeVersion','Fees','AccessConstraints'],
                    'elements': {
                        'Title':{
                            'oblig':'m',
                            'ns':'ows:'
                            },
                        'Abstract':{
                            'oblig':'o',
                            'ns':'ows:'
                            },
                        'Keywords':{
                            'oblig':'o',
                            'ns':'ows:',
                            },
                        'ServiceType':{
                            'oblig':'m',
                            'ns':'ows:'
                            },
                        'ServiceTypeVersion':{
                            'oblig':'m',
                            'ns':'ows:'
                            },
                        'Fees':{
                            'oblig':'o',
                            'ns':'ows:'
                            },
                        'AccesConstraints':{
                            'oblig':'o',
                            'ns':'ows:'
                            },
                        }
                    }, #  Service Identification

                    'ServiceProvider':{
                        'oblig':'m',
                        'ns':'ows:',
                        'order':['ProviderName',
                                 'ServiceContact',],
                        'elements':{
                            'ProviderName':{
                                'oblig':'m',
                                'ns':'ows:'
                                },
                            'ServiceContact': {
                                'oblig':'m',
                                'ns':'ows:',
                                'order':['IndividualName','PositionName',
                                        'ContactInfo','Role'],
                                'elements':{
                                    'IndividualName':{
                                        'oblig':'m',
                                        'ns':'ows:'
                                        },
                                    'PositionName':{
                                        'oblig':'m',
                                        'ns':'ows:'
                                        },
                                    'ContactInfo':{
                                        'oblig':'m',
                                        'ns':'ows:',
                                        'elements': {
                                            'Address':{
                                                'ns':'ows:',
                                                'oblig':'m',
                                                'order':['DeliveryPoint',
                                                        'City',
                                                        'PostalCode',
                                                        'Country',
                                                        'ElectronicMailAddress'],
                                                'elements':{
                                                    'DeliveryPoint':{
                                                        'oblig':'m',
                                                        'ns':'ows:'
                                                        },
                                                    'City':{
                                                        'oblig':'m',
                                                        'ns':'ows:'
                                                        },
                                                    'PostalCode':{
                                                        'oblig':'m',
                                                        'ns':'ows:'
                                                        },
                                                    'Country':{
                                                        'oblig':'m',
                                                        'ns':'ows:'
                                                        },
                                                    'ElectronicMailAddress':{
                                                        'oblig':'m',
                                                        'ns':'ows:'
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    'Role':{
                                        'oblig':'m',
                                        'ns':'ows:',
                                        },
                                    },
                                },
                            },
                        },

                    'OperationsMetadata':{
                            'ns':'ows:',
                            'order':['Operation','Parameter','Constraint',
                                'Metadata','ExtendedCapabilities'],
                            'elements': {
                                'Operation': {
                                    'ns': 'ows:',
                                    'values':['GetCapabilities','DescribeProcess','Execute'],
                                    'attributes': {
                                        'name': {
                                            'oblig':'m',
                                            'ns':'ows:'
                                            },
                                        },
                                    'elements': {
                                        'DCP':{
                                            'oblig':'m',
                                            'ns':'ows:',
                                            'HTTP':{
                                                'oblig':'m',
                                                'ns':'ows:',
                                                'elements':{
                                                    'Get': {
                                                        'oblig':'o',
                                                        'ns': 'ows:',
                                                        'attributes': {
                                                            'href': {
                                                                'oblig':'m',
                                                                'ns':'xlink:',
                                                                }
                                                        },
                                                    },
                                                    'Post': {
                                                        'oblig':'o',
                                                        'ns': 'ows:',
                                                        'attributes': {
                                                            'href': {
                                                                'oblig':'m',
                                                                'ns':'xlink:',
                                                                }
                                                            },
                                                        },
                                                    },
                                                }, 
                                            },
                                        'Parameter':{ # table 15
                                            'oblig':'o',
                                            'ns':'ows:',
                                            'content':{
                                                'Name':{
                                                    'oblig':'m',
                                                    'ns':'ows:',
                                                    },
                                                'Value':{
                                                    'oblig':'o',
                                                    'ns':'ows:',
                                                    },
                                                'Metadata':{
                                                    'oblig':'o',
                                                    'ns':'ows:',
                                                    },
                                            }
                                        },
                                        'Constraint':{ # table 15
                                            'oblig':'o',
                                            'ns':'ows:',
                                            'content':{
                                                'Name':{
                                                    'oblig':'m',
                                                    'ns':'ows:',
                                                    },
                                                'Value':{
                                                    'oblig':'o',
                                                    'ns':'ows:',
                                                    },
                                                'Metadata':{
                                                    'oblig':'o',
                                                    'ns':'ows:',
                                                    },
                                            }
                                        },
                                        'Metadata':{
                                            'oblig':'o',
                                            'ns':'ows:'
                                            },
                                        }
                                    },
                                'Parameter':{ # table 15
                                    'oblig':'o',
                                    'ns':'ows:',
                                    'content':{
                                        'Name':{
                                            'oblig':'m',
                                            'ns':'ows:',
                                            },
                                        'Value':{
                                            'oblig':'o',
                                            'ns':'ows:',
                                            },
                                        'Metadata':{
                                            'oblig':'o',
                                            'ns':'ows:',
                                            },
                                    }
                                },
                                'Constraint':{ # table 15
                                    'oblig':'o',
                                    'ns':'ows:',
                                    'content':{
                                        'Name':{
                                            'oblig':'m',
                                            'ns':'ows:',
                                            },
                                        'Value':{
                                            'oblig':'o',
                                            'ns':'ows:',
                                            },
                                        'Metadata':{
                                            'oblig':'o',
                                            'ns':'ows:',
                                            },
                                    }
                                },
                                'Metadata':{
                                    'oblig':'o',
                                    'ns':'ows:'
                                    },
                                'ExtendedCapabilities':{
                                    'oblig':'o',
                                    'ns':'ows:'
                                    },
                            },
                    }, #/OperationMetadata

                    'ProcessOfferings': {
                        'ns':"",
                        'Process':{
                            'ns':"",
                            'attributes': {
                                'processVersion': {
                                    'ns':"",
                                    }
                                },
                            'order': ['Identifier','Title','Abstract',
                                'Metadata'],
                            'elements': {
                                'Identifier': {
                                    'oblig':'m',
                                    'ns':"ows:",
                                    },
                                'Title': {
                                    'oblig':'m',
                                    'ns':"ows:",
                                    },
                                'Abstract':{
                                    'oblig':'o',
                                    'ns':"ows:",
                                    },
                                'Metadata':{
                                    'oblig':'o',
                                    'ns':"ows:",
                                    'attributes': {
                                        'title': {
                                            'oblig':'o',
                                            'ns':"xlink:",
                                            }
                                        }
                                    },
                                }
                            }
                        }
                    } # /elements
            } # /getCapabilities
        return


