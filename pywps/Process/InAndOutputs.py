"""
Inputs and outputs of OGC WPS Processes
"""
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

import types,re, base64,logging
try:
    import magic
except:
    pass
from pywps import Exceptions

class Input:
    """Class WPS Input

    :param identifier: input identifier
    :param title: input title
    :param abstract: input description. 
    :param metadata: List of metadata references. 
    :param minOccurs: minimum number of occurrences. 
    :param maxOccurs: maximum number of occurrences. 
    :param type: one of "LiteralValue", "ComplexValue" or "BoundingBoxValue"

    .. attribute :: identifier

        input identifier

    .. attribute :: title

        input title

    .. attribute :: abstract 

        input abstract

    .. attribute :: metadata 

        input metadata reference

    .. attribute :: minOccurs 

        minimum occurense

    .. attribute :: maxOccurs

        maximum occurense

    .. attribute :: type

        type, one of "LiteralValue", "ComplexValue", "BoundingBoxValue"

    .. attribute :: value

        actual value of this input

    .. attribute :: ms
        
        :mod:`magic` cookie
        
    """

    identifier = None
    title = None
    abstract = None
    metadata = None
    minOccurs = None
    maxOccurs = None
    type = None
    value = None
    ms = None # magic mimeTypes

    def __init__(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,type=None):
        """Class constructor"""

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
        """Control in some way the input value from the client
        
        :param input: input value, parsed in :mod:`pywps.Parser.Execute`
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

    :param identifier: input identifier
    :param title: input title
    :param abstract: input description. Default: None
    :param uoms: List of string value units
    :param minOccurs: minimum number of occurrences. 
    :param maxOccurs: maximum number of occurrences. 
    :param allowedValues:  List of strings or lists of allowed values,
                which can be used with this input. You can set interval
                using list with two items, like::

                    (1,2,3,(5,9),10,"a",("d","g"))

                This will produce allowed values 1,2,3,10, "a" and
                any value between 5 and 9 or "d" and "g".

                If "*" is used, it means "any value"
    :param type: :class:`types.TypeType` value type, e.g. Integer, String, etc. you
                can uses the :mod:`types` module of python.
    :param default:  default value.
    :param spacing:

        .. note: PyWPS does not support spacing parameter yet

    .. attribute:: dataType

        :class:`types.TypeType` type of literal data. Default is integer

    .. attribute:: uoms

        list of units

    .. attribute: restrictedCharacters

        characters, which will be ommited in the input from security
        reasons

    .. attribute:: values

        allowed values
    
    .. attribute:: default

        default value

    ..  attribute:: spacing

        .. note:: this attribute is not used

    .. attribute:: uom
        
        units
    """

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
        """Class constructor"""
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
        """Set input value to this input
        
        :param input: input parsed by parsers
        :return: None or Error message
        """
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
        """Get the input value

        :returns: :attr:`value`
        """
        if self.value != None:
            return self.value
        elif self.default != None:
            return self.default
        else:
            return

    def _control(self,value):
        """Control input value for dangerous characters or types, like "#"

        :param value: value to be controled
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
            raise Exceptions.InvalidParameterValue(value)

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
    """ComplexInput type

    :param identifier: input identifier
    :param title: input title
    :param abstract: input description. 
    :param metadata: List of metadata references. 
    :param minOccurs: minimum number of occurencies. 
    :param maxOccurs: maximum number of occurencies. 
    :param formats: List of objects according to table 23 (page 25). E.g.

        ::

            [
                {"mimeType": "image/tiff"},
                {
                    "mimeType": "text/xml",
                    "encoding": "utf-8",
                    "schema":"http://foo/bar"
                }
            ]

    :param maxmegabites: Maximum input file size. Can not be bigger, as
            `maxfilesize` defined in global configuration file. 
    
    .. attribute:: maxFileSize 
    
        maximal allowed file size
        
    .. attribute:: formats
    
        list of supported formats
        
    .. attribute:: format
    
        the final format

    .. attribute:: value

        file name with the complex data
    """
    maxFileSize = None
    formats = None
    format = None

    def __init__(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,
                maxmegabites=5,formats=[{"mimeType":"text/xml"}]):
        """Class constructor"""

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

        try:
            self.ms = magic.open(magic.MAGIC_MIME)
            self.ms.load()
        except:
            pass

        return

    def setValue(self, input):
        """Set input value for this input

        :param input: parsed input value
        """
        
        # if HTTP GET was performed, the type does not have to be set
        if not input.has_key("type") and\
                (input["value"].find("http://") == 0 or input["value"].find("http%3A%2F%2F") == 0):
            input["asReference"] = True

        #self.value = input["value"]

        # download data
        if input.has_key("asReference") and input["asReference"] == True:
            self.downloadData(input["value"])
        else:
            self.storeData(input["value"])
        return

    def storeData(self,data):
        """Store data from given file. Not bigger, then
        :attr:`maxFileSize`
        
        :param data: the data, which should be stored
        :type data: string
        """
        import tempfile
        from os import curdir, rename

        outputName = tempfile.mktemp(prefix="pywpsInput",dir=curdir)
        fout = None
        try:
            fout=open(outputName,'wb')
        except IOError, what:
            self.onProblem("NoApplicableCode","Could not open file for writing")

        # NOTE: the filesize should be already checked in pywps/Post.py,
        # while getting the input XML file
        fout.write(data)
        fout.close()

        
        # check, if the file is binary or not
        if self.format["mimeType"].find("text") == -1:
            # it *should* be binary, is the file really binary?
            # if so, convert it to binary using base64
            if self.ms and self.ms.file(fout.name).find("text") > -1: 
                rename(fout.name,fout.name+".base64")
                try:
                    base64.decode(open(fout.name+".base64"),
                                open(fout.name,"w"))
                except:
                    self.onProblem("NoApplicableCode",
                    "Could not convert text input to binary using base64 encoding.")

                

        # check the mimeType again
        if self.ms:
            self.checkMimeType(fout.name,self.ms.file(fout.name))
            
        resp = self._setValueWithOccurence(self.value, outputName)
        if resp:
            return resp
        return

    def getValue(self, asFile=False):
        """Get this value
        
        :param asFile: return the value not as file name (default), but as  file object
        :return: :attr:`value`
        :rtype: string or file
        """

        if asFile == True:
            return open(self.value,"r")
        else:
            return self.value

    def downloadData(self, url):
        """Download data from given url. Do not download more, then
        :attr:`maxFileSize`

        :param url: URL where the data are lying
        """
        import urllib, tempfile
        from os import curdir

        try:
            inputUrl = urllib.urlopen(urllib.unquote(url))
        except IOError,e:
            self.onProblem("NoApplicableCode",e)

        outputName = tempfile.mktemp(prefix="pywpsInput",dir=curdir)

        fout = None
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
                        url)
        fout.close()

        # check the mimetypes
        if self.ms:
            self.checkMimeType(fout.name,self.ms.file(fout.name))

        resp = self._setValueWithOccurence(self.value, outputName)
        if resp:
            return resp
        return
    
    def onProblem(self,what, why):
        """Empty method, called, when there was any problem with the input.
        
        :param what: Message with error description
        :param why: Error code
        """
        pass

    def checkMimeType(self,fileName,mimeType):
        """Check, if the given mimetype is in self.formats

        :param fileName:
        :param mimeType:
        """
        mimeTypes = "";
        for format in self.formats:
            mimeTypes += format["mimeType"] + " ";
            if self.ms.file(fileName) in format["mimeType"]:
                self.format = format
                return
        if self.format == None:
            self.onProblem("InvalidParameterValue",
                "Files mimeType ["+ self.ms.file(fileName) +
                " does not correspond with allowed mimeType values, which can be on from ["+ mimeTypes+"]")


    def onMaxFileSizeExceeded(self, what):
        """Empty method, called, when there was any problem with the input.
        
        :param what: Error code
        """
        pass

    def onNotFound(self,what):
        """Empty method, called, when there was any problem with the input.
        
        :param what: Error code
        """
        pass

class BoundingBoxInput(Input):
    """Add BoundingBox input

    :param identifier: input identifier
    :param title: input title
    :param abstract: input description. 
    :param metadata: List of metadata references. 
    :param minOccurs: minimum number of occurrences. 
    :param maxOccurs: maximum number of occurrences. 
    :param crss: List of strings supported coordinate systems.

    .. attribute:: crss
        
        Supported coordinate systems

    .. attribute:: dimensions
        
        Bbox dimensions

    .. attribute:: crs
        
        Used coordinate system

    .. attribute:: coords
        
        List of list of coordinates in form::

            (
                (minx,miny [, minz,  [...] ] ),
                (maxx,maxy [, minz, [...] ])
                [, (maxx,maxy [, maxz, [...] ]),
                    [, ...]
                ]
            )

        So, most common case::

            ((minx,miny),(maxx, maxy))
        
    """

    crss = None
    dimensions = None
    crs = None
    coords = None

    def __init__(self,identifier,title,abstract=None,
                metadata=[],minOccurs=1,maxOccurs=1,dimensions=None,
                crss=[]):
        """Class constructor"""
        Input.__init__(self,identifier,title,abstract=abstract,
                metadata=metadata,minOccurs=minOccurs,maxOccurs=maxOccurs,type="BoundingBoxValue")
        
        self.crss = crss
        self.dimensions = dimensions
        self.crs = self.crss[0]

        return

    def setValue(self,input):
        """Set value of this input

        :param input: bounding box parsed input in format::
            
                {identifier:"id",dimensions:2, value:(minx,miny,maxx,maxy),
                crs:"epsg4326"}

            or similar

        :type value: tuple
        """


        class BBOX:
            """BBOX class is designed to contain attributes of Bounding
            Box, such as

            coords
            dimensions
            crs
            """
            coords = []
            dimensions = None
            crs = None

        # define new instance
        value = BBOX()


        # convert possible string value to array
        if type(input["value"]) == type(""):
            input["value"] = input["value"].split(",")

        # set dimensions
        if input.has_key("crs"):
            value.crs = input["crs"]
            
        # set dimensions
        if input.has_key("dimensions"):
            value.dimensions = int(input["dimensions"])
        else:
            # from the KVP
            coordsLen = len(input["value"])
                
            # last one is crs, take it
            if len(input["value"])%2 == 1:
                coordsLen = coordsLen-1
                value.crs = input["value"][-1]
                input["value"] = input["value"][:-1]

            value.dimensions = int(coordsLen/2)

        value.coords = self._getCoords(input["value"])

        resp = self._setValueWithOccurence(self.value, value)
        if resp:
            return resp

    def _getCoords(self,coords):
        lowercorner = []
        uppercorner = []
        dimensions = int(len(coords)/2)
        lowercorner = map(lambda x: float(x), coords[:dimensions])
        uppercorner = map(lambda x: float(x), coords[dimensions:])
        return (lowercorner, uppercorner)

    def getValue(self):
        """Get this value
        
        :returns: bounding box in format::
            
                (minx, miny, maxx, maxy)
                
        """
        return self.value

class Output:
    """Class WPS Input

    :param identifier: input identifier
    :param title: input title
    :param abstract: input description. 
    :param metadata: List of metadata references. 
    :param type: one of "LiteralValue", "ComplexValue"  or "BoundingBoxValue"
    :param asReference:  whether this output will be given back as
            reference or as file
    :type asReference: boolean

    .. attribute:: identifier

    .. attribute:: title

    .. attribute:: abstract

    .. attribute:: metadata

    .. attribute:: type

        "ComplexValue", "LiteralValue", "BoundingBoxValue"

    .. attribute:: asReference
    
        this output should be formated as reference (URL) or give the file
        content back 

    .. attribute:: value

        output value
        
    .. attribute:: ms
    
        mime cookie

    """
    identifier = None
    title = None
    abstract = None
    metadata = None
    type = None
    asReference = None
    value = None
    ms = None # magic mimeTypes

    def __init__(self,identifier,title,abstract=None,
                metadata=[],type=None, asReference=False):
        """Class Constructor"""
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
    """Literal output class

    :param identifier: input identifier
    :param title: input title
    :param abstract: input description. Default: None
    :param metadata: List of meatadata references
    :param uoms: List of string values units
    :param dataType: :class:`types.TypeType` value type, e.g. Integer, String, etc. you
                can uses the "types" module of python.
    :param default: default value.
    :param asReference: whether this output will be given back as
            reference or as file
    """

    def __init__(self,identifier,title,abstract=None,
                metadata=[], uoms=(), dataType = types.StringType, 
                default=None, asReference=False):
        """Class Constructor"""
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
    """Complex value output
    
    :param identifier: output identifier
    :param title: output title
    :param metadata: List of metadata references
    :param formats: List of format structure according to table 23 (page
        25). E.g.::

                [
                    {"mimeType": "image/tiff"},
                    {
                        "mimeType": "text/xml",
                        "encoding": "utf-8",
                        "schema":"http://foo/bar"
                    }
                ]

    :param asReference: whether this output will be given back as
            reference or as file
    :param projection: proj4 text, used for the proj init parameter,
            e.g. "epsg:4326", used for mapserver
    :param bbox: of 4 elements (minx,miny,maxx,maxy), used for
            mapserver
    :param useMapscript: For this output, setup special MapServer
        MapFile, and give the output back as link to it, WMS, WCS or WFS

    .. attribute :: formats

        list of supported formats.::
            
            [
                {
                    'mimeType':'text/xml',
                    'encoding':'utf-8',
                    'schema':'http://schemas.opengis.net/gml/3.2.1/gml.xsd'
                },
                {
                    ....
                }
            ]

    .. attribute :: format

        file format of the input file

    .. attribute :: projection

        file projection (used by mapserver)

    .. attribute :: bbox

        data bounding box (used by mapserver)

    .. attribute :: width
    .. attribute :: height
    .. attribute :: useMapscript
    
        create dynamicaly mapfile and setup MapServer environment
        
    """
    formats = None
    format = None
    projection = None
    bbox = None
    width = None
    height = None
    useMapscript = False

    def __init__(self,identifier,title,abstract=None,
                metadata=[], formats=[{"mimeType":"text/xml"}],
                asReference=False, projection=None, bbox=None, useMapscript
                =  False):
        """Class constructor"""
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
        
        self.projection = projection
        self.bbox = bbox

        try:
            self.ms = magic.open(magic.MAGIC_MIME)
            self.ms.load()
            self.useMapscript = useMapscript
        except:
            pass

        return

    def setValue(self, value):
        """Set the output value

        :param value: value to be returned (file name or file itself)
        :type value: string or file
        """

        if type(value) == types.StringType:
            self.value = value
        elif type(value) == types.FileType:
            self.value = value.name
        # TODO add more types, like Arrays and lists for example
        else:
            raise Exception("Output type '%s' of '%s' output not known" %\
                    (type(value),self.identifier))


class BoundingBoxOutput(Output):
    """Bounding box ouput 
        
    :param identifier: input identifier
    :param title: input title
    :param abstract: input description. 
    :param crss: List of strings of supported coordinate systems.
    :param dimensions: number of dimensions
    :param asReference:  whether this output will be given back as
            reference or as file
        
    .. attribute:: crss
        
        list of supporte coordinate systems

    .. attribute:: crs

        coordinate system

    .. attribute:: dimensions

        bbox dimensions

    .. attribute:: coords
    """
    crss = None
    crs = None
    dimensions = None
    value = None

    def __init__(self,identifier,title,abstract=None,
                metadata=[], crss=[], dimensions=None, asReference=False):
        """BoundingBox output"""
        Output.__init__(self,identifier,title,abstract=None,
                metadata=[],type="BoundingBoxValue",asReference=asReference)
        self.crss = crss
        self.crs = crss[0]
        self.dimensions = dimensions
        self.value = []
        return

    def setValue(self, value):
        """Set value to bbox output

        :param value: boundngbox::
        
            (minx,miny,maxx,maxy)

        """

        if len(value) != 2:
            raise Exception("Bounding box value is wrong, it has to have a form: "+
                    "[[minx,miny],[maxx,maxy]]")

        # from the object
        newval = None
        try:
            newvalue = value.coords
        # directly
        except:
            newvalue = value


        if type([]) in map(lambda x: type(x), newvalue):
            self.value = newvalue
        else:
            dimensions = int(len(newvalue))
            self.value = []
            for i in range(dimensions):
                self.value.append(newvalue[i*dimensions,i*dimensions+dimensions])
