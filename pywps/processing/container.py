##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import pywps.configuration as config
from pywps.processing.basic import Processing
from pywps.exceptions import SchedulerNotAvailable

import docker
import requests

import logging
LOGGER = logging.getLogger("PYWPS")


class Container(Processing):
    def __init__(self, process, wps_request, wps_response):
        super().__init__(process, wps_request, wps_response)
        self.job.wps_response.update_status('Creating container...', 0)
        self.port = 5050
        self.client = docker.from_env()
        self.cntnr = self.create()
        self.job.wps_response.update_status('Created container {}'.format(self.cntnr.id))

    def create(self):
        container = self.client.containers.create("pywps4-demo", ports={"5000/tcp": self.port}, detach=True)
        return container

    def start(self):
        self.job.wps_response.update_status('Submitting job ...', 0)
        self.cntnr.start()
        url_execute = "http://localhost:{}/wps"\
            .format(self.port)
        post_resp = requests.post(url=url_execute,
                                  data=self.job.wps_request.http_request.data.decode("utf-8"),
                                  headers={'Content-Type': 'application/octet-stream'})
        pass

    def cancel(self):
        pass

    def pause(self):
        pass
