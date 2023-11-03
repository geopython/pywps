##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

from setuptools import find_packages, setup

with open("VERSION.txt") as ff:
    VERSION = ff.read().strip()

DESCRIPTION = (
    "PyWPS is an implementation of the Web Processing Service "
    "standard from the Open Geospatial Consortium. PyWPS is "
    "written in Python."
)

with open("README.md") as ff:
    LONG_DESCRIPTION = ff.read()

KEYWORDS = "PyWPS WPS OGC processing"

with open("requirements.txt") as fr:
    INSTALL_REQUIRES = fr.read().splitlines()

with open("requirements-dev.txt") as frd:
    DEV_REQUIRES = frd.read().splitlines()

CONFIG = {
    "name": "pywps",
    "version": VERSION,
    "description": DESCRIPTION,
    "long_description": LONG_DESCRIPTION,
    "long_description_content_type": "text/markdown",
    "keywords": KEYWORDS,
    "license": "MIT",
    "platforms": "all",
    "author": "Jachym Cepicky",
    "author_email": "jachym.cepicky@gmail.com",
    "maintainer": "Jachym Cepicky",
    "maintainer_email": "jachym.cepicky@gmail.com",
    "url": "https://pywps.org",
    "download_url": "https://github.com/geopython/pywps",
    "classifiers": [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    "install_requires": INSTALL_REQUIRES,
    "extras_require": dict(
        dev=DEV_REQUIRES,
    ),
    "python_requires": ">=3.8,<4",
    "packages": find_packages(exclude=["docs", "tests.*", "tests"]),
    "include_package_data": True,
    "scripts": [],
    "entry_points": {
        "console_scripts": [
            "joblauncher=pywps.processing.job:launcher",
        ]
    },
}

setup(**CONFIG)
