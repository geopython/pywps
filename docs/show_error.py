from pywps import Process, LiteralInput
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

import logging
LOGGER = logging.getLogger("PYWPS")


class ShowError(Process):
    def __init__(self):
        inputs = [
            LiteralInput('message', 'Error Message', data_type='string',
                         abstract='Enter an error message that will be returned.',
                         default="This process failed intentionally.",
                         min_occurs=1,)]

        super(ShowError, self).__init__(
            self._handler,
            identifier='show_error',
            title='Show a WPS Error',
            abstract='This process will fail intentionally with a WPS error message.',
            metadata=[
                Metadata('User Guide', 'https://pywps.org/')],
            version='1.0',
            inputs=inputs,
            # outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    @staticmethod
    def _handler(request, response):
        response.update_status('PyWPS Process started.', 0)

        LOGGER.info("Raise intentionally an error ...")
        raise ProcessError(request.inputs['message'][0].data)
