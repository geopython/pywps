##########################
Frequently asked questions
##########################

Last updated according to PyWPS 3.0.x branch.

`Which version of PyWPS should I use?`
    Always, you should use the latest stable version. Older versions (1.0.0, 2.0.x) are really outdated and you should better not use them.

`How to debug PyWPS processes?`
    You have several possibilities:
        * Run PyWPS from command line directly from command line::

            $ ./wps.py "&service=wps&version=0.4.0&request=execute&datainputs=input1,value1,input2,value2,..."

        * See error log file from your web server. I use program tail::

            $ tail -f /var/log/apache/error.log |sed -e "s/\[.*\] //g"
            PyWPS GCmd: r.rescale out=kat_dop_k_2004_1188372842 in=dop_k_2004_1188372842\
                        to=0,255 to kat_dop_k_2004_1188372842[0,255]
            PyWPS GCmd: r.support map=dop_k_2004_1188372842 title="drasil2"
            PyWPS GCmd: r.support map=kat_dop_k_2004_1188372842 title="drasil2" 
            PyWPS ERROR: Could not perform command:
                    r.support map=kat_dop_k_2004_1188372842 title="drasil2"
                    in process K2O, method execute() /home/bnhelp/pfwps/wps.py:
                        79: DeprecationWarning:
                            Non-ASCII character '\xc2' in file
                            /usr/home/bnhelp/pfwps/pywps/processes/pf_interpolate_grass.py
                            on line 51, but no encoding declared;
                    see http://www.python.org/peps/pep-0263.html for details
            from pywps.processes import *
            PyWPS GCmd: g.region rast=mask2004@medlov res=5 1>&2

        * See the logfile, which you have set in the configuration file, in
          the `[server]` section

`How to run command line commands?`
    Use build-in :meth:`cmd` method of the process::

        self.cmd(["ogr2ogr","output","input"])

`How to run GRASS commands?`
    The same way, like normal commands::

        self.cmd(["g.region","rast=raster"])

`Where can I find documentation to process writing in general?`
    Ofcourse, there is `Documentation </documentation/>`_, but it does not
    contain modules documentation yet. To get this, try::
        
        pydoc pywps/Process/Process.py
        pydoc pywps/Process/InputsAndOutputs.py

    Have a look at :file:`doc/examples/processes` directory
                                  


