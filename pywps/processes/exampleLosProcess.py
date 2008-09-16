import sys, os

from pywps.Wps.process import GRASSWPSProcess

class Process(GRASSWPSProcess):
    def __init__(self):
        GRASSWPSProcess.__init__(self,
                Identifier = "los",
                Title= "Lines of sight",
                processVersion = "0.1",
                storeSupported = True,
                statusSupported = True)

        self.AddComplexInput(Identifier = "dmt",
                            Title = "Digital elevation model",
                            Formats= ["image/tiff"])
                             
        self.AddLiteralInput(Identifier = "x",
                            Title = "x coordinate",
                            value = ["*"],
                            type = type(0.0))
                
        self.AddLiteralInput(Identifier = "y",
                            Title = "y coordinate",
                            value = ["*"],
                            type = type(0.0))

        self.AddLiteralInput(Identifier = "extent",
                            Title = "Extent",
                            Abstract = "w s e n",
                            type = type(""),
                            value = "")

        self.AddLiteralInput(Identifier = "height",
                            Title = "Height",
                            Abstract = "Observer height",
                            type = type(0.0),
                            value = 0)

        self.AddLiteralInput(Identifier = "min",
                            Title = "Min level",
                            Abstract = "Min level in dem",
                            type = type(0.0),
                            value = 0)

        self.AddLiteralInput(Identifier = "max",
                            Title = "Max level",
                            Abstract = "Max level in dem",
                            type = type(0.0),
                            value = 0)

        self.AddComplexReferenceOutput(Identifier = "map",
                            Title = "Resulting output map",
                            Formats = ["image/gif"])
        self.AddLiteralOutput(Identifier = "size",
                            Title = "Image size")
        self.AddLiteralOutput(Identifier = "extent",
                            Title = "Image extent")

    def execute(self):

        w,s,e,n = [None, None, None, None]
        dmt = self.GetInputValue("dmt")
        height = self.GetInputValue("height");

        min = self.GetInputValue("min");
        max = self.GetInputValue("max");

        # import of the data
        if (self.GetInputValue("extent") != ""):
            w,s,e,n = self.GetInputValue("extent").split(" ")
            try:
                w = float(w)
                s = float(s)
                e = float(e)
                n = float(n)
            except Exception, e:
                return e

            self.GCmd("gdal_translate -ot Byte -a_ullr %s %s %s %s -of GTiff %s dmt.tif" % (w,n,e,s,dmt))
            dmt = "dmt.tif"

        if float(height) >0:
            #height = float(256)/float(3000)*float(height)
            pass
        else:
            height = 0
        self.GCmd("r.in.gdal -o input=%s output=dmt" % (dmt))
        self.GCmd("g.region rast=dmt")
        if min != max:
            if min == 0:
                min = 1
            if min < max:
                self.GCmd("r.mapcalc dmt=(%s-%s)/dmt+%s" % \
                        (float(max),float(min),float(min)))
            else:
                self.GCmd("r.mapcalc dmt=(%s-%s)/dmt+%s" % \
                        (float(min),float(max),float(min)))


        self.SetStatus(message="Data  imported", percent=10)

        self.SetStatus(message="Calculating  lines of sigth", percent=20)
        # adding the value
        max = abs(float(e)-float(w))
        if max > 5000:
            max = 5000
        self.GCmd("r.los in=dmt out=los coor=%f,%f obs_e=%s max=%s >&2" % \
                (self.GetInputValue('x'),self.GetInputValue("y"),height,max))

        self.SetStatus(message="Making transparency", percent=70)
        self.GCmd("r.null map=los setnull=0")

        self.SetStatus(message="Exporting resulting image", percent=80)
        self.GCmd("r.out.png in=los out=los.png")

        self.SetStatus(message="Creating png image file", percent=90)
        #self.GCmd("export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/cepicky/lib; /home/cepicky/bin/convert los.png -alpha reset -transparent white los.png")
        self.GCmd("convert los.png -transparent white los.png")
        self.SetOutputValue("map","los.png")
        self.SetStatus(message="Final region settings", percent=100)

        n = None
        s = None
        w = None
        e = None
        rows = 0
        cols = 0

        for line in self.GCmd("g.region -g"):
            key,val=line.strip().split("=")
            if key == "n":
                n=val
            elif key == "s":
                s=val
            elif key == "w":
                w=val
            elif key == "e":
                e=val
            elif key == "rows":
                rows=val
            elif key == "cols":
                cols=val

        self.SetOutputValue("size","%s %s" % (cols, rows))
        self.SetOutputValue("extent","%s %s %s %s" % (w,s,e,n))

