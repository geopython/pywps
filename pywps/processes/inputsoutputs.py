class Process:
    def __init__(self):
        self.Identifier = "inputsoutputs"
        self.processVersion = "0.1"
        self.Title="Test input and output structures"
        self.statusSupported="false"
        self.storeSupported="false"
        #self.grassLocation = None
        self.Inputs = [
                # 0
                 {
                    'Identifier': 'literal',
                    'Title': 'Literal Value',
                    'Abstract': ' "literal value" ',
                    'LiteralValue': {'UOMs':["cm"],
                                     "values":[[1,10],[20,40]]},
                    'MinimumOccurs': "3",
                    'value': "",
                 },
                # 1
                 {
                    'Identifier': 'complexref',
                    'Title': 'Literal Value Reference',
                    'Abstract': ' "complex value reference" ',
                    'ComplexValueReference': {"Formats":["image/jpeg"]},
                    'value': "http://les-ejk.cz/img/jaja.jpg",
                 },
                # 2
                 {
                    'Identifier': 'bbox',
                    'Title': 'Bounding Box Value',
                    'Abstract': ' "bounding box value" ',
                    'BoundingBoxValue': {},
                    'value': [0,0, 10,10],
                 },
                # 3
                 {
                    'Identifier': 'xml',
                    'Title': 'ComplexValue input',
                    'Abstract': ' "embed xml" ',
                    'ComplexValue': {"Formats":['text/xml']},
                 },


                ]
        self.Outputs = [
                # 0
                 {
                    'Identifier': 'literal',
                    'Title': 'Literal Value',
                    'Abstract': ' "literal value" ',
                    'LiteralValue':{'UOMs':["cm"]},
                    'value': "10",
                 },
                # 1
                 {
                    'Identifier': 'complexref',
                    'Title': 'Literal Value Reference',
                    'Abstract': ' "complex value reference" ',
                    'ComplexValueReference': {"Formats":["image/jpeg"]},
                    'value': None,
                 },
                # 2
                 {
                    'Identifier': 'bbox',
                    'Title': 'Bounding Box Value',
                    'Abstract': ' "bounding box value" ',
                    'BoundingBoxValue': {},
                    'value': [11, 11, 14,14.4],
                 },
                # 3
                 {
                    'Identifier': 'xml',
                    'Title': 'ComplexValue input',
                    'Abstract': ' "embed xml" ',
                    'ComplexValue': {"Formats":['text/xml']},
                 },
        ]
        
    def execute(self):
        self.Outputs[1]['value'] = self.Inputs[1]['value']
        self.Outputs[2]['value'] = [self.Inputs[2]['value'][0],
                                    self.Inputs[2]['value'][1],
                                    self.Inputs[2]['value'][2],
                                    self.Inputs[2]['value'][3]]

        self.Outputs[3]['value'] = self.Inputs[3]['value']
        return 
