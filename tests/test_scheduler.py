import unittest
import pickle


class Process(object):
    def __init__(self, identifier):
        self.identifier = identifier

    def _run_process(self, wps_request, wps_response):
        print "job done"


class WPSRequest(object):
    def __init__(self):
        self.status = 'accepted'


class WPSResponse(object):
    def __init__(self):
        self.status = 'done'


class Scheduler(object):
    def __init__(self, target, method, args):
        self._target = target
        self._method = method
        self._args = args

    def run(self):
        getattr(self._target, self._method)(*self._args)

    def start(self):
        marshalled_str = pickle.dumps(self)
        obj = pickle.loads(marshalled_str)
        obj.run()


class SchedulerTest(unittest.TestCase):

    def test_scheduler(self):
        p = Process(1234)
        s = Scheduler(target=p, method='_run_process', args=(WPSRequest(), WPSResponse()))
        s.start()


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(SchedulerTest),
    ]
    return unittest.TestSuite(suite_list)
