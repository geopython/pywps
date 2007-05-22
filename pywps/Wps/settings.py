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


def ConsolidateSettings(settings):
    """
    This function merges custom settings together with default settings
    """

    if settings:
        try:
            default_settings.WPS = _fillSetting(
                                    default_settings.WPS,settings.WPS)
            default_settings.ServerSettings = _fillSetting(
                                    default_settings.ServerSettings,
                                    settings.ServerSettings)
            
        except AttributeError,e:
            if str(e) == "'module' object has no attribute 'WPS'"\
                or str(e) == "'module' object has no attribute 'ServerSettings'":
                pass
            else:
                raise AttributeError(e)

    return default_settings



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

if __name__ == "__main__":
    try:
        import tmp
    except:
        print "File tmp.py with custom settings not found"
    customsettings = tmp
    ConsolidateSettings(customsettings)

