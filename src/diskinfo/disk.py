#
#    Module `disk`: implements classes `DiskType` and `Disk`.
#    Peter Sulyok (C) 2022.
#
import glob
import os
from typing import List, Tuple


class DiskType:
    """Constant values for disk types and for their names."""
    HDD = 1
    """Hard disk type."""
    SSD = 2
    """SSD disk type."""
    NVME = 4
    """NVME disk type."""
    HDD_STR = "HDD"
    """Hard disk type name."""
    SSD_STR = "SSD"
    """SSD disk type name."""
    NVME_STR = "NVME"
    """NVME disk type name."""


class Disk:
    """The class can be initialized with specifying one unique identifier of the disk. Based on this identifier
    disk information will be collected  (from ``/sys`` and ``udev`` system data) and stored in the class. Here are
    the unique identifiers of the disk:

        - a disk name
        - a ``by-id`` name of the disk (from ``"/dev/disk/by-id/..."``  directory)
        - a ``by-path`` name of the disk (from ``"/dev/disk/by-path/..."``  directory)
        - a disk serial number
        - a disk wwn name

    and one of them MUST be specified as an input parameter otherwise :py:obj:`ValueError` exception will be raised.
    During the class initialization the disk will not be directly accessed, so its power state will not change
    (e.g. it will not be awakened from a `STANDBY` or `SLEEP` state).

    Operators (``<``, ``>`` and ``==``) are also implemented for this class to compare class instances, they
    use the disk name for comparision.

    Args:
        disk_name (str): disk name (e.g. ``"sda"`` or ``"nvmep0n1"``) located in directory ``/dev/``.
        byid_name (str): by-id name of the disk (e.g. ``"ata-WDC_WD320GLAX-68UNT16_A9HM3FTY"``) located in
                         directory ``/dev/disk/by-id/``.
        bypath_name (str): by-path name of the disk (e.g. ``"pci-0000:00:17.0-ata-1"``) located in
                           directory ``/dev/disk/by-path/``.
        serial_number (str): serial number of the disk (e.g. ``"92837A469FF876"``)
        wwn_name (str): WWN name of the disk (e.g. ``"0x5002638c807270be"``)

    Raises:
        ValueError: in case of missing or invalid parameters
        RuntimeError: in case of any system error

    Example:
        This exampe shows how to create a ``Disk`` class then how to print the disk path and disk serial number:

        >>> from diskinfo import Disk
        >>> d = Disk("sda")
        >>> d.get_path()
        '/dev/sda'
        >>> d.get_serial_number()
        'S3D2NY0J819210S'

    """

    # Disk attributes:
    __name: str                         # Disk name (e.g. sda)
    __path: str                         # Disk path (e.g. /dev/sda)
    __byid_path: List[str]              # Disk by-byid paths (e.g. /dev/disk/by-byid/ata-WDC_WD80FLAX...)
    __bypath_path: List[str]            # Disk by-path paths (e.g. /dev/disk/by-path/pci-0000:00:17.0-ata-1)
    __wwn: str                          # Disk WWN
    __model: str                        # Disk model
    __serial_number: str                # Disk serial number
    __firmware: str                     # Disk firmware
    __type: int                         # Disk type (HDD, SSD or NVME)
    __size: int                         # Disk size (number of 512-byte blocks)
    __device_id: str                    # Disk device id (e.g. 8:0)
    __physical_block_size: int          # Disk physical block size
    __logical_block_size: int           # Disk logical block size
    __part_table_type: str              # Disk partition table type
    __part_table_uuid: str              # Disk partition table UUID
    __hwmon_path: str                   # Path for the HWMON temperature file

    def __init__(self, disk_name: str = None, byid_name: str = None, bypath_name: str = None,
                 serial_number: str = None, wwn_name: str = None) -> None:
        """See class definition."""

        # Initialize with a disk name.
        if disk_name:
            self.__name = disk_name
        # Initialize with a disk `by-id` name.
        elif byid_name:
            self.__name = os.path.basename(os.readlink("/dev/disk/by-id/" + byid_name))
        # Initialize with a disk `by-path` name.
        elif bypath_name:
            self.__name = os.path.basename(os.readlink("/dev/disk/by-path/" + bypath_name))
        # Initialize with a disk serial number.
        elif serial_number:
            name = ""
            for file in os.listdir("/sys/block/"):
                self.__device_id = self._read_file("/sys/block/" + file + "/dev")
                self.__serial_number = self._read_udev_property("ID_SERIAL_SHORT=")
                if serial_number == self.__serial_number:
                    name = file
                    break
            if name == "":
                raise ValueError("Disk serial number (" + serial_number + ") cannot be found!")
            self.__name = name
        # Initialize with a disk WWN name.
        elif wwn_name:
            name = ""
            for file in os.listdir("/sys/block/"):
                self.__device_id = self._read_file("/sys/block/" + file + "/dev")
                self.__wwn = self._read_udev_property("ID_WWN=")
                if wwn_name in self.__wwn:
                    name = file
                    break
            if name == "":
                raise ValueError("Disk WWN  name (" + wwn_name + ") cannot be found!")
            self.__name = name
        # If none of them was specified.
        else:
            raise ValueError("Missing initializer parameter, Disk() class cannot be initialized.")

        # Check the existence of disk name in /dev and /sys/block folders.
        self.__path = "/dev/" + self.__name
        if not os.path.exists(self.__path):
            raise ValueError("Disk path (" + self.__path + ") does not exist!")
        path = "/sys/block/" + self.__name
        if not os.path.exists(path):
            raise ValueError("Disk path (" + path + ") does not exist!")

        # Determine disk type (HDD, SSD, NVME)
        path = "/sys/block/" + self.__name + "/queue/rotational"
        result = self._read_file(path)
        if result == "1":
            self.__type = DiskType.HDD
        elif result == "0":
            self.__type = DiskType.SSD
        else:
            raise RuntimeError("Disk type cannot be determined based on this value (" + path + "=" + result + ").")
        if "nvme" in self.__name:
            self.__type = DiskType.NVME

        # Read attributes from /sys filesystem and from udev.
        self.__size = int(self._read_file("/sys/block/" + self.__name + "/size"))
        self.__model = self._read_file("/sys/block/" + self.__name + "/device/model")
        self.__device_id = self._read_file("/sys/block/" + self.__name + "/dev")
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

        # Read `/dev/disk/by-byid/` path elements from udev and check their existence.
        self.__byid_path = self._read_udev_path(True)
        for file_name in self.__byid_path:
            if not os.path.exists(file_name):
                raise RuntimeError("Disk by-id path (" + file_name + ") does not exist!")

        # Read `/dev/disk/by-path/` path elements from udev and check their existence.
        self.__bypath_path = self._read_udev_path(False)
        for file_name in self.__bypath_path:
            if not os.path.exists(file_name):
                raise RuntimeError("Disk by-path path (" + file_name + ") does not exist!")

        # Find the path for HWMON file of the disk.
        # Step 1: Check typical HWMON path for HDD, SSD disks
        path = "/sys/block/" + self.__name + "/device/hwmon/hwmon*/temp1_input"
        file_names = glob.glob(path)
        if file_names and os.path.exists(file_names[0]):
            self.__hwmon_path = file_names[0]
        else:
            # Step 2: Check HWMON path for NVME disks in Linux kernel 5.10-5.18?
            path = "/sys/block/" + self.__name + "/device/device/hwmon/hwmon*/temp1_input"
            file_names = glob.glob(path)
            if file_names and os.path.exists(file_names[0]):
                self.__hwmon_path = file_names[0]
            else:
                # Step 3: Check HWMON path for NVME disks in Linux kernel 5.19+?
                path = "/sys/block/" + self.__name + "/device/hwmon*/temp1_input"
                file_names = glob.glob(path)
                if file_names and os.path.exists(file_names[0]):
                    self.__hwmon_path = file_names[0]

    def get_name(self) -> str:
        """Returns the disk name."""
        return self.__name

    def get_path(self) -> str:
        """Returns the disk path. Please note this path is not persistent."""
        return self.__path

    def get_byid_path(self) -> List[str]:
        """Returns the disk path elements in a persistent ``/dev/disk/by-byid/...`` form.
        The result could be one or more path elements."""
        return self.__byid_path

    def get_bypath_path(self) -> List[str]:
        """Returns the disk path elements in a persistent ``/dev/disk/by-path/...`` form.
        The result could be one or more path elements."""
        return self.__bypath_path

    def get_wwn(self) -> str:
        """Returns the WWN name of the disk. Read more about
        `WWN names here <https://en.wikipedia.org/wiki/World_Wide_Name>`_."""
        return self.__wwn

    def get_model(self) -> str:
        """Returns the disk model."""
        return self.__model

    def get_serial_number(self) -> str:
        """Returns the disk serial number."""
        return self.__serial_number

    def get_firmware(self) -> str:
        """Returns the disk firmware."""
        return self.__firmware

    def get_type(self) -> int:
        """Returns the type of the disk."""
        return self.__type

    def is_ssd(self) -> bool:
        """Returns True if the disk type is SSD, otherwise False."""
        return bool(self.__type == DiskType.SSD)

    def is_nvme(self) -> bool:
        """Returns True if the disk type is NVME, otherwise False."""
        return bool(self.__type == DiskType.NVME)

    def is_hdd(self) -> bool:
        """Returns True if the disk type is HDD, otherwise False."""
        return bool(self.__type == DiskType.HDD)

    def get_type_str(self) -> str:
        """Returns the name of the disk type. See the return values in :class:`~diskinfo.DiskType` class."""
        if self.is_nvme():
            return DiskType.NVME_STR
        if self.is_ssd():
            return DiskType.SSD_STR
        return DiskType.HDD_STR

    def get_size(self) -> int:
        """Returns the size of the disk in 512-byte units."""
        return self.__size

    def get_size_in_hrf(self, units: int = 0) -> Tuple[float, str]:
        """Returns the size of the disk in a human-readable form (e.g. ``"1 TB"``).

        Args:
            units (int): unit system will be used in result:

                            - 0 metric units (default)
                            - 1 IEC units
                            - 2 legacy units

                         Read more about `units here <https://en.wikipedia.org/wiki/Byte>`_.

        Returns:
            Tuple[float, str]: size of the disk, proper unit

        Example:
            This example showa the basic use of this method:

                >>> from diskinfo import Disk
                >>> d = Disk("sda")
                >>> s, u = d.get_size_in_hrf()
                >>> print(f"{s:.1f} {u}")
                8.0 TB

        """
        metric_units: List[str] = ["B", "kB", "MB", "GB", "TB", "PB", "EB"]
        iec_units: List[str] = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"]
        legacy_units: List[str] = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
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
        number_of_units = len(metric_units)
        for i in range(number_of_units):
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

    def get_device_id(self) -> str:
        """Returns the disk device id."""
        return self.__device_id

    def get_physical_block_size(self) -> int:
        """Returns the physical block size of the disk in bytes."""
        return self.__physical_block_size

    def get_logical_block_size(self) -> int:
        """Returns the logical block size of the disk in bytes."""
        return self.__logical_block_size

    def get_partition_table_type(self) -> str:
        """Returns the type of the partition table on the disk."""
        return self.__part_table_type

    def get_partition_table_uuid(self) -> str:
        """Returns the UUID of the partition table on the disk."""
        return self.__part_table_uuid

    def get_temperature(self) -> float:
        """Returns the disk temperature. Important notes about using this function:

            - This function relies on Linux kernel HWMON system, and the required functionality is available
              from Linux kernel version ``5.6``.
            - NVME disks do not require to load any kernel driver (this is a built-in functionality).
            - SATA SSDs and HDDs require to load ``drivetemp`` kernel module! Without this the HWMON system
              will not provide the temperature information.
            - :py:obj:`RuntimeError` exception will be raised if the HWMON file cannot be found

        Returns:
            float: temperature in C degree

        Raises:
              RuntimeError: HWMON file cannot be found for this disk
        """
        if not self.__hwmon_path:
            raise RuntimeError("HWMON file cannot be found for this disk.")
        return float(int(self._read_file(self.__hwmon_path)) / 1000)

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
            with open(path, "rt", encoding="UTF-8") as file:
                result = file.read()
        except (IOError, FileNotFoundError):
            pass
        return result.strip()

    def _read_udev_property(self, udev_property: str) -> str:
        """Reads a property from udev data file belonging to the disk (/run/udev/data/b?:?).
        It will hide IOError and FileNotFound exceptions during the file operation. The result string
        will be decoded and stripped.

        Args:
            udev_property (str): udev property string

        Returns:
            str: value of the property
        """
        file_content: List[str] = []
        result: str = ""

        # Read proper udev data file.
        try:
            path = "/run/udev/data/b" + self.__device_id
            with open(path, "rt", encoding="unicode_escape") as file:
                file_content = file.read().splitlines()
        except (IOError, FileNotFoundError):
            pass

        # Find the specified udev_property and copy its value.
        for lines in file_content:
            pos = lines.find(udev_property)
            if pos != -1:
                result = lines[pos+len(udev_property):]

        return result.strip()

    def _read_udev_path(self, byid: bool) -> List[str]:
        """Reads one or more path elements from udev data file belonging to the disk (/run/udev/data/b?:?).
        It will hide any IO exception during the file operation.

        Args:
            byid (bool):
                True: `by-id` path elements will be loaded
                False: `by-path` path elements will be loaded
        Returns:
            List[str]: path elements
        """
        path: str
        file_content: List[str] = []
        result: List[str] = []
        udev_property: str

        # Read proper udev data file.
        try:
            path = "/run/udev/data/b" + self.__device_id
            with open(path, "rt", encoding="UTF-8") as file:
                file_content = file.read().splitlines()
        except (IOError, FileNotFoundError):
            pass

        # Find the specified path elements and collect their value.
        if byid:
            udev_property = "disk/by-id/"
        else:
            udev_property = "disk/by-path/"
        for lines in file_content:
            pos = lines.find(udev_property)
            if pos != -1:
                result.append("/dev/" + lines[pos:].strip())

        return result

    def __gt__(self, other) -> bool:
        """Implementation of '>' operator for Disk class."""
        return bool(self.__name > other.__name)

    def __lt__(self, other) -> bool:
        """Implementation of '<' operator for Disk class."""
        return bool(self.__name < other.__name)

    def __eq__(self, other) -> bool:
        """Implementation of '==' operator for Disk class."""
        return bool(self.__name == other.__name)

    def __repr__(self):
        """String representation of the Disk class."""
        return f"Disk(name={self.__name}, " \
               f"path={self.__path}, " \
               f"byid_path={self.__byid_path}, " \
               f"by_path={self.__bypath_path}, " \
               f"wwn={self.__wwn}, " \
               f"model={self.__model}, " \
               f"serial={self.__serial_number}, " \
               f"firmware={self.__firmware}, " \
               f"type={self.get_type_str()}, " \
               f"size={self.__size}, " \
               f"device_id={self.__device_id}, " \
               f"physical_block_size={self.__physical_block_size}, " \
               f"logical_block_size={self.__logical_block_size}" \
               f"partition_table_type={self.__part_table_type}, " \
               f"partition_table_uuid={self.__part_table_uuid})"

# End.
