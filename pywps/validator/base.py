from pywps.validator.mode import MODE

def emptyvalidator(data_input, mode):
    """Empty validator will return always false for security reason
    """

    if mode <= MODE.NONE:
        return True
    else:
        return False


