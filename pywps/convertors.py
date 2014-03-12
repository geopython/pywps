from abc import ABCMeta, abstractmethod, abstractproperty
# TODO cover with tests
"""Convertors are used for LiteralInputs, to make sure, input data are OK
"""

class MODE:
    """Convertion mode

    NONE: return input value as it is
    BASIC: make only convertion
    VALIDATE: check for aditional input rules
    STRICT: check for various potential problems (SQL injection etc.)
    """
    NONE = 0
    BASIC = 1
    VALIDATE = 2
    STRICT = 3


class ConvertorAbstract(object):
    """Abstract class for all convertors
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def convert(self, inpt, level=MODE.STRICT):
        """Perform input conversion
        """
        pass

class BasicConvertor(ConvertorAbstract):
    """Data convertor implements ConvertorAbstract class

    """

    def convert(self, lit_input, level=MODE.STRICT):
        """Perform input validation
        """
        return lit_input


def convert_boolean(bool_input, mode):
    """Return boolean value from input bool_input"""

    data = bool_input.data

    if mode >= MODE.NONE:
        pass

    elif mode >= MODE.BASIC:
        if str(data).lower() in ['false', 'f']:
            data = False
        else:
            try:
                data = int(data)
                if data == 0:
                    data = False
                else:
                    data = True
            except:
                data = True

    return data

def convert_integer(lit_input, mode):
    """Return integer value from input lit_input"""

    data = lit_input.data

    if mode >= MODE.NONE:
        pass

    elif mode >= MODE.BASIC:
        data = int(data)

    return data

def convert_string(lit_input, mode):
    """Return string value from input lit_input"""

    data = lit_input.data

    if mode >= MODE.NONE:
        pass

    elif mode >= MODE.BASIC:
        data = str(data)

    elif mode >= MODE.VALIDATE:
        # check for not allowed characters
        # TODO
        # raise ValidationException()
        pass

    return data

