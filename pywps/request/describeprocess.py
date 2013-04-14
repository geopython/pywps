from pywps.request import *

class DescribeProcess(Request):
    """Parser of DescribeProcess
    """

    request="describeprocess"
    identifier=None

    def parse(self, data):
        """Parse given data
        """
        super(DescribeProcess, self).parse(data)
    
