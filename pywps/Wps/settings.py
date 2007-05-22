"""
Custom vs. default settings for PyWPS
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


import default_settings
import default_grass
import wpsexceptions
from wpsexceptions import ServerError

import os


def ConsolidateSettings(settings, grass=False):
    """
    This function merges custom settings together with default settings
    """

    if not grass:
        default = default_settings
        if settings:
            try:
                default.WPS = _fillSetting(
                               default.WPS,settings.WPS)
                default.ServerSettings = _fillSetting(
                                        default.ServerSettings,
                                        settings.ServerSettings)
                
            except AttributeError,e:
                if str(e) == "'module' object has no attribute 'WPS'"\
                    or str(e) == "'module' object has no attribute 'ServerSettings'":
                    pass
                else:
                    raise AttributeError(e)

        ret = _checkPaths(default,grass)
    else:
        default = default_grass
        if settings:
            try:
                default.grassenv = _fillSetting(
                                        default.grassenv,grass.grassenv)
            except AttributeError,e:
                if str(e) == "'module' object has no attribute 'grassenv'":
                    pass
                else:
                    raise AttributeError(e)
        ret = _checkPaths(default,grass)


    if ret:
        raise ServerError(ret)
    else:
        return default


def _fillSetting(default,custom):
    """
    Calls recursive function
    """
    
    for key in default.keys():
        _FillRecursive(key,default,custom)
    return default

def _FillRecursive(key,default, custom):
    """
    Goes through default settings and tryes to replace default settings
    with custom ones.
    """
        
    # replace, if no recursion is needed
    if type(default[key]) != type({}):
        try:
            default[key] = custom[key]
        except:
            pass
    # recurse
    else:
        try:
            for dkey in default[key].keys():
                _FillRecursive(dkey, default[key],custom[key])
        except:
            pass

def _checkPaths(default,grass):
    """
    Checks, if paths are read(write)able
    """

    if grass:
        if default.grassenv["GRASS_ADDON_PATH"] and\
            not os.path.isdir(default.grassenv['GRASS_ADDON_PATH']):
                pass
        if not os.path.isdir(default.grassenv['GISBASE']):
            return "Could not locate GISBASE directory (pywps/etc/grass.py)"
        if not os.path.isdir(default.grassenv['LD_LIBRARY_PATH']):
            return "Could not locate LD_LIBRARY_PATH directory (pywps/etc/grass.py)"
        if not os.path.isdir(default.grassenv['HOME']):
            return "Could not locate HOME directory (pywps/etc/grass.py)"
    else:
        if not os.path.isdir(default.ServerSettings['outputPath']):
            return "Could not locate 'outputPath' directory (pywps/etc/settings.py): %s" % (default.ServerSettings['outputPath'])
        if not os.access(default.ServerSettings['outputPath'],os.W_OK):
            return "Could not write to 'outputPath' directory (pywps/etc/settings.py): %s. Please, setup permissions" % (default.ServerSettings['outputPath'])
        if not isdir(default.ServerSettings['tempPath']):
            return "Could not locate 'tempPath' directory (pywps/etc/settings.py): %s" % (default.ServerSettings['tempPath'])
        if not os.access(default.ServerSettings['tempPath'],os.W_OK):
            return "Could not write to 'tempPath' directory (pywps/etc/settings.py): %s. Please, setup permissions" % (default.ServerSettings['tempPath'])

if __name__ == "__main__":
    try:
        import tmp
    except:
        print "File tmp.py with custom settings not found"
    customsettings = tmp
    ConsolidateSettings(customsettings)

