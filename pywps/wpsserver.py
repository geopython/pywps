from abc import abstractmethod, ABCMeta
from contextlib import contextmanager
import tempfile
import flask
from path import path

@contextmanager
def temp_dir():
    tmp = path(tempfile.mkdtemp())
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