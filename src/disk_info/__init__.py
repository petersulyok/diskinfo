"""This Python package can discover and collect disk information on Linux. It can also provide persistent disk names
for stable device referencing.

Installation
============
Standard installation from `pypi.org`:

    pip install disk_info

The package does not have extra dependencies.

How to use
==========
There are two different ways how this package can be used. Either you can collect information about a specific disk
or you can discover all existing disks on your system.

Option 1: collect information about a disk
------------------------------------------
Information can be collected about a specific disk with the creation of an `Disk` class instance. Here the caller has
to provide a unique identifier for the disk. Disk information will be collected at class creation time then the user
can call several member functions to get collected attributes.

    >>> from disk_info import Disk
    >>> d = Disk("sda")
    >>> d.get_model()
    'Samsung SSD 870 QVO 8TB'
    >>> d.is_ssd()
    True
    >>> s, u = d.get_size_in_hrf()
    >>> print(f"{s:.1f} {u}")
    8.0 TB
    >>> d.get_serial()
    'S5SXNG0MB01829M'

See the complete list of the class methods in documentation of class `Disk`.

Option 2: discover disks
------------------------
Disk can be discovered by creation of an instance of the class `DiskInfo`. After having an instance of DiskInfo class
the list and the number of identified disks can be queried with `get_disk_number()` and `get_disk_list()` functions:

    >>> from disk_info import Disk, DiskInfo
    >>> di = DiskInfo()
    >>> di.get_disk_number()
    4
    >>> disks = di.get_disk_list(sorting=True)
    >>> for d in disks:
    >>>     print(d.get_path())
    /dev/nvme0n1
    /dev/sda
    /dev/sdb
    /dev/sdc

The caller can apply filters (included and ecluded disk types) for both functions. The list of disk can be also sorted.

Persistent disk names
=====================
Please note that not all kind of block device names are persistent. For example this disk path

     "/dev/sdb"

could refer different physical disk after a reboot. That is reason why other persistent names have been introduced in
Linux and udev. The physical device can be referenced by the following path type:

     "/dev/disk/by-id/nvme-WDS80T1X06-00AFY1_2130GF574294"

This type of reference is called `by-id` path in this documentation. The physical connector (i.e. where the disck is
connected) can be also referenced with the following path:

     "/dev/disk/by-path/pci-0000:02:00.0-nvme-1"

This type of reference is called `by-path` path in this documentation. Both references are persistent and
safe in disk referencing.

Read more about this topic at [Arch Linux wiki: Persistent block device naming] \
(https://wiki.archlinux.org/title/persistent_block_device_naming).

Demo
====
There is a simple demo included in the package. You can execute it with in the following way:

     python -m disk_info.demo

"""
from disk_info.disk import Disk, DiskType
from disk_info.disk_info import DiskInfo

__all__ = ["Disk", "DiskType", "DiskInfo"]
