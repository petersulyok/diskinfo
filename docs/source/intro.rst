Introduction
============
This Python library can assist in collecting disk information on Linux. In more details, it can:

    - collect information about a specific disk
    - explore existing disks in the system
    - translate between traditional and persistent disk names
    - read disk temperature
    - read SMART attributes of a disk
    - read partition list of a disk


Installation
------------
Standard installation from `pypi <https://pypi.org>`_::

    pip install diskinfo

The library has the following run-time requirements:

    - Python version >= `3.8`
    - for reading SMART data with :meth:`~diskinfo.Disk.get_smart_data()` method, the `smartmontools` package is required
    - for reading disk temperature with :meth:`~diskinfo.Disk.get_temperature()` method, the following dependencies
      needs to be considered:

        .. list-table::
            :header-rows: 1

            *   - Disk type
                - Requirement
            *   - SATA HDD/SSD
                - `drivetemp` kernel module (Linux kernel version `5.6+`) has to be loaded
            *   - SCSI/ATA HDD
                - `smartmontools` has to be installed
            *   - NVME
                - none

    - for reading disk partition information with :meth:`~diskinfo.Disk.get_partition_list()` method, the `df` command
      is required.
    - optionally, `Rich Python library <https://pypi.org/project/rich/>`_ is required for the demo


Demo
----
The library contains a demo application with multiple screens. The `Rich Python library <https://pypi.org/project/rich/>`_
must be installed for the running the demo::

     pip install rich

The first demo screen will list the explored disks::

     python -m diskinfo.demo

.. image:: https://github.com/petersulyok/diskinfo/raw/main/docs/diskinfo_rich_demo.png

The second demo screen will display the attributes of a specified disk::

     python -m diskinfo.demo sdb

.. image:: https://github.com/petersulyok/diskinfo/raw/main/docs/diskinfo_rich_demo_2.png

The third demo screen will display the SMART attributes of a specified disk::

     python -m diskinfo.demo nvme0n1 -s

.. image:: https://github.com/petersulyok/diskinfo/raw/main/docs/diskinfo_rich_demo_4.png


The fourth demo screen will display the list of partitions on a specified disk::

     python -m diskinfo.demo nvme0n1 -p

.. image:: https://github.com/petersulyok/diskinfo/raw/main/docs/diskinfo_rich_demo_3.png


Persistent disk names
---------------------
Please note that the traditional disk names in Linux are not persistent::

     /dev/sda
     /dev/sdb

It means they can refer a different physical disk after a reboot. Read more about this topic
at `Arch Linux wiki: Persistent block device naming
<https://wiki.archlinux.org/title/persistent_block_device_naming>`_.

On the other hand, there are real persistent ways to refer disk or block devices in Linux:

    1. `by-id` path: it can be found in `/dev/disk/by-id` directory and it is constructed with disk serial numbers::

            /dev/disk/by-id/ata-Samsung_SSD_850_PRO_1TB_92837A469FF876
            /dev/disk/by-id/wwn-0x5002539c417223be

    2. `by-path` path: it can be found in `/dev/disk/by-path` directory and it is constructed with a physical path
       to the disk::

            /dev/disk/by-path/pci-0000:00:17.0-ata-3

There are similar persistent constructions for disk partitions, too.


How to use
----------
The following chapters will present the six use cases listed in the :ref:`Introduction` chapter above.

Use case 1: collect information about a disk
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Disk attributes can be collected with the creation of a :class:`~diskinfo.Disk` class. All disk attributes will be
collected at class creation time::

    >>> from diskinfo import Disk
    >>> d = Disk("sda")

and later the attributes can be accessed with the help of `get` functions of the class::

    >>> d.get_model()
    'Samsung SSD 870 QVO 8TB'
    >>> d.is_ssd()
    True
    >>> s, u = d.get_size_in_hrf()
    >>> print(f"{s:.1f} {u}")
    8.0 TB
    >>> d.get_serial()
    'S5SXNG0MB01829M'


The :class:`~diskinfo.Disk` class contains the following disk attributes:

