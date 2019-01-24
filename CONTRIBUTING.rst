Contributing to PyWPS
=====================

The PyWPS project openly welcomes contributions (bug reports, bug fixes, code
enhancements/features, etc.).  This document will outline some guidelines on
contributing to PyWPS.  As well, the PyWPS `community <https://pywps.org/community>`_ is a
great place to get an idea of how to connect and participate in the PyWPS community
and development.

PyWPS has the following modes of contribution:

- GitHub Commit Access
- GitHub Pull Requests

Code of Conduct
---------------

Contributors to this project are expected to act respectfully towards others in
accordance with the `OSGeo Code of Conduct
<https://www.osgeo.org/code_of_conduct>`_.

Contributions and Licensing
---------------------------

Contributors are asked to confirm that they comply with the project `license
<https://github.com/geopython/PyWPS/blob/master/LICENSE.txt>`_ guidelines.

GitHub Commit Access
^^^^^^^^^^^^^^^^^^^^

- proposals to provide developers with GitHub commit access shall be emailed to
  the pywps-devel `mailing list`_.  Proposals shall be approved by the PyWPS
  development team.  Committers shall be added by the project admin
- removal of commit access shall be handled in the same manner
- each committer must send an email to the PyWPS mailing list agreeing to the license guidelines (see
  `Contributions and Licensing Agreement Template
  <#contributions-and-licensing-agreement-template>`_).  **This is only required once**
- each committer shall be listed in https://github.com/geopython/pywps/blob/master/COMMITTERS.txt

GitHub Pull Requests
^^^^^^^^^^^^^^^^^^^^

- pull requests can provide agreement to license guidelines as text in the pull
  request or via email to the PyWPS `mailing list`_  (see `Contributions and
  Licensing Agreement Template
  <#contributions-and-licensing-agreement-template>`_).  **This is only required
  for a contributor's first pull request.  Subsequent pull requests do not
  require this step**
- pull requests may include copyright in the source code header by the
  contributor if the contribution is significant or the contributor wants to
  claim copyright on their contribution
- all contributors shall be listed at
  https://github.com/geopython/pywps/graphs/contributors
- unclaimed copyright, by default, is assigned to the main copyright holders as
  specified in https://github.com/geopython/pywps/blob/master/LICENSE.txt
- make sure, the tests are passing on [travis-ci](https://travis-ci.org/geopython/pywps) sevice, as well as on your local machine `tox`::

    tox

Contributions and Licensing Agreement Template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``Hi all, I'd like to contribute <feature X|bugfix Y|docs|something else> to
PyWPS.  I confirm that my contributions to PyWPS will be compatible with the
PyWPS license guidelines at the time of contribution.``


GitHub
------

Code, tests, documentation, wiki and issue tracking are all managed on GitHub.
Make sure you have a `GitHub account <https://github.com/signup/free>`_.

Code Overview
-------------

- the PyWPS `wiki <https://github.com/geopython/pywps/wiki/Code-Architecture>`_
  documents an overview of the codebase [TODO]

Documentation
-------------

- documentation is managed in ``docs/``, in reStructuredText format
- `Sphinx`_ is used to generate the documentation
- See the `reStructuredText Primer <http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_ on rST
  markup and syntax

Bugs
----

The PyWPS `issue tracker <https://github.com/geopython/pywps/issues>`_ is the
place to report bugs or request enhancements. To submit a bug be sure to specify
the PyWPS version you are using, the appropriate component, a description of how
to reproduce the bug, as well as the Python version and the platform.

Forking PyWPS
-------------

Contributions are most easily managed via GitHub pull requests.  `Fork
<https://github.com/geopython/pywps/fork>`_ PyWPS into your own GitHub
repository to be able to commit your work and submit pull requests.

Development
-----------

GitHub Commit Guidelines
^^^^^^^^^^^^^^^^^^^^^^^^

- enhancements and bug fixes should be identified with a GitHub issue
- commits should be granular enough for other developers to understand the
  nature / implications of the change(s)
- for trivial commits that do not need `Travis CI
  <https://travis-ci.org/geopython/pywps>`_ to run, include ``[ci skip]`` as
  part of the commit message
- non-trivial Git commits shall be associated with a GitHub issue.  As
  documentation can always be improved, tickets need not be opened for improving
  the docs
- Git commits shall include a description of changes
- Git commits shall include the GitHub issue number (i.e. ``#1234``) in the Git
  commit log message
- all enhancements or bug fixes must successfully pass all
  `OGC CITE <https://cite.opengeospatial.org>`_ tests before they are committed
- all enhancements or bug fixes must successfully pass all tests
  before they are committed
- enhancements which can be demonstrated from the PyWPS tests should be
  accompanied by example WPS request XML or KVP

Coding Guidelines
^^^^^^^^^^^^^^^^^

- PyWPS instead of pywps, pyWPS, Pywps, PYWPS
- always code with `PEP 8`_ conventions
- always run source code through ``flake8``
- for exceptions which make their way to OGC ``ows:ExceptionReport`` XML, always
  specify the appropriate ``locator`` and ``code`` parameters

Submitting a Pull Request
^^^^^^^^^^^^^^^^^^^^^^^^^

This section will guide you through steps of working on PyWPS.  This section
assumes you have forked PyWPS into your own GitHub repository. Note that 
``master`` is the main development branch in PyWPS.
for stable releases and managed exclusively by the PyWPS team.

.. code-block:: bash

  # setup a virtualenv
  virtualenv mypywps && cd mypywps
  . ./bin/activate

  # clone the repository locally
  git clone git@github.com:USERNAME/pywps.git
  cd pywps
  pip install -e . && pip install -r requirements.txt

  # add the main PyWPS development branch to keep up to date with upstream changes
  git remote add upstream https://github.com/geopython/pywps.git
  git pull upstream master

  # create a local branch off master
  # The name of the branch should include the issue number if it exists
  git branch issue-72
  git checkout issue-72

   
  # make code/doc changes
  git commit -am 'fix xyz (#72)'
  git push origin issue-72

Your changes are now visible on your PyWPS repository on GitHub.  You are now
ready to create a pull request.  A member of the PyWPS team will review the pull
request and provide feedback / suggestions if required.  If changes are
required, make them against the same branch and push as per above (all changes
to the branch in the pull request apply).

The pull request will then be merged by the PyWPS team.  You can then delete
your local branch (on GitHub), and then update
your own repository to ensure your PyWPS repository is up to date with PyWPS
master:

.. code-block:: bash

  git checkout master
  git pull upstream master

Release Packaging
-----------------

Release packaging notes are maintained at https://github.com/geopython/pywps/wiki/ReleasePackaging


.. _`Corporate`: http://www.osgeo.org/sites/osgeo.org/files/Page/corporate_contributor.txt
.. _`Individual`: http://www.osgeo.org/sites/osgeo.org/files/Page/individual_contributor.txt
.. _`info@osgeo.org`: mailto:info@osgeo.org
.. _`OSGeo`: http://www.osgeo.org/content/foundation/legal/licenses.html
.. _`PEP 8`: https://www.python.org/dev/peps/pep-0008/
.. _`flake8`: https://flake8.readthedocs.io/en/latest/
.. _`Sphinx`: http://sphinx-doc.org/
.. _`mailing list`: https://pywps.org/community
