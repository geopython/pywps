from abc import abstractmethod, ABCMeta
from contextlib import contextmanager
import tempfile
from unipath import Path


@contextmanager
def temp_dir():
    tmp = Path(tempfile.mkdtemp())
    try:
        yield tmp
    finally:
        tmp.rmtree()


class PyWPSServerAbstract(object):

    __metaclass__ = ABCMeta

    route_base = '/'

    @abstractmethod
    def run(self):
        raise NotImplementedError()