##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import pywps.configuration as config
from pywps.processing.basic import Processing

from owslib.wps import WebProcessingService as WPS
from pywps.response.status import STATUS
from pywps.exceptions import NoAvailablePortException
import docker
import requests
import socket
import time
import json

import logging
LOGGER = logging.getLogger("PYWPS")


class Container(Processing):
    def __init__(self, process, wps_request, wps_response):
        super().__init__(process, wps_request, wps_response)
        self.job.wps_response.update_status('Creating container...', 0)
        self.port = self._assign_port()
        self.client = docker.from_env()
        self.cntnr = self._create()
        # self.json = self.job.wps_request.json
        self.job.wps_response.update_status('Created container {}'.format(self.cntnr.id))

    def _create(self):
        container = self.client.containers.create("pywps4-demo", ports={"5000/tcp": self.port}, detach=True)
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
        # TODO dat docker chvili cas nez nastartuje
        time.sleep(0.5)
        self._execute()
        self._parse_outputs()
        # TODO stopnout a smaznout docker isntanci

    def stop(self):
        self.job.wps_response.update_status('Stopping process ...')
        self.cntnr.stop()

    def kill(self):
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
        # TODO proc balit data do jsonu?
        # WPSRequest funkce json, zabalit data
        # Pro WPSExecution potrebuju tuples
        inputs = self.job.wps_request.get_inputs_in_tuples()

        # TODO ziskam objekt WPSExecution, co s nim?
        # Jak naparsovat do WPSResponse
        wps = WPS(url=url_execute, skip_caps=True)
        self.execution = wps.execute(self.job.wps_request.identifier, inputs)

    # def _get_outputs_old(self):
    #     self.job.wps_response.outputs['response'].data = self.execution.processOutputs[0].data[0]
    #     # TODO UOM??
    #     # self.job.wps_response.outputs['response'].uom = UOM('unity')
    #     self.job.wps_response.update_status('Job finished', status_percentage=100, status=STATUS.DONE_STATUS)

    def _parse_outputs(self):
        for output in self.execution.processOutputs:
            self.job.wps_response.outputs[output.identifier].data = output.data[0]
        self.job.wps_response.update_status('PyWPS process {} finished'.format(self.job.process.identifier), status_percentage=100, status=STATUS.DONE_STATUS)

    # def _execute_na_prase(self):
    #     Stary zpusob rovnou pres request
    #     post_resp = requests.post(url=url_execute,
    #                               data=self.job.wps_request.http_request.data.decode("utf-8"),
    #                               headers={'Content-Type': 'application/octet-stream'})
    #
    #     String s odpovedi
    #     exec = WPSExecution()
    #     exec_req = exec.buildRequest(self.job.process.identifier, inputs)
    #     exec_reader = WPSExecuteReader()
    #     data = etree.tostring(exec_req)
    #     response = exec_reader.readFromUrl(url=url_execute, data=data, method='Post')
    #     string = etree.tostring(response)
