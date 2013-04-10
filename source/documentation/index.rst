.. _documentation:
#############
Documentation
#############
This document describes installation and  configuration of PyWPS in it's
latest version. Little 'howto' about your custom process definition is
included as well. 

In case, you found any bug, please report them to
pywps-devel@wald.intevation.org or `jachym.cepicky gmail com` 

Documentation for various versions:

    * `PYWPS 3.2 (trunk) <pywps-3.2>`_

Tutorial
********

    * `PyWPS Tutorial <course>`_

You can also obtain a copy of this tutorial from svn::

    # you need trunk, the course is pointing there for some files
    svn checkout https://svn.wald.intevation.org/svn/pywps/trunk
        
    # now you can get the docs
    svn checkout https://svn.wald.intevation.org/svn/pywps/docs

After you download the docs, you can chdir to docs/course and make it::

    cd docs/course
    make html
    make pdf
    

Old Documentation < 3.2
***********************

.. toctree::
    :maxdepth: 1
    
    How to get PyWPS <getting>
    how_it_works
    installation
    configuration_and_testing
    process
