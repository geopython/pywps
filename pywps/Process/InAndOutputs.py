"""
Inputs and outputs of OGC WPS Processes
"""
# Author:    Jachym Cepicky
#            http://les-ejk.cz
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

import os,types,re, base64,logging
from pywps import Exceptions
import sys
import urllib, tempfile

LOGGER = logging.getLogger(__name__)

try:
    import magic
except:
    LOGGER.debug("Could not import magic module")

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

    def _setValueWithOccurence(self, oldValues, newValue):
        """Check max occurrence and set this.value"""
        maxOccursViolated = False

        if (self.maxOccurs == 0) or (self.maxOccurs == 1 and oldValues):
            maxOccursViolated = True
        elif self.maxOccurs > 1:
            if not oldValues:
                oldValues =  [newValue]
            else:
                if self.maxOccurs > len(oldValues):
                    oldValues.append(newValue)
                else:
                    maxOccursViolated = True
        else:
            oldValues = newValue

        if maxOccursViolated:
            return "Too many occurrences of input [%s]: %s" % (self.identifier, newValue)

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
                metadata=metadata,minOccurs=minOccurs,maxOccurs=maxOccurs,type="LiteralValue")

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

         # ugly characters, only if string
        if  type(value)!= types.BooleanType:
            for char in self.restrictedCharacters:
                if value.find(char) > -1:
                    raise Exceptions.InvalidParameterValue("datainputs",
                        "Input [%s] has a value %s which contains unallowed characters." % (self.identifier, str(value)))

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
            raise Exceptions.InvalidParameterValue("datainputs",
                "Input [%s] has a value %s which is the wrong data type." % (self.identifier, str(value)))

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

        raise Exceptions.InvalidParameterValue("datainputs",
            "Input [%s] has a value %s which is out of range." % (self.identifier, str(value)))

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
                maxmegabites=None,formats=[{"mimeType":None}]):
        """Class constructor"""

        Input.__init__(self,identifier,title,abstract=abstract,
                metadata=metadata,minOccurs=minOccurs,maxOccurs=maxOccurs,type="ComplexValue")
        #If maxmegabites not present, then it will be set in  consolidateInputs()
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
        self.format = {}
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
        if not input.has_key("type") and self._isURL(input["value"]):
            input["asReference"] = True

        # download data

        if input.has_key("asReference") and input["asReference"] == True:
            self.downloadData2(input["value"])
        else:
            self.storeData(input["value"])
        return

    def setMimeType(self,input):
        """Sets the MimeType from input before going to setValue() this allows
        for some self.format to be filled febore base64 decoding. URL inputs don't have an input[], since they are just URLs.
        There mimeType was implemented to URL references, basically it sets a self.format based on the input provided by the user e.g:http://localhost/wps.cgi?request=Execute&service=wps&version=1.0.0&identifier=geotiff2png&datainputs=[input=@xlink:href=http://rsg.pml.ac.uk/wps/testdata/elev_srtm_30m.tif@method=POST@mimeType=text%2Fxml]
        this example shall raise an exception"""

        #NOTE: setting mimeType in URL and direct input should be the same, this if structure is here
        #for historical reasons and allows to differencite between the 2 types or requests if in the future
        # changes need to be done e.g setting mimetypes from HTTP stream etc
        keys=["mimetype","schema","encoding"]
        if not input.has_key("type") or self._isURL(input["value"]):
            for key in keys:
                if key in input.keys():
                    self.format[key]=input[key]
                else:
                    LOGGER.debug("input define by user didnt contain %s" % key)
                    self.format[key]=None
        else:
            for key in keys:
                if key in input.keys():
                    self.format[key]=input[key]
                else:
                    LOGGER.debug("input define by user didnt contain %s" % key)
                    self.format[key]=None

        return

    def storeData(self,data):
        """Store data from given file. Not bigger, then
        :attr:`maxFileSize`

        :param data: the data, which should be stored
        :type data: string
        """
        from os import curdir, rename

        outputName = tempfile.mktemp(prefix="pywpsInput",dir=curdir)
        fout = None
        try:
            fout=open(outputName,'wb')
        except IOError, what:
            self.onProblem("NoApplicableCode","Could not open file for writing")
        # NOTE: the filesize should be already checked in pywps/Post.py,
        # while getting the input XML file
        fout.write(data.encode("utf-8","utf-8"))
        fout.close()

        self.checkMimeTypeIn(fout.name)

        #self.format already set
        if  (self.format["mimetype"].lower().split("/")[0] != "text" and self.format["mimetype"].lower() != "application/xml"):
               # convert it to binary using base64
               #Python problem: The file object has to be closed after base64.decode, so that ALL content is flushed, otherwise the binary files are corrupted
               #This happens if the base64 has some 'trash' before and after the string. Better to use close() to be certain
               rename(fout.name,fout.name+".base64")
               try:
                   f1=open(fout.name+".base64","r")
                   f2=open(fout.name,"w")
                   base64.decode(f1, f2)
                   f1.close()
                   f2.close()
               except:
                   self.onProblem("NoApplicableCode", "Could not convert text input to binary using base64 encoding.")
               finally:
                    os.remove(fout.name+".base64")
        #Checking what is actu
        try:
            mimeTypeMagic=self.ms.file(fileName).split(';')[0]
            if self.format["mimetype"]!=mimeTypeMagic:
                LOGGER.debug("ComplexDataInput defines mimeType %s (default set) but libMagic detects %s" % (str(self.format["mimetype"]),mimeTypeMagic))
        except:
            pass


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

    def downloadData2(self, url):
        """Download data from given file url.

        :param url: File URL where the data are lying
        """
        from urlparse import urlparse
        url_parsed = urlparse(url)
        # if not file use old downloadData
        if url_parsed.scheme != 'file':
            return self.downloadData(url)
    
        # try to make symbolic link to file otherwise download it
        from os import curdir, symlink
        outputName = tempfile.mktemp(prefix="pywpsInput",dir=curdir)
        try:
            symlink(url_parsed.path, outputName)
        except Exception, what:
            LOGGER.exception('could not create symbolic link for file %s.', url_parsed.path)
            return self.downloadData(url)

        self.checkMimeTypeIn(outputName)
        resp = self._setValueWithOccurence(self.value, outputName)
        if resp:
            return resp
        return

    def downloadData(self, url):
        """Download data from given url. Do not download more, then
        :attr:`maxFileSize`

        :param url: URL where the data are lying
        """
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
            if (self.maxFileSize!=0 and (size > self.maxFileSize)):
                self.onProblem("FileSizeExceeded","Maximum file size is "+
                        str(self.maxFileSize/1024/1024)+" MB for input "+
                        url)
        fout.close()

        self.checkMimeTypeIn(fout.name)
        resp = self._setValueWithOccurence(self.value, outputName)
        if resp:
            return resp
        return

    def onProblem(self,what, why):
        """Empty method, called, when there was any problem with the input.
        This method is replaced in Execute.consolidateInputs, basically input.onProblem = self.onInputProblem
        therefore Exception raise is implemented in Execute.onInputProblem()
        :param what: Message with error description
        :param why: Error code
       """
        pass

    def checkMimeTypeIn(self,fileName):

        """Check, if the given mimetype is in self.formats
        checkMimeType is done after process.format is set by parsing user's content.
        1) if process.format[mimetype] has content it will be check in formats
        2) if process.format[mimetype]-->None assume process.format as first in list
            a) no exceptions should be risen
        3) If formats dict is empty then there is nothing that can be done, and self.format=None
        4) As request by wps-grass-process, in case of missing information even schema is passed. This is necessary
        for vector processes and to differenciate between text/xml from GML and KML
        :param fileName:
        :param mimeType:
        """
         #Note: magic output something like: 'image/tiff; charset=binary' we only need the typeContent
        if (self.format["mimetype"] is None) or (self.format["mimetype"]==""):
            #No mimeType let's set it from default
            LOGGER.debug("Missing ComplexDataInput mimeType in: %s, adopting default mimeType (first in formats list)" % self.identifier)
            self.format["mimetype"]=self.formats[0]["mimeType"]
            #wps-grass bridge, default schema and encoding
            try:
                self.format["schema"]=self.formats[0]["schema"]
                LOGGER.debug("Adding schema: %s" % self.format["schema"])
                self.format["encoding"]=self.formats[0]["encoding"]
                LOGGER.debug("Adding encoding: %s" % self.format["encoding"])
            except:
                LOGGER.debug("Adding schema and/or encoding failed, ")
            #checking format with libmagic
            #--> new funcion aget base64 change
            #mimeTypeMagic=self.ms.file(fileName).split(';')[0]
            #if self.format["mimetype"]!=mimeTypeMagic:
            #    LOGGER.debug("ComplexDataInput defines mimeType %s (default set) but libMagic detects %s" % (str(self.format["mimetype"]),mimeTypeMagic))
        else:
            #Checking is mimeType is in the acceptable formats
            if self.format["mimetype"] not in [dic["mimeType"] for dic in self.formats]:
                #ATTENTION: False positive if dictionary is not set in process/empty
                if (len(self.formats)==1) and (type(self.formats[0]["mimeType"])==types.NoneType):
                    LOGGER.debug("Input %s without mimetype list, cant check if ComplexDataInput mimtype is correct or not" % self.identifier)
                else:
                    LOGGER.debug("ComplexDataInputXML defines mimeType %s  which is not in Input %s formats list" % (str(self.format["mimetype"]),str(self.identifier)))
                    self.onProblem("InvalidParameterValue",self.identifier)


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

    def _isURL(self,text):
        """Check wheather given text is url or not
        """

        try:
            (urltype, opaquestring) = urllib.splittype(text)

            if urltype in ["http","https","ftp","file"]:
                return True
            else:
                return False
        except:
            return False


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
        if type(input["value"]) == type("") or\
           type(input['value']) == type(u""):
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
                default=None,asReference=False):
        """Class Constructor"""
        Output.__init__(self,identifier,title,abstract=abstract,
                metadata=metadata,type="LiteralValue",asReference=asReference)

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

        file projection (used by mapserver, see useMapscript below), is not set, will be determined
        automatically

    .. attribute :: bbox

        data bounding box (used by mapserver, see useMapscript below)
        if not set, will be determined automatically

    .. attribute :: width

        (used by mapserver, see useMapscript below)
        if not set, will be determined automatically

    .. attribute :: height

        (used by mapserver, see useMapscript below)
        if not set, will be determined automatically

    .. attribute :: useMapscript

        If set to true and asReference is set to true (by request), PyWPS
        will gerenate UMN MapServer mapfile and point the reference URL to
        it, so that raster layer will be accessible as OGC WCS and vector
        layer will be accessible as OGC WFS. This enables the client more
        flexible bindings of resulting ouput files.

        Attributes projection, bbox, width and height will be used. If not
        set, they will be determined using gdal/ogr libraries. If something
        does not work, try to adjust them manualy.

        Unlike ComplexInput, the check for mimeType is done in Execute during
        output consolidation.
    """
    formats = None
    format = {"mimetype":None,"encoding":None,"schema":None}
    projection = None
    bbox = None
    width = None
    height = None
    useMapscript = False

    def __init__(self,identifier,title,abstract=None,
                metadata=[], formats=[{"mimeType":None}],
                asReference=False, projection=None, bbox=None, useMapscript
                =  False):
        """Class constructor"""
        Output.__init__(self,identifier,title,abstract=abstract,
                metadata=metadata,type="ComplexValue", asReference=asReference)

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
        self.format={}

        self.projection = projection
        self.bbox = bbox
        self.useMapscript = useMapscript
        try:
            self.ms = magic.open(magic.MAGIC_MIME)
            self.ms.load()
        except:
            pass

        return

    def setValue(self, value):
        """Set the output value

        :param value: value to be returned (file name or file itself)
        :type value: string or file
        """

        #Note: cStringIO and StringIO are totally messed up, StringIO is type instance, cString is type cStringIO.StringO
        #Better to also use __class__.__name__ to be certain what is is
        # StringIO => StringIO but cStringIO => StringO
        if type(value) == types.StringType or type(value)==types.UnicodeType:
            self.value = value
        elif type(value) == types.FileType:
            self.value = value.name
        elif value.__class__.__name__=='StringIO' or value.__class__.__name__=='StringO':
            from os import curdir
            fh, stringIOName = tempfile.mkstemp(prefix="pywpsOutput",
                                                dir=curdir) #(5, '/tmp/pywps-instanceS2j6ve/pywpsOutputZxSM6V')
            os.write(fh, value.getvalue())
            os.close(fh)
            self.value=stringIOName
        # TODO add more types, like Arrays and lists for example
        else:
            raise Exception("Output type '%s' of '%s' output not known, not FileName, File or (c)StringIO object" %\
                    (type(value),self.identifier))


    def checkMimeTypeIn(self):
            #Checking the mimeType
            #-1)Easier to set the schema and utf if present then deal with mimetype
            #0) check if format has mimetype key, if input request has no mimeType then the key will be missing
            #1) If missing mimeType, pick the default one from list
            #2) check if mimeType is in the output.formats list, if not raise exception
            #3) if no mimeType and no outputs.formats then do nothin
            #4) Adding schema and encondig passing for wps-grass-bridge
        try:
            if (self.format["schema"] is None) or (self.format["schema"]==""):
                self.format["schema"]=self.formats[0]["schema"]
                LOGGER.debug("Adding schema: %s" % self.format["schema"])
            if (self.format["encoding"] is None) or (self.format["schema"]==""):
                self.format["encoding"]=self.formats[0]["encoding"]
                LOGGER.debug("Adding encoding: %s" % self.format["encoding"])
        except:
            LOGGER.debug("Adding schema and/or encoding failed, ")

        if (self.format["mimetype"] is None) or (self.format["mimetype"]==""):
                LOGGER.debug("Missing ComplexDataOutput mimeType in %s, adopting default mimeType %s (first in formats list)" % (self.identifier,self.formats[0]["mimeType"]))
                self.format["mimetype"]=self.formats[0]["mimeType"]
                #wps-grass-bridge
        else:
            #Checking is mimeType is in the acceptable formats
            if self.format["mimetype"] not in [dic["mimeType"] for dic in self.formats]:
                #ATTENTION: False positive if dictionary is not set in process/empty formats list
                if (len(self.formats)==1) and (type(self.formats[0]["mimeType"])==types.NoneType):
                    LOGGER.debug("Process without mimetype list, cant check if ComplexDataOutput mimtype is correct or not")
                else:
                    LOGGER.debug("ComplexDataOutputXML defines mimeType %s  which is not in process %s formats list" % (str(self.format["mimetype"]),str(self.identifier)))
                    self.onProblem("InvalidParameterValue",self.identifier)


    def onProblem(self,what, why):
        """Empty method, called, when there was any problem with the input.
        This method is replaced in Execute.consolidateInputs, basically output.onProblem = self.onOutputProblem
        therefore Exception raise is implemented in Execute.onInputProblem()
        :param what: Message with error description
        :param why: Error code
       """
        pass

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
        Output.__init__(self,identifier,title,abstract=abstract,
                metadata=metadata,type="BoundingBoxValue",asReference=asReference)
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
