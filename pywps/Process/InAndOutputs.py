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

import types,re
from pywps import Exceptions

class Input:
    """Class WPS Input"""
    identifier = None
    title = None
    abstract = None
    metadata = None
    minOccurs = None
    maxOccurs = None
    type = None
    value = None

    def __init__(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,type=None):
        """Input initialization

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description. 
                default: None
        metadata List of {Dict} {key:value} pairs. 
                default: None
        minOccurs {Integer} minimum number of occurrences. 
                default: 1
        maxOccurs {Integer} maximum number of occurrences. 
                default: 1
        type {String} one of "LiteralValue", "ComplexValue"  or
                "BoundingBoxValue"
                default: None
        """
        self.identifier = identifier
        self.title = title
        self.abstract = abstract
        self.metadata = metadata

        self.minOccurs = minOccurs
        self.maxOccurs = maxOccurs
        self.type = type
        self.value = None
        return
    
    def setValue(self,input):
        """
        Control in some way the input value
        
        Parameters:
        input {pywps.Process.Input} 
        """

        for inpt in input["value"]:
            resp =  self._setValueWithOccurence(self.value, inpt)
            if resp:
                return resp
        return

    def _setValueWithOccurence(self,oldValues, newValue):
        """Check min and max occurrence and set this.value"""

        if self.maxOccurs > 1:
            if not oldValues:
                oldValues =  [newValue]
            else:
                if self.maxOccurs > len(oldValues):
                    oldValues.append(newValue)
                else:
                    return "Too many occurrences of input [%s]: %s" % (self.identifier,newValue)
        else:
            oldValues = newValue

        self.value = oldValues
        return

    def getValue(self, idx=0):
        """Get this value """

        return self.value

class LiteralInput(Input):
    """Literal input type of input. 
    
    NOTE: The spacing parameter was not used yet"""
    dataType = None
    uoms = None
    restrictedCharacters = ['\\',"#",";", "&","!"]
    values = None
    default = None
    spacing = None
    uom = None

    def __init__(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,dataType=types.StringType,
                uoms=(),values=("*"),spacing=None,default=None):
        """Init the literal value type of input

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description. Default: None
                    default: None
        uoms List of {String} value units
                    default: ()
        minOccurs {Integer} minimum number of occurrences. 
                    default: 1
        maxOccurs {Integer} maximum number of occurrences. 
                    default: 1
        allowedValues  List of {String} or {List} list of allowed values,
                    which can be used with this input. You can set interval
                    using list with two items, like:

                    (1,2,3,(5,9),10,"a",("d","g"))

                    This will produce allowed values 1,2,3,10, "a" and
                    any value between 5 and 9 or "d" and "g".

                    If "*" is used, it means "any value"
                    default: ("*")
        type {types.TypeType} value type, e.g. Integer, String, etc. you
                    can uses the "types" module of python.
                    default: types.StringType
        default {Any} default value.
                    default: None
        spacing {Float} 
                    default: None
        """
        Input.__init__(self,identifier,title,abstract=abstract,
                metadata=[],minOccurs=minOccurs,maxOccurs=maxOccurs,type="LiteralValue")
        
        self.dataType = dataType
        self.uoms = uoms
        self.restrictedCharacters = ['\\',"#",";", "&","!"]
        if type(values) == types.StringType:
            self.values = (values)
        elif type(values) == types.ListType:
            self.values = values
        self.default = default
        self.spacing = spacing
        self.uom = None 
        return

    def setValue(self, input):
        """Set input value value to this input"""

        if type(input["value"]) == types.ListType:
            for inpt in input["value"]:
                resp = self._setValueWithOccurence(self.value, self._control(inpt))
                if resp:
                    return resp
        else:
            resp = self._setValueWithOccurence(self.value, self._control(input["value"]))
            if resp:
                return resp

    def getValue(self):
        """
        Get the input.value
        """
        if self.value:
            return self.value
        elif self.default:
            return self.default
        else:
            return

    def _control(self,value):
        """
        Control input value for dangerous characters or types, like "#"

        Parameters: value
        """

        # ugly characters
        for char in self.restrictedCharacters:
            if value.find(char) > -1:
                raise Exceptions.InvalidParameterValue(value)

        # type 
        try:
            if self.dataType == types.FloatType:
                value = float(value)
            elif self.dataType == types.StringType:
                value = str(value)
            elif self.dataType == types.IntType:
                value = int(value)
            elif self.dataType == types.BooleanType:
                value = bool(value)
            #TODO other types missing
        except (ValueError), e:
            raise Exceptions.InvalidParameterValue(value,e)

        # value list
        if "*" in self.values:
            return value
        
        for allowed in self.values:
            if type(allowed) == types.ListType:
                if allowed[0] <= value <= allowed[-1]:
                    if self.spacing:
                        if (value - allowed[0])%spacing == 0:
                            return value
                    else:
                        return value
                    
            else:
                if str(value) == str(allowed):
                    return value
            
        raise Exceptions.InvalidParameterValue(value)

