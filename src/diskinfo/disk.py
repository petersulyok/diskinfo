#
#    Module `disk`: implements classes `DiskType` and `Disk`.
#    Peter Sulyok (C) 2022-2024.
#
import glob
import os
import re
from typing import List, Tuple, Union
from pySMART import Device, SMARTCTL
from diskinfo.utils import _read_file, _read_udev_property, _read_udev_path, size_in_hrf
from diskinfo.disktype import DiskType
from diskinfo.partition import Partition
from diskinfo.disksmart import DiskSmartData, SmartAttribute, NvmeAttributes


class Disk:
    """The Disk class contains all disk related information. The class can be initialized with specifying one of the
    five unique identifiers of the disk:

        * a disk name (e.g. `sda` or `nvme0n1`) located in `/dev/` directory.
        * a disk serial number (e.g. `"92837A469FF876"`)
        * a disk `wwn identifier <https://en.wikipedia.org/wiki/World_Wide_Name>`_ (e.g. `"0x5002638c807270be"`)
        * a `by-id` name of the disk (e.g. `"ata-Samsung_SSD_850_PRO_1TB_92837A469FF876"`) located in `/dev/disk/by-id/`
          directory
        * a `by-path` name of the disk (e.g. `"pci-0000:00:17.0-ata-3"`) located in `/dev/disk/by-path/`  directory

    Based on the specified input parameter the disk will be identified and its attributes will be collected and
    stored. A :py:obj:`ValueError` exception will be raised in case of missing or invalid disk identifier.
    Encoding parameter will be used for processing disk attribute strings.

    Operators (``<``, ``>`` and ``==``) are also implemented for this class to compare different class instances,
    they use the disk name for comparison.

    .. note::
        During the class initialization the disk will not be physically accessed.

    Args:
        disk_name (str): the disk name
        serial_number (str): serial number of the disk
        wwn (str): wwn identifier of the disk
        byid_name (str): by-id name of the disk
        bypath_name (str): by-path name of the disk
        encoding (str): encoding (default is `utf-8`)

    Raises:
        ValueError: in case of missing or invalid parameters
        RuntimeError: in case of any system error

    Example:
        This example shows how to create a :class:`~diskinfo.Disk` class then how to get its path and serial number::

            >>> from diskinfo import Disk
            >>> d = Disk("sda")
            >>> d.get_path()
            '/dev/sda'
            >>> d.get_serial_number()
            'S3D2NY0J819210S'

        and here are additional ways how the :class:`~diskinfo.Disk` class can be initialized::

            >>> d = Disk(serial_number="92837A469FF876")
            >>> d.get_name()
            'sdc'
            >>> d = Disk(wwn="0x5002539c417223be")
            >>> d.get_name()
            'sdc'
            >>> d = Disk(byid_name="ata-Samsung_SSD_850_PRO_1TB_92837A469FF876")
            >>> d.get_name()
            'sdc'
            >>> d = Disk(bypath_name="pci-0000:00:17.0-ata-3")
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
    __hwmon_path: str                   # Path for the /sys/HWMON temperature file
    __encoding: str                     # Character encoding

    def __init__(self, disk_name: str = None, serial_number: str = None, wwn: str = None,
                 byid_name: str = None, bypath_name: str = None, encoding="utf-8") -> None:
        """See class definition docstring above."""

        # Save encoding.
        self.__encoding = encoding

        # Initialization 1: disk name.
        if disk_name:
            self.__name = disk_name

        # Initialization 2: disk serial number.
        elif serial_number:
            name = ""
            for file in os.listdir("/sys/block/"):
                self.__device_id = _read_file("/sys/block/" + file + "/dev", self.__encoding)
                dev_path = "/run/udev/data/b" + self.__device_id
                self.__serial_number = _read_udev_property(dev_path, "ID_SERIAL_SHORT=", self.__encoding)
                if serial_number == self.__serial_number:
                    name = file
                    break
            if name == "":
                raise ValueError(f"Invalid serial number ({serial_number})!")
            self.__name = name

        # Initialization 3: disk WWN name.
        elif wwn:
            name = ""
            for file in os.listdir("/sys/block/"):
                self.__device_id = _read_file("/sys/block/" + file + "/dev", self.__encoding)
                dev_path = "/run/udev/data/b" + self.__device_id
                self.__wwn = _read_udev_property(dev_path, "ID_WWN=", self.__encoding)
                if wwn in self.__wwn:
                    name = file
                    break
            if name == "":
                raise ValueError(f"Invalid wwn identifier ({wwn})!")
            self.__name = name

        # Initialization 4: disk `by-id` name.
        elif byid_name:
            self.__name = os.path.basename(os.readlink("/dev/disk/by-id/" + byid_name))

        # Initialization 5: disk `by-path` name.
        elif bypath_name:
            self.__name = os.path.basename(os.readlink("/dev/disk/by-path/" + bypath_name))

        # Initialization error (none of them was specified).
        else:
            raise ValueError("Missing disk identifier, Disk() class cannot be initialized.")

        # Check the existence of disk name in /dev and /sys/block folders.
        self.__path = "/dev/" + self.__name
        if not os.path.exists(self.__path):
            raise ValueError(f"Disk path ({self.__path}) does not exist!")
        path = "/sys/block/" + self.__name
        if not os.path.exists(path):
            raise ValueError(f"Disk path ({self.__path}) does not exist!")

        # Read disk attributes from /sys filesystem.
        self.__size = int(_read_file("/sys/block/" + self.__name + "/size", self.__encoding))
        self.__model = _read_file("/sys/block/" + self.__name + "/device/model", self.__encoding)
        self.__device_id = _read_file("/sys/block/" + self.__name + "/dev", self.__encoding)
        self.__physical_block_size = int(_read_file("/sys/block/" + self.__name + "/queue/physical_block_size",
                                                    self.__encoding))
        self.__logical_block_size = int(_read_file("/sys/block/" + self.__name + "/queue/logical_block_size",
                                                   self.__encoding))

        # Determination of the disk type (HDD, SSD, NVME or LOOP)
        # Type: LOOP
        if re.match(r'^7:', self.__device_id):
            self.__type = DiskType.LOOP

        # Type: NVME
        elif "nvme" in self.__name:
            self.__type = DiskType.NVME

        # Type: SSD or HDD
        else:
            path = "/sys/block/" + self.__name + "/queue/rotational"
            result = _read_file(path, self.__encoding)
            if result == "1":
                self.__type = DiskType.HDD
            elif result == "0":
                self.__type = DiskType.SSD
            else:
                raise RuntimeError(f"Disk type cannot be determined based on this value ({path}={result}).")

        # Read attributes from udev data.
        dev_path = "/run/udev/data/b" + self.__device_id
        self.__serial_number = _read_udev_property(dev_path, "ID_SERIAL_SHORT=", self.__encoding)
        self.__firmware = _read_udev_property(dev_path, "ID_REVISION=", self.__encoding)
        self.__wwn = _read_udev_property(dev_path, "ID_WWN=", self.__encoding)
        self.__part_table_type = _read_udev_property(dev_path, "ID_PART_TABLE_TYPE=", self.__encoding)
        self.__part_table_uuid = _read_udev_property(dev_path, "ID_PART_TABLE_UUID=", self.__encoding)
        model = _read_udev_property(dev_path, "ID_MODEL_ENC=", self.__encoding)
        if model:
            self.__model = model

        # Read `/dev/disk/by-byid/` path elements from udev and check their existence.
        self.__byid_path = _read_udev_path(dev_path, 0, self.__encoding)
        for file_name in self.__byid_path:
            if not os.path.exists(file_name):
                raise RuntimeError(f"Disk by-id path ({file_name}) does not exist!")

        # Read `/dev/disk/by-path/` path elements from udev and check their existence.
        self.__bypath_path = _read_udev_path(dev_path, 1, self.__encoding)
        for file_name in self.__bypath_path:
            if not os.path.exists(file_name):
                raise RuntimeError(f"Disk by-path path ({file_name}) does not exist!")

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
                >>> d = Disk(serial_number="92837A469FF876")
                >>> d.get_name()
                'sdc'

        """
        return self.__name

    def get_path(self) -> str:
        """Returns the disk path.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk(serial_number="92837A469FF876")
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
                >>> d = Disk("sdc")
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
                >>> d = Disk("sdc")
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
                >>> d = Disk("sdc")
                >>> d.get_wwn()
                '0x5002539c417223be'

        """
        return self.__wwn

    def get_model(self) -> str:
        """Returns the disk model string.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
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
                >>> d = Disk("sdc")
                >>> d.get_serial_number()
                '92837A469FF876'

        """
        return self.__serial_number

    def get_firmware(self) -> str:
        """Returns the disk firmware string.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.get_firmware()
                'EXM04B6Q'

        """
        return self.__firmware

    def get_type(self) -> int:
        """Returns the type of the disk. One of the constants in :class:`~diskinfo.DiskType` class:

            - ``DiskType.HDD`` for hard disks (with spinning platters)
            - ``DiskType.SSD`` for SDDs on SATA or USB interface
            - ``DiskType.NVME`` for NVME disks
            - ``DiskType.LOOP`` for LOOP disks

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.get_type()
                2

        """
        return self.__type

    def is_ssd(self) -> bool:
        """Returns `True` if the disk type is SSD, otherwise `False`.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.is_ssd()
                True

        """
        return bool(self.__type == DiskType.SSD)

    def is_nvme(self) -> bool:
        """Returns `True` if the disk type is NVME, otherwise `False`.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.is_nvme()
                False

        """
        return bool(self.__type == DiskType.NVME)

    def is_hdd(self) -> bool:
        """Returns `True` if the disk type is HDD, otherwise `False`.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.is_hdd()
                False

        """
        return bool(self.__type == DiskType.HDD)

    def is_loop(self) -> bool:
        """Returns `True` if the disk type is LOOP, otherwise `False`.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("loop0")
                >>> d.is_loop()
                True

        """
        return bool(self.__type == DiskType.LOOP)

    def get_type_str(self) -> str:
        """Returns the name of the disk type. See the return values in :class:`~diskinfo.DiskType` class:

            - ``DiskType.HDD_STR`` for hard disks (with spinning platters)
            - ``DiskType.SSD_STR`` for SDDs on SATA or USB interface
            - ``DiskType.NVME_STR`` for NVME disks
            - ``DiskType.LOOP_STR`` for LOOP disks

        Raises:
            RuntimeError: in case of unknown disk type.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.get_type_str()
                'SSD'

        """
        if self.is_nvme():
            return DiskType.NVME_STR
        if self.is_ssd():
            return DiskType.SSD_STR
        if self.is_hdd():
            return DiskType.HDD_STR
        if self.is_loop():
            return DiskType.LOOP_STR
        raise RuntimeError(f'Unknown disk type (type={self.__type})')

    def get_size(self) -> int:
        """Returns the size of the disk in 512-byte units.

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
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
                >>> s,u = d.get_size_in_hrf()
                >>> print(f"{s:.1f} {u}")
                1.0 TB

        """
        return size_in_hrf(self.__size * 512, units)

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
        """Returns the type of the partition table on the disk (e.g. `mbr` or `gpt`).

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

    def get_temperature(self, sudo: bool = False, smartctl_path: str = "/usr/sbin/smartctl") -> Union[float, None]:
        """Returns the current disk temperature. The method will try to read disk temperature from the Linux kernel
        HWMON interface first then will try to execure the `smartctl` command. The method has the following
        requirements:

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

        .. note::
            Please note that reading disk temperature from HWMON kernel interface will not access the disk and
            will not change its power state (e.g. HDD can be in STANDBY state) but reading disk temperature with
            `smartctl` will do.

        Args:
            sudo (bool): ``sudo`` command should be used for ``smartctl``, default value is ``False``
            smartctl_path (str): Path for ``smartctl`` command, default value is ``/usr/sbin/smartctl``

        Returns:
            float: disk temperature in C degree or None if the temperature cannot be determined

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk
                >>> d = Disk("sdc")
                >>> d.get_temperature(sudo=True)
                28.5

        """
        temp:   float
        sd:     Device

        # Read disk temperature from HWMON system of the Linux kernel.
        if hasattr(self, '_Disk__hwmon_path') and \
           self.__hwmon_path and \
           os.path.exists(self.__hwmon_path):
            try:
                return float(_read_file(self.__hwmon_path, self.__encoding)) / 1000.0
            except ValueError:
                pass

        # Read disk temperature from `smartctl` command.
        SMARTCTL.options = []
        SMARTCTL.smartctl_path = smartctl_path
        if sudo:
            SMARTCTL.sudo = True
        else:
            SMARTCTL.sudo = False
        sd = Device(self.__path)
        temp = sd.temperature
        if not temp:
            return None
        return float(temp)

    def get_smart_data(self, nocheck: bool = False, sudo: bool = False, smartctl_path: str = "/usr/sbin/smartctl") \
            -> Union[DiskSmartData, None]:
        """Returns SMART data of the disk. This function will execute ``smartctl`` command from `smartmontools
        <https://www.smartmontools.org/>`_ package, it needs to be installed.

        .. note::

            ``smartctl`` command needs root priviledge for reading device SMART attributes. This function has
            to be used as `root` user or called with ``sudo=True`` parameter.

            In case of HDDs, the ``smartctl`` command will access the disk directly and the HDD could be woken up. If
            the ``nocheck=True`` parameter is used then the current power state of the disk will be preserved.

        Args:
            nocheck (bool):  No check should be applied for a HDDs (``"-n standby"`` argument will be used)
            sudo (bool): ``sudo`` command should be used, default value is ``False``
            smartctl_path (str): Path for ``smartctl`` command, default value is ``/usr/sbin/smartctl``

        Returns:
            DiskSmartData: SMART information of the disk (see more details at
            :class:`~diskinfo.DiskSmartData` class) or None if `smartctl` cannot be executed

        Example:
            The example show the use of the function::

                >>> from diskinfo import Disk, DiskSmartData
                >>> d = Disk("sda")
                >>> d = d.get_smart_data()

            In case of SSDs and HDDs the traditional SMART attributes can be accessed via
            :attr:`~diskinfo.DiskSmartData.smart_attributes` list::

                >>> for item in d.smart_attributes:
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

            In case of NVME disks they have their own SMART data in :attr:`~diskinfo.DiskSmartData.nvme_attributes`
            field::

                >>> if d.is_nvme():
                ...     print(f"Power on hours: {d.nvme_attributes.power_on_hours} h")
                ...
                Power on hours: 1565 h

        """
        sd: Device          # Device class created by pySMART
        rv: DiskSmartData   # return value

        # Ignore loop disks.
        if self.is_loop():
            return None

        rv = DiskSmartData()
        rv.standby_mode = False
        SMARTCTL.options = []
        SMARTCTL.smartctl_path = smartctl_path

        # If sudo command should be used
        if sudo:
            SMARTCTL.sudo = True
        else:
            SMARTCTL.sudo = False

        # If no check should be applied in standby power mode of an HDD
        if nocheck:
            SMARTCTL.add_options(["-n", "standby"])

        # Check if `smartctl` can be executed.
        output = SMARTCTL.info(self.__path)
        if not output:
            return None

        # Check if the disk is in STANDBY mode
        if "Device is in STANDBY mode" in output[3]:
            rv.standby_mode = True
            return rv

        # Get SMART data from pySMART.
        sd = Device(self.__path)

        # Check if the device interface was not identified (i.e. unknown device).
        if not sd.interface:
            return None

        # Save SMART flags.
        rv.smart_enabled = sd.smart_enabled
        rv.smart_capable = sd.smart_capable

        # Find overall-health status
        if sd.assessment == "PASS":
            rv.healthy = True
        else:
            rv.healthy = False

        # Read and store of NVME attributes
        if self.is_nvme():
            if hasattr(sd, "if_attributes"):
                rv.nvme_attributes = NvmeAttributes(
                    sd.if_attributes.criticalWarning
                    if hasattr(sd.if_attributes, "criticalWarning") else None,
                    sd.if_attributes._temperature
                    if hasattr(sd.if_attributes, "_temperature") else None,
                    sd.if_attributes.availableSpare
                    if hasattr(sd.if_attributes, "availableSpare") else None,
                    sd.if_attributes.availableSpareThreshold
                    if hasattr(sd.if_attributes, "availableSpareThreshold") else None,
                    sd.if_attributes.percentageUsed
                    if hasattr(sd.if_attributes, "percentageUsed") else None,
                    sd.if_attributes.dataUnitsRead
                    if hasattr(sd.if_attributes, "dataUnitsRead") else None,
                    sd.if_attributes.dataUnitsWritten
                    if hasattr(sd.if_attributes, "dataUnitsWritten") else None,
                    sd.if_attributes.hostReadCommands
                    if hasattr(sd.if_attributes, "hostReadCommands") else None,
                    sd.if_attributes.hostWriteCommands
                    if hasattr(sd.if_attributes, "hostWriteCommands") else None,
                    sd.if_attributes.controllerBusyTime
                    if hasattr(sd.if_attributes, "controllerBusyTime") else None,
                    sd.if_attributes.powerCycles
                    if hasattr(sd.if_attributes, "powerCycles") else None,
                    sd.if_attributes.powerOnHours
                    if hasattr(sd.if_attributes, "powerOnHours") else None,
                    sd.if_attributes.unsafeShutdowns
                    if hasattr(sd.if_attributes, "unsafeShutdowns") else None,
                    sd.if_attributes.integrityErrors
                    if hasattr(sd.if_attributes, "integrityErrors") else None,
                    sd.if_attributes.errorEntries
                    if hasattr(sd.if_attributes, "errorEntries") else None,
                    sd.if_attributes.warningTemperatureTime
                    if hasattr(sd.if_attributes, "warningTemperatureTime") else None,
                    sd.if_attributes.criticalTemperatureTime
                    if hasattr(sd.if_attributes, "criticalTemperatureTime") else None
                )

        # Read and save SATA attributes
        else:
            if hasattr(sd, "if_attributes") and hasattr(sd.if_attributes, "legacyAttributes"):
                rv.smart_attributes = []
                for i in sd.if_attributes.legacyAttributes:
                    if i:
                        rv.smart_attributes.append(SmartAttribute(
                            i.num, i.name, i.flags, i.value_int, i.worst, i.thresh, i.type, i.updated,
                            i.when_failed, i.raw_int)
                        )

        return rv

    def get_partition_list(self) -> List[Partition]:
        """Reads partition information of the disk and returns the list of partitions. See
        :class:`~diskinfo.Partition` class for more details for a partition entry.

        Returns:
            List[Partition]: list of partitions

        Example:
            >>> from diskinfo import *
            >>> disk=Disk("nvme0n1")
            >>> plist=disk.get_partition_list()
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
        result: List[Partition] = []
        index = 1
        while True:
            path = "/sys/block/" + self.__name + "/" + self.__name
            if self.is_nvme():
                path += "p"
            path += str(index)
            if not os.path.exists(path):
                break   # If partition path dos not exists.
            result.append(Partition(os.path.basename(path), _read_file(path + "/dev", self.__encoding)))
            index += 1
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
        return (f"Disk(name={self.__name}, "
                f"path={self.__path}, "
                f"byid_path={self.__byid_path}, "
                f"by_path={self.__bypath_path}, "
                f"wwn={self.__wwn}, "
                f"model={self.__model}, "
                f"serial={self.__serial_number}, "
                f"firmware={self.__firmware}, "
                f"type={self.get_type_str()}, "
                f"size={self.__size}, "
                f"device_id={self.__device_id}, "
                f"physical_block_size={self.__physical_block_size}, "
                f"logical_block_size={self.__logical_block_size}, "
                f"partition_table_type={self.__part_table_type}, "
                f"partition_table_uuid={self.__part_table_uuid})")

# End.
