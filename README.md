# diskinfo
[![Tests](https://github.com/petersulyok/smfc/actions/workflows/test.yml/badge.svg)](https://github.com/petersulyok/smfc/actions/workflows/tests.yml)
[![Codecov](https://codecov.io/gh/petersulyok/diskinfo/branch/main/graph/badge.svg)](https://app.codecov.io/gh/petersulyok/diskinfo)
[![Documentation Status](https://readthedocs.org/projects/diskinfo/badge/?version=latest)](https://diskinfo.readthedocs.io/en/latest/?badge=latest)
[![Issues](https://img.shields.io/github/issues/petersulyok/diskinfo)](https://github.com/petersulyok/diskinfo/issues)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/diskinfo)](https://pypi.org/project/diskinfo)
[![PyPI version](https://badge.fury.io/py/diskinfo.svg)](https://badge.fury.io/py/diskinfo)

Disk information Python library can assist in collecting disk information on Linux. In more details, it can:

- collect information about a specific disk
- explore existing disks in the system
- translate between traditional and persistent disk names
- read disk temperature
- read SMART data of the disk

Installation
------------
Standard installation from [pypi.org](https://pypi.irg):

    pip install diskinfo

The package requires Python version >= `3.7`. 

Demo
----
The library contains a simple demo, it can be executed in the following way:

    python -m diskinfo.demo

<img src="https://github.com/petersulyok/diskinfo/raw/main/docs/diskinfo_rich_demo.png" align="left">

Please note that [rich](https://pypi.org/project/rich/) Python library needs to be installed for this colorful demo.

API documentation
-----------------
The detailed API documentation can be found on [readthedocs.io](https://diskinfo.readthedocs.io/en/latest/index.html).
