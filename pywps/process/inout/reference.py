class Reference:
    """Basic reference input class
    """

    href = None
    method = None
    header = None
    body = None
    bodyref = None

    def __init__(self, href, method="GET", header=None, body=None, bodyref=None):
        
        self.href = href
        self.method = method
        self.header = header
        self.body = body
        self.bodyref = bodyref

