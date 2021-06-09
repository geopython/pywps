##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from json import JSONEncoder


class ArrayEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'tolist'):
            # this will work for array.array and numpy.ndarray
            return obj.tolist()
        return JSONEncoder.default(self, obj)
