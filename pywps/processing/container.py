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
import requests
import socket
import time
import json

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
        prcs_dir = self.job.wps_response.process.workdir
        prcs_out_dir = os.path.abspath(config.get_config_value("server", "outputpath"))
        dckr_inp_dir = config.get_config_value("processing", "dckr_inp_dir")
        dckr_out_dir = config.get_config_value("processing", "dckr_out_dir")
        container = self.client.containers.create(cntnr_img, ports={"5000/tcp": self.port}, detach=True,
                                                  volumes={
                                                  prcs_out_dir: {'bind': dckr_out_dir, 'mode': 'rw'},
                                                  prcs_dir: {'bind': dckr_inp_dir, 'mode': 'ro'}
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
        # TODO dat docker chvili cas nez nastartuje
        time.sleep(0.5)
        self._execute()
        self._parse_outputs()
        # TODO stopnout a smaznout docker isntanci

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
        inputs = self.job.wps_request.get_inputs_in_tuples()
        wps = WPS(url=url_execute, skip_caps=True)
        self.execution = wps.execute(self.job.wps_request.identifier, inputs)

    def _parse_outputs(self):
        for output in self.execution.processOutputs:
            self.job.wps_response.outputs[output.identifier].data = output.data[0]
        self.job.wps_response.update_status('PyWPS process {} finished'.format(self.job.process.identifier), status_percentage=100, status=STATUS.DONE_STATUS)
