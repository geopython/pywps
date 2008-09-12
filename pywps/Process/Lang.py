""" Set and get language codes, initialize translated messages, so that the
user scan use them directly in processes.

In the process:

    User has to define set of messages for all supported languages, like

    self.lang["eng"]["key1"] = "Hallo, world!"
    self.lang["eng"]["key2"] = "Foo"
    self.lang["eng"]["key3"] = "Bar"

    Than the user can use self.i18n(key) method, which returns the string
    in preset language (given by client request)

"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz 
# Lince: 
# 
# Web Processing Service implementation 
# Copyright (C) 2006 Jachym Cepicky 
# 
# This program is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; either version 2 of the License.  
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import os

class Lang:
    def __init__(self):

        # taken from
        # http://www.loc.gov/standards/iso639-2/php/code_list.php

        # self.codes[0] = ISO 639-2 
        # self.codes[1] = ISO 639-1
        # self.codes[2] = English name

        self.codes = [
                ["eng","en","english"],
                ["ger","de","german"],
                ["fre","fr","french"],
                ["cze","cz","czech"],
                ["ita","it","italian"]
                # to be continued ...
        ]

        # default
        self.code = "eng"
        self.defaultCode ="eng"
        self.strings = {}

        self.initStrings()
        self.setCode()

    def getCode(self, langString):

        for lang in self.codes:
            if langString in lang:
                return lang[0]

        # return english, if nothing found
        return self.defaultCode

    def setCode(self):
        """ Set chosen language code """

        # HACK - wouldn't there be some better way, that to use the
        # environment variable ?
        if os.getenv("PYWPS_LANGUAGE"):
            self.code = self.getCode(os.getenv("PYWPS_LANGUAGE"))

    def initStrings(self):
        """ Initialize self.strings object according to known codes from
        Lang.py

        It can be used later like:
            self.strings["eng"]["foo"] = "bar"

        """

        for lang in self.codes:
            self.strings[lang[0]] = {}
        return

    def get(self,key):
        """ Will return desired string in selected language """
        
        for string in self.strings:
            if self.strings[self.code].has_key(key):
                return self.strings[self.code][key]
        # return key, if not found
        return key

