##################################################################
# Copyright 2016 OSGeo Foundation,                               #
# represented by PyWPS Project Steering Committee,               #
# licensed under GPL 2.0, Please consult LICENSE.txt for details #
##################################################################
"""FTP helper class derived from ftplib.FTP to store login, password and fileName for remote response storage
to enable relogin after connection closed without providing extra login information. For implementation details have 
a look at the ftplib.FTP documentation.
"""

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

 