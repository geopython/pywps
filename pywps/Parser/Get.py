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

import types,sys

class Get:
    wps = None
    fieldStorage = None
    unparsedInputs =  {}
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
        maxInputLength = self.wps.config.getint("server","maxinputparamlength")

        # converting all key names to lowercase
        for i in range(len(keys)):
            newKey = keys[i].lower()
            newValue = ""

            # if there are multiple inputs with same key, take the last one
            if (type(fieldStorage.getvalue(keys[i]))) == types.ListType:
                newValue = fieldStorage.getvalue(keys[i])[-1].strip()
            else:
                newValue = fieldStorage.getvalue(keys[i]).strip()

            # if maxInputLength > 0, cut
            if (maxInputLength > 0):
                newValue = newValue[0:maxInputLength]
            keys[i] = newKey
            self.unparsedInputs[newKey] = newValue

        try:
            self.controlInputs()
        except KeyError,e:
            raise self.wps.exceptions.MissingParameterValue(e.message)



    def controlInputs(self):
            
        key = None
        value = None

        for key in self.unparsedInputs.keys():
            value = self.unparsedInputs[key]

            # check size
            if self.wps.maxInputLength > 0 and\
                    len(value) > self.wps.maxInputLength:
               
                raise FileSizeExceeded(key)


        if self.unparsedInputs[self.SERVICE].lower() != self.WPS:
            raise self.wps.exceptions.InvalidParameterValue(
                    self.unparsedInputs[self.SERVICE])

        if self.unparsedInputs["request"].lower() ==\
           self.GET_CAPABILITIES:
            import GetCapabilities 
            self.requestParser = GetCapabilities.Get(self.wps)
        elif self.unparsedInputs["request"].lower() ==\
           self.DESCRIBE_PROCESS:
            import DescribeProcess 
            self.requestParser = DescribeProcess.Get(self.wps)
        elif self.unparsedInputs["request"].lower() ==\
           self.EXECUTE:
            import Execute 
            self.requestParser = Execute.Get(self.wps)
        else:
            raise self.wps.exceptions.InvalidParameterValue(
                    self.unparsedInputs["request"])

        self.requestParser.parse(self.unparsedInputs)
        return
