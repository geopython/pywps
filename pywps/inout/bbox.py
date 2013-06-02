from pywps.inout import *
from owslib import crs as owscrs

from pywps.request import namespaces

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

    type = "bbox"

    def set_value(self,value, crs=None):
        """Set bbox
        
        value = (minx,miny,maxx,maxy) or
        value = (minx,miny,minz, maxx, maxy, maxz)"""


        # 2 dimensions
        if len(value) == 4:
            (self.left, self.bottom, self.right, self.top) = list(map(float,value))
            self.dimensions = 2

        # 3 dimensions
        elif len(value) == 6:
            (self.left, self.bottom, self.base, self.right, self.top, self.cover) = list(map(float,value))
            self.dimensions = 3

        if crs:
            self.set_crs(crs)

    def set_crs(self, crs):
        """Set crs
        """
        if isinstance (crs, str):
            self.crs = owscrs.Crs(crs)

    def get_value(self):
        return self

    def get_crs(self):
        return self.crs

    def get_dimensions(self):
        return self.dimensions

class BoundingBoxOutput(BoundingBox,Output):
    """BoundingBox output object"""
    pass
