import os
import tempfile
import pywps.configuration as config

import logging
LOGGER = logging.getLogger("PYWPS")


def Process(process, wps_request, wps_response):
    #return MultiProcessing(process, wps_request, wps_response)
    return Slurm(process, wps_request, wps_response)


class Processing(object):

    def __init__(self, process, wps_request, wps_response):
        self.process = process
        self.method = '_run_process'
        self.wps_request = wps_request
        self.wps_response = wps_response

    def start(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")

    def cancel(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")

    def suspend(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")

    def resume(self):
        raise NotImplementedError("Needs to be implemented in a subclass.")


class MultiProcessing(Processing):

    def start(self):
        import multiprocessing
        process = multiprocessing.Process(
            target=getattr(self.process, self.method),
            args=(self.wps_request, self.wps_response)
        )
        process.start()


SLURM_TMPL = """\
#!/bin/bash
#SBATCH -e /tmp/emu.err
#SBATCH -o /tmp/emu.out
#SBATCH -J emu
#SBATCH --time=12:30:00
#set -eo pipefail -o nounset
export PATH="/home/pingu/anaconda/bin:$PATH"
source activate emu;python -c 'from pywps.app.processing import launch_slurm_job\nlaunch_slurm_job()'
"""


class Slurm(Processing):

    def run(self):
        getattr(self.process, self.method)(self.wps_request, self.wps_response)

    def start(self):
        import dill
        from pathos import SSH_Launcher
        from pathos.secure import Copier
        workdir = config.get_config_value('server', 'workdir')
        host = config.get_config_value('extra', 'host')
        # marshall process
        dump_file_name = tempfile.mkstemp(prefix='process_', suffix='.dump', dir=workdir)[1]
        dill.dump(self, open(dump_file_name, 'w'))
        # copy marshalled file to remote
        copier = Copier("dump")
        copier.config(source=dump_file_name, destination='{}:/tmp/marshalled'.format(host))
        copier.launch()
        LOGGER.debug("dump file=%s", dump_file_name)
        # write sbatch script
        submit_file_name = tempfile.mkstemp(prefix='slurm_', suffix='.submit', dir=workdir)[1]
        with open(submit_file_name, 'w') as fp:
            fp.write(SLURM_TMPL)
        # copy marshalled file to remote
        copier = Copier("batch")
        copier.config(source=submit_file_name, destination='{}:/tmp/emu.submit'.format(host))
        copier.launch()
        LOGGER.debug("batch file=%s", submit_file_name)
        # run remote pywps process
        launcher = SSH_Launcher("test")
        launcher.config(command="sbatch /tmp/emu.submit", host=host, background=False)
        #launcher.config(command="hostname", host="testuser@docker.example.com", background=False)
        launcher.launch()
        LOGGER.info("Starting slurm job: %s", launcher.response())


def launch_slurm_job(filename=None):
    import dill
    filename = filename or '/tmp/marshalled'
    job = dill.load(open(filename))
    job.run()
