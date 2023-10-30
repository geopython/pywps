##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Tests for the configuration."""

import os
import unittest
import pytest

from pywps import configuration


class TestEnvInterpolation(unittest.TestCase):
    """Test cases for env variable interpolation within the configuration."""

    @pytest.mark.skip(reason="not working with tox")
    def test_expand_user(self):
        """Ensure we can parse a value with the $USER entry."""
        user = os.environ.get("USER")
        configuration.CONFIG.read_string("[envinterpolationsection]\nuser=$USER")
        assert user == configuration.CONFIG["envinterpolationsection"]["user"]

    @pytest.mark.xfail(reason="not working with tox")
    def test_expand_user_with_some_text(self):
        """Ensure we can parse a value with the $USER entry and some more text."""
        user = os.environ.get("USER")
        new_user = "new_" + user
        configuration.CONFIG.read_string("[envinterpolationsection]\nuser=new_${USER}")
        assert new_user == configuration.CONFIG["envinterpolationsection"]["user"]

    def test_dont_expand_value_without_env_variable(self):
        """
        Ensure we don't expand values that are no env variables.

        Could be an important case for existing config keys that need to
        contain the $symbol.
        """
        key = "$example_key_that_hopefully_will_never_be_a_real_env_variable"
        configuration.CONFIG.read_string("[envinterpolationsection]\nuser=" + key)
        assert key == configuration.CONFIG["envinterpolationsection"]["user"]


def load_tests(loader=None, tests=None, pattern=None):
    """Load the tests and return the test suite for this file."""
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(TestEnvInterpolation),
    ]
    return unittest.TestSuite(suite_list)
