from abc import ABCMeta, abstractmethod, abstractproperty
# TODO cover with tests
"""Literaltypes are used for LiteralInputs, to make sure, input data are OK
"""

def convert_boolean(inpt):
    """Return boolean value from input boolean input

    >>> convert_boolean('1')
    True
    >>> convert_boolean('-1')
    True
    >>> convert_boolean('FaLsE')
    False
    >>> convert_boolean('FaLsEx')
    True
    >>> convert_boolean(0)
    False
    """

    val = False
    if str(inpt).lower() in ['false', 'f']:
        val = False
    else:
        try:
            val = int(inpt)
            if val == 0:
                val = False
            else:
                val = True
        except:
            val = True
    return val

def convert_float(inpt):
    """Return float value from inpt

    >>> convert_float('1')
    1.0
    """

    return float(inpt)

def convert_integer(inpt):
    """Return integer value from input inpt

    >>> convert_integer('1.0')
    1
    """

    return int(float(inpt))

def convert_string(inpt):
    """Return string value from input lit_input

    >>> convert_string(1)
    '1'
    """

    return str(inpt)

if __name__ == "__main__":
    import doctest

    doctest.testmod()
