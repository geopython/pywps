##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from basic import TestBase
from pywps.app.exceptions import format_message, ProcessError, DEFAULT_ALLOWED_CHARS


class AppExceptionsTest(TestBase):

    def test_format_message(self):
        assert format_message('no data available') == 'no data available'
        assert format_message(' no data available! ') == 'no data available!'
        assert format_message('no') == ''
        assert format_message('no data available', max_length=7) == 'no data'
        assert format_message('no &data% available') == 'no data available'
        assert format_message(DEFAULT_ALLOWED_CHARS) == DEFAULT_ALLOWED_CHARS

    def test_process_error(self):
        assert ProcessError(' no &data available!').message == 'no data available!'
        assert ProcessError('no', min_length=2).message == 'no'
        assert ProcessError('0 data available', max_length=6).message == '0 data'
        assert ProcessError('no data? not available!', allowed_chars='?').message == 'no data? not available'
        assert ProcessError('').message == 'Sorry, process failed. Please check server error log.'
        assert ProcessError(1234).message == 'Sorry, process failed. Please check server error log.'
        try:
            raise ProcessError('no data!!')
        except ProcessError as e:
            assert f"{e}" == 'no data!!'
        else:
            assert False
