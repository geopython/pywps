##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################


import logging

LOGGER = logging.getLogger("PYWPS")


class Metadata(object):
    """
    ows:Metadata content model.

    :param title: Metadata title, human readable string
    :param href: fully qualified URL
    :param type_: fully qualified URL
    """

    def __init__(self, title, href=None, type_='simple'):
        self.title = title
        self.href = href
        self.type = type_

    def __iter__(self):
        yield '{http://www.w3.org/1999/xlink}title', self.title
        if self.href is not None:
            yield '{http://www.w3.org/1999/xlink}href', self.href
        yield '{http://www.w3.org/1999/xlink}type', self.type