class ComplexInput(Input):
    """ComplexInput type"""
    maxFileSize = None
    formats = None
    format = None

    def __init__(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,
                maxmegabites=5,formats=[{"mimeType":"text/xml"}]):
        """ Init complex input

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description. 
                default: None
        metadata List of {Dict} {key:value} pairs. 
                default: None
        minOccurs {Integer} minimum number of occurencies. 
                default: 1
        maxOccurs {Integer} maximum number of occurencies. 
                default: 1
        formats List of {Dict} according to table 23 (page 25). E.g.
                    [
                        {"mimeType": "image/tiff"},
                        {
                            "mimeType": "text/xml",
                            "encoding": "utf-8",
                            "schema":"http://foo/bar"
                        }
                    ]
                default: [{"mimeType":"text/xml"}]
        maxmegabites {Float} Maximum input file size. Can not be bigger, as
                defined in global configuration file. 
                default: 5
        """

        Input.__init__(self,identifier,title,abstract=abstract,
                metadata=[],minOccurs=minOccurs,maxOccurs=maxOccurs,type="ComplexValue")
        
        if maxmegabites:
            self.maxFileSize = float(maxmegabites)*1024*1024
        else:
            self.maxFileSize = None


        if type(formats) == types.StringType:
            formats = [{"mimeType":formats,"encoding":None,"schema":None}]
        elif type(formats) == types.DictType:
            formats = [formats]

        for format in formats:
            if not "encoding" in format.keys():
                format["encoding"] = None
            if not "schema" in format.keys():
                format["schema"] = None

        self.formats = formats
        self.format = self.formats[0]
        return

    def setValue(self, input):
        """Set input value for this input"""
        
        # if HTTP GET was performed, the type does not have to be set
        if not input.has_key("type") and\
                input["value"].find("http://") == 0:
            input["asReference"] = True

        #self.value = input["value"]

        # download data
        if input["asReference"] == True:
            self.downloadData(input["value"])
        else:
            self.storeData(input["value"])
        return

    def storeData(self,data):
        """To be redefined in each instance"""
        pass

    def getValue(self):
        """Get this value"""

        return self.value

    def downloadData(self, url):
        """Download data from given url. Do not download more, then
        self.maxmegabites

        Parameters:
        url {String} URL where the data are lying
        """
        import urllib, tempfile
        from os import curdir

        try:
            inputUrl = urllib.urlopen(url)
        except IOError,e:
            self.onProblem("NoApplicableCode",e)

        outputName = tempfile.mktemp(prefix="pywpsInput",dir=curdir)

        try:
            fout=open(outputName,'wb')
        except IOError, what:
            self.onProblem("NoApplicableCode","Could not open file for writing")

        # ok, get the file!
        size = 0
        while 1:
            # reading after 100kB
            size += 100000
            chunk = inputUrl.read(100000)

            # something is wrong
            if re.search("not found",chunk,re.IGNORECASE):
                self.onProblem("NoApplicableCode",
                    "Remote server says: [%s] not found" % (url))

            # everything is here, break
            if not chunk: 
                break
            fout.write (chunk)

            # TOO BIG! STOP THIS
            if size > self.maxFileSize: 
                self.onProblem("FileSizeExceeded","Maximum file size is "+
                        str(self.maxFileSize/1024/1024)+" MB for input "+
                        uNNrl)
        fout.close()

        resp = self._setValueWithOccurence(self.value, outputName)
        if resp:
            return resp
        return
    
    def onProblem(self,what, why):
        """Empty method, called, when there was any problem with the input.
        
        Parameters:
        what {String} Message with error description
        why {String} Error code
        """
        pass

    def onMaxFileSizeExceeded(self, why):
        """Empty method, called, when there was any problem with the input.
        
        Parameters:
        why {String} Error code
        """
        pass

    def onNotFound(self,what):
        """Empty method, called, when there was any problem with the input.
        
        Parameters:
        what {String} Error code
        """
        pass

class BoundingBoxInput(Input):
    crss = None
    dimensions = None
    crs = None
    minx = None
    miny = None
    maxx = None
    maxy = None

    def __init__(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,dimensions=2,
                crss=[]):
        """Add BoundingBox input

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description. 
                default: None
        metadata List of {Dict} {key:value} pairs. 
                default: None
        minOccurs {Integer} minimum number of occurrences. 
                default: 1
        maxOccurs {Integer} maximum number of occurrences. 
                default: 1
        crss List of {String} supported coordinate systems.
                default: ["EPSG:4326"]
        """
        Input.__init__(self,identifier,title,abstract=abstract,
                metadata=metadata,minOccurs=minOccurs,maxOccurs=maxOccurs,type="BoundingBoxValue")
        
        self.crss = crss
        self.dimensions = dimensions
        self.crs = self.crss[0]
        self.minx = None
        self.minx = None
        self.maxx = None
        self.maxy = None
        return

    def setValue(self,value):
        """Set value of this input

        Parameters:
        value {Tuple} (minx,miny,maxx,maxy)
        """

        resp = self._setValueWithOccurence(self.value,
                self._control(value))
        if resp:
            return resp

        if type(self.value) == type([]):
            if len(self.value) == 1:
                self.minx[value[0]]
                self.minx[value[1]]
                self.maxx[value[2]]
                self.maxy[value[3]]
            else:
                self.minx.append(value[0])
                self.minx.append(value[1])
                self.maxx.append(value[2])
                self.maxy.append(value[3])
        else:
            self.minx = value[0]
            self.minx = value[1]
            self.maxx = value[2]
            self.maxy = value[3]

    def getValue(self):
        """Get this value"""
        return (self.minx,self.miny,self.maxx,self.maxy)

