##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Tests for the configuration."""

from basic import TestBase
import os
import unittest
import pytest

from pywps import configuration


class TestEnvInterpolation(TestBase):
    """Test cases for env variable interpolation within the configuration."""
    test_value = "SOME_RANDOM_VALUE"

    def setUp(self) -> None:
        super().setUp()
        # Generate an unused environment key
        self.test_key = "SOME_RANDOM_KEY"
        while self.test_key in os.environ:
            self.test_key = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=32))
        os.environ[self.test_key] = self.test_value

    def tearDown(self) -> None:
        del os.environ[self.test_key]
        super().tearDown()

    def test_expand_user(self):
        """Ensure we can parse a value with the $USER entry."""
        configuration.CONFIG.read_string(f"[envinterpolationsection]\nuser=${self.test_key}")
        assert self.test_value == configuration.CONFIG["envinterpolationsection"]["user"]

    def test_expand_user_with_some_text(self):
        """Ensure we can parse a value with the $USER entry and some more text."""
        new_user = "new_" + self.test_value
        configuration.CONFIG.read_string(f"[envinterpolationsection]\nuser=new_${{{self.test_key}}}")
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
    import unittest

    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(TestEnvInterpolation),
    ]
    return unittest.TestSuite(suite_list)