.. list-table::
    :header-rows: 1

    *   - Attribute
        - Description
        - Sample value
    *   - name
        - Disk name
        - `sda` or `nvme0n1`)
    *   - path
        - Disk path
        - `/dev/sda` or `/dev/nvme0n1`
    *   - `by-id` path
        - Persistent disk path in `/dev/disk/by-id` directory
        -
    *   - `by-path` path
        - Persistent disk path in `/dev/disk/by-path` directory
        -
    *   - wwn
        - `World Wide Name <https://en.wikipedia.org/wiki/World_Wide_Name>`_
        - `0x5002538c307370ec`
    *   - model
        - Disk model
        - `Samsung SSD 850 PRO 1TB`
    *   - serial number
        - Disk serial number
        - `S3E2NY0J723218R`
    *   - firmware
        - Disk firmware
        - `EXM04B6Q`
    *   - type
        - Disk type
        - `HDD`, `SSD` or `NVME`
    *   - size
        - Disk size in 512-byte blocks
        -
    *   - device id
        - Disk device id, in `'major:minor'` form
        - `8:0`
    *   - physical block size
        - Disk physical block size in bytes
        - `512` or `4096`
    *   - logical block size
        - Disk logical block size in bytes
        - `512`
    *   - partition table type
        - Type of the partition table on disk
        - `gpt` or `mbr`
    *   - partition table uuid
        - UUID of the partition table on disk
        -

Use case 2: explore disks
^^^^^^^^^^^^^^^^^^^^^^^^^
Disks can be explored with the creation of the :class:`~diskinfo.DiskInfo` class. During this process all disks will
identified and their attributes will be stored::

    >>> from diskinfo import Disk, DiskInfo
    >>> di = DiskInfo()

After that, the number of identified disks can be read with the help of :meth:`~diskinfo.DiskInfo.get_disk_number()`
method::

    >>> di.get_disk_number()
    4

and the list of the disks can be accessed (see more details in :meth:`~diskinfo.DiskInfo.get_disk_list()` method)::

    >>> disks = di.get_disk_list(sorting=True)
    >>> for d in disks:
    >>>     print(d.get_path())
    /dev/nvme0n1
    /dev/sda
    /dev/sdb
    /dev/sdc

The caller can also apply filters (i.e. included and excluded disk types) for both functions and can query only subset
of the disks based on one or more specific :class:`~diskinfo.DiskType`. The list of disk can be also sorted.

Use case 3: translate between traditional and persistent disk names
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Translation from traditional disk names to persistent ones can be done this way::

    >>> from diskinfo import Disk
    >>> d = Disk("sda")
    >>> d.get_byid_path()
    ['/dev/disk/by-id/ata-Samsung_SSD_850_PRO_1TB_92837A469FF876', '/dev/disk/by-id/wwn-0x5002539c417223be']
    >>> d.get_bypath_path()
    ['/dev/disk/by-path/pci-0000:00:17.0-ata-3', '/dev/disk/by-path/pci-0000:00:17.0-ata-3.0']
    >>> d.get_serial_numner()
    '92837A469FF876'
    >>> d.get_wwn()
    '0x5002539c417223be'

In the opposite direction several unique (persistent) identifier can be used to initialize :class:`~diskinfo.Disk`
class then the traditional disk path or name can be read::

    >>> from diskinfo import Disk
    >>> d = Disk(byid_name="ata-Samsung_SSD_850_PRO_1TB_92837A469FF876")
    >>> d.get_path()
    '/dev/sda'
    >>> d = Disk(bypath_name="pci-0000:00:17.0-ata-3")
    >>> d.get_path()
    '/dev/sda'
    >>> d = Disk(serial_number="92837A469FF876")
    >>> d.get_path()
    '/dev/sda'
    >>> d = Disk(wwn="0x5002539c417223be")
    >>> d.get_name()
    'sda'

Use case 4: read disk temperature
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
After having a :class:`~diskinfo.Disk` class instance, the disk temperature can be read in this way::

    >>> from diskinfo import Disk
    >>> d = Disk("sda")
    >>> d.get_temperature()
    28

Please note that the `drivetemp <https://www.kernel.org/doc/html/latest/hwmon/drivetemp.html>`_ kernel module should
be loaded for SSDs and HDDs (available from Linux Kernel 5.6+). NVME disks do not require anything.

Use case 5: read disk SMART attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
After having a :class:`~diskinfo.Disk` class instance, the SMART attributes of the disk can be read with the help of
:meth:`~diskinfo.Disk.get_smart_data()` method.

    >>> from diskinfo import Disk, DiskSmartData
    >>> d = Disk("sda")
    >>> sd = d.get_smart_data()

In case of HDDs, we can skip checking if they are in STANDBY mode::

    >>> sd = d.get_smart_data(nocheck=True)
    >>> if sd.standby_mode:
    ...     print("Disk is in STANDBY mode.")
    ... else:
    ...     print("Disk is ACTIVE.")
    ...
    Disk is in STANDBY mode.

If we dont use the `nocheck` parameter here (when the HDD is in STANDBY mode) then the HDD will spin up and will
return to ACTIVE mode. Please note if :attr:`~diskinfo.DiskSmartData.standby_mode` is `True` then no other
SMART attributes are loaded.

