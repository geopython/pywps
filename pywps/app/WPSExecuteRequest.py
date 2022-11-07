##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging

from pywps.exceptions import MissingParameterValue, InvalidParameterValue
from pywps.inout.inputs import ComplexInput, LiteralInput, BoundingBoxInput
from collections import deque

LOGGER = logging.getLogger("PYWPS")


class WPSExecuteRequest(object):

    def __init__(self, process, wps_request):
        self.wps_request = wps_request

        LOGGER.debug('Checking if all mandatory inputs have been passed')
        self.inputs = dict()
        for inpt in process.inputs:
            # Replace the dicts with the dict of Literal/Complex inputs
            # set the input to the type defined in the process.

            request_inputs = None
            if inpt.identifier in wps_request.inputs:
                request_inputs = wps_request.inputs[inpt.identifier]

            if not request_inputs:
                if inpt._default is not None:
                    if not inpt.data_set and isinstance(inpt, ComplexInput):
                        inpt._set_default_value()

                    self.inputs[inpt.identifier] = [inpt.clone()]
            else:

                if isinstance(inpt, ComplexInput):
                    self.inputs[inpt.identifier] = self.create_complex_inputs(
                        inpt, request_inputs)
                elif isinstance(inpt, LiteralInput):
                    self.inputs[inpt.identifier] = self.create_literal_inputs(
                        inpt, request_inputs)
                elif isinstance(inpt, BoundingBoxInput):
                    self.inputs[inpt.identifier] = self.create_bbox_inputs(
                        inpt, request_inputs)

        for inpt in process.inputs:

            if inpt.identifier not in self.inputs:
                if inpt.min_occurs > 0:
                    LOGGER.error('Missing parameter value: {}'.format(inpt.identifier))
                    raise MissingParameterValue(
                        inpt.identifier, inpt.identifier)

    @property
    def json(self):
        raise NotImplementedError("WPSExectuteRequest is not serialisable to json")

    # Fall back to attibute of WPSRequest
    def __getattr__(self, item):
        return getattr(self.wps_request, item)

    @staticmethod
    def create_complex_inputs(source, inputs):
        """Create new ComplexInput as clone of original ComplexInput
        because of inputs can be more than one, take it just as Prototype.

        :param source: The process's input definition.
        :param inputs: The request input data.
        :return collections.deque:
        """

        outinputs = deque(maxlen=source.max_occurs)

        for inpt in inputs:
            data_input = source.clone()
            frmt = data_input.supported_formats[0]
            if 'mimeType' in inpt:
                if inpt['mimeType']:
                    frmt = data_input.get_format(inpt['mimeType'])
                else:
                    frmt = data_input.data_format

            if frmt:
                data_input.data_format = frmt
            else:
                raise InvalidParameterValue(
                    'Invalid mimeType value {} for input {}'.format(inpt.get('mimeType'), source.identifier),
                    'mimeType')

            data_input.method = inpt.get('method', 'GET')
            data_input.process(inpt)
            outinputs.append(data_input)

        if len(outinputs) < source.min_occurs:
            description = "At least {} inputs are required. You provided {}.".format(
                source.min_occurs,
                len(outinputs),
            )
            raise MissingParameterValue(description=description, locator=source.identifier)
        return outinputs

    @staticmethod
    def create_literal_inputs(source, inputs):
        """ Takes the http_request and parses the input to objects
        :return collections.deque:
        """

        outinputs = deque(maxlen=source.max_occurs)

        for inpt in inputs:
            newinpt = source.clone()
            # set the input to the type defined in the process
            newinpt.uom = inpt.get('uom')
            data_type = inpt.get('datatype')
            if data_type:
                newinpt.data_type = data_type

            # get the value of the field
            newinpt.data = inpt.get('data')

            outinputs.append(newinpt)

        if len(outinputs) < source.min_occurs:
            description = "At least {} inputs are required. You provided {}.".format(
                source.min_occurs,
                len(outinputs),
            )
            raise MissingParameterValue(description, locator=source.identifier)

        return outinputs

    @staticmethod
    def create_bbox_inputs(source, inputs):
        """ Takes the http_request and parses the input to objects
        :return collections.deque:
        """

        outinputs = deque(maxlen=source.max_occurs)

        for inpt in inputs:
            newinpt = source.clone()
            newinpt.data = inpt.get('data')
            LOGGER.debug(f'newinpt bbox data={newinpt.data}')
            newinpt.crs = inpt.get('crs')
            newinpt.dimensions = inpt.get('dimensions')
            outinputs.append(newinpt)

        if len(outinputs) < source.min_occurs:
            description = "At least {} inputs are required. You provided {}.".format(
                source.min_occurs,
                len(outinputs),
            )
            raise MissingParameterValue(description=description, locator=source.identifier)

        return outinputs
