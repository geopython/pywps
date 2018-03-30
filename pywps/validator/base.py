##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from pywps.validator.mode import MODE


def emptyvalidator(data_input, mode):
    """Empty validator will return always false for security reason
    """

    if mode <= MODE.NONE:
        return True
    else:
        return False
