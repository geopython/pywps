"""
This module generates XML file with GetCapabilities response of WPS
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

# TODO: Wps/ows content -> attributes/elements
# TODO: Wps/ows mandatory -> oblig 'mandatory' x 'optional' x 'conditional'

from ogc import getcapabilities
from xml.dom.minidom import Document
import append
from pywps.Wps.wpsexceptions import *

class Capabilities:
    def __init__(self,serverSettings,processes):
        """
        Inicialize and create 4 sections of GetCapabilities XML output:

            * ServiceIdentification
            * ServiceProvider
            * OperationsMetadata
            * ProcessOfferings
        
        TODO: ServiceProvider contact is somehow very complicated :-/

        Inputs:
            serverSettings  - file with settings of server (etc/settings.py)
            processes      - module with operations provided by this server
        """

        self.settings = serverSettings  # server settings
        self.WPS = getcapabilities.WPS()
        self.gc = self.WPS.gc            # Structure with all parameters defined in WPS
        self.processes = processes    # Package with operations 
        self.document = Document()
        self.Append = append.Append()

        # creating of the root element Capabilities
        self.Capabilities = self.document.createElementNS(self.WPS.namespaces['wps'],"Capabilities")
        self.Capabilities.setAttribute("version", self.settings.WPS['version'])
        self.Capabilities.setAttribute("xmlns",self.WPS.namespaces['wps'])
        self.Capabilities.setAttribute("xmlns:xlink",self.WPS.namespaces['xlink'])
        self.Capabilities.setAttribute("xmlns:ows",self.WPS.namespaces['ows'])
        self.Capabilities.setAttribute("xmlns:xsi",self.WPS.namespaces['xsi'])
        self.Capabilities.setAttribute("xsi:schemaLocation",self.WPS.namespaces['wps']+' '+self.WPS.schemalocation['wps'])
        self.document.appendChild(self.Capabilities)

        # GetCapabilities has 4 section. Every Section will be added
        self.serviceIdentification(self.Capabilities)
        self.serviceProvider(self.Capabilities)
        self.operationsMetadata(self.Capabilities)
        self.processOfferings(self.Capabilities)
        return
    
    def serviceIdentification(self,parent):
        """
        Creates ServiceIdentification XML Node

        Inputs:
            parent  - node to which the ServiceIdentification node should be appended
        """

        serviceIdentOWS = self.gc['elements']['ServiceIdentification']['elements']
        ServiceIdentificationNode = self.document.createElement("ows:ServiceIdentification")
        parent.appendChild(ServiceIdentificationNode)
        userSettings = self.settings.WPS['ServiceIdentification']

        # for each value in responce structure
        for opt in self.gc['elements']['ServiceIdentification']['order']:
            # keywords
            if opt == "Keywords":
                try:
                    if len(self.settings.WPS['Keywords']) > 0:
                        namespace = self.gc['elements']['ServiceIdentification']['elements']['Keywords']['ns']
                        node = self.document.createElement("%s%s" % (namespace, "Keywords"))
                        for word in self.settings.WPS['Keywords']:
                            keynode = self.document.createElement("%s%s" % (namespace,"Keyword"))
                            keytext = self.document.createTextNode(word)
                            keynode.appendChild(keytext)
                            node.appendChild(keynode)
                        ServiceIdentificationNode.appendChild(node)
                except KeyError:
                    comment = self.document.createComment("Keywords not defined")
                    ServiceIdentificationNode.appendChild(comment)
            else:
                self.Append.Node(
                            document=self.document, 
                            childNode=opt, 
                            parentNode=ServiceIdentificationNode,
                            Elements=serviceIdentOWS, 
                            Values=self.settings.WPS['ServiceIdentification']
                            )
        return

    def serviceProvider(self,parent):
        """
        Creates ServiceIdentification XML Node

        Inputs:
            parent  - node to which the ServiceIdentification node should be appended
        """

        provider = self.document.createElement("ows:ServiceProvider")
        parent.appendChild(provider)

        # FIXME: This should be solved with help of some seperate "contact" function
        for opt in self.gc['elements']['ServiceProvider']['order']:
            if opt == "ServiceContact":
                ns = self.gc['elements']['ServiceProvider']['elements']['ServiceContact']['ns']
                servicecontact =  self.document.createElement("%sServiceContact"% (ns))
                provider.appendChild(servicecontact)
                
                for optS in self.gc['elements']['ServiceProvider']['elements']['ServiceContact']['order']:
                    if optS == "ContactInfo":
                        ns = self.gc['elements']['ServiceProvider']['elements']['ServiceContact']['elements']['ContactInfo']['ns']
                        contactinfo = self.document.createElement("%sContactInfo"% (ns))
                        servicecontact.appendChild(contactinfo)

                        ns = self.gc['elements']['ServiceProvider']['elements']['ServiceContact']['elements']['ContactInfo']['elements']['Address']['ns']
                        address = self.document.createElement("%sAddress"% (ns))
                        contactinfo.appendChild(address)

                        for optA in self.gc['elements']['ServiceProvider']['elements']['ServiceContact']['elements']['ContactInfo']['elements']['Address']['order']:
                            self.Append.Node(
                                document=self.document, 
                                childNode=optA, 
                                parentNode=address,
                                Elements=self.gc['elements']['ServiceProvider']['elements']['ServiceContact']['elements']['ContactInfo']['elements']['Address']['elements'],
                                Values=self.settings.WPS['ServiceProvider']
                                )

                    else:
                        self.Append.Node(
                            document=self.document, 
                            childNode=optS, 
                            parentNode=servicecontact,
                            Elements=self.gc['elements']['ServiceProvider']['elements']['ServiceContact']['elements'],
                            Values=self.settings.WPS['ServiceProvider']
                            )
            else:
                self.Append.Node (
                    document=self.document, 
                    childNode=opt, 
                    parentNode=provider,
                    Elements=self.gc['elements']['ServiceProvider']['elements'],
                    Values=self.settings.WPS['ServiceProvider']
                    )
        return

    def operationsMetadata(self,parent):
        """
        Creates OperationsMetadata XML Node

        Inputs:
            parent  - node to which the ServiceIdentification node should be appended
        """

        operations = self.document.createElement("ows:OperationsMetadata")
        opMetDat = self.gc['elements']['OperationsMetadata']
        parent.appendChild(operations)


        # Operation part
        for request in opMetDat['elements']['Operation']['values']:
            # Create one <Operation> node
            namespace = opMetDat['elements']['Operation']['ns']
            operation = self.document.createElement("%s%s" % 
                    (namespace,"Operation"))
            operation.setAttribute("name",request)
            operations.appendChild(operation)

            # and in the <Operation> node is only one <DCP> node
            namespace = opMetDat['elements']['Operation']['elements']['DCP']['ns']
            dcp = self.document.createElement("%s%s"%(namespace,"DCP"))
            operation.appendChild(dcp)
            
            # and in the <DCP> node is only one <HTTP> node
            namespace = \
                opMetDat['elements']['Operation']['elements']['DCP']['HTTP']['ns']
            http = self.document.createElement("%s%s"%(namespace,"HTTP"))
            dcp.appendChild(http)

            # for each protocol (Get and Post) create the appropriate node
            protocols =\
                opMetDat['elements']['Operation']['elements']['DCP']['HTTP']['elements']
            for proto in protocols:
                node = self.document.createElement("%s%s"%(namespace,proto))
                http.appendChild(node)
                try:
                    address = self.settings.WPS['OperationsMetadata']['ServerAddress']
                    
                    # appending '?' or '&' to the end of address, if needed
                    if proto.lower() == "get":
                        if address[-1] != "?" and address[-1] != "&": 
                            address = address + "?"
                    else:
                        if address[-1] == "?" or address[-1] == "&": 
                            address = address[:-1]

                    node.setAttribute("%shref" % (protocols[proto]['attributes']['href']['ns']),address)
                except KeyError: 
                   node.appendChild(self.document.createComment("===== Server Address not set =====")) 

            
        return

    def processOfferings(self,parent):
        """
        Creates ProcessOfferings XML Node

        Inputs:
            parent  - node to which the ServiceIdentification node should be appended
        """

        processesOfferings = self.document.createElement("ProcessOfferings")
        parent.appendChild(processesOfferings)
        POff = self.gc['elements']['ProcessOfferings']

        # for each process 
        for process in self.processes.__all__:
            try:
                thisProcess = eval("self.processes."+process+".Process()")
            except Exception, e:
                raise ServerError("Process %s not initialized well: %s" % \
                        (process, e))

            processNode = self.document.createElement("%s%s" % (POff['Process']['ns'],"Process"))
            try:
                processNode.setAttribute("%s%s" % (POff['Process']['attributes']['processVersion']['ns'],\
                        "processVersion"),thisProcess.processVersion)
            except KeyError:
                pass

                
            # append defined nodes to process
            for opt in POff['Process']['order']:
                if opt == "Metadata":
                    continue
                self.Append.Node(
                    document=self.document, 
                    childNode=opt, 
                    parentNode=processNode,
                    Elements=POff['Process']['elements'], 
                    Values=thisProcess,
                    )
            processesOfferings.appendChild(processNode)
        return

if __name__ == "__main__":
    print """
    This file can be used only as module
    """

