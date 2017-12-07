##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import pywps.configuration as config
from pywps.processing.basic import Processing

from OWSLib.owslib.wps import WebProcessingService as WPS
from pywps.response.status import STATUS
from pywps.exceptions import NoAvailablePortException
import docker
import socket
import time
from lxml import etree

from pywps.inout.basic import LiteralInput, ComplexInput, BBoxInput
from OWSLib import owslib
from pywps import FORMATS

import logging
LOGGER = logging.getLogger("PYWPS")


class ClientError:
    pass


class Container(Processing):
    def __init__(self, process, wps_request, wps_response):
        super().__init__(process, wps_request, wps_response)
        self.job.wps_response.update_status('Creating container...', 0)
        self.port = self._assign_port()
        self.client = docker.from_env()
        self.cntnr = self._create()
        self.job.wps_response.update_status('Created container {}'.format(self.cntnr.id))

    def _create(self):
        cntnr_img = config.get_config_value("processing", "docker_img")
        workdir = self.job.wps_response.process.workdir
        prcs_inp_dir = os.path.join(workdir, 'inputs')
        prcs_out_dir = os.path.join(workdir, 'outputs')
        dckr_inp_dir = config.get_config_value("processing", "dckr_inp_dir")
        dckr_out_dir = config.get_config_value("processing", "dckr_out_dir")
        container = self.client.containers.create(cntnr_img, ports={"5000/tcp": self.port}, detach=True,
                                                  volumes={
                                                  prcs_out_dir: {'bind': dckr_out_dir, 'mode': 'rw'},
                                                  prcs_inp_dir: {'bind': dckr_inp_dir, 'mode': 'ro'}
                                                  })
        return container

    def _assign_port(self):
        port_min = int(config.get_config_value("processing", "port_min"))
        port_max = int(config.get_config_value("processing", "port_max"))
        for port in range(port_min, port_max):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            res = sock.connect_ex(('127.0.0.1', port))
            # TODO poresit errno
            if res != 0:
                return port
        raise NoAvailablePortException("No port from range {}-{} available.".format(port_min, port_max))

    def start(self):
        self.job.wps_response.update_status('Starting process ...', 0)
        self.cntnr.start()
        # TODO dat dockeru chvili cas nez nastartuje
        time.sleep(0.5)
        self._execute()
        self._parse_outputs()
        # TODO stopnout a smaznout docker instanci

    def stop(self):
        self.job.wps_response.update_status('Stopping process ...')
        self.cntnr.stop()

    def cancel(self):
        self.job.wps_response.update_status('Killing process ...')
        self.cntnr.kill()

    def pause(self):
        self.job.wps_response.update_status('Pausing process ...')
        self.cntnr.pause()

    def unpause(self):
        self.job.wps_response.update_status('Unpausing process ...')
        self.cntnr.unpause()

    def _execute(self):
        url_execute = "http://localhost:{}/wps".format(self.port)
        inputs = get_inputs(self.job.wps_request.inputs)
        output = get_output(self.job.wps_request.outputs)
        # request = self._prepare_request()
        wps = WPS(url=url_execute, skip_caps=True)
        self.execution = wps.execute(self.job.wps_request.identifier, inputs=inputs, output=output)

    def _parse_outputs(self):
        for output in self.execution.processOutputs:
            # TODO what if len(data) > 1 ??
            if output.data:
                self.job.wps_response.outputs[output.identifier].data = output.data[0]
            if output.reference:
                rp = output.reference[output.reference.index('outputs/'):]
                self.job.wps_response.outputs[output.identifier].file = rp

        self.job.wps_response.update_status('PyWPS process {} finished'.format(self.job.process.identifier), status_percentage=100, status=STATUS.DONE_STATUS)

    # TODO way how to force sync request
    # def _prepare_request(self):
    #     request_xml = etree.fromstring(self.job.wps_request.http_request.data)
    #     requestElement = owslib.wps.WPSExecution().buildRequest(self.job.wps_request.identifier, self.inputs, self.output)
    #     for child in request_xml:
    #         if "ResponseForm" in child.tag:
    #             child[0].set('status', 'false')
    #             responseFormElement = child
    #             requestElement.append(responseFormElement)
    #             break
    #
    #     request = etree.tostring(requestElement)
    #
    #     return request


def get_inputs(job_inputs):
    """
    Return all inputs in [(input_name1, input_value1), (input_name2, input_value2)]
    Return value can be used for WPS.execute method.
    :return: input values
    :rtype:list of tuples
    """
    the_inputs = []
    for key in job_inputs.keys():
        inp = job_inputs[key][0]
        if isinstance(inp, LiteralInput):
            # TODO use inp.source or inp.data?
            ows_inp = str(job_inputs[key][0].source)
        elif isinstance(inp, ComplexInput):
            fp = os.path.basename(job_inputs[key][0].file)
            dckr_inp_dir = config.get_config_value('processing', 'dckr_inp_dir')
            ows_inp = owslib.wps.ComplexDataInput("file://" + os.path.join(dckr_inp_dir, fp))
        elif isinstance(inp, BBoxInput):
            ows_inp = owslib.wps.BoundingBoxDataInput(job_inputs[key][0].source)
        else:
            raise Exception
        the_inputs.append((key, ows_inp))

    return the_inputs


def get_output(job_output):
    """
    Return all outputs name
    Return value can be used for WPS.execute method.
    :return: output names
    :rtype:list
    """
    the_output = []
    for key in job_output.keys():
        the_output.append((key, job_output[key]['asReference']))
    return the_output
