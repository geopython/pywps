class Extent:
    """Basic extent class
    """

    left = None
    bottom = None
    right = None
    top = None
    crs = None

    def __init__(self,left,bottom,right,top,crs=None):

        self.left = left
        self.bottom = bottom
        self.right = right
        self.top = top

        self.crs = crs

    def toString(self):

        return ",".join([str(a) for a in self.toArray()])

    def toArray(self):

        return (self.left, self.bottom,
                self.right, self.top)


