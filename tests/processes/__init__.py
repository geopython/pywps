from pywps.process import Process
from pywps.process.inout.standards import LiteralLengthInput

class SimpleProcess(Process):
    identifier = "simpleprocess"

    def __init__(self):
        self.add_input(LiteralLengthInput())
