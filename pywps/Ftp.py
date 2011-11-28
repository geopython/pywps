"""FTP helper class derived from ftplib.FTP to store login, password and fileName for remote response storage
to enable relogin after connection closed without providing extra login information. For implementation details have 
a look at the ftplib.FTP documentation.
"""
# Author:    Soeren Gebbert
#            soerengebbert@googlemail.com
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


import ftplib
import pywps

class FTP(ftplib.FTP):
    def __init__(self, host='', port=21):
        """Store the user name, password and acct for futher uses and call the ftplib.FTP.__init__()"""
        ftplib.FTP.__init__(self)
        try:
            self.connect(host=host, port=port)
        except Exception,e:
            raise pywps.NoApplicableCode(e.__str__()+": host=%s,port=%s" %(host,port))
        #connect(host=host, port=6666)
    def login(self, user='', passwd='', acct=''):
        """Store the user name, password and acct for futher uses and call ftplib.FTP.login()"""
        ftplib.FTP.login(self, user, passwd, acct)
    def relogin(self):
        """"New method to allow the relogin without providing username and password"""
        self.login(self.user, self.passwd, self.acct)
    def setFileName(self, fileName):
        """"New method to set the filename which should be used on the ftp server"""
        self.fileName = fileName

 