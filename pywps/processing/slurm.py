##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import tempfile
import pywps.configuration as config
from pywps.processing.basic import Processing

import logging
LOGGER = logging.getLogger("PYWPS")


SLURM_TMPL = """\
#!/bin/bash
#SBATCH -e /tmp/emu.err
#SBATCH -o /tmp/emu.out
#SBATCH -J emu
#SBATCH --time=12:30:00
#set -eo pipefail -o nounset
export PATH="/home/pingu/anaconda/bin:$PATH"
source activate emu;python -c 'from pywps.processing import launch_slurm_job\nlaunch_slurm_job()'
"""


def ssh_copy(source, target, host):
    """
    Copy source file to remote host.
    """
    from pathos.secure import Copier
    copier = Copier(source)
    destination = '{}:{}'.format(host, target)
    copier.config(source=source, destination=destination)
    copier.launch()
    LOGGER.debug("copied source=%s, destination=%s", source, destination)


def launch(filename, host):
    from pathos import SSH_Launcher
    launcher = SSH_Launcher("sbatch")
    launcher.config(command="sbatch {}".format(filename), host=host, background=False)
    launcher.launch()
    LOGGER.info("Starting slurm job: %s", launcher.response())


class Slurm(Processing):

    def run(self):
        getattr(self.process, self.method)(self.wps_request, self.wps_response)

    def start(self):
        import dill
        workdir = config.get_config_value('server', 'workdir')
        host = config.get_config_value('extra', 'host')
        # marshall process
        dump_file_name = tempfile.mkstemp(prefix='process_', suffix='.dump', dir=workdir)[1]
        dill.dump(self, open(dump_file_name, 'w'))
        # copy dumped file to remote
        ssh_copy(source=dump_file_name, target="/tmp/marshalled", host=host)
        # write submit script
        submit_file_name = tempfile.mkstemp(prefix='slurm_', suffix='.submit', dir=workdir)[1]
        with open(submit_file_name, 'w') as fp:
            fp.write(SLURM_TMPL)
        # copy submit file to remote
        ssh_copy(source=submit_file_name, target="/tmp/emu.submit", host=host)
        # run remote pywps process
        launch(filename="/tmp/emu.submit", host=host)


def launch_slurm_job(filename=None):
    import dill
    filename = filename or '/tmp/marshalled'
    job = dill.load(open(filename))
    job.run()
