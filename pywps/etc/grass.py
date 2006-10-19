"""
This is configuration file for pywps. In this file, you can set your GRASS
environment and other variables.

"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# Lince: 
# 
# Web Processing Service implementation (conf. file)
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



###########################################################
#
# In this env structure the main configuration for GRASS GIS
# is stored
#
###########################################################
grassenv = {
    # PATH in which your modules (processes) shold be able the search.
    # Defatult value:
    # 'PATH': "/usr/lib/grass/bin/:/usr/lib/grass/scripts/:/usr/bin/:/bin/:",
    'PATH': "/usr/lib/grass/bin/:/usr/lib/grass/scripts/:/usr/bin/:/bin/:",

    # Add eventualy some other path, in which should GRASS search for modules
    #'GRASS_ADDON_PATH': "",
    'GRASS_ADDON_PATH': "",

    # Version of GRASS, you are using
    # 'GRASS_VERSION': "6.1.cvs",
    'GRASS_VERSION': "6.1.cvs",

    # GRASS_PERL, where is your PERL bin installed
    # 'GRASS_PERL': "/usr/bin/perl",
    #'GRASS_PERL': "/usr/bin/perl",


    # GRASS_GUI should be always "text" unless you know, what you are doing
    # 'GRASS_GUI': "text",
    'GRASS_GUI': "text",

    # GISBASE is place, where your GRASS installation is
    # 'GISBASE': "/usr/lib/grass",
    'GISBASE': "/usr/lib/grass",

    # LD_LIBRARY_PATH
    'LD_LIBRARY_PATH':"/usr/lib/grass/lib",

    # HOME has to be set
    # 'HOME':'/var/www',
    'HOME':"/var/www",
}
