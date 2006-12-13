"""
This module generates XML file with DescribeProcess response of WPS
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

import wpsexceptions

class Append:
    """
    Appending XML nodes or their attributes
    """
    def Node(self,document,childNode,parentNode,Elements,Values):
        """
        Append Node to parent node

        document    - for creating nodes or comments
        childNode   - node, which is tryed to be clipped
        parentNode  - node, to which the child node should be appended
        Elements    - structure with ogs's configuration
        Values      - Structure with settings values, which should
                      corespond to Elements structure
        """
        try: 
            try:
                ns = Elements[childNode]['ns']
            except KeyError:
                ns = ""
            node = document.createElement("%s%s" % (ns,childNode))
            if type(Values) == type({}):
               str = Values[childNode]
               if type(str) != type(''):
                   str = repr(str)
               text = document.createTextNode(str)
            else:
                text = document.createTextNode(eval("Values.%s" % (childNode)))
            node.appendChild(text)
            parentNode.appendChild(node)
        except (KeyError,AttributeError):
            # is this option mandatory?
            try:
                if Elements[childNode]['oblig'] == 'm':
                    # try to create the node with default value
                    try:
                        ns = Elements[childNode]['ns']
                    except KeyError:
                        ns = ""
                    try:
                        node = document.createElement("%s%s" % (ns,childNode))
                        str = Elements[childNode]['default']
                        if type(str) != type(''):
                            str = repr(str)
                        text = document.createTextNode(str)
                        node.appendChild(text)
                        parentNode.appendChild(node)
                    # error - OK, giving up
                    except KeyError:
                        parentNode.appendChild(
                                document.createComment(
                """===== !! Mandatory element `%s' not set. Verify your conf. file !! =====""" % \
                                    (childNode)))

                # let it be else
                else:
                    try:
                        node = document.createElement("%s%s" % (ns,childNode))
                        str = Elements[childNode]['default']
                        if type(str) != type(''):
                            str = repr(str)
                        text = document.createTextNode(str)
                        node.appendChild(text)
                        parentNode.appendChild(node)
                    except KeyError:
                        parentNode.appendChild(document.createComment("Element %s not set" % (childNode)))
            except KeyError, what:
                parentNode.appendChild(document.createComment("Element %s not set" % (childNode)))
        return
   
    def Attribute(self,document,attributeName,Node,Attributes,Values):
        """
        Try to add attribute, to node

        document    -   XML document, for creating comments and attributes
                        and nodes
        attributeName - e.g. "version"
        Node        -   node name, e.g. <Execute>
        Attributes  -   ogc's configuration structure
        Values      -   coresponding settings values
        """
        try: 
            try:
                ns = Attributes[attributeName]['ns']
            except KeyError:
                ns = ""
            if type(Values) == type({}):
                Node.setAttribute(attributeName,Values[attributeName])
            else:
                Node.setAttribute("%s%s" % (ns,attributeName),eval("Values.%s" % (attributeName)))
        except (KeyError,AttributeError),e:
            # is this option mandatory?
            try:
                if Attributes[attributeName]['oblig'] == 'm':
                    # try to create the node with default value
                    try:
                        ns = Attributes[attributeName]['ns']
                    except KeyError:
                        ns = ""
                    try:
                        Node.setAttribute("%s%s" % \
                                (ns,attributeName),Attributes[attributeName]['default'])
                    # error - OK, giving up
                    except (KeyError, AttributeError), what:
                        Node.appendChild(document.createComment(
                "===== !! Mandatory attribute `%s' not set. Verify your conf. file !! =====" %\
                        (attributeName)))

                # else try to determine the default value, or let it just be
                else:
                    try:
                        try:
                            ns = Attributes[attributeName]['ns']
                        except KeyError:
                            ns = ""
                        Node.setAttribute("%s%s" % \
                                (ns,attributeName),Attributes[attributeName]['default'])
                    except (KeyError,AttributeError):
                        Node.appendChild(document.createComment("Attribute %s not set" % \
                                    (attributeName)))
            except (KeyError, AttributeError), what:
                Node.appendChild(document.createComment("Attribute %s not set" % (Attribute)))
        return
