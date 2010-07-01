# Author:	Jachym Cepicky
#        	http://les-ejk.cz
#               jachym at les-ejk dot cz
# License:
#
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import pywps
from pywps import config
from pywps.Wps import Request
from pywps.Template import TemplateError
import types, traceback,sys

class GetCapabilities(Request):
    """
    Parses input request obtained via HTTP POST encoding - should be XML
    file.

    :param wps: :class:`pywps.Pywps`
    """

    def __init__(self,wps,processes=None):
        """
        """
        Request.__init__(self,wps,processes)

        #
        # ServiceIdentification
        #
        self.templateProcessor.set("encoding",
                                    config.getConfigValue("wps","encoding"))
        self.templateProcessor.set("lang",
                                    self.wps.inputs["language"])
        self.templateProcessor.set("servertitle",
                                    config.getConfigValue("wps","title"))
        self.templateProcessor.set("serverabstract",
                                    config.getConfigValue("wps","abstract"))

        keywordList=[]
        for keyword in config.getConfigValue("wps","keywords").split(','):
            keywordList.append({'keyword':keyword.strip()})
        self.templateProcessor.set("Keywords",keywordList)

        self.templateProcessor.set("Versions",
                                    [{'version':
                                      config.getConfigValue("wps","version")}])
        self.templateProcessor.set("fees",
                                    config.getConfigValue("wps","fees"))
        self.templateProcessor.set("constraints",
                                    config.getConfigValue("wps","constraints"))
        self.templateProcessor.set("url",
                                    config.getConfigValue("wps","serveraddress"))

        #
        # ServiceProvider
        #
        self.templateProcessor.set("providername",
                            config.getConfigValue("provider","providerName"))
        self.templateProcessor.set("individualname",
                        config.getConfigValue("provider","individualName"))
        self.templateProcessor.set("positionname",
                            config.getConfigValue("provider","positionName"))
        self.templateProcessor.set("providersite",
                            config.getConfigValue("provider","providerSite"))
        # phone
        if config.getConfigValue("provider","phoneVoice") or \
        config.getConfigValue("provider","phoneFacsimile"):
            self.templateProcessor.set("phone", 1)
            if config.getConfigValue("provider","phoneVoice"):
                self.templateProcessor.set("phonevoice",
                                    config.getConfigValue("provider","phoneVoice"))
            if config.getConfigValue("provider","phoneFacsimile"):
                self.templateProcessor.set("phonefacsimile",
                                    config.getConfigValue("provider","phoneFacsimile"))
        else:
            self.templateProcessor.set("phone", 0)

        # address
        if config.getConfigValue("provider","deliveryPoint") or \
           config.getConfigValue("provider","city") or \
           config.getConfigValue("provider","administrativeArea") or \
           config.getConfigValue("provider","postalCode") or \
           config.getConfigValue("provider","country") or \
           config.getConfigValue("provider","electronicMailAddress"):

            self.templateProcessor.set("address", 1)
            if config.getConfigValue("provider","deliveryPoint"):
                self.templateProcessor.set("deliverypoint",
                            config.getConfigValue("provider","deliveryPoint"))
            if config.getConfigValue("provider","city"):
                self.templateProcessor.set("city",
                            config.getConfigValue("provider","city"))
            if config.getConfigValue("provider","administrativeArea"):
                self.templateProcessor.set("administrativearea",
                        config.getConfigValue("provider","administrativeArea"))
            if config.getConfigValue("provider","postalCode"):
                self.templateProcessor.set("postalcode",
                            config.getConfigValue("provider","postalCode"))
            if config.getConfigValue("provider","country"):
                self.templateProcessor.set("country",
                            config.getConfigValue("provider","country"))
            if config.getConfigValue("provider","electronicMailAddress"):
                self.templateProcessor.set("electronicmailaddress",
                    config.getConfigValue("provider","electronicMailAddress"))
        else:
           self.templateProcessor.set("address", 0)

        # other ContactInfo
        if config.getConfigValue("provider","role"):
            self.templateProcessor.set("role",
                        config.getConfigValue("provider","role"))
        if config.getConfigValue("provider","hoursofservice"):
            self.templateProcessor.set("hoursofservice",
                        config.getConfigValue("provider","hoursofservice"))
        if config.getConfigValue("provider","contactinstructions"):
            self.templateProcessor.set("contactinstructions",
                        config.getConfigValue("provider","contactinstructions"))

        # OperationsMetadata
        self.templateProcessor.set("Operations",
             [{"operation":"GetCapabilities",
               "url":config.getConfigValue("wps","serveraddress")},
              {"operation":"DescribeProcess",
               "url":config.getConfigValue("wps","serveraddress")},
              {"operation":"Execute",
               "url":config.getConfigValue("wps","serveraddress")}])

        # Processes
        processesData = []

        for process in self.getProcesses("all"):
            processData = {}
            if type(process) == types.InstanceType:
                process.lang.setCode(self.wps.inputs["language"])

                processData["processok"] = 1
                processData["identifier"] = process.identifier
                processData["processversion"] = process.version
                processData["title"] = process.i18n(process.title)
                if process.abstract:
                    processData["abstract"] = process.i18n(process.abstract)
                if process.metadata:
                    processData["Metadata"] = self.formatMetadata(process)
                if process.profile:
                    profiles=[]
                    if type(process.profile) == types.ListType:
                        for profile in process.profile:
                            profiles.append({"profile":profile})
                    else:
                        profiles.append({"profile":process.profile})
                    processData["Profiles"] = profiles
                if process.wsdl:
                    processData["wsdl"] = process.wsdl

            else:
                processData["processok"] = 0
                processData["process"] = repr(process)
            processesData.append(processData)
        self.templateProcessor.set("Processes",processesData)

        # Language
        self.templateProcessor.set("defaultlanguage", pywps.DEFAULT_LANG)
        languages = []
        for lang in self.wps.languages:
            languages.append({"language":lang})
        self.templateProcessor.set("Languages",languages)

        self.response = self.templateProcessor.__str__()
        return
