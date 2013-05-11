from pywps.process.inout import *
from owslib import crs

class BoundingBox:
    """Basic bbox input or output object"""
    left = None
    bottom = None
    right = None
    top = None
    base = None
    cover = None

    crs = None
    dimensions = None

    def set_value(self,value, crs=None):
        """Set bbox
        
        value = (minx,miny,maxx,maxy) or
        value = (minx,miny,minz, maxx, maxy, maxz)"""

        # 2 dimensions
        if len(value) == 4:
            (left, bottom, right, top) = list(map(float,value))
            self.dimensions = 2

        # 3 dimensions
        if len(value) == 6:
            (left, bottom, base, right, top, cover) = list(map(float,value))
            self.dimensions = 3

        if crs:
            self._set_crs(crs)

    def set_crs(self, crs):
        """Set crs
        """
        if isinstance (crs, str):
            self.crs = crs.Crs(crs)

class BoundingBoxInput(BoundingBox,Input):
    """BoundingBox input object"""

    def set_from_url(self,inpt_str):
        """Set input vlaue based on input string
        """
        (identifier,value) = inpt_str.split("=",1)
        vals = value.split(",")

        crs = None

        if len(vals)%2 == 1:
            crs = vals.pop()

        self.set_value(vals,crs)

    def set_from_xml(self,node):
        """Set input vlaue based on input node
        """

        vals = None
        crs = None
    
        if "BoundingBox" in dir(node)
            vals = node.BoundingBox.LowerCorner.split()
            vals.extend(node.BoundingBox.UpperCorner.split())
        
            if crs in node.BoundingBox.attrib:
                crs = node.BoundingBox.attrib["crs"]
        elif "WGS84BoundingBox" in dir(node):
            vals = node.WGS84BoundingBox.LowerCorner.split()
            vals.extend(node.WGS84BoundingBox.UpperCorner.split())
        
            crs = "epsg:4326"

        self.set_value(vals,crs)


class BoundingBoxOutput(BoundingBox,Output):
    """BoundingBox output object"""
    pass
