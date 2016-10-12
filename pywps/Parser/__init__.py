##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################

"""Parser parses input parameters, send via HTTP Post or HTTP Get method. If
send via HTTP Post, the input is usually XML file.

Each class in the package is resposible for each type of the request.

"""


__all__ = [
        "Get",
        "Post",
        "GetCapabilities",
        "DescribeProcess",
        "Execute"
        ]


class Parser:
    """Parent class for all request parsers.
    
    .. attribute:: wps

        instace of :class:`pywps.Pywps`

    .. attribute:: isSoap

        indicates, whether the request is in Soap envelope or not

    .. attribute:: inputs

        object, where results of parsing is stored
    """

    wps = None
    isSoap = False
    soapVersion=None
    isSoapExecute=None
    inputs = None

    def __init__(self,wps):
        self.wps = wps
        self.inputs = {}
    
    def _trueOrFalse(self,str):
        """Return True or False, if input is "true" or "false" 
        :param str: String to be checks and returned
        :returns: bool or str 
        """
        if str.lower() == "false":
            return False
        elif str.lower() == "true":
            return True
        else:
            return str

