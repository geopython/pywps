"""
Debuging functions
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

from sys import stderr as Stderr
from os import environ as Env

def PyWPSdebug(d,level=0,pref="debug"):
    try:
        if Env["PyWPS_DEBUG"] and\
            int(Env["PyWPS_DEBUG"]) >= level:
                pass
        else:
            return

    except (KeyError, ValueError):
        PyWPS_DEBUG = 0

    # debug messages can be list
        if type(d) == type([]):
            for line in d:
                Stderr.write("PyPWS %s %d: %s\n" % \
                        (pref,level,line.strip()))
        else:
            Stderr.write("PyWPS %s %d: %s\n" %\
                    (pref,level,str(d).strip()))

