# diskinfo
[![Documentation Status](https://readthedocs.org/projects/diskinfo/badge/?version=latest)](https://disk-info.readthedocs.io/en/latest/?badge=latest)

A disk information Python library for Linux.

This library provides API for:
1. collecting information about a specific disk
2. discovering existing disks in your system
3. translation between device names and persistent names, for example:

       "/dev/sda" <-> "/dev/disk/by-id/ata-Samsung_SSD_850_PRO_1TB_S3D2NY0J819218R" 

Installation
------------
Standard installation from `pypi`:

    pip install diskinfo

The package does not have extra dependencies.

API documentation
-----------------
The detailed [API documentation](https://diskinfo.readthedocs.io/en/latest/index.html) can be found on ``readthedocs.io``.

Demo
----
In the package a short demo can be found. For running the demo, execute this:

    python -m diskinfo.demo
    There are 2 disks installed in this system (0 HDDs, 2 SSDs, 0 NVMEs).
    [sda]
        path:                     /dev/sda
        model:                    Samsung SSD 850 PRO 1TB
        size:                     953.9 GB
        serial:                   S3D2NY0J819218R
        firmware:                 EXM04B6Q
        device type:              SSD
        by-id path:               ['/dev/disk/by-id/wwn-0x5002539c407370be', '/dev/disk/by-id/ata-Samsung_SSD_850_PRO_1TB_S3D2NY0J819218R']
        by-path path:             ['/dev/disk/by-path/pci-0000:00:17.0-ata-1.0', '/dev/disk/by-path/pci-0000:00:17.0-ata-1']
        wwn id:                   0x5002539c407370be
        device id:                (8:0)
        Physical block size:      512
        Logical block size:       512
        Partition table type:     gpt
        Partition table UUID:     008e4c54-96c9-4771-9e13-60dfe00ebb7f
    [sdb]
        path:                     /dev/sdb
        model:                    Samsung SSD 850 EVO 2TB
        size:                     1.8 TB
        serial:                   S3HDNWBG801398X
        firmware:                 EMT02B6Q
        device type:              SSD
        by-id path:               ['/dev/disk/by-id/ata-Samsung_SSD_850_EVO_2TB_S3HDNWBG801398X', '/dev/disk/by-id/wwn-0x5002538c8000a847']
        by-path path:             ['/dev/disk/by-path/pci-0000:00:17.0-ata-2', '/dev/disk/by-path/pci-0000:00:17.0-ata-2.0']
        wwn id:                   0x5002538c8000a847
        device id:                (8:16)
        Physical block size:      512
        Logical block size:       512
        Partition table type:     gpt
        Partition table UUID:     d3f932e0-7107-455e-a569-9acd5b60d204
