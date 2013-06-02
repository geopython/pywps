from pywps.request.execute import Input
from pywps.inout.bbox import BoundingBox
from pywps import namespaces
from owslib import crs as owscrs

import logging

class BoundingBoxInput(Input):
    """BoundingBox input object"""

    def __init__(self,identifier=None,value=None, title=None, abstract=None):
        super(Input,self).__init__(identifier=identifier , value=value, title=title, abstract= abstract)

    def parse_url(self,inpt_str):
        """Set input vlaue based on input string
        """

        # check for max occurs
        if self.check_maxoccurs():
            # continue with parsing
                
            (identifier,value) = inpt_str.split("=",1)

            if self.identifier != identifier:
                raise Exception("Identifiers do not match") # TODO custom exception

            vals = value.split(",")

            crs = None

            if len(vals)%2 == 1:
                crs = vals.pop()

            single_bbox = BoundingBox()
            single_bbox.set_value(vals,crs)
            self.append(single_bbox)

    def parse_xml(self,node):
        """Set input value based on input node
        """

        vals = None
        crs = None

        # check for max occurs
        if self.check_maxoccurs():

            identifier = node.xpath("ows:Identifier",
                    namespaces=namespaces)[0].text
            if self.identifier != identifier:
                raise Exception("Identifiers do not match") # TODO custom exception
        
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

            single_bbox = BoundingBox()
            single_bbox.set_value(vals,crs)
            self.append(single_bbox)

    def get_crs(self, idx=0):

        return self.inputs[idx].get_crs()

    def get_dimensions(self, idx=0):

        return self.inputs[idx].get_dimensions()
