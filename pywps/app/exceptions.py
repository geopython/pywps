##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""
Process exceptions raised intentionally in processes to provide information for users.
"""

import re

DEFAULT_ALLOWED_CHARS = ".:!?=,;-_/"

import logging

LOGGER = logging.getLogger('PYWPS')


def format_message(text, min_length=3, max_length=300, allowed_chars=None):
    allowed_chars = allowed_chars or DEFAULT_ALLOWED_CHARS
    special = re.escape(allowed_chars)
    pattern = rf'[\w{special}]+'
    msg = ' '.join(re.findall(pattern, text))
    msg.strip()
    if len(msg) >= min_length:
        msg = msg[:max_length]
    else:
        msg = ''
    return msg


class ProcessError(Exception):
    """:class:`pywps.app.exceptions.ProcessError` is an :class:`Exception`
    you can intentionally raise in a process
    to provide a user-friendly error message.
    The error message gets formatted (3<= message length <=300) and only
    alpha numeric characters and a few special characters are allowed.
    """
    default_msg = 'Sorry, process failed. Please check server error log.'

    def __init__(self, msg=None, min_length=3, max_length=300, allowed_chars=None):
        self.msg = msg
        self.min_length = min_length
        self.max_length = max_length
        self.allowed_chars = allowed_chars or DEFAULT_ALLOWED_CHARS

    def __str__(self):
        return self.message

    @property
    def message(self):
        try:
            msg = format_message(
                self.msg,
                min_length=self.min_length,
                max_length=self.max_length,
                allowed_chars=self.allowed_chars)
        except Exception as e:
            LOGGER.warning(f"process error formatting failed: {e}")
            msg = None
        if not msg:
            msg = self.default_msg
        return msg
