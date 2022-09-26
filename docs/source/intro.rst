Introduction
============
This Python library can discover and can collect disk information on Linux. It can also provide persistent disk names
for stable device referencing.

Installation
------------
Standard installation from `pypi <https://pypi.org>`_::

    pip install diskinfo

The package requires Python version >= 3.6 and does not have extra dependencies.

Demo
----
The library contains a simple demo, it can be executed in the following way::

     python -m diskinfo.demo

.. image:: https://github.com/petersulyok/diskinfo/raw/main/docs/diskinfo_rich_demo.png

Please note that `rich <https://pypi.org/project/rich/>`_ Python library needs to be installed for this colorful demo.

How to use
----------
There are two different use cases how this library can be used. In the first case the user can collect information about
a specific disk, while in the second one all existing disks can be explored in the system.

Option 1: collect information about a disk
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Information can be collected about a specific disk with the creation of a :class:`~diskinfo.Disk` class. Here the user
has to provide a unique identifier for the disk. Disk information will be collected at class creation time then the
user can access the collected disk attributes through get functions of the class::

    >>> from diskinfo import Disk
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


Here is the list about the collected disk attributes:

.. list-table::
    :header-rows: 1

    *   - Attribute
        - Description
        - Example
    *   - name
        - Disk name
        - ``sda`` or ``nvme0n1``
    *   - path
        - Disk path
        - ``/dev/sda`` or ``/dev/nvme0n1``
    *   - by-id path
        - Persistent disk path in ``/dev/disk/by-id`` directory
        - ``/dev/disk/by-id/ata-Samsung_SSD_850_PRO_1TB_S3E2NY0J723218R``
    *   - by-path path
        - Persistent disk path in ``/dev/disk/by-path`` directory
        - ``/dev/disk/by-id/pci-0000:00:17.0-ata-2``
    *   - wwn
        - world wide name (unique identifier) for the disk
        - ``0x5002538c307370ec``
    *   - model
        - Disk model
        - ``Samsung SSD 850 PRO 1TB``
    *   - serial number
        - Disk serial number
        - ``S3E2NY0J723218R``
    *   - firmware
        - Disk firmware
        - ``EXM04B6Q``
    *   - type
        - Disk type
        - ``HDD``, ``SSD``, ``NVME``
    *   - size
        - Disk size in 512-byte units
        - ``2000409264``
    *   - device id
        - Disk device id (in ``major:minor`` form)
        - ``8:0``
    *   - physical block size
        - Disk physical block size in bytes
        - ``512``
    *   - logical block size
        - Disk logical block size in bytes
        - ``512``
    *   - partition table type
        - Type of the partition table on disk
        - ``gpt`` or ``mbr``
    *   - partition table uuid
        - UUID of the partition table on disk
        - ``008e4c54-96c9-4771-9e13-60dfe00ebb7f``

See the complete list of the class methods in documentation of :class:`~diskinfo.Disk` class.

Option 2: explore disks
^^^^^^^^^^^^^^^^^^^^^^^
Disks can be explored with the creation of the :class:`~diskinfo.DiskInfo` class. After that the list and
the number of identified disks can be queried with :meth:`~diskinfo.DiskInfo.get_disk_number()`
and :meth:`~diskinfo.DiskInfo.get_disk_list()` functions::

    >>> from diskinfo import Disk, DiskInfo
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

The caller can also apply filters (i.e. included and excluded disk types) for both functions and can query only subset
of the disks based on one or more specific :class:`~diskinfo.DiskType`. The list of disk can be also sorted.

Persistent disk names
---------------------
Please note that not all kind of block device names are persistent. For example this disk path::

     "/dev/sdb"

could refer different physical disk after a reboot. That is reason why other persistent names have been introduced in
``Linux`` and ``udev``. The physical device can be referenced by the following path type::

     "/dev/disk/by-id/nvme-WDS80T1X06-00AFY1_2130GF574294"

This type of reference is called `by-id` path in this documentation. The physical connector (i.e. where the disk is
connected) can be also referenced with the following path::

     "/dev/disk/by-path/pci-0000:02:00.0-nvme-1"

This type of reference is called `by-path` path in this documentation. Both references are persistent and
safe in disk referencing.

Read more about this topic at `Arch Linux wiki: Persistent block device naming
<https://wiki.archlinux.org/title/persistent_block_device_naming>`_.

