import os
import sys

pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.insert(0,pywpsPath)
sys.path.append(pywpsPath)

import unittest

from pywps.request.execute import Execute

class RequestParseExecuteTestCase(unittest.TestCase):

    test_values = {
            "version":"1.0.0",
            "language":"en",
            "request":"execute",
            "service":"wps"
    }

    def setUp(self):
        self.ex = Execute()
        self.ex.validate = True

    def testParseExecuteProcessGET_rawdataoutput(self):
        """Test if Execute request is parsed and if GET
        methods are producing the same result"""

        TODO: fix this request (remove brackets from DataInputs
        #HEREIAM
        self.ex.set_from_url(request.parse_params("Service=WPS&Version=1.0.0&Language=en&Request=Execute&Identifier=Buffer&DataInputs=[InputPolygon=@xlink:href=http%3A%2F%2Ffoo.bar%2Fsome_WFS_request.xml;BufferDistance=400]&RawDataOutput=[BufferedPolygon]"))

        self.__test_vals(self.test_values)

    def __test_vals(self, vals):
        for key in vals:
            self.assertEquals(eval("self.ex.%s"%key), vals[key])


if __name__ == "__main__":
   suite = unittest.TestLoader().loadTestsFromTestCase(RequestParseExecuteTestCase)
   unittest.TextTestRunner(verbosity=4).run(suite)
