##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import sys
import tempfile
import pywps.configuration as config
from pywps.processing.basic import Processing

import logging
LOGGER = logging.getLogger("PYWPS")


SLURM_TMPL = """\
#!/bin/bash
#SBATCH -e {workdir}/slurm_{name}.error
#SBATCH -o {workdir}/slurm_{name}.log
#SBATCH -J {name}
#SBATCH --time=00:30:00
#set -eo pipefail -o nounset
export PYWPS_CFG={pywps_cfg}
"{prefix}/bin/launch" "{filename}"
"""


def secure_copy(source, target, host=None):
    """
    Copy source file to remote host.
    """
    from pathos.secure import Copier
    host = host or "localhost"
    copier = Copier(source)
    destination = '{}:{}'.format(host, target)
    copier.config(source=source, destination=destination)
    copier.launch()
    LOGGER.debug("copied source=%s, destination=%s", source, destination)


def sbatch(filename, host=None):
    from pathos import SSH_Launcher
    host = host or "localhost"
    launcher = SSH_Launcher("sbatch")
    launcher.config(command="sbatch {}".format(filename), host=host, background=False)
    launcher.launch()
    slurm_response = launcher.response()
    LOGGER.info("Submitted job to slurm: %s", slurm_response)
    return slurm_response


class Slurm(Processing):
    @property
    def workdir(self):
        return self.job.workdir

    @property
    def uuid(self):
        return self.job.uuid

    def _build_submit_file(self, dump_file_name):
        submit_file_name = tempfile.mkstemp(prefix='slurm_', suffix='.submit', dir=self.workdir)[1]
        with open(submit_file_name, 'w') as fp:
            fp.write(SLURM_TMPL.format(
                name=self.uuid,
                workdir=self.workdir,
                pywps_cfg=os.getenv('PYWPS_CFG'),
                prefix=config.get_config_value('extra', 'prefix'),
                filename=dump_file_name))
            return submit_file_name
        return None

    def start(self):
        LOGGER.info("Submitting job to slurm ...")
        host = config.get_config_value('extra', 'host')
        # dump job to file
        dump_file_name = self.job.dump()
        # copy dumped job to remote host
        # secure_copy(source=dump_file_name, target="/tmp/marshalled", host=host)
        # write submit script
        submit_file_name = self._build_submit_file(dump_file_name)
        # copy submit file to remote
        # secure_copy(source=submit_file_name, target="/tmp/emu.submit", host=host)
        # run remote pywps process
        slurm_response = sbatch(filename=submit_file_name, host=host)
        self.job.wps_response.update_status('PyWPS Process submitted to slurm: %s'.format(slurm_response), 0)
