##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import platform
from typing import Union

from pathlib import Path
from urllib.parse import urlparse
import os

is_windows = platform.system() == 'Windows'

import struct
import fcntl


def file_uri(path: Union[str, Path]) -> str:
    path = Path(path)
    path = path.as_uri()
    return str(path)


def uri_to_path(uri) -> str:
    p = urlparse(uri)
    path = p.path
    if is_windows:
        path = str(Path(path)).lstrip('\\')
    return path


class FileLock():
    """Implement a file based lock"""

    def __init__(self, filename):
        self._fd = os.open(filename, os.O_RDWR | os.O_CREAT)

    def acquire(self):
        # Wait to lock the whole file
        fcntl.fcntl(self._fd, fcntl.F_SETLKW, struct.pack("hhlll", fcntl.F_WRLCK, os.SEEK_SET, 0, 0, 0))
        pass

    def release(self):
        # Unlock the file
        fcntl.fcntl(self._fd, fcntl.F_SETLKW, struct.pack("hhlll", fcntl.F_UNLCK, os.SEEK_SET, 0, 0, 0))
        pass

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args, **kwargs):
        self.release()

    def __del__(self):
        self.release()
        os.close(self._fd)
