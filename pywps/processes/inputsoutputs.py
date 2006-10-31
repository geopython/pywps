class Process:
    def __init__(self):
        self.Identifier = "inputsoutputs"
        self.processVersion = "0.1"
        self.Title="Test input and output structures"
        self.statusSuported="false"
        self.storeSuported="false"
        self.Inputs = [
                 {
                    'Identifier': 'literal',
                    'Title': 'Literal Value',
                    'Abstract': ' "literal value" ',
                    'LiteralValue': {'UOMs':["cm"]},
                    'MinimumOccurs': "3",
                    'value': "",
                 },
                 {
                    'Identifier': 'complexref',
                    'Title': 'Literal Value Reference',
                    'Abstract': ' "complex value reference" ',
                    'ComplexValueReference': {"Formats":["image/jpeg"]},
                    'value': "http://les-ejk.cz/img/jaja.jpg",
                 },
                 {
                    'Identifier': 'bbox',
                    'Title': 'Bounding Box Value',
                    'Abstract': ' "bounding box value" ',
                    'BoundingBoxValue': {},
                    'value': ["0 0", "10 10"],
                 },

                ]
        self.Outputs = [
                 {
                    'Identifier': 'literal',
                    'Title': 'Literal Value',
                    'Abstract': ' "literal value" ',
                    'LiteralValue':{'UOMs':["cm"]},
                    'value': "10",
                 },
                 {
                    'Identifier': 'complexref',
                    'Title': 'Literal Value Reference',
                    'Abstract': ' "complex value reference" ',
                    'ComplexValueReference': {"Formats":["image/jpeg"]},
                    'value': None,
                 },
                 {
                    'Identifier': 'bbox',
                    'Title': 'Bounding Box Value',
                    'Abstract': ' "bounding box value" ',
                    'BoundingBoxValue': {},
                    'value': ["0 0", "10 10"],
                 },

        ]
        
    def execute(self):
        print self.Inputs[1]['value']
        self.Outputs[1]['value'] = self.Inputs[1]['value']
        self.Outputs[2]['value'] = [self.Inputs[2]['value'][0].split()[0],
                                    self.Inputs[2]['value'][0].split()[1],
                                    self.Inputs[2]['value'][1].split()[0],
                                    self.Inputs[2]['value'][1].split()[1]]
        return 
