##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import pywps.configuration as config
from pywps.processing.basic import Processing

from owslib.wps import WebProcessingService as WPS
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
        self.json = self.job.wps_request.json
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
        raise NoAvailablePortException(port_min, port_max)

    def start(self):
        self.job.wps_response.update_status('Submitting job ...', 0)
        self.cntnr.start()
        # TODO dat docker chvili cas nez nastartuje
        time.sleep(1)
        url_execute = "http://localhost:{}/wps".format(self.port)
        # TODO proc balit data do jsonu?
        # WPSRequest funkce json, zabalit data
        inputs = self.job.wps_request.get_inputs_in_tuples()

        # TODO OWSlib
        #  OWSlib
        wps = WPS(url=url_execute, skip_caps=True)
        # TODO ziskam objekt WPSExecution, co s nim?
        # Jak naparsovat do WPSResponse

        execution = wps.execute(self.job.wps_request.identifier, inputs)
        self.job.wps_response.update_status('Response received')



        # post_resp = requests.post(url=url_execute,
        #                           data=self.job.wps_request.http_request.data.decode("utf-8"),
        #                           headers={'Content-Type': 'application/octet-stream'})

    def cancel(self):
        pass

    def pause(self):
        pass


class NoAvailablePortException(Exception):
    def __init__(self, port_min, port_max):
        self.port_min = port_min
        self.port_max = port_max