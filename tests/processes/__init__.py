from pywps import Process
from pywps.inout import LiteralInput

class SimpleProcess(Process):
    identifier = "simpleprocess"

    def __init__(self):
        self.add_input(LiteralInput())