The most important SMART information for all disk types is the health status::

    >>> if sd.healthy:
    ...     print("Disk is HEALTHY.")
    ... else:
    ...     print("Disk is FAILED!")
    ...
    Disk is HEALTHY.

In case of SSDs and HDDs the traditional SMART attributes can be accessed via
:attr:`~diskinfo.DiskSmartData.smart_attributes` list::

    >>> for item in sd.smart_attributes:
    ...     print(f"{item.id:>3d} {item.attribute_name}: {item.raw_value}")
    ...
      5 Reallocated_Sector_Ct: 0
      9 Power_On_Hours: 6356
     12 Power_Cycle_Count: 2308
    177 Wear_Leveling_Count: 2
    179 Used_Rsvd_Blk_Cnt_Tot: 0
    181 Program_Fail_Cnt_Total: 0
    182 Erase_Fail_Count_Total: 0
    183 Runtime_Bad_Block: 0
    187 Uncorrectable_Error_Cnt: 0
    190 Airflow_Temperature_Cel: 28
    195 ECC_Error_Rate: 0
    199 CRC_Error_Count: 0
    235 POR_Recovery_Count: 67
    241 Total_LBAs_Written: 9869978356

See more details in :class:`~diskinfo.DiskSmartData` and :class:`~diskinfo.SmartAttribute` classes.

In case of NVME disks they have their own SMART data in :attr:`~diskinfo.DiskSmartData.nvme_attributes` attribute::

    >>> if d.is_nvme():
    ...     print(f"Power on hours: {sd.nvme_attributes.power_on_hours} h")
    ...
    Power on hours: 1565 h

See the detailed list of the NVME attributes in :class:`~diskinfo.NvmeAttributes` class.

Please note that the :meth:`~diskinfo.Disk.get_smart_data()` method relies on `smartctl` command.
It means that the caller needs to have special access rights (i.e. `sudo` or `root`).

Use case 6: read partition list
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
After having a :class:`~diskinfo.Disk` class instance, the partition list can be read with the help of
:meth:`~diskinfo.Disk.get_partition_list()` method.

    >>> from diskinfo import Disk, DiskSmartData
    >>> d = Disk("sda")
    >>> plist = d.get_partition_list()

The return value is a list of :class:`~diskinfo.Partition` classes. This class provides several get functions to access
the partition attributes::

    >>> from diskinfo import Disk
    >>> disk = Disk("nvme0n1")
    >>> plist = disk.get_partition_list()
    >>> for item in plist:
    ...     Disk(item.get_name())
    ...
    nvme0n1p1
    nvme0n1p2
    nvme0n1p3
    nvme0n1p4
    nvme0n1p5
    nvme0n1p6

The :class:`~diskinfo.Partition` class contains the following partition attributes:

.. list-table::
    :header-rows: 1

    *   - Attribute
        - Description
        - Sample value
    *   - name
        - Partition name
        - `sda1` or `nvme0n1p1`
    *   - Path
        - Partition path
        - `/dev/sda1` or `/dev/nvme0n1p1`
    *   - `by-id` path
        - Persistent path in `/dev/disk/by-id` directory
        -
    *   - `by-path` path
        - Persistent path in `/dev/disk/by-path` directory
        -
    *   - `by-partuuid` path
        - Persistent path in `/dev/disk/by-partuuid` directory
        -
    *   - `by-partlabel` path
        - Persistent path in `/dev/disk/by-partlabel` directory
        -
    *   - `by-uuid` path
        - Persistent path in `/dev/disk/by-uuid` directory
        -
    *   - `by-label` path
        - Persistent path in `/dev/disk/by-label` directory
        -
    *   - Device id
        - Partition device id
        - `8:1`
    *   - Partition scheme
        - Partition scheme
        - `gtp` or `mbr`
    *   - Partition label
        - Partition label
        - `Basic data partition`
    *   - Partition UUID
        - Partition UUID
        - `acb8374d-fb60-4cb0-8ac4-273417c6f847`
    *   - Partition type
        - Partition `type UUID <https://en.wikipedia.org/wiki/GUID_Partition_Table#Partition_type_GUIDs>`_
        -
    *   - Partition number
        - Partition number in the partition table
        -
    *   - Partition offset
        - Partition starting offset in 512-byte blocks
        -
    *   - Partition size
        - Partition size in 512-byte blocks
        -
    *   - File system label
        - File system label
        -
    *   - File system UUID
        - File system UUID
        -
    *   - File system type
        - File system type
        - `ntfs` or `ext4`)
    *   - File system version
        - File system version
        - `1.0` in case of `ext4`)
    *   - File system usage
        - File system usage
        - `filesystem` or `other`
    *   - File system free size
        - File system free size in 512-byte blocks
        -
    *   - File system mounting point
        - File system mounting point
        - `/` or `/home`
