"""
Example Linies of sight process (visibility analysis. Needs temporary
GRASS location.

Author: jachym
Licence: GNU/GPL

Changes: 
    2008-09-16
        Version 0.2
        updated for PyWPS 3.0.0, czech translation
"""

from pywps.Process.Process import WPSProcess


class Process(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
                identifier = "exampleLosProcess",
                title= "Lines of sight",
                abstract = """Visibility analysis on input digital elevation model""",
                version = "0.2",
                storeSupported = True,
                statusSupported = True,
                grassLocation = True)

        self.dem = self.addComplexInput(identifier = "dem",
                            title = "Digital elevation model",
                            abstract = """Input digital elevation model in
                            GeoTIFF format""",
                            formats= [{"mimeType":"image/tiff"}])
                             
        self.easting = self.addLiteralInput(identifier = "easting",
                            title = "Easting coordinate",
                            type = type(0.0))

        self.northing = self.addLiteralInput(identifier = "northing",
                            title = "Northing coordinate",
                            type = type(0.0))
                
        self.height = self.addLiteralInput(identifier = "height",
                            title = "Observer height",
                            type = type(0.0),
                            allowedValues = [[0,50]],
                            default = 1.3,
                            minOccurs=0)

        self.los = self.addComplexOutput(identifier = "los",
                            title = "Resulting output map",
                            formats = [
                                {"mimeType":"image/tiff"},
                                {"mimeType":"image/png"}
                            ])

    def execute(self):

        self.cmd("r.in.gdal -o input=%s output=dem" % (self.dem.value))
        self.cmd("g.region rast=dem")

        self.status.set(msg="Calculating  lines of sigth", percentDone=20)
        self.cmd("r.los in=dem out=los coor=%f,%f obs_e=%s >&2" % \
                (self.easting.value,self.northing.value,self.height.value))

        self.status.set(msg="Making transparency", percentDone=70)
        self.cmd("r.null map=los setnull=0")

        self.status.set(msg="Exporting resulting image", percentDone=80)

        # deside, if the user wants PNG or GeoTIFF format
        losfile = "los.png"
        if self.los.format["mimeType"] == "image/tiff":
            losfile = "los.tif"
            self.cmd("r.out.gdal in=los out=los.tif type=Byte")
        else:
            self.cmd("r.out.png in=los out=los.png")

        self.los.setValue(losfile)

