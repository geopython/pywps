"""
This module parses OGC Web Processing Service (WPS) GetCapabilities request.
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
#               jachym at les-ejk dot cz
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

from wpsexceptions import *

class Post:
    """
    Parses input request obtained via HTTP POST encoding - should be XML
    file.
    """
    def __init__(self,dom):
        """
        Arguments:
            self
            dom - Document Object Model of input XML request encoding
        """

        self.dom = dom  # input DOM
        self.input = {} # output Object with data structure
        return

class Get:
    """
    Parses input request obtained via HTTP GET encoding.
    """
    def __init__(self,parameters):
        """
        Arguments:
           self
           parameters   - input values
        """
