##################################################################
# Copyright 2019 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from abc import ABCMeta, abstractmethod


class StorageImplementationBuilder(object):
    """
    Storage implementations should implement
    this class and build method then import and register
    the build class into the StorageBuilder.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def build(self):
        """
        :returns: An object which implements the
                  StorageAbstract class
        """
        raise NotImplementedError
