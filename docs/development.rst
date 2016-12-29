.. _development:

Developers Guide
================

If you identify a bug in the PyWPS code base and want to fix it, if you would 
like to add further functionality, or if you wish to expand the documentation, 
you are welcomed to contribute such changes. However, contributions to the 
code base must follow an orderly process, described below. This facilitates 
both the work on your contribution as its review. 

0. GitHub account
-----------------

The PyWPS source code is hosted at GitHub, therefore you need an account to contribute.
If you do not have one, you can follow 
`these instructions <https://help.github.com/categories/setup/>`_.

1. Open a new issue
-------------------

The first action to take is to clearly identify the goal of your contribution.
Be it a bug fix, a new feature or documentation, a clear record must be left
for future tracking. This is made by opening an issue at the `GitHub issue
tracker <https://github.com/geopython/pywps/issues>`_. In this new issue you 
should identify not only the subject or goal, but also a draft 
of the changes you expect to achieve. For example:

	**Title**: Process class must be magic
	
	**Description**: The Process class must start performing some magics. Give it 
	a magic wand.

	
2. Fork and clone the PyWPS repository
--------------------------------------

When you start modifying the code, there is always the possibility for 
something to go wrong, rendering PyWPS unusable. The first action to avoid such 
a situation is to create a development sand box. In GitHub this can
easily be made by creating a fork of the main PyWPS repository. Access the 
`PyWPS code repository <https://github.com/geopython/PyWPS>`_ and click the 
*Fork* button. This action creates a copy of the repository associated with 
your GitHub user. For more details please read `the forking guide 
<https://guides.github.com/activities/forking/>`_.

Now you can clone this forked repository into your development environment, 
issuing a command like::

	git clone https://github.com/<github-user>/PyWPS.git pywps 

Where you should replace *<github-user>* with your GitHub user name.

Before you start coding ensure you are working on the `develop` branch:

	git checkout develop
	
This is the main development branch in the PyWPS project; the traditional 
`master` branch is strictly used to keep track of code releases. All your
modifications to the PyWPS code base must be kept in the `develop` branch. 

You can now start programming your new feature, or fixing that bug you 
found. Keep in mind that PyWPS depends on a few libraries, refer to the  
:ref:`installation` section to make sure you have all of them installed.


3. Commit and pull request
--------------------------

If your modification to the code is relatively small and can be included in a 
single *commit* then all you need to is reference the issue in the **commit**
message, e.g.::

	git commit -m "Fixes #107"
	
Where *107* is the number of the issue you opened initially in the PyWPS 
issue tracker. Please refer to `the guide on closing issues with commits 
messages 
<https://help.github.com/articles/closing-issues-via-commit-messages/>`_. Then 
you push the changes to your forked repository, issuing a command like::

	git push origin develop
	
Once again, make sure your commit(s) are pushed to the `develop` branch.

Finally you can create a pull request. This is a formal request to merge your 
contribution with the code base; it is fully managed by GitHub and greatly 
facilitates the review process. You do so by accessing the repository 
associated with your user and clicking the *New pull request* button. Make sure 
your contribution is not creating conflicts and click *Create pull request*. 
If needed, there is also a `guide on pull requests 
<https://help.github.com/articles/creating-a-pull-request/>`_.

If you contribution is more substantial, and composed of multiple commits, then 
you must identify the issue it closes in the pull request itself. Check out 
`this guide 
<https://github.com/blog/1506-closing-issues-via-pull-requests>`_ for 
the details.

The members of the PyWPS PSC are then notified of your pull request. They 
review your contribution and hopefully accept merging it to the code base.


4. Updating local repository
----------------------------

Later on, if you wish to make further contributions, you must make sure to be 
working with the very latest version of the code base. You can add another 
*remote* reference in your local repository pointing to the main PyWPS 
repository::

	git remote add upstream https://github.com/geopython/PyWPS
	
You can use the *fetch* command to update your local repository metadata:: 
	
	git fetch upstream
	
Then you use a *pull* command to merge the latest *commits* into your local 
repository::
	
	git pull upstream develop


5. Help and discussion
----------------------

If you have any doubts or questions about this contribution process or about 
the code please use the `PyWPS mailing list 
<http://lists.osgeo.org/mailman/listinfo/pywps-dev>`_ or the `PyWPS Gitter 
<https://gitter.im/PyWPS>`_ . This is also the right place to propose and 
discuss the changes you intend to introduce.

