##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################
""" Set and get language codes, initialize translated messages, so that the
user scan use them directly in processes.

In the process:

    User has to define set of messages for all supported languages, like::

        self.lang["eng"]["key1"] = "Hallo, world!"
        self.lang["eng"]["key2"] = "Foo"
        self.lang["eng"]["key3"] = "Bar"

    Than the user can use self.i18n(key) method, which returns the string
    in preset language (given by client request)

"""

import os

class Lang:
    """Lang class"""

    # static list of language codes

    # taken from
    # http://www.loc.gov/standards/iso639-2/php/code_list.php

   
    #  self.codes[0] =  RFC 4646
    # self.codes[1] = ISO 639-1
    # self.codes[2] = English name
    
    #Good code list RFC 4646:http://sharpertutorials.com/list-of-culture-codes/
    #Note: Previous versions supported  # self.codes[0] = ISO 639-2
    
    codes = [
            ["en-CA","en","english"],
            ["de-DE","de","german"],
            ["fr-FR","fr","french"],
            ["cz-CZ","cz","czech"],
            ["it-IT","it","italian"],
            ["gr-GR","el","greek"],
            ["ca-ES","ca","catalan"],
            ["es-ES","es","spanish"],
            ["fi-FI","fi","finnish"],
            ["sv-SE","sv","swedish"],
            ["pt-PT","pt","portuguese"],
            # to be continued ...
    ]
    defaultCode ="en-CA"

    # static method
    def getCode(langString):
       
        for lang in Lang.codes:
            if langString.lower() in [code.lower() for code in lang]:
                return lang[0]
        # return None if nothing found
        return None

    getCode = staticmethod(getCode)

    def __init__(self):

        # default
        self.code = self.defaultCode
        self.strings = {}
        self.initStrings()

    def setCode(self, code):
        """ Set chosen language code """
        
        self.code = Lang.getCode(code)
        if not self.code:
            self.code = self.defaultCode
        return

    def initStrings(self):
        """ Initialize self.strings object according to known codes from
        Lang.py

        It can be used later like::

            self.strings["eng"]["foo"] = "bar"

        """

        for lang in self.codes:
            self.strings[lang[0]] = {}
        return

    def get(self,key):
        """ Will return desired string in selected language """
       
        if self.strings[self.code].has_key(key):
            return self.strings[self.code][key]
        

        return key

