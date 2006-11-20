ka-Map - README.TXT
===================

ka-Map ("ka" as in  ka-boom!) is an open source javascript API for 
developing highly interactive web-mapping interfaces using features
available in modern web browsers.

For more information about the project and to get the latest release,
please visit the project webpage at:

    http://ka-map.maptools.org/

A community-run wiki has been kindly contributed by Lorenzo and Andrea
and can be found at:

    http://ka-map.ominiverdi.org/wiki/
    
There is a user's mailing list located at:

    http://lists.maptools.org/mailman/listinfo/ka-map

and a developer's list located at:

    http://lists.maptools.org/mailman/listinfo/ka-map-dev
INSTALLATION INSTRUCTIONS:
--------------------------

The current version of ka-Map requires MapServer's PHP MapScript on the
server. MapServer version 4.4.x will work, but better results will be 
obtained with MapServer 4.6 or more recent. 

If you do not have a working MapServer environment then you may want to
look at the following precompiled packages:

- For Windows, MS4W at http://maptools.org/ms4w/
- For Linux, FGS at http://maptools.org/fgs/

The rest of those instructions assume that you have a working PHP MapScript,
accessible as php_mapscript_46.so. We use the GMap demo as an example here,
but any MapServer mapfile can be used.

1- Download and install the GMap demo data and mapfile. It may have come
   preinstalled with your MS4W or FGS, if not then you can get the source
   package from http://maptools.org/dl/gmap-ms40.zip

   From now on we'll assume the gmap75.map mapfile is located at 
     /opt/fgs/apps/gmap-ms40/htdocs/gmap75.map

2- Copy the contents of the ka-map/htdocs directory and sub-directories 
   to your web server's htdocs.
     cp -r ka-map/htdocs/ /opt/fgs/www/htdocs/ka-map/

   Note: there are cleaner ways to install packages in FGS and MS4W that 
         will be documented later.

3- Edit ka-Map's config.php to configure your installation for your local
   settings. All configurable parameters are documented in the file.
   Things to watch for:
    - Make sure the $szPHPMapScriptModule and $szPHPGDModule filenames match
      your installation
    - Make sure the path to the gmap75.map mapfile is right in the $aszMapFiles
      array.
    - Make sure $szBaseCacheDir points to a valid directory on your system
      to hold the tile cache. 

4- ka-Map should be ready to use at  http://your.server.name/ka-map/

BROWSER COMPATIBILITY
---------------------

ka-Map is built for browsers that support AJAX-style interaction including
XmlHttpRequest, XML parsing, DOM node manipulation via javascript, and CSS2
styling.  We haven't tested ka-Map in a lot of browsers, but we try to take
feedback from the community, including bug-fixes that would make it work in
a wider variety of browsers.  However, ka-Map will NEVER work in Netscape
Navigator 4.7X so don't ask :)

The compatibility matrix looks something like this:

Browser         Windows  Linux   Mac OS X

IE 6              yes      -         -
IE 5.5             ?       ?         no
IE 5               ?       ?         ?
IE 4               no      no        no
FireFox X         yes     yes       yes
Mozilla X         yes     yes       yes
Netscape 7.X      yes     yes       yes
Netscape 6         ?       ?         ?
Netscape 4.X       no      no        no
Epiphany           -      yes        -
Opera 7 (1)       yes     yes       yes
Opera 8 (1)       yes     yes       yes
Konqueror (2,3)    -       no        no
Safari (3)         -       ?        yes

(1) CSS opacity is not supported by Opera.  Home and End keys do not map to unique key values in Opera.

(2) not tested by me, but reported on mailing list as not working

(3) Safari is based on a modified version of Konqueror.  Apparently Safari has
or will be open-sourced and the modifications moved back into Konqueror ... at
which point, Konqueror will catch up I guess.

--------------
$Id: README.TXT,v 1.7 2006/02/07 17:29:25 pspencer Exp $
--------------
