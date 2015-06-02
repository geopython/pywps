""" Validators package, contains classes to validate inputs content.
"""
# Author:    Jachym Cepicky
#            
# License:
#
# Web Processing Service implementation
# Copyright (C) 2014-2015 PyWPS Development Team, represented by Jachym Cepicky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from abc import ABCMeta, abstractmethod, abstractproperty

__all__ = ['literalvalidator', 'complexvalidator']

class MODE(object):
    """Validation modes

    NONE: always true
    SIMPLE: mimeType check
    STRICT: can be opened using standard library (e.g. GDAL)
    VERYSTRICT: Schema passes
    """

    NONE = 0
    SIMPLE = 1
    STRICT = 2
    VERYSTRICT = 3

class ValidatorAbstract(object):
    """Data validator abstract class
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, input, level=MODE.VERYSTRICT):
        """Perform input validation
        """
        True
