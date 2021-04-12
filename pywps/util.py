##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import platform
from typing import Union

from pathlib import Path
from urllib.parse import urlparse

is_windows = platform.system() == 'Windows'


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
