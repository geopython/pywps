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

    @property
    def json(self):
        """Get JSON representation of the metadata
        """
        data = {
            'title': self.title,
            'href': self.href,
            'role': self.role,
            'type': self.type,
        }
        return data

    @classmethod
    def from_json(cls, json_input):
        instance = cls(
            title=json_input['title'],
            href=json_input['href'],
            role=json_input['role'],
            type_=json_input['type'],
        )
        return instance

    def __eq__(self, other):
        return all([
            self.title == other.title,
            self.href == other.href,
            self.role == other.role,
            self.type == other.type,
        ])
