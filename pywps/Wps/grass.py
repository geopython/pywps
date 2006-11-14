"""
This module is here for work with GRASS GIS environment varibales and
locations and mapsets
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

import os
import time, shutil, tempfile
#
import sys

class GRASS:
    def  __init__(self,grassenv):
        """
        Initalization of GRASS environment variables (except GISRC).

        Edit this function, if your settings are different
        """
        self.env = grassenv
        self.export_vars()
        return

    def export_vars(self,env=None):
        """
        Exports GRASS evnironment variables defined in __init__ function

        Attributes:
            env     -   eventualy dictionary with 'VAR':'VALUE' pares
                        default: self.env
        """
        if not env:
            for key in self.env.keys():
                os.putenv(key,self.env[key])
        else:
            for key in env.keys():
                os.putenv(key,env[key])

        # GIS_LOCK
        os.putenv('GIS_LOCK',str(os.getpid()))
        
    def mkmapset(self,location=None):
        """
        Create GRASS mapset in current directory. Mapsets name is 'mapset'.
        At the end, GRASS will beleve, it was runned correctly.

        Returns name of new created mapset. location!=None, this mapset
        should be deleted!

        Argumnets:
            location     -  Should the new mapset be created in the some old
                            location, which is allread on this server?
                            Default: only mapset within
                            /tmp/grasstmpSOMEHTIN/
                            will be created
        """
        sys.stderr.write("##################### creating\n")
        self.grassenv = {}
        tempdir = os.path.abspath(os.path.curdir)# suppose, he has a

        # we have to create new mapset within this directory
        # suppose, this directory is somewhere in /tmp/grasstmpSOMETHING
        if not location:
            os.mkdir("mapset")
            self.writeWIND("mapset")
            os.mkdir("PERMANENT")
            self.writeWIND("PERMANENT")
                        # exporting of importand variables, writing the gisrc file
            self.grassenv['LOCATION_NAME'] = os.path.split(
                                    os.path.abspath(os.path.curdir))[-1]
            self.grassenv['MAPSET'] = "mapset"
            self.grassenv['GISDBASE'] = os.path.split(os.path.abspath(os.path.curdir))[0]
            
        # location is here, we justhave to use it
        else:
            # make mapset
            mapset = tempfile.mkdtemp(prefix="tmpmapset",dir=location)
            shutil.copy(os.path.join(location,"PERMANENT","DEFAULT_WIND"),os.path.join(mapset,"WIND"))
            # export env. vars
            (gisdbase,location_name) = os.path.split(location)
            if not location_name:
                (gisdbase,location_name) = os.path.split(os.path.split(location)[0])
                
            self.grassenv['LOCATION_NAME'] = location_name
            self.grassenv['MAPSET'] = os.path.split(mapset)[-1]
            self.grassenv['GISDBASE'] = gisdbase
             
        self.export_vars(env=self.grassenv)

        # gisrc
        gisrc = open(os.path.join(tempdir,"grass61rc"),"w")
        gisrc.write("LOCATION_NAME: %s\n" % (self.grassenv['LOCATION_NAME']))
        gisrc.write("MAPSET: %s\n" % (self.grassenv['MAPSET']))
        gisrc.write("DIGITIZER: none\n")
        gisrc.write("GISDBASE: %s\n" % (self.grassenv['GISDBASE']))
        gisrc.write("OVERWRITE: 1\n")
        gisrc.write("GRASS_GUI: text\n")
        gisrc.close()

        os.putenv("GISRC",os.path.join(tempdir,"grass61rc"))
        
        return self.grassenv['MAPSET']

    def writeWIND(self,mapset):
        """
        Create default WIND file
        """
        if mapset == "PERMANENT":
            windname = "DEFAULT_WIND"
        else:
            windname = "WIND"

        wind =open(
                os.path.join(
                    os.path.abspath(os.path.curdir),mapset,windname),"w")
        wind.write("""proj:       0\n""")
        wind.write("""zone:       0\n""")
        wind.write("""north:      1000\n""")
        wind.write("""south:      0\n""")
        wind.write("""east:       1000\n""")
        wind.write("""west:       0\n""")
        wind.write("""cols:       1000\n""")
        wind.write("""rows:       1000\n""")
        wind.write("""e-w resol:  1\n""")
        wind.write("""n-s resol:  1\n""")
        wind.close()
        return


