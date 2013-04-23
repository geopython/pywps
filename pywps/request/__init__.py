import types
import logging
import io

namespaces = {
    "ows":"http://www.opengis.net/ows/1.1",
    "wps": "http://www.opengis.net/wps/1.0.0"
}

# indicates, if xsd-based validation of the request should return
VALIDATE = False

class Request:
    """ Base request class
    """

    version = None
    request = None
    service = "wps"
    request = None

    validate = False
    lang = "en"

    def set_from_url(self,pairs):
        """Set values of this request based on url key-value pairs
        """
        pass

    def set_from_xml(self,root):
        """Set values of this request based on url ETree root 
        """
        pass


    def is_valid(self):
        """Returns  self-control of the reuquest - if all necessary variables
        are set"""
        return True

def get_request(data):
    """returns request object in for of key-value pairs (for HTTP GET) or Tree
    (POST)
    """

    # parse get request
    if isinstance(data, str):
        kvs = parse_params(data)
        return __get_request_from_url(kvs)
        
    # post request is supposed to be file object
    elif isinstance(data, io.IOBase):
        root =  parse_xml(data)
        return __get_request_from_xml(root)
    else:
        pass

def parse_xml(data):
    """Parse xml tree
    """

    from lxml import etree
    from lxml import objectify
    logging.debug("Continuing with lxml xml etree parser")

    schema = None
    if VALIDATE:
        schema = etree.XMLSchema(file="pywps/resources/schemas/wps_all.xsd")
    parser = objectify.makeparser(remove_blank_text = True,
                                remove_comments = True,
                             schema = schema)
    objects = objectify.parse(data,parser)

    return objects.getroot()

def parse_params(data):
    """Parse params
    """
    from urllib.parse import parse_qs
    logging.debug("Continuing with urllib.parse parser")

    params = parse_qs(data)
    return params

def __get_request_from_url(pairs):
    """return Request object based on url key-value pairs params
    """

    # convert keys to lowercase
    pairs = dict((k.lower(), v) for k, v in pairs.items())
    keys = pairs.keys()
    request = None

    if "request" in keys:
        if pairs["request"][0].lower() == "getcapabilities":
            from pywps.request import getcapabilities
            request = getcapabilities.GetCapabilities()
        elif pairs["request"][0].lower() == "describeprocess":
            from pywps.request import describeprocess
            request = describeprocess.DescribeProcess()
        elif pairs["request"][0].lower() == "execute":
            from pywps.request import execute
            request = execute.Execute()

    if request:
        request.set_from_url(pairs)

    # return request, whatever it may be
    return request

def __get_request_from_xml(root):
    """return Request object based on xml etree root node
    """
    global namespaces

    # convert keys to lowercase
    request = None

    if root.tag == "{%s}GetCapabilities"%namespaces["wps"]:
        from pywps.request import getcapabilities
        request = getcapabilities.GetCapabilities()
    elif root.tag == "{%s}DescribeProcess"%namespaces["wps"]:
        from pywps.request import describeprocess
        request = describeprocess.DescribeProcess()
    elif root.tag == "{%s}Execute"%namespaces["wps"]:
        from pywps.request import execute
        request = execute.Execute()

    if request:
        request.set_from_xml(root)

    # return request, whatever it may be
    return request
