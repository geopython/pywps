"""
Generic benchmark framework  for pywps.  

The generic benchmark tries to follow the same strategy as unittest, where a generic class (suite)
runs methods that start with keyword test

The framework works with cProfile and will only return the CPU time, there shouldn't
be a problem to return the complete report of the most time consuming  functions by
manipulating the cProfile properties in method run()
"""
__author__ = "Jorge de Jesus"
__license__ = "GPL"
__version___ = "0.1"
__maintainer__ = "Jorge de Jesus"
__email__ = "jorge.jesus@gmail.com"
__status__ = "Prototype"

import cProfile
import StringIO
import os
import sys
import re
from pstats import Stats
pywpsPath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],".."))
sys.path.insert(0, pywpsPath)

import pywps

os.putenv("PYWPS_CFG", os.path.join(pywpsPath, "pywps", "default"))
os.environ["PYWPS_CFG"] = os.path.join(pywpsPath, "pywps", "default.cfg")
os.putenv("PYWPS_TEMPLATES", os.path.join(pywpsPath, "tests", "Templates"))
os.environ["PYWPS_TEMPLATES"] = os.path.join(pywpsPath, "tests", "Templates")
os.putenv("PYWPS_PROCESSES", os.path.join(pywpsPath, "tests", "processes"))
os.environ["PYWPS_PROCESSES"] = os.path.join(pywpsPath, "tests", "processes")

class BenchMarkWPS(object):
    def __init__(self):
        self.getCapabilitiesReq = "service=wps&request=getcapabilities"
        self.getDescribeProcessReq = "service=wps&request=describeprocess&version=1.0.0&identifier=all"
        self.getWSDL="WSDL"
        #To silence  WPS warnings. Note this will silence any error in the code!!
        sys.stderr = open('/dev/null',"w") 
    
    def run(self):
        """method calling cProfile and printing the output"""
        tests=self.tests()
       
        for test in tests:
            tmpBuffer=StringIO.StringIO()
            profile=cProfile.Profile()
            profile.runctx('self.'+str(test[0])+"()",globals(),locals())
            stats=Stats(profile,stream=tmpBuffer)
            stats.sort_stats('time','calls')
            stats.print_stats(1)
            #match=re.findall(r'\bin\b(.*?)\bCPU\b',tmpBuffer.getvalue())
            match=re.findall(r'\bin\b(.*?)\bseconds\b',tmpBuffer.getvalue())
            #There is some difference between 2.6 and 2.7, re with seconds fits both version
            #but in 2.6 it returns CPU string, the filter will clean it 
            print str(test[1].__doc__ )+":"+filter(lambda x: x.isdigit() or x==".", str(match[0]))+" CPU Time"
        
    def tests(self):
        """filters class methods and returns methods that will be run"""
        dic=BenchMarkWPS.__dict__
        return [(key,value) for key,value in dic.items() if ("test" in key and key!="tests") ]

    def testGetCapabilitiesGET(self):
        """GetCapabilities GET"""
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = getpywps.parseRequest(self.getCapabilitiesReq)
        getpywps.performRequest(inputs)
        
    def testGetCapabilitiesPOST(self):
        """GetCapabilities POST"""
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getCapabilitiesRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_getcapabilities_request.xml"))
        postinputs = postpywps.parseRequest(getCapabilitiesRequestFile)
        postpywps.performRequest(postinputs)
    
    def testDescribeProcessGET(self):
        """DescribeProcess all GET"""
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        getpywps.parseRequest(self.getDescribeProcessReq)
        getpywps.performRequest()
    
    def testDescribeProcessPOST(self):
        """DescribeProcess all POST"""
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        getCapabilitiesRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_describeprocess_request_all.xml"))
        postinputs = postpywps.parseRequest(getCapabilitiesRequestFile)
        postpywps.performRequest(postinputs)
    
    def testExecuteComplexInput(self):
        """Execute raster/vector input"""
        postpywps = pywps.Pywps(pywps.METHOD_POST)
        executeRequestFile = open(os.path.join(pywpsPath,"tests","requests","wps_execute_request-complexinput-direct.xml"))
        postinputs = postpywps.parseRequest(executeRequestFile)
        postpywps.performRequest(postinputs)
    
    def testWSDL(self):
        """WSDL request"""
        getpywps = pywps.Pywps(pywps.METHOD_GET)
        inputs = getpywps.parseRequest(self.getWSDL)
        getpywps.performRequest(inputs)
            
if __name__ == "__main__":
    bench = BenchMarkWPS()
    bench.run()

