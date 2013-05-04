from pywps.process.inout import *

class BoundingBox:
    """Basic bbox input or output object"""
    pass

class BoundingBoxInput(BoundingBox,Input):
    """BoundingBox input object"""
    pass

class BoundingBoxOutput(BoundingBox,Output):
    """BoundingBox output object"""
    pass
