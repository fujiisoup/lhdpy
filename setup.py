#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from setuptools import setup
import re

# load version form _version.py
VERSIONFILE = "lhdpy/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

# module

setup(
    name="lhdpy",
    version=verstr,
    author="Keisuke Fujii",
    author_email="fujiisoup@gmail.com",
    description=("Python small library to download LHD data archives."),
    license="BSD 3-clause",
    keywords="plasma fusion",
    include_package_data=True,
    ext_modules=[],
    packages=["lhdpy",],
    package_dir={"lhdpy": "lhdpy"},
    py_modules=["lhdpy.__init__"],
    test_suite="tests",
    install_requires="""
        numpy>=1.11
        xarray>=0.10
        """,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
