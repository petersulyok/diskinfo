#
#    Module `disk`: implements classes `DiskType` and `Disk`.
#    Peter Sulyok (C) 2022.
#
import glob
import os
import re
import subprocess
from typing import List, Tuple
from diskinfo.disktype import DiskType
from diskinfo.disksmart import DiskSmartData, SmartAttribute, NvmeAttributes


class Disk:
    """The class can be initialized with specifying one of the five unique identifiers of the disk:

        * a disk name (e.g. `sda` or `nvme0n1`) located in `/dev/` directory.
        * a disk serial number (e.g. `"92837A469FF876"`)
        * a disk `wwn identifier <https://en.wikipedia.org/wiki/World_Wide_Name>`_ (e.g. `"0x5002638c807270be"`)
        * a `by-id` name of the disk (e.g. `ata-Samsung_SSD_850_PRO_1TB_92837A469FF876`) located in `/dev/disk/by-id/`
          directory
        * a `by-path` name of the disk (e.g. `pci-0000:00:17.0-ata-3`) located in `/dev/disk/by-path/`  directory

    Based on the specified input parameter the disk will be indentified and its attributes will be collected and
    saved. :py:obj:`ValueError` exception will be raised in case of missing or invalid disk identifier.

    During the class initialization the disk will not be directly accessed, so its power state will not change
    (e.g. it will not be awakened from a `STANDBY` state).

    Operators (``<``, ``>`` and ``==``) are also implemented for this class to compare different class instances,
    they use the disk name for comparision.

    Args:
        disk_name (str): the disk name
        serial_number (str): serial number of the disk
        wwn (str): wwn identifier of the disk
        byid_name (str): by-id name of the disk
        bypath_name (str): by-path name of the disk

    Raises:
        ValueError: in case of missing or invalid parameters
        RuntimeError: in case of any system error

    Example:
        This exampe shows how to create a :class:`~diskinfo.Disk` class then how to get its path and serial number::

            >>> from diskinfo import Disk
            >>> d = Disk("sda")
            >>> d.get_path()
            '/dev/sda'
            >>> d.get_serial_number()
            'S3D2NY0J819210S'

        and these are the additional ways how the :class:`~diskinfo.Disk` class can be initialized::

            >>> d=Disk(serial_number="92837A469FF876")
            >>> d.get_name()
            'sdc'
            >>> d=Disk(wwn="0x5002539c417223be")
            >>> d.get_name()
            'sdc'
            >>> d=Disk(byid_name="ata-Samsung_SSD_850_PRO_1TB_92837A469FF876")
            >>> d.get_name()
            'sdc'
            >>> d=Disk(bypath_name="pci-0000:00:17.0-ata-3")
            >>> d.get_name()
            'sdc'

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

    def __init__(self, disk_name: str = None, serial_number: str = None, wwn: str = None,
                 byid_name: str = None, bypath_name: str = None,) -> None:
        """See class definition docstring above."""

        # Initialize with a disk name.
        if disk_name:
            self.__name = disk_name
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
                raise ValueError(f"Invalid serial number ({ serial_number })!")
            self.__name = name
        # Initialize with a disk WWN name.
        elif wwn:
            name = ""
            for file in os.listdir("/sys/block/"):
                self.__device_id = self._read_file("/sys/block/" + file + "/dev")
                self.__wwn = self._read_udev_property("ID_WWN=")
                if wwn in self.__wwn:
                    name = file
                    break
            if name == "":
                raise ValueError(f"Invalid wwn identifier ({ wwn })!")
            self.__name = name
        # Initialize with a disk `by-id` name.
        elif byid_name:
            self.__name = os.path.basename(os.readlink("/dev/disk/by-id/" + byid_name))
        # Initialize with a disk `by-path` name.
        elif bypath_name:
            self.__name = os.path.basename(os.readlink("/dev/disk/by-path/" + bypath_name))
        # If none of them was specified.
        else:
            raise ValueError("Missing disk identifier, Disk() class cannot be initialized.")

        # Check the existence of disk name in /dev and /sys/block folders.
        self.__path = "/dev/" + self.__name
        if not os.path.exists(self.__path):
            raise ValueError(f"Disk path ({ self.__path }) does not exist!")
        path = "/sys/block/" + self.__name
        if not os.path.exists(path):
            raise ValueError(f"Disk path ({ self.__path }) does not exist!")

        # Determine disk type (HDD, SSD, NVME)
        path = "/sys/block/" + self.__name + "/queue/rotational"
        result = self._read_file(path)
        if result == "1":
            self.__type = DiskType.HDD
        elif result == "0":
            self.__type = DiskType.SSD
        else:
            raise RuntimeError(f"Disk type cannot be determined based on this value ({ path }={ result }).")
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
                raise RuntimeError(f"Disk by-id path ({ file_name }) does not exist!")

        # Read `/dev/disk/by-path/` path elements from udev and check their existence.
        self.__bypath_path = self._read_udev_path(False)
        for file_name in self.__bypath_path:
            if not os.path.exists(file_name):
                raise RuntimeError(f"Disk by-path path ({ file_name }) does not exist!")

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
        """Returns the disk name.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk(serial_number="92837A469FF876")
                >>> d.get_name()
                'sdc'

        """
        return self.__name

    def get_path(self) -> str:
        """Returns the disk path.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk(serial_number="92837A469FF876")
                >>> d.get_path()
                '/dev/sdc'

        .. note::

            Please note this path is not persistent (i.e. it may refer different physical disk after a reboot).

        """
        return self.__path

    def get_byid_path(self) -> List[str]:
        """Returns disk path in a persistent ``/dev/disk/by-byid/...`` form.
        The result could be one or more path elements in a list.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.get_byid_path()
                ['/dev/disk/by-id/ata-Samsung_SSD_850_PRO_1TB_92837A469FF876', '/dev/disk/by-id/wwn-0x5002539c417223be']

        """
        return self.__byid_path

    def get_bypath_path(self) -> List[str]:
        """Returns disk path in a persistent ``/dev/disk/by-path/...`` form.
        The result could be one or more path elements in a list.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.get_bypath_path()
                ['/dev/disk/by-path/pci-0000:00:17.0-ata-3', '/dev/disk/by-path/pci-0000:00:17.0-ata-3.0']

        """
        return self.__bypath_path

    def get_wwn(self) -> str:
        """Returns the world-wide name (WWN) of the disk. Read more about
        `WWN here <https://en.wikipedia.org/wiki/World_Wide_Name>`_.

        .. note::
            This is a unique and persistent identifier of
            the disk.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.get_wwn()
                '0x5002539c417223be'

        """
        return self.__wwn

    def get_model(self) -> str:
        """Returns the disk model string.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.get_model()
                'Samsung SSD 850 PRO 1TB'

        """
        return self.__model

    def get_serial_number(self) -> str:
        """Returns the disk serial number .

        .. note::
            This is a unique and persistent identifier of
            the disk.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.get_serial_number()
                '92837A469FF876'

        """
        return self.__serial_number

    def get_firmware(self) -> str:
        """Returns the disk firmware string.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.get_firmware()
                'EXM04B6Q'

        """
        return self.__firmware

    def get_type(self) -> int:
        """Returns the type of the disk. One of the constants in :class:`~diskinfo.DiskType` class:

            - ``DiskType.HDD`` for hard disks (with spinning platters)
            - ``DiskType.SSD`` for SDDs on SATA or USB interface
            - ``DiskType.NVME`` for NVME disks

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.get_type()
                2

        """
        return self.__type

    def is_ssd(self) -> bool:
        """Returns `True` if the disk type is SSD, otherwise `False`.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.is_ssd()
                True

        """
        return bool(self.__type == DiskType.SSD)

    def is_nvme(self) -> bool:
        """Returns `True` if the disk type is NVME, otherwise `False`.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.is_nvme()
                False

        """
        return bool(self.__type == DiskType.NVME)

    def is_hdd(self) -> bool:
        """Returns `True` if the disk type is HDD, otherwise `False`.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.is_hdd()
                False

        """
        return bool(self.__type == DiskType.HDD)

    def get_type_str(self) -> str:
        """Returns the name of the disk type. See the return values in :class:`~diskinfo.DiskType` class:

            - ``DiskType.HDD_STR`` for hard disks (with spinning platters)
            - ``DiskType.SSD_STR`` for SDDs on SATA or USB interface
            - ``DiskType.NVME_STR`` for NVME disks

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> d.get_type_str()
                'SSD'

        """
        if self.is_nvme():
            return DiskType.NVME_STR
        if self.is_ssd():
            return DiskType.SSD_STR
        return DiskType.HDD_STR

    def get_size(self) -> int:
        """Returns the size of the disk in 512-byte units.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d=Disk("sdc")
                >>> s = d.get_size()
                >>> print(f"Disk size: { s * 512 } bytes.")
                Disk size: 1024209543168 bytes.

        """
        return self.__size

    def get_size_in_hrf(self, units: int = 0) -> Tuple[float, str]:
        """Returns the size of the disk in a human-readable form.

        Args:
            units (int): unit system will be used in result:

                            - 0 metric units (default)
                            - 1 IEC units
                            - 2 legacy units

                         Read more about `units here <https://en.wikipedia.org/wiki/Byte>`_.

        Returns:
            Tuple[float, str]: size of the disk, proper unit

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> s, u = d.get_size_in_hrf()
                >>> print(f"{s:.1f} {u}")
                1.0 TB

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
        """Returns the disk device id in `'major:minor'` form.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.get_device_id()
                '8:32'

        """
        return self.__device_id

    def get_physical_block_size(self) -> int:
        """Returns the physical block size of the disk in bytes. Typically, it is 512 bytes for SSDs and NVMEs, and
        it could be 4096 bytes for HDDs.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.get_physical_block_size()
                512

        """
        return self.__physical_block_size

    def get_logical_block_size(self) -> int:
        """Returns the logical block size of the disk in bytes. Typically, it is 512 bytes.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.get_logical_block_size()
                512

        """
        return self.__logical_block_size

    def get_partition_table_type(self) -> str:
        """Returns the type of the partition table on the disk. It could be 'mbr or 'gpt'.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.get_partition_table_type()
                'gpt'

        """
        return self.__part_table_type

    def get_partition_table_uuid(self) -> str:
        """Returns the UUID of the partition table on the disk.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.get_partition_table_uuid()
                'd3f932e0-7107-455e-a569-9acd5b60d204'

        """
        return self.__part_table_uuid

    def get_temperature(self) -> int:
        """Returns the current disk temperature. Important notes about using this function:

            - This function relies on Linux kernel HWMON system, and the required functionality is available
              from Linux kernel version ``5.6``.
            - NVME disks do not require to load any kernel driver (this is a built-in functionality).
            - SATA SSDs and HDDs require to load ``drivetemp`` kernel module! Without this the HWMON system
              will not provide the temperature information.
            - :py:obj:`RuntimeError` exception will be raised if the HWMON file cannot be found

        .. note::

            This function will not access the disk and will not change its power state.

        Returns:
            float: temperature in C degree

        Raises:
              RuntimeError: if HWMON file cannot be found for this disk

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.get_temperature()
                28

        """
        if not self.__hwmon_path:
            raise RuntimeError("HWMON file cannot be found for this disk.")
        return int(int(self._read_file(self.__hwmon_path)) / 1000)

    def get_smart_data(self, nocheck: bool = False, sudo: str = None, smartctl_path: str = "/usr/sbin/smartctl"):
        """Returns smart data for the disk. This function will execute `smartctl` command from `smartmontools
        <https://www.smartmontools.org/>`_ package, so it has to be installed.

        .. note::

            `smartctl` command needs special access right for reading device smart attributes. This function has
            to be used as `root` user or call with `sudo=` parameter.

            In case of HDDs, the `smartctl` command will access the disk directly and the HDD can wake up. If
            the `nocheck=True` parameter is used then the disk will preserve its current power state.

        Args:
            nocheck (bool):  No check should be applied for a HDDs (`"-n standby"` argument will be used)
            sudo (str): sudo command should be used. Valid value is the full path for sudo command (e.g.
             `"/usr/bin/sudo"`), default is `None`
            smartctl_path (str): Path for `smartctl` command, default value is `/usr/sbin/smartctl`

        Returns:
            DiskSmartData: SMART information of the disk (see more details at
            :class:`~diskinfo.DiskSmartData` class)

        Raises:
            FileNotFoundError: if `smartctl` command cannot be found
            ValueError: if invalid parameters passed to `smartctl` command
            RuntimeError: in case of parsing errors of `smartctl` output

        Example:

        """
        result: subprocess.CompletedProcess     # result of the executed process
        arguments: List[str] = []               # argument list for execution of `smartctl` command

        # If sudo command should be used.
        if sudo:
            arguments.append(sudo)

        # Path for `smartctl`
        arguments.append(smartctl_path)

        # If no check should be applied in standby power mode of an HDD
        if nocheck:
            arguments.append("-n")
            arguments.append("standby")

        # The standards arguments.
        arguments.append("-H")
        arguments.append("-A")
        arguments.append(self.__path)

        # Execute `smartctl` command.
        try:
            result = subprocess.run(arguments, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except (FileNotFoundError, ValueError) as e:
            raise e

        value = DiskSmartData()
        value.raw_output = result.stdout
        value.return_code = result.returncode
        value.standby_mode = False

        output_lines = str(result.stdout).splitlines()
        # Remove first three lines (copyright and an empty line), e.g.:
        # smartctl 7.2 2020-12-30 r5155 [x86_64-linux-5.10.0-14-amd64] (local build)
        # Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org
        #
        del output_lines[0:3]

        # Processing of normal smart attributes
        if output_lines[0].startswith("==="):

            # Remove next line, e.g.:
            # === START OF SMART DATA SECTION ===
            del output_lines[0]

            # Find overall-health status e.g.:
            # SMART overall-health self-assessment test result: PASSED
            if "PASSED" in output_lines[0]:
                value.healthy = True
            else:
                value.healthy = False

            # Read and store of NVME attributes
            if self.is_nvme():

                # Remove three or more lines, e.g.:
                # SMART overall-health self-assessment test result: PASSED
                #
                # SMART/Health Information (NVMe Log 0x02)
                while not output_lines[0].startswith("Critical Warning"):
                    del output_lines[0]

                # Save all NVME attributes.
                na = NvmeAttributes()
                while output_lines[0]:

                    if "Critical Warning" in output_lines[0]:
                        mo = re.search(r"[\dxX]+$", output_lines[0])
                        if mo:
                            na.critical_warning = int(mo.group(), 16)
                        else:
                            raise RuntimeError(f"Error in processing this line: { output_lines[0] }")
                    if output_lines[0].startswith("Temperature:"):
                        mo = re.search(r"\d+", output_lines[0])
                        if mo:
                            na.temperature = int(mo.group())
                        else:
                            raise RuntimeError(f"Error in processing this line: { output_lines[0] }")
                    if "Data Units Read" in output_lines[0]:
                        mo = re.search(r"[\d,]+", output_lines[0])
                        if mo:
                            na.data_units_read = int(re.sub(",", "", mo.group()))
                        else:
                            raise RuntimeError(f"Error in processing this line: { output_lines[0] }")
                    if "Data Units Written" in output_lines[0]:
                        mo = re.search(r"[\d,]+", output_lines[0])
                        if mo:
                            na.data_units_written = int(re.sub(",", "", mo.group()))
                        else:
                            raise RuntimeError(f"Error in processing this line: { output_lines[0] }")
                    if "Power Cycles" in output_lines[0]:
                        mo = re.search(r"[\d,]+$", output_lines[0])
                        if mo:
                            na.power_cycles = int(re.sub(",", "", mo.group()))
                        else:
                            raise RuntimeError(f"Error in processing this line: { output_lines[0] }")
                    if "Power On Hours" in output_lines[0]:
                        mo = re.search(r"[\d,]+$", output_lines[0])
                        if mo:
                            na.power_on_hours = int(re.sub(",", "", mo.group()))
                        else:
                            raise RuntimeError(f"Error in processing this line: { output_lines[0] }")
                    if "Unsafe Shutdowns" in output_lines[0]:
                        mo = re.search(r"[\d,]+$", output_lines[0])
                        if mo:
                            na.unsafe_shutdowns = int(re.sub(",", "", mo.group()))
                        else:
                            raise RuntimeError(f"Error in processing this line: { output_lines[0] }")
                    if "Media and Data Integrity Errors" in output_lines[0]:
                        mo = re.search(r"[\d,]+$", output_lines[0])
                        if mo:
                            na.media_and_data_integrity_errors = int(re.sub(",", "", mo.group()))
                        else:
                            raise RuntimeError(f"Error in processing this line: { output_lines[0] }")
                    if "Error Information Log Entries" in output_lines[0]:
                        mo = re.search(r"[\d,]+$", output_lines[0])
                        if mo:
                            na.error_information_log_entries = int(re.sub(",", "", mo.group()))
                        else:
                            raise RuntimeError(f"Error in processing this line: { output_lines[0] }")
                    del output_lines[0]
                value.nvme_attributes = na

            # Read and store of SMART attributes of HDDs and SDDs
            else:

                # Remove lines until we reach the header of the SMART attributes, e.g.:
                # SMART overall-health self-assessment test result: PASSED
                #
                # SMART Attributes Data Structure revision number: 1
                # Vendor Specific SMART Attributes with Thresholds:
                # ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
                while not output_lines[0].startswith("ID#"):
                    del output_lines[0]
                del output_lines[0]

                # Save all SMART attributes.
                value.smart_attributes = []
                while output_lines[0]:
                    # Normalize multiple spaces then split the line.
                    split = re.sub(" +", " ", output_lines[0]).split()
                    # Store all ten values of a SMART attribute
                    sa = SmartAttribute()
                    sa.id = int(split[0])
                    sa.attribute_name = split[1]
                    sa.flag = split[2]
                    sa.value = int(split[3])
                    sa.worst = int(split[4])
                    sa.thresh = int(split[5])
                    sa.type = split[6]
                    sa.updated = split[7]
                    sa.when_failed = split[8]
                    sa.raw_value = int(split[9])
                    value.smart_attributes.append(sa)
                    # Remove the actual line.
                    del output_lines[0]

        # Process error messages or standby state.
        else:
            if "STANDBY" in output_lines[0]:
                value.standby_mode = True
            if "Smartctl open device" in output_lines[0]:
                raise RuntimeError(f"Error: { output_lines[0] }")

        return value

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
