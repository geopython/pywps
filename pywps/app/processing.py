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
#SBATCH -e emu.err
#SBATCH -o emu.out
#SBATCH -J emu
#SBATCH --time=00:30:00
set -eo pipefail -o nounset
source activate emu
python -c 'from pywps.app.processing import launch_slurm_job\nlaunch_slurm_job()'
"""


class Slurm(Processing):

    def run(self):
        getattr(self.process, self.method)(self.wps_request, self.wps_response)

    def start(self):
        import dill
        from pathos import SSH_Launcher
        from pathos.secure import Copier
        dill.dump(self, open('/tmp/marshalled', 'w'))
        copier = Copier("marshalled")
        copier.config(source='/tmp/marshalled', destination='testuser@localhost:/tmp/marshalled')
        launcher = SSH_Launcher("test")
        launcher.config(command="sbatch", rhost="localhost", background=True)
        launcher.launch()


def launch_slurm_job(filename=None):
    import dill
    filename = filename or '/tmp/marshalled'
    job = dill.load(open(filename))
    job.run()
