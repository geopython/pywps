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


class Slurm(Processing):

    def run(self):
        getattr(self.process, self.method)(self.wps_request, self.wps_response)

    def start(self):
        import dill
        from pathos import SSH_Launcher
        dill.dump(self, open('/tmp/marshalled', 'w'))
        launcher = SSH_Launcher("test")
        command = "source activate emu;"
        command += """python -c 'from pywps.app.processing import launch_slurm_job\nlaunch_slurm_job()'"""
        launcher.config(command=command, rhost="localhost", background=True)
        launcher.launch()


def launch_slurm_job(filename=None):
    import dill
    filename = filename or '/tmp/marshalled'
    job = dill.load(open(filename))
    job.run()
