"""
Module is here for work with GRASS GIS environmental variables and
locations and mapsets
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
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

import os
import time, shutil, tempfile
import sys
from pywps import config
import logging

LOGGER = logging.getLogger(__name__)

class Grass:
    """ GRASS initialization interface """

    locationDir = ""
    locationName = ""
    mapsetDir = ""
    mapsetName = ""
    gisbase = ""

    def  __init__(self,executeRequest):
        """ Initialization of GRASS environmental variables (except GISRC).  """

        self.executeRequest = executeRequest
        self.wps = self.executeRequest.wps
        self.envs = {
                "path":"PATH",
                "addonPath":"GRASS_ADDON_PATH",
                "version":"GRASS_VERSION",
                "gui":"GRASS_GUI",
                "gisbase": "GISBASE",
                "ldLibraryPath": "LD_LIBRARY_PATH",
                "home": "HOME",
                "pythonpath":"PYTHONPATH"
        }

        # put env
        for key in self.envs.keys():
            try:
                self.setEnv(self.envs[key],config.getConfigValue("grass",key))
                LOGGER.info("GRASS environment variable %s set to %s" %\
                        (key, config.getConfigValue("grass",key)))
            except :
                LOGGER.info("GRASS environment variable %s set to %s" %\
                        (key, self.envs[key]))
                pass

        # GIS_LOCK
        self.setEnv('GIS_LOCK', str(os.getpid()))
        LOGGER.info("GRASS GIS_LOCK set to %s" % str(os.getpid()))

    def mkMapset(self,location=None):
        """
        Create GRASS mapset in current directory. Mapsets name is 'mapset'.
        At the end, GRASS will believe, it has run correctly.

        Returns name of new created mapset. location!=None, this mapset
        should be deleted!

        Arguments:
            location     -  Should the new mapset be created in the some old
                            location, which is already on this server?
                            Default: only mapset within
                            /tmp/grasstmpSOMEHTIN/
                            will be created
        """

        if location == None:
            self.locationDir = self.executeRequest.workingDir

            self.mapsetDir = tempfile.mkdtemp(prefix="pywps",dir=self.locationDir)
            self.mapsetName = os.path.split(self.mapsetDir)[1]
            self.locationName = os.path.split(self.locationDir)[1]

            # create new WIND file
            self._windFile(self.mapsetName)

            # create mapset PERMANENT
            os.mkdir("PERMANENT")
            self._windFile("PERMANENT")

            self.gisdbase = os.path.split(os.path.abspath(os.path.curdir))[0]

        # location is here, we justhave to use it
        else:
            self.locationDir = os.path.join(config.getConfigValue("grass","gisdbase"), location)
            self.mapsetDir = tempfile.mkdtemp(prefix="pywps",dir=self.locationDir)
            self.mapsetName = os.path.split(self.mapsetDir)[1]
            self.locationName = os.path.split(location)[-1]

            self.executeRequest.dirsToBeRemoved.append(os.path.abspath(self.mapsetDir))

            # copy
            shutil.copy(os.path.join(
                self.locationDir,"PERMANENT","DEFAULT_WIND"),
                os.path.join(self.mapsetDir,"WIND"))

            # export env. vars
            (self.gisdbase,location) = os.path.split(self.locationDir)

        # GRASS creates a temp dir for the display driver.
        # Add it to dirsToBeRemoved
        try:
            grassTmpDir = os.path.join(tempfile.gettempdir(),
                                       "grass"+config.getConfigValue("grass","version")[:1]+\
                                       "-"+os.getenv("USERNAME")+\
                                       "-"+str(os.getpid()))
            self.executeRequest.dirsToBeRemoved.append(grassTmpDir)
        except :
            pass

        self.setEnv('MAPSET', self.mapsetName)
        self.setEnv('LOCATION_NAME',self.locationName)
        self.setEnv('GISDBASE', self.gisdbase)

        # gisrc
        gisrc = open(os.path.join(self.executeRequest.workingDir,"grassrc"),"w")
        gisrc.write("LOCATION_NAME: %s\n" % self.locationName)
        gisrc.write("MAPSET: %s\n" % self.mapsetName)
        gisrc.write("DIGITIZER: none\n")
        gisrc.write("GISDBASE: %s\n" % self.gisdbase)
        gisrc.write("OVERWRITE: 1\n")
        gisrc.write("GRASS_GUI: text\n")
        gisrc.close()

        LOGGER.info("GRASS MAPSET set to %s" % self.mapsetName)
        LOGGER.info("GRASS LOCATION_NAME set to %s" % self.locationName)
        LOGGER.info("GRASS GISDBASE set to %s" % self.gisdbase)

        self.setEnv("GISRC",os.path.join(self.executeRequest.workingDir,"grassrc"))
        LOGGER.info("GRASS GISRC set to %s" % os.path.join(self.executeRequest.workingDir,"grassrc"))

        return self.mapsetName

    def _windFile(self,mapset):
        """ Create default WIND file """

        if mapset == "PERMANENT":
            windname = "DEFAULT_WIND"
        else:
            windname = "WIND"

        wind =open(
                os.path.join(
                    os.path.abspath(self.executeRequest.workingDir),mapset,windname),"w")
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

    def setEnv(self, key, value):
        """Set GRASS environmental variables """
        os.putenv(key, value)
        os.environ[key] = value

        if key == 'GISBASE':
            sys.path.append(os.path.join(value, 'etc', 'python'))
