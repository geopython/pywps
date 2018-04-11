##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import logging

LOGGER = logging.getLogger("PYWPS")


class Metadata(object):
    """
    ows:Metadata content model.

    :param title: Metadata title, human readable string
    :param href: fully qualified URL
    :param role: fully qualified URL
    :param type_: fully qualified URL
    """

    def __init__(self, title, href=None, role=None, type_='simple'):
        self.title = title
        self.href = href
        self.role = role
        self.type = type_

    def __iter__(self):
        metadata = {"title": self.title}

        if self.href is not None:
            metadata['href'] = self.href
        if self.role is not None:
            metadata['role'] = self.role
        metadata['type'] = self.type
        yield metadata
