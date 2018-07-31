from os.path import join as pjoin

# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
_version_major = 0
_version_minor = 8
_version_micro = ''  # use '' for first of series, number for 1 and above
_version_extra = 'dev'
# _version_extra = ''  # Uncomment this for full releases

# Construct full version string from these.
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)
if _version_extra:
    _ver.append(_version_extra)

__version__ = '.'.join(map(str, _ver))

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: MIT License",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering"]

# Description should be a one-liner:
description = "labdrivers: python drivers for lab instruments"
# Long description will go up on the pypi page
long_description = """

labdrivers
========
labdrivers is a collection of drivers for common research lab instruments.

It contains a suite of instrument-specific drivers which can be used to 
interface measurement hardware with Python code, along with a set of 
Jupyter notebooks demonstrating example use cases. 

To get started using these components in your own software, please go to the
repository README_.

.. _README: https://github.com/masonlab/labdrivers/blob/master/README.md

License
=======
``labdrivers`` is licensed under the terms of the MIT license. See the file
"LICENSE" for information on the history of this software, terms & conditions
for usage, and a DISCLAIMER OF ALL WARRANTIES.

All trademarks referenced herein are property of their respective holders.

Copyright (c) 2016--, Henry Hinnefeld.
"""

NAME = "labdrivers"
MAINTAINER = "Jeff Damasco"
MAINTAINER_EMAIL = "jeffdamasco@gmail.com"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "http://github.com/masonlab/labdrivers"
DOWNLOAD_URL = ""
LICENSE = "MIT"
AUTHOR = "Henry Hinnefeld"
AUTHOR_EMAIL = "henry.hinnefeld@gmail.com"
PLATFORMS = "OS Independent"
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
VERSION = __version__
PACKAGES = ['labdrivers',
            'labdrivers.keithley',
			'labdrivers.lakeshore',
            'labdrivers.srs',
            'labdrivers.quantumdesign',
            'labdrivers.oxford',
            'labdrivers.ni']
PACKAGE_DATA = {'labdrivers': [pjoin('data', '*')]}
REQUIRES = ["numpy", "pyvisa", "pythonnet", "PyDAQmx"]
