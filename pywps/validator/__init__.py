"""Validatating functions for various inputs
"""
from collections import namedtuple

__all__ = ['literalvalidator', 'complexvalidator']

_MODE = namedtuple('Mode', 'NONE, SIMPLE, STRICT, VERYSTRICT')

MODE = _MODE(0, 1, 2, 3)
