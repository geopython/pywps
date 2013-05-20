from pywps.process.inout import *
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
        """Set input value based on input node
        """

        vals = None
        crs = None
    
        bbox_node = "{%s}BoundingBox" % namespaces["ows"]
        if getattr(node, bbox_node,None) is not None:

            bbox_node = node[bbox_node]
            vals = bbox_node.LowerCorner.text.split()
            vals.extend(bbox_node.UpperCorner.text.split())
        
            if "crs" in bbox_node.attrib.keys():
                crs = bbox_node.attrib["crs"]

        elif getattr(node, "{%s}WGS84BoundingBox" % namespaces["ows"], None) is not None:
            bbox_node = node["{%s}WGS84BoundingBox" % namespaces["ows"]]
            vals = bbox_node.LowerCorner.text.split()
            vals.extend(bbox_node.UpperCorner.text.split())
        
            crs = "epsg:4326"

        self.set_value(vals,crs)


class BoundingBoxOutput(BoundingBox,Output):
    """BoundingBox output object"""
    pass
