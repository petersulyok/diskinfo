"""

    disk.py (C) 2022, Peter Sulyok
    Disk information Python Package for Linux.

"""
import os
from enum import Enum
from typing import List, Tuple


class DiskType(Enum):
    """Enumeration values for disk types """
    HDD = 1
    SSD = 2
    NVME = 4


class Disk:
    """Disk class implementation"""
    __name: str                         # Disk name (e.g. sda)
    __path: str                         # Disk path (e.g. /dev/sda)
    __byid_path: List[str]              # Disk by-byid paths (e.g. /dev/disk/by-byid/ata-WDC_WD80FLAX...)
    __bypath_path: List[str]            # Disk by-path paths (e.g. /dev/disk/by-path/pci-0000:00:17.0-ata-1)
    __dev_id: str                       # Disk device id (e.g. 8:0)
    __model: str                        # Disk model name
    __type: set                         # Disk type (HDD, SSD and/or NVME)
    __size: int                         # Disk size (number of 512-byte blocks)
    __physical_block_size: int          # Disk physical block size
    __logical_block_size: int           # Disk logical block size
    __serial_number: str                # Disk serial number
    __firmware: str                     # Disk firmware
    __wwn: str                          # Disk WWN byid
    __part_table_type: str              # Disk partition table type
    __part_table_uuid: str              # Disk partition table UUID
    __device_hwmon_path: str            # Path of the hwmon temperature file

    def __init__(self, disk_name: str = None, byid_name: str = None, bypath_name: str = None) -> None:
        """Initializes Disk() class. Based on one of the input parameters this function will identify
         disk, will collect information about it and store them in the class. One of the input parameter must
         be specified otherwise ValueError exception will be raised. The function can alse raise RuntimeError
         exception.

         Args:
             disk_name (str):   disk name (e.g. "sda" or "nvme0n1")
             byid_name (str):   a by-id typed name of the disk (e.g. "ata-WDC_WD320GLAX-68UNT16_A9HM3FTY")
             bypath_name (str): a by-path typed name of the disk (e.g. "pci-0000:00:17.0-ata-1"
         """
        # Identify disk name and path.
        if disk_name:
            # Save disk name and check device path.
            self.__name = disk_name
            self.__path = "/dev/" + disk_name
        elif byid_name:
            self.__name = os.path.basename(os.readlink("/dev/disk/by-id/" + byid_name))
            self.__path = "/dev/" + self.__name
        elif bypath_name:
            self.__name = os.path.basename(os.readlink("/dev/disk/by-path/" + bypath_name))
            self.__path = "/dev/" + self.__name
        else:
            raise ValueError("Missing initializer parameter, Disk() class cannot be initialized.")

        # Check the existence of disk name in /dev and /sys/block folders.
        if not os.path.exists(self.__path):
            raise ValueError("Disk path (" + self.__path + ") does not exist!")
        path = "/sys/block/" + self.__name
        if not os.path.exists(path):
            raise ValueError("Disk path (" + path + ") does not exist!")

        # Determine disk type (HDD, SSD, NVME)
        self.__type = set()
        path = "/sys/block/" + self.__name + "/queue/rotational"
        r = self._read_file(path)
        if r == "1":
            self.__type.add(DiskType.HDD)
        elif r == "0":
            self.__type.add(DiskType.SSD)
        else:
            raise RuntimeError(f"Disk type cannot be determined ({path}={r})")
        if "nvme" in self.__name:
            self.__type.add(DiskType.NVME)

        # Read attributes from /sys filesystem and from udev.
        self.__size = int(self._read_file("/sys/block/" + self.__name + "/size"))
        self.__model = self._read_file("/sys/block/" + self.__name + "/device/model")
        self.__dev_id = self._read_file("/sys/block/" + self.__name + "/dev")
        self.__physical_block_size = int(self._read_file("/sys/block/" + self.__name + "/queue/physical_block_size"))
        self.__logical_block_size = int(self._read_file("/sys/block/" + self.__name + "/queue/logical_block_size"))
        self.__serial_number = self._read_udev_property("ID_SERIAL_SHORT=")
        self.__firmware = self._read_udev_property("ID_REVISION=")
        self.__wwn = self._read_udev_property("ID_WWN=")
        self.__part_table_type = self._read_udev_property("ID_PART_TABLE_TYPE=")
        self.__part_table_uuid = self._read_udev_property("ID_PART_TABLE_UUID=")
        model = self._read_udev_property("ID_MODEL_ENC=")
        if model:
            self.__model = model

        # Read /dev/disk/by-byid/ path elements from udev and check their existence.
        self.__byid_path = self._read_udev_path(True)
        for f in self.__byid_path:
            if os.path.isfile(f):
                raise RuntimeError("Disk by-id path (" + f + ") does not exist!")

        # Read /dev/disk/by-path/ path elements from udev and check their existence.
        self.__bypath_path = self._read_udev_path(False)
        for f in self.__bypath_path:
            if os.path.isfile(f):
                raise RuntimeError("Disk by-path path (" + f + ") does not exist!")

    def get_name(self) -> str:
        """Returns the disk name. Please note that this name is not persistent."""
        return self.__name

    def get_path(self) -> str:
        """Returns the disk path. Please note this path is not persistent."""
        return self.__path

    def get_byid_path(self) -> List[str]:
        """Returns the disk path elements in a persistent '/dev/disk/by-byid/...' form.
        The result could be one or more path elements."""
        return self.__byid_path

    def get_bypath_path(self) -> List[str]:
        """Returns the disk path elements in a persistent '/dev/disk/by-path/...' form.
        The result could be one or more path elements."""
        return self.__bypath_path

    def get_wwn(self) -> str:
        """Returns the wwn id of the disk."""
        return self.__wwn

    def get_dev_id(self) -> str:
        """Returns the disk device id."""
        return self.__dev_id

    def get_model(self) -> str:
        """Returns the disk model."""
        return self.__model

    def get_serial(self) -> str:
        """Returns the disk serial number."""
        return self.__serial_number

    def get_firmware(self) -> str:
        """Returns the disk firmware."""
        return self.__firmware

    def get_type(self) -> set:
        """Returns True if the disk is an HDD, otherwise False."""
        return self.__type

    def get_type_str(self) -> str:
        """Returns disk type str."""
        if self.is_nvme():
            return "NVME"
        if self.is_ssd():
            return "SSD"
        return "HDD"

    def is_ssd(self) -> bool:
        """Returns True if the disk is a SSD, otherwise False."""
        result: bool = False
        if DiskType.SSD in self.__type:
            result = True
        return result

    def is_nvme(self) -> bool:
        """Returns True if the disk is a NVME device, otherwise False."""
        result: bool = False
        if DiskType.NVME in self.__type:
            result = True
        return result

    def get_size(self) -> int:
        """Returns the size of the disk in 512-byte units."""
        return self.__size

    def get_size_in_hrf(self, units: int = 0) -> Tuple[float, str]:
        """Returns the size of the disk in a human-readable form.

        Args:
            units (int): unit system will be used in result (0-default, 1, 2)
                0 - metric unit system
                1 - IEC unit system
                2 - legacy unit system
                read more about here <https://en.wikipedia.org/wiki/Byte>
        Returns:
            Tuple[float, str]: size of the disk, proper unit
        """
        metric_units: List[str] = ["B", "kB", "MB", "GB", "TB", "PT", "EB"]
        iec_units: List[str] = ["B", "KiB", "MiB", "GiB", "TiB", "PiT", "EiB"]
        legacy_units: List[str] = ["B", "KB", "MB", "GB", "TB", "PT", "EB"]
        divider: int    # Divider for the specified unit.
        size: float     # Result size
        unit: str       # Result unit
        i: int = 0      # Unit index

        # Set up the proper divider.
        if units == 0:
            divider = 1000
        elif units == 1:
            divider = 1024
        else:
            divider = 1024

        # Calculate the proper disk size.
        size = self.__size * 512
        for i, u in enumerate(metric_units):
            if size < divider:
                break
            size /= divider

        # Identify the proper unit for the calculated size.
        if units == 0:
            unit = metric_units[i]
        elif units == 1:
            unit = iec_units[i]
        else:
            unit = legacy_units[i]

        return size, unit

    @staticmethod
    def _read_file(path) -> str:
        """Reads the text content of the specified file. The function will hide IOError and FileNotFound exceptions
         during the file operation. The result string will be decoded (UTF-8) and stripped.

        Args:
            path (str): file path
        Returns:
            str: file content text
        """
        result: str = ""
        try:
            with open(path, "rt", encoding="UTF-8") as f:
                result = f.read()
        except (IOError, FileNotFoundError):
            pass
        return result.strip()

    def _read_udev_property(self, udev_property: str) -> str:
        """Reads a property from udev data file belonging to the disk (/run/udev/data/b?:?).
        It will hide IOError and FileNotFound exceptions during the file reading. The result string
        will be decoded (unicode_escaped) and stripped.

        Args:
            udev_property (str): udev property
        Returns:
            str: value of the property
        """
        lines: List[str]    # File content.
        result: str = ""    # Result string.

        # Read proper udev data file.
        try:
            path = "/run/udev/data/b" + self.__dev_id
            with open(path, "rt", encoding="unicode_escape") as f:
                lines = f.read().splitlines()
        except (IOError, FileNotFoundError):
            pass

        # Find the specified udev_property and copy its value.
        for li in lines:
            pos = li.find(udev_property)
            if pos != -1:
                result = li[pos+len(udev_property):]

        return result.strip()

    def _read_udev_path(self, byid: bool) -> List[str]:
        """Reads one or more path elements from udev data file belonging to the disk (/run/udev/data/b?:?).
        It will hide any IO exception during the file operation.

        Args:
            byid (bool):    True - by-id path elements will be loaded
                            False - by-path path elements will be loaded
        Returns:
            List[str]: path elements
        """
        path: str               # Path for udev data file
        lines: List[str]        # Data file line.
        result: List[str] = []  # Result list for path elements.
        udev_property: str      # udev property.

        # Read proper udev data file.
        try:
            path = "/run/udev/data/b" + self.__dev_id
            with open(path, "rt", encoding="UTF-8") as f:
                lines = f.read().splitlines()
        except (IOError, FileNotFoundError):
            pass

        # Find the specified path elements and collect their value.
        if byid:
            udev_property = "disk/by-id/"
        else:
            udev_property = "disk/by-path/"
        for li in lines:
            pos = li.find(udev_property)
            if pos != -1:
                result.append("/dev/" + li[pos:].strip())

        return result

    def __gt__(self, other):
        """Implementation of '>' operator for Disk class."""
        if self.__name > other.__name:
            return True
        else:
            return False

    def __lt__(self, other):
        """Implementation of '<' operator for Disk class."""
        if self.__name < other.__name:
            return True
        else:
            return False

    def __eq__(self, other):
        """Implementation of '==' operator for Disk class."""
        if self.__name == other.__name:
            return True
        else:
            return False

# End.
