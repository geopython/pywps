#!/usr/bin/python

###### NOTES AT THE BOTTOM !!!! #####################

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import sys,os,logging,signal,subprocess,time

__author__="Jorge S. Mendes de Jesus"
__email___="jmdj__AT__pml.ac.uk"
__version__=0.1
##########   GENERIC PARAMETERS, CONFIGURE HERE ###########
HOST_NAME="localhost"
PORT_NUMBER=8000
LOG_FILE="/var/log/ogcproxy.log"

#Add here HOST and local path to folder with content, change /users/rsg/jmdj/ogc{w3c}, to folder with ogc/w3c content
cachedHost={"schemas.opengis.net":"/users/rsg/jmdj/ogc","www.w3.org":"/users/rsg/jmdj/w3c"}
#Add here IP of site
#Same dictionary key in cachedHost and ipDic
ipDic={"schemas.opengis.net":"66.244.86.50","www.w3.org":"128.30.52.37"}


##### GENERIC FUNCTIONS ###############

def exit_func(sig=None,stack=None):
    server.log_message("Got TERM sinal")
    print "Got TERM signal"
    server.log_message("Removing IPtables")
    doIPTables(type="-D")
    server.log_message("EXIT")
    sys.exit(0)
    
def doIPTables(type="-A"):
    #type="-A" --> append
    #type="-D" --> remove
    for ip in ipDic.values():
        #sudo iptables -A OUTPUT -t nat -d 128.30.52.45 -p tcp --dport 80 -j REDIRECT --to-ports 8000 
        args=['iptables', str(type), 'OUTPUT', '-t', 'nat', '-d', str(ip),'-p','tcp','--dport','80','-j','REDIRECT','--to-ports',str(PORT_NUMBER),'-m','comment','--comment' ,'"set by ogcproxy.py PID:%s"' % os.getpid()]
        server.log_message(str(args))
        p=subprocess.Popen(args,shell=False,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        server.log_message("STOUT:%s" % stdout)
        server.log_message("STERR:%s" % stderr)
        retcode=p.wait()
        if retcode!=0:
            print "Error please check log"
            sys.exit()
            
def wait4TERM():
    signal.pause() 
    time.sleep(1)
        
class RequestHandler(BaseHTTPRequestHandler):
    """Class dealing with requests"""
    
    def cached(self,host):
        localPath=cachedHost[host]
        fullPath=localPath+self.path
        fh=open(fullPath,"r")
        return fh.read()
        
    def do_GET(self):
        host=(self.headers.get('Host'))
        returnResponse=None
        if host in cachedHost.keys():
            try:
                returnResponse=self.cached(host)
                self.send_response(200)
                self.send_header("Content-type", "text/xml")
                self.end_headers()
                self.wfile.write(returnResponse )
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write("NO CONTENT IN FOLDER STRUCTURE")
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("NO CACHE") 
        
    def log_message(self, format, *args):
        #sys.stdout.write((format % args) + '\n')
        logging.debug((format % args))

    #Anyother HTTP gets treated as do_GET
    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT  = do_GET
    do_DELETE = do_GET


class ThreadingHTTPServer(ThreadingMixIn,HTTPServer):
    
    def log_message(self,format,*args):
        logging.debug((format % args))


if __name__ == '__main__':
    #set logging structure
    logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    
    #start server object
    server = ThreadingHTTPServer((HOST_NAME, PORT_NUMBER), RequestHandler)
    server.log_message('proxy serving on %s port %s' % (HOST_NAME,PORT_NUMBER))
    server.log_message('PID:%s' % os.getpid())
    
    #set IPtables
    doIPTables(type="-A")
    
    #Prepare for signal
    signal.signal(signal.SIGTERM, exit_func)
    
    try:
        server.serve_forever()
        server.log_message('Everything seems ok')
        sinalThread=threading.Thread(target=wait4TERM, name='signal')
        #sinalThread.setDaemon(False)
        sinalThread.start()
        sinalThread.run()
        print "Proxy working\n"
       
    except KeyboardInterrupt:
        server.log_message('KeyboardKill')
        doIPTables(type="-D")
        print "Exit\n"
        server.log_message("EXIT")
        
#NOTES:
#
#- signal.wait() has to be run in a thread otherwise the script freezes and nothing runs. 
#- Script has to be run as root otherwise IPtables can't be configured
#- To stop script either ^C in keyboard or kill <PID> (no kill -9 !!!) better -10 (sigterm)


#Explain
#Copy site's content to a folder, local content has to be identical to site's URI
#For OGC schemas decompress the zip file (SCHEMAS_OPENGIS_NET.zip) found in the site http://schemas.opengis.net/ 
#use the command dig to determine the site IPs
#IPtables will redirect the URLs to the scrpt and in turn to the files   

#To check who is using a specific port 
#sudo fuser -v 8000/tcp

