#
#    Module `partition`: implements `Partition` class.
#    Peter Sulyok (C) 2022-2026.
#
from typing import List, Tuple
from pyudev import Device
from diskinfo.utils import size_in_hrf, _pyudev_getint
from diskinfo.filesystem import FileSystem


class Partition:
    """This class implements a partition entry containing all the relevant information. All partition attributes
    are collected at class creation time and these attributes can be accessed through get functions of the class.

    .. note::

        1. The class creation and the get functions will not generate disk operations and will not change the
           power state of the hard disk.
        2. A list of partition classes are created with the creation of :class:`~diskinfo.Disk` class and later can
           be accessed with :meth:`~diskinfo.Disk.get_partition_list()` method.

    Args:
        _device (pyudev.Device): pyudev.Device class


    Example:
        This example shows the basic use of the class::

            >>> from diskinfo import Disk
            >>> disk = Disk("nvme0n1")
            >>> plist = disk.get_partition_list()
            >>> for item in plist:
            ...     print(item.get_name())
            ...
            nvme0n1p1
            nvme0n1p2
            nvme0n1p3
            nvme0n1p4
            nvme0n1p5
            nvme0n1p6

    """

    # Partition attributes.
    __name: str                 # Partition name (e.g. sda1)
    __path: str                 # Partition path (e.g. /dev/sda1)
    __device_id: str            # Partition device id (e.g. 8:1)
    __byid_path: List[str]      # Partition by-byid path elements, located in /dev/disk/by-byid/ folder
    __bypath_path: str          # Partition by-path path located in /dev/disk/by-path/ folder
    __bypartuuid_path: str      # Partition by-partuuid path located in /dev/disk/by-partuuid/ folder
    __bypartlabel_path: str     # Partition by-partlabel path located in /dev/disk/by-partlabel/ folder
    __bylabel_path: str         # Partition by-label path located in /dev/disk/by-label/ folder
    __byuuid_path: str          # Partition by-uuid path located in /dev/disk/by-uuid/ folder
    __part_dev_id: str          # Partition device id (e.g. 8:1)
    __part_scheme: str          # Partition scheme (e.g. gpt)
    __part_label: str           # Partition label
    __part_uuid: str            # Partition uuid
    __part_type: str            # Partition type uuid
    __part_number: int          # Partition number
    __part_offset: int          # Partition first sector
    __part_size: int            # Partition size, in sectors
    __filesystem: FileSystem    # File system information

    def __init__(self, _device: Device) -> None:
        # Save partition name, path and device id.
        self.__name = _device.sys_name
        self.__path = _device.device_node
        self.__part_dev_id = _device.attributes.asstring("dev")

        # Save several path elements for the partition.
        self.__byid_path = []
        self.__bypath_path = ""
        self.__bypartuuid_path = ""
        self.__bypartlabel_path = ""
        self.__bylabel_path = ""
        self.__byuuid_path = ""
        for link in _device.device_links:
            if link.startswith("/dev/disk/by-id"):
                self.__byid_path.append(link)
                continue
            if link.startswith("/dev/disk/by-path"):
                self.__bypath_path = link
                continue
            if link.startswith("/dev/disk/by-partuuid"):
                self.__bypartuuid_path = link
                continue
            if link.startswith("/dev/disk/by-partlabel"):
                self.__bypartlabel_path = link
                continue
            if link.startswith("/dev/disk/by-label"):
                self.__bylabel_path = link
                continue
            if link.startswith("/dev/disk/by-uuid"):
                self.__byuuid_path = link
                continue

        # Save further partition attributes.
        self.__part_scheme = _device.get("ID_PART_ENTRY_SCHEME")
        self.__part_label = _device.get("ID_PART_ENTRY_NAME")
        self.__part_uuid = _device.get("ID_PART_ENTRY_UUID")
        self.__part_type = _device.get("ID_PART_ENTRY_TYPE")
        self.__part_number = _pyudev_getint(_device, "ID_PART_ENTRY_NUMBER", 0)
        self.__part_offset = _pyudev_getint(_device, "ID_PART_ENTRY_OFFSET", -1)
        self.__part_size = _pyudev_getint(_device, "ID_PART_ENTRY_SIZE", 0)

        # Delegate filesystem information to FileSystem.
        self.__filesystem = FileSystem(_device)

    def get_name(self) -> str:
        """Returns the name of the partition (e.g. `sda1` or `nvme0n1p1`).

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name())
                ...
                nvme0n1p1
                nvme0n1p2
                nvme0n1p3
                nvme0n1p4
                nvme0n1p5
                nvme0n1p6

        """
        return self.__name

    def get_path(self) -> str:
        """Returns the path of the partition (e.g. `/dev/sda1` or `/dev/nvme0n1p1`).

        .. note::

            This is not a persistent path!

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_path())
                ...
                /dev/nvme0n1p1
                /dev/nvme0n1p2
                /dev/nvme0n1p3
                /dev/nvme0n1p4
                /dev/nvme0n1p5
                /dev/nvme0n1p6

        """
        return self.__path

    def get_byid_path(self) -> List[str]:
        """Returns the `by-id` persistent path of the partition. The result could be one or more path elements.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_byid_path())
                ...
                nvme0n1p1 - ["/dev/disk/by-id/nvme-WDS100T1X0E-00AFY0_2140GF374501-part1",
                 "/dev/disk/by-id/nvme-eui.e8238fa6bf540001001b555a49bfc681-part1"]
                nvme0n1p2 - ["/dev/disk/by-id/nvme-WDS100T1X0E-00AFY0_2140GF374501-part2",
                 "/dev/disk/by-id/nvme-eui.e8238fa6bf540001001b555a49bfc681-part2"]
                nvme0n1p3 - ["/dev/disk/by-id/nvme-eui.e8238fa6bf540001001b555a49bfc681-part3",
                "/dev/disk/by-id/nvme-WDS100T1X0E-00AFY0_2140GF374501-part3"]
                nvme0n1p4 - ["/dev/disk/by-id/nvme-WDS100T1X0E-00AFY0_2140GF374501-part4",
                 "/dev/disk/by-id/nvme-eui.e8238fa6bf540001001b555a49bfc681-part4"]
                nvme0n1p5 - ["/dev/disk/by-id/nvme-WDS100T1X0E-00AFY0_2140GF374501-part5",
                 "/dev/disk/by-id/nvme-eui.e8238fa6bf540001001b555a49bfc681-part5"]
                nvme0n1p6 - ["/dev/disk/by-id/nvme-WDS100T1X0E-00AFY0_2140GF374501-part6",
                 "/dev/disk/by-id/nvme-eui.e8238fa6bf540001001b555a49bfc681-part6"]

        """
        return self.__byid_path

    def get_bypath_path(self) -> str:
        """Returns the `by-path` persistent path of the partition (see sample value in the example).

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_bypath_path())
                ...
                nvme0n1p1 - /dev/disk/by-path/pci-0000:02:00.0-nvme-1-part1
                nvme0n1p2 - /dev/disk/by-path/pci-0000:02:00.0-nvme-1-part2
                nvme0n1p3 - /dev/disk/by-path/pci-0000:02:00.0-nvme-1-part3
                nvme0n1p4 - /dev/disk/by-path/pci-0000:02:00.0-nvme-1-part4
                nvme0n1p5 - /dev/disk/by-path/pci-0000:02:00.0-nvme-1-part5
                nvme0n1p6 - /dev/disk/by-path/pci-0000:02:00.0-nvme-1-part6

        """
        return self.__bypath_path

    def get_bypartuuid_path(self) -> str:
        """Returns the `by-partuuid` persistent path of the partition (see sample values in the example).

        .. note::
            This is a GPT partition-specific value.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_bypartuuid_path())
                ...
                nvme0n1p1 - /dev/disk/by-partuuid/acb8374d-fb60-4cb0-8ac4-273417c6f847
                nvme0n1p2 - /dev/disk/by-partuuid/59417232-6e42-4c03-b258-2d20ddb0486a
                nvme0n1p3 - /dev/disk/by-partuuid/ec51c644-3ad7-44a5-9750-fc577a3d1ccf
                nvme0n1p4 - /dev/disk/by-partuuid/9192cde2-b90d-4fd1-99ed-a3584f66c87c
                nvme0n1p5 - /dev/disk/by-partuuid/6fd87857-265c-489c-8401-a47944c940f2
                nvme0n1p6 - /dev/disk/by-partuuid/d5e53353-1943-4827-9b46-63459432f51c

        """
        return self.__bypartuuid_path

    def get_bypartlabel_path(self) -> str:
        """Returns the `by-partlabel` persistent path of the partition (see sample value in the example).
        The result could be empty if the partition does not have a label.

        .. note::
            This is a GPT partition-specific value.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_bypartlabel_path())
                ...
                nvme0n1p1 - /dev/disk/by-partlabel/EFI system partition
                nvme0n1p2 - /dev/disk/by-partlabel/Microsoft reserved partition
                nvme0n1p3 - /dev/disk/by-partlabel/Basic data partition
                nvme0n1p4 - /dev/disk/by-partlabel/Basic data partition
                nvme0n1p5 -
                nvme0n1p6 -

        """
        return self.__bypartlabel_path

    def get_bylabel_path(self) -> str:
        """Returns the `by-label` persistent path of the partition (see sample value in the example).
        The result could be empty if the filesystem does not have a label.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_bylabel_path())
                ...
                nvme0n1p1 - /dev/disk/by-label/SYSTEM
                nvme0n1p2 -
                nvme0n1p3 - /dev/disk/by-label/Windows
                nvme0n1p4 - /dev/disk/by-label/Recovery tools
                nvme0n1p5 - /dev/disk/by-label/Debian
                nvme0n1p6 - /dev/disk/by-label/Arch Linux

        """
        return self.__bylabel_path

    def get_byuuid_path(self) -> str:
        """Returns the `by-uuid` persistent path of the partition (see sample value in the example).
        The result could be empty if the partition does not have a file system.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_byuuid_path())
                ...
                nvme0n1p1 - /dev/disk/by-uuid/6432-935A
                nvme0n1p2 -
                nvme0n1p3 - /dev/disk/by-uuid/0CA833E3A833CA4A
                nvme0n1p4 - /dev/disk/by-uuid/784034274033EB10
                nvme0n1p5 - /dev/disk/by-uuid/d54d33ea-d892-44d9-ae24-e3c6216d7a32
                nvme0n1p6 - /dev/disk/by-uuid/a0b1c6e7-2541-4e89-93eb-898f6d544a1e

        """
        return self.__byuuid_path

    def get_part_device_id(self) -> str:
        """Returns the device id of the partition in `major:minor` form.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_part_device_id())
                ...
                nvme0n1p1 - 259:1
                nvme0n1p2 - 259:2
                nvme0n1p3 - 259:3
                nvme0n1p4 - 259:4
                nvme0n1p5 - 259:5
                nvme0n1p6 - 259:6

        """
        return self.__part_dev_id

    def get_part_scheme(self) -> str:
        """Returns the scheme of the partition. The result could be `gpt` or `mbr`.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_part_scheme())
                ...
                nvme0n1p1 - gpt
                nvme0n1p2 - gpt
                nvme0n1p3 - gpt
                nvme0n1p4 - gpt
                nvme0n1p5 - gpt
                nvme0n1p6 - gpt

        """
        return self.__part_scheme

    def get_part_label(self) -> str:
        """Returns the label of the partition. The result could be empty if the partition does not have a label.

        .. note::
            This is a GPT partition-specific value.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_part_label())
                ...
                nvme0n1p1 - EFI system partition
                nvme0n1p2 - Microsoft reserved partition
                nvme0n1p3 - Basic data partition
                nvme0n1p4 - Basic data partition
                nvme0n1p5 -
                nvme0n1p6 -

        """
        return self.__part_label

    def get_part_uuid(self) -> str:
        """Returns the UUID of the partition.

        .. note::
            This is a GPT partition-specific value.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_part_uuid())
                ...
                nvme0n1p1 - acb8374d-fb60-4cb0-8ac4-273417c6f847
                nvme0n1p2 - 59417232-6e42-4c03-b258-2d20ddb0486a
                nvme0n1p3 - ec51c644-3ad7-44a5-9750-fc577a3d1ccf
                nvme0n1p4 - 9192cde2-b90d-4fd1-99ed-a3584f66c87c
                nvme0n1p5 - 6fd87857-265c-489c-8401-a47944c940f2
                nvme0n1p6 - d5e53353-1943-4827-9b46-63459432f51c

        """
        return self.__part_uuid

    def get_part_type(self) -> str:
        """Returns the UUID of the partition type. See available GPT partition types listed on
        `wikipedia <https://en.wikipedia.org/wiki/GUID_Partition_Table#Partition_type_GUIDs>`_.

        .. note::
            This is a GPT partition-specific value.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_part_type())
                ...
                nvme0n1p1 - c12a7328-f81f-11d2-ba4b-00a0c93ec93b
                nvme0n1p2 - e3c9e316-0b5c-4db8-817d-f92df00215ae
                nvme0n1p3 - ebd0a0a2-b9e5-4433-87c0-68b6b72699c7
                nvme0n1p4 - de94bba4-06d1-4d40-a16a-bfd50179d6ac
                nvme0n1p5 - 0fc63daf-8483-4772-8e79-3d69d8477de4
                nvme0n1p6 - 0fc63daf-8483-4772-8e79-3d69d8477de4

        """
        return self.__part_type

    def get_part_number(self) -> int:
        """Returns the number of the partition.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_part_number())
                ...
                nvme0n1p1 - 1
                nvme0n1p2 - 2
                nvme0n1p3 - 3
                nvme0n1p4 - 4
                nvme0n1p5 - 5
                nvme0n1p6 - 6

        """
        return self.__part_number

    def get_part_offset(self) -> int:
        """Returns the starting offset of the partition in 512-byte blocks.

        Example:
            An example about use of the function::

                >>> from diskinfo import Disk
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_part_offset())
                ...
                nvme0n1p1 - 2048
                nvme0n1p2 - 1050624
                nvme0n1p3 - 1312768
                nvme0n1p4 - 838125568
                nvme0n1p5 - 840173568
                nvme0n1p6 - 1035485184

        """
        return self.__part_offset

    def get_part_size(self) -> int:
        """Returns the size of the partition in 512-byte blocks.

        Example:
            An example about use of the function::

                >>> from diskinfo import *
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     print(item.get_name(), "-", item.get_part_size())
                ...
                nvme0n1p1 - 1048576
                nvme0n1p2 - 262144
                nvme0n1p3 - 836812800
                nvme0n1p4 - 2048000
                nvme0n1p5 - 195311616
                nvme0n1p6 - 209715200

        """
        return self.__part_size

    def get_part_size_in_hrf(self, units: int = 0) -> Tuple[float, str]:
        """Returns the size of the partition in human-readable form.

        Args:
            units (int): unit system will be used for the calculation and in the result:

                            - 0 metric units (default)
                            - 1 IEC units
                            - 2 legacy units

                         Read more about `units here <https://en.wikipedia.org/wiki/Byte>`_.

        Returns:
            Tuple[float, str]: size in human-readable form, proper unit

        Example:
            An example about use of the function::

                >>> from diskinfo import *
                >>> disk = Disk("nvme0n1")
                >>> plist = disk.get_partition_list()
                >>> for item in plist:
                ...     s, u = item.get_part_size_in_hrf()
                ...     print(item.get_name(), "-", "{s:.1f} {u}")
                ...
                nvme0n1p1 - 536.9 MB
                nvme0n1p2 - 134.2 MB
                nvme0n1p3 - 428.4 GB
                nvme0n1p4 - 1.0 GB
                nvme0n1p5 - 100.0 GB
                nvme0n1p6 - 107.4 GB

        """
        return size_in_hrf(self.__part_size * 512, units)

    def get_filesystem(self) -> FileSystem:
        """Returns the :class:`~diskinfo.FileSystem` object associated with this partition.

        Returns:
            FileSystem: filesystem information for this partition

        """
        return self.__filesystem

    def __repr__(self):
        """String representation of the Partition class."""
        return (f"Partition(name={self.__name}, "
                f"path={self.__path}, "
                f"device_id={self.__part_dev_id}, "
                f"part_scheme={self.__part_scheme}, "
                f"part_label={self.__part_label}, "
                f"part_uuid={self.__part_uuid}, "
                f"part_type={self.__part_type}, "
                f"part_number={self.__part_number}, "
                f"part_offset={self.__part_offset}, "
                f"part_size={self.__part_size}, "
                f"filesystem={self.__filesystem})")


# End
