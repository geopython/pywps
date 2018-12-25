##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import pywps.configuration as config
from pywps.processing.basic import Processing

from owslib.wps import WebProcessingService as WPS
from pywps.response.status import WPS_STATUS
from pywps.exceptions import NoAvailablePort

import docker
import socket
import time
import threading

from pywps.inout.basic import LiteralInput, ComplexInput, BBoxInput
import owslib
from pywps.dblog import store_status


import logging
LOGGER = logging.getLogger("PYWPS")


class ClientError:
    pass


class Container(Processing):
    def __init__(self, process, wps_request, wps_response):
        super().__init__(process, wps_request, wps_response)
        self.port = _assign_port()
        self.client = docker.from_env()
        self.cntnr = self._create()

    def _create(self):
        cntnr_img = config.get_config_value("processing", "docker_img")
        prcs_inp_dir = self.job.wps_response.process.workdir
        prcs_out_dir = config.get_config_value("server", "outputpath")
        dckr_inp_dir = config.get_config_value("processing", "dckr_inp_dir")
        dckr_out_dir = config.get_config_value("processing", "dckr_out_dir")
        container = self.client.containers.create(cntnr_img, ports={"5000/tcp": self.port}, detach=True,
                                              volumes={
                                              prcs_out_dir: {'bind': dckr_out_dir, 'mode': 'rw'},
                                              prcs_inp_dir: {'bind': dckr_inp_dir, 'mode': 'ro'}
                                              })
        return container

    def start(self):
        self.cntnr.start()
        # it takes some time to start the container
        time.sleep(1)
        self._execute()

        if self.job.process.async:
            self._parse_status()
            daemon = threading.Thread(target=check_status, args=(self,))
            daemon.start()
        else:
            self._parse_outputs()
            daemon = threading.Thread(target=self.dirty_clean)
            daemon.start()

    def stop(self):
        self.cntnr.stop()

    def cancel(self):
        self.cntnr.kill()

    def pause(self):
        self.cntnr.pause()

    def unpause(self):
        self.cntnr.unpause()

    def _execute(self):
        url_execute = "http://localhost:{}/wps".format(self.port)
        inputs = get_inputs(self.job.wps_request.inputs)
        output = get_output(self.job.wps_request.outputs)
        wps = WPS(url=url_execute, skip_caps=True)
        if self.job.process.async:
            mode = "async"
        else:
            mode = "sync"
        self.execution = wps.execute(self.job.wps_request.identifier, inputs=inputs, output=output, mode=mode)

    def _parse_outputs(self):
        for output in self.execution.processOutputs:
            # TODO what if len(data) > 1 ??
            if output.data:
                self.job.wps_response.outputs[output.identifier].data = output.data[0]
            if output.reference:
                rp = output.reference[output.reference.index('outputs/'):]
                self.job.wps_response.outputs[output.identifier].file = rp

        self.job.wps_response.update_status_succeeded('PyWPS Process {} finished'.format(self.job.process.title))
        store_status(self.job.wps_response.uuid, self.job.wps_response.status, self.job.wps_response.message)

    def _parse_status(self):
        self.job.process.status_url = self.execution.statusLocation
        self.job.wps_response.update_status(message=self.execution.statusMessage)

    def dirty_clean(self):
        self.cntnr.stop()
        self.cntnr.remove()
        self.job.process.clean()
        self.update_status()

    def update_status(self):
        self.job.wps_response.message = 'PyWPS Process {} finished'.format(self.job.process.title)
        self.job.wps_response.percentage = 100
        self.job.wps_response.status = WPS_STATUS.SUCCEEDED
        store_status(self.job.wps_response.uuid, self.job.wps_response.status, self.job.wps_response.message,
                     self.job.wps_response.percentage)


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
            ows_inp = str(inp.data)
        elif isinstance(inp, ComplexInput):
            fp = os.path.basename(inp.file)
            dckr_inp_dir = config.get_config_value('processing', 'dckr_inp_dir')
            ows_inp = owslib.wps.ComplexDataInput("file://" + os.path.join(dckr_inp_dir, fp))
        elif isinstance(inp, BBoxInput):
            ows_inp = owslib.wps.BoundingBoxDataInput(inp.data)
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


def _assign_port():
    port_min = int(config.get_config_value("processing", "port_min"))
    port_max = int(config.get_config_value("processing", "port_max"))
    for port in range(port_min, port_max):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = sock.connect_ex(('127.0.0.1', port))
        # TODO find better solution for errno
        if res != 0:
            return port
    raise NoAvailablePort("No port from range {}-{} available.".format(port_min, port_max))


def check_status(container):
    sleep_secs = int(config.get_config_value('processing', 'sleep_secs'))
    while True:
        container.execution.checkStatus(sleepSecs=sleep_secs)
        if container.execution.isComplete():
            container.dirty_clean()
            break
