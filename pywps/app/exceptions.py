##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""
Process exceptions raised intentionally in processes to provide information for users.
"""


class ProcessError(Exception):
    """:class:`pywps.app.exceptions.ProcessError` is an :class:`Exception`
    you can intentionally raise in a process
    to provide a user-friendly error message.
    The error message gets validated (3<= message length <=144) and only
    alpha numeric characters and a few special characters are allowed.
    The special characters are: `.`, `:`, `!`, `?`, `=`, `,`, `-`.
    """
    min_msg_length = 3
    max_msg_length = 144
    allowed_chars = ['.', ':', '!', '?', '=', ',', '-']
    default_msg = 'Sorry, process failed. Please check server error log.'

    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return self.message

    def _validate_message(self):
        valid = False
        if self.msg and self.min_msg_length <= len(self.msg) <= self.max_msg_length:
            # remove spaces
            test_str = self.msg.replace(' ', '')
            # remove allowed non alpha-numeric chars
            for char in self.allowed_chars:
                test_str = test_str.replace(char, '')
            # only alpha numeric string accepted
            valid = test_str.isalnum()
        return valid

    @property
    def message(self):
        if self._validate_message():
            new_msg = "{}".format(self.msg)
        else:
            new_msg = self.default_msg
        return new_msg