class Output:
    """Class WPS Input"""
    identifier = None
    title = None
    abstract = None
    metadata = None
    type = None
    asReference = None
    value = None

    def __init__(self,identifier,title,abstract=None,
                metadata=[],type=None, asReference=False):
        """Output initialization

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description. 
                default: None
        metadata List of {Dict} {key:value} pairs. 
                default: None
        type {String} one of "LiteralValue", "ComplexValue"  or
                "BoundingBoxValue"
                default: None
        asReference {Boolean} whether this output will be given back as
                reference or as file
                default: False
        """
        self.identifier = identifier
        self.title = title
        self.abstract = abstract
        self.metadata = metadata
        self.type = type
        self.asReference = asReference
        self.value = None
        return

    def setValue(self,value):
        """Set this output value"""
        self.value = value

class LiteralOutput(Output):
    """Literal output class"""
    def __init__(self,identifier,title,abstract=None,
                metadata=[], uoms=(), dataType = types.StringType, 
                default=None, asReference=False):
        """
        Output of type LiteralValue

        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description. Default: None
                    default: None
        metadata List of {Dict} additional metadata
                    default: ()
        uoms List of {String} value units
                    default: ()
        dataType {types.TypeType} value type, e.g. Integer, String, etc. you
                    can uses the "types" module of python.
                    default: types.StringType
        default {Any} default value.
                    default: None
        asReference {Boolean} whether this output will be given back as
                reference or as file
                default: False
        """
        Output.__init__(self,identifier,title,abstract=None,
                metadata=[],type="LiteralValue",asReference=asReference)
        
        self.uoms = uoms
        if len(self.uoms) > 0:
            self.uom = self.uoms[0]
        else:
            self.uom = None
        self.default = default
        self.dataType = dataType
        return

class ComplexOutput(Output):
    """Complex value output"""
    formats = None
    format = None

    def __init__(self,identifier,title,abstract=None,
                metadata=[], formats=[{"mimeType":"text/xml"}],
                asReference=False):
        """Complex output

        Mandatory parameters:
        identifier {String} output identifier
        title {String} output title

        Optional parameters:
        metadata List of {Dict} {key:value} pairs. 
                default: None
        formats List of {Dict} according to table 23 (page 25). E.g.
                    [
                        {"mimeType": "image/tiff"},
                        {
                            "mimeType": "text/xml",
                            "encoding": "utf-8",
                            "schema":"http://foo/bar"
                        }
                    ]
                default: [{"mimeType":"text/xml"}]
        asReference {Boolean} whether this output will be given back as
                reference or as file
                default: False
        """
        Output.__init__(self,identifier,title,abstract=None,
                metadata=[],type="ComplexValue", asReference=asReference)
        
        if type(formats) == types.StringType:
            formats = [{"mimeType":formats,"encoding":None,"schema":None}]
        elif type(formats) == types.DictType:
            formats = [formats]

        for format in formats:
            if not "encoding" in format.keys():
                format["encoding"] = None
            if not "schema" in format.keys():
                format["schema"] = None

        self.formats = formats
        self.format = formats[0]
        return

class BoundingBoxOutput(Output):
    crss = None
    crs = None
    dimensions = None
    minx = None
    miny = None
    maxx = None
    maxy = None

    def __init__(self,identifier,title,abstract=None,
                metadata=[], crss=[], dimensions=2, asReference=False):
        """BoundingBox output
        
        Mandatory parameters:
        identifier {String} input identifier
        title {String} input title

        Optional parameters:
        abstract {String} input description. 
                default: None
        crss List of {String} supported coordinate systems.
                default: ["EPSG:4326"]
        dimensions {Integer} number of dimensions
                default: 2
        asReference {Boolean} whether this output will be given back as
                reference or as file
                default: False
        """
        Output.__init__(self,identifier,title,abstract=None,
                metadata=[],type="BoundingBoxValue",asReference=asReference)
        self.crss = crss
        self.crs = crss[0]
        self.dimensions = dimensions
        self.minx = None
        self.miny = None
        self.maxx = None
        self.maxy = None
        return

    def setValue(self, value):
        """Set value to bbox output

        Parameters:
        value {Tuple} (minx,miny,maxx,maxy)
        """

        if len(value) != 4:
            raise Exception("Bounding box value is wrong, it has to have a form: "+
                    "[minx,miny,maxx,maxy]")
        self.value = value
        self.minx  = value[0]
        self.miny  = value[1]
        self.maxx  = value[2]
        self.maxy  = value[3]
