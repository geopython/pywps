from pywps.process.inout.literal import LiteralInput
from pywps.process.inout.bbox import BoundingBoxInput
from pywps.process.inout.complex import ComplexInput

from owslib.crs import Crs

class LiteralLengthInput(LiteralInput):
    """Standard literal input for length in meters
    """

    identifier = "length"
    datatype = "float"
    uom = "m"
    title = "Length"
    abstract = "Input length, given in meters as float number, default 0"
    default = 0

class BBoxInput(BoundingBoxInput):
    """Standard bbox input, wgs84
    """

    identifier = "bbox"
    crs = Crs("epsg:4326")
    title = "Bounding box"
    abstract = "Bounding box, wgs84, epsg:4326"

class ComplexVectorInput(ComplexInput):
    """Standard literal input for length in meters
    """

    identifier = "vector"
    title = "Vector data"
    abstract = "Input vector data"
