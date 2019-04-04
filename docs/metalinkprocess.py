from pywps import Process, LiteralInput, ComplexOutput, FORMATS
from pywps.inout.outputs import MetaLink4, MetaFile


class MultipleOutputs(Process):
    def __init__(self):
        inputs = [
            LiteralInput('count', 'Number of output files',
                         abstract='The number of generated output files.',
                         data_type='integer',
                         default=2)]
        outputs = [
            ComplexOutput('output', 'Metalink4 output',
                          abstract='A metalink file storing URIs to multiple files',
                          as_reference=True,
                          supported_formats=[FORMATS.META4])
        ]

        super(MultipleOutputs, self).__init__(
            self._handler,
            identifier='multiple-outputs',
            title='Multiple Outputs',
            abstract='Produces multiple files and returns a document'
                     ' with references to these files.',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        max_outputs = request.inputs['count'][0].data

        ml = MetaLink4('test-ml-1', 'MetaLink with links to text files.', workdir=self.workdir)
        for i in range(max_outputs):
            # Create a MetaFile instance, which instantiates a ComplexOutput object.
            mf = MetaFile('output_{}'.format(i), 'Test output', format=FORMATS.TEXT)
            mf.data = 'output: {}'.format(i)  # or mf.file = <path to file> or mf.url = <url>
            ml.append(mf)

        # The `xml` property of the Metalink4 class returns the metalink content.
        response.outputs['output'].data = ml.xml
        return response
