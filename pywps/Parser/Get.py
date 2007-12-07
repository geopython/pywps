# Author:	Jachym Cepicky
#        	http://les-ejk.cz
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

#import wpsExceptions

import types

class Get:
    wps = None
    fieldStorage = None
    inputValues =  {}
    GET_CAPABILITIES = "getcapabilities"
    DESCRIBE_PROCESS = "describeprocess"
    EXECUTE = "execute"
    SERVICE = "service"
    WPS = "wps"
    requestParser = None

    def __init__(self,wps):
        self.wps = wps

    def parse(self,fieldStorage):
        
        key = None
        keys = fieldStorage.keys()

        # converting all key names to lowercase
        for (i = 0; i < len(keys); i++):
            newKey = keys[i].lower()

            if (type(fieldStorage.getvalue(keys[i]))) == types.ListType:
                self.inputValues[newKey] = fieldStorage.getvalue(keys[i])[-1].strip()
            else:
                self.inputValues[newKey] = fieldStorage.getvalue(keys[i]).strip()
            keys[i] = newKey

        try:
            self.controlInputs()
        except Error,e: #!!! this should be done with help of WPS exeptions
            print >>sys.stderr, "ERROR: e"


    def controlInputs():
            
        key = None
        value = None

        for key in self.inputValues.keys()
            value = self.inputValues(key)

            # check size
            if self.wps.maxInputLength > 0 and\
                    len(value) > self.wps.maxInputLength:
               
                raise FileSizeExceeded(key)


        if self.inputValues[self.SERVICE].lower() != self.WPS:
            raise ValueError("Service '%s' not supported!" %\
                    (self.inputValues[self.SERVICE]))
            # FIXME !!!! Should be InvalidInputValue or somthing like this

        if self.inputValues["request"].lower() ==\
           self.GET_CAPABILITIES:
            import GetCapabilities 
            self.requestParser = GetCapabilities.Get(self.wps)

        elif self.inputValues["request"].lower() ==\
           self.DESCRIBE_PROCESS:
            import DescribeProcess 
            self.requestParser = DescribeProcess.Get(self.wps)
        elif self.inputValues["request"].lower() ==\
           self.EXECUTE:
            import Execute 
            self.requestParser = Execute.Get(self.wps)
        else:
            raise ValueError("Request type '%s' unknown!" % \
                    (self.inputValues["request"])
            # FIXME !!!! Should be InvalidInputValue or somthing like this
        self.requestParser.parse(self.inputValues)
        return
