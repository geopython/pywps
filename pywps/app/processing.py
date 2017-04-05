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
        # marshall process
        dill.dump(self, open('/tmp/marshalled', 'w'))
        # copy marshalled file to remote
        copier = Copier("marshalled")
        copier.config(source='/tmp/marshalled', destination='pingu@docker.example.com:/tmp/marshalled')
        copier.launch()
        # write sbatch script
        with open("/tmp/emu.submit", 'w') as fp:
            fp.write(SLURM_TMPL)
        # copy marshalled file to remote
        copier = Copier("sbatch")
        copier.config(source='/tmp/emu.submit', destination='pingu@docker.example.com:/tmp/emu.submit')
        copier.launch()
        # run remote pywps process
        launcher = SSH_Launcher("test")
        launcher.config(command="sbatch /tmp/emu.submit", host="pingu@docker.example.com", background=False)
        #launcher.config(command="hostname", host="testuser@docker.example.com", background=False)
        launcher.launch()
        LOGGER.info("Starting slurm job: %s", launcher.response())


def launch_slurm_job(filename=None):
    import dill
    filename = filename or '/tmp/marshalled'
    job = dill.load(open(filename))
    job.run()
