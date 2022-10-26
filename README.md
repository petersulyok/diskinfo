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
- read current disk temperature
- read SMART data of a disk
- read partition list of a disk 

Installation
------------
Standard installation from [pypi.org](https://pypi.org):

    pip install diskinfo

See the complete list of dependencies and requirements in the 
[documentation](https://diskinfo.readthedocs.io/en/latest/intro.html#installation). 

Demo
----
The library contains a demo application with multiple screens ([`rich`](https://pypi.org/project/rich)
needs to be installed):

    pip install rich
    python -m diskinfo.demo

![Demo screen](https://github.com/petersulyok/diskinfo/raw/main/docs/diskinfo_rich_demo.png)

See more demo screens in the [documentation](https://diskinfo.readthedocs.io/en/latest/intro.html#demo).

API documentation
-----------------
The detailed API documentation can be found on [readthedocs.io](https://diskinfo.readthedocs.io/en/latest/index.html).
