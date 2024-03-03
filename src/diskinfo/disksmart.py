#
#    Module `disksmart`: implements classes `DiskSmartData`, SmartAttribute, and NvmeAttributes.
#    Peter Sulyok (C) 2022-2024.
#
from typing import List


class SmartAttribute:
    """This class implements a SMART attribute. It stores ten values from `smartctl` command.

    Example:
        This class presents one line in the following sample output (from a`smartctrl` command)::

            ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
              5 Reallocated_Sector_Ct   0x0033   100   100   010    Pre-fail  Always       -       0
              9 Power_On_Hours          0x0032   095   095   000    Old_age   Always       -       23268
             12 Power_Cycle_Count       0x0032   092   092   000    Old_age   Always       -       7103
            177 Wear_Leveling_Count     0x0013   099   099   000    Pre-fail  Always       -       20
            179 Used_Rsvd_Blk_Cnt_Tot   0x0013   100   100   010    Pre-fail  Always       -       0
            181 Program_Fail_Cnt_Total  0x0032   100   100   010    Old_age   Always       -       0
            182 Erase_Fail_Count_Total  0x0032   100   100   010    Old_age   Always       -       0
            183 Runtime_Bad_Block       0x0013   100   099   010    Pre-fail  Always       -       0
            187 Uncorrectable_Error_Cnt 0x0032   100   100   000    Old_age   Always       -       0
            190 Airflow_Temperature_Cel 0x0032   072   045   000    Old_age   Always       -       28
            195 ECC_Error_Rate          0x001a   200   200   000    Old_age   Always       -       0
            199 CRC_Error_Count         0x003e   100   100   000    Old_age   Always       -       0
            235 POR_Recovery_Count      0x0012   099   099   000    Old_age   Always       -       218
            241 Total_LBAs_Written      0x0032   099   099   000    Old_age   Always       -       51650461687

    """
    id: int
    """ID of the SMART attribute (`1-255`)."""
    attribute_name: str
    """Name of the SMART attribute."""
    flag: int
    """SMART attribute handling flag."""
    value: int
    """Normalized value of SMART attribute (`0-255`). Notes:

            - values `0`, `254`, `255` are reserved for internal use
            - value `253` means not used yet
            - many cases it is starting at `value=100` case then dropping to `value=1`

    """
    worst: int
    """Lowest value of the SMART attribute."""
    thresh: int
    """Lowest value (defined by manufacturer) that ``worst`` is allowed to reach for a SMART attribute."""
    type: str
    """Type of the SMART attribute:

            - `Pre-fail`: the attribute is considered a critical one
            - `Old_age`: the attribute does not fail the disk

    """
    updated: str
    """Indicator when the SMART attribute is updated (values are `Always` or `Offline`)."""
    when_failed: str
    """Usually it is blank, or it contains the last operational hour when this SMART attribute failed."""
    raw_value: int
    """The raw value for the SMART attribute, defined by the manufacturer."""

    def __init__(self, _id: int, attribute_name: str, flag: int, value: int, worst: int, thresh: int, _type: str,
                 updated: str, when_failed: str, raw_value: int):
        """Initialize class properties."""
        self.id = _id
        self.attribute_name = attribute_name
        self.flag = flag
        self.value = value
        self.worst = worst
        self.thresh = thresh
        self.type = _type
        self.updated = updated
        self.when_failed = when_failed
        self.raw_value = raw_value


class NvmeAttributes:
    """This class implements NVME attributes. Read more about NVME attributes:

        - `smartmontools: NVME support <https://www.smartmontools.org/wiki/NVMe_Support>`_
        -  `NVME standard v1.4 (page 121-125)
           <https://nvmexpress.org/wp-content/uploads/NVM-Express-1_4-2019.06.10-Ratified.pdf>`_

    """
    critical_warning: int
    """This attributes indicates critical warnings for the state of the controller."""

    temperature: int
    """Contains the current composite temperature value of the NVME disk."""

    available_spare: int
    """Contains a normalized percentage (0% to 100%) of the remaining spare capacity available."""

    available_spare_threshold: int
    """When the Available Spare falls below the threshold indicated in this field, an asynchronous event
    completion may occur. The value is indicated as a normalized percentage (0% to 100%)."""

    percentage_used: int
    """Contains a vendor specific estimate of the percentage of NVM subsystem life used based on the actual usage
    and the manufacturer’s prediction of NVM life. A value of 100 indicates that the estimated endurance of the
    NVM in the NVM subsystem has been consumed, but may not indicate an NVM subsystem failure."""

    data_units_read: int
    """Contains the number of 512-byte blocks the host has read from the NVME controller. The value reported in
    thousands (i.e. 1 means 1000 units of 512-byte blocks) and rounded up. Value 0 means that this attribute is
    not reported."""

    data_units_written: int
    """Contains the number of 512-byte blocks the host has written to the NVME controller. The value reported in
    thousands (i.e. 1 means 1000 units of 512-byte blocks) and rounded up. Value 0 means that this attribute is
    not reported."""

    host_read_commands: int
    """Contains the number of read commands completed by the controller."""

    host_write_commands: int
    """Contains the number of write commands completed by the controller."""

    controller_busy_time: int
    """Contains the amount of time (in minutes) the controller is busy with I/O commands."""

    power_cycles: int
    """Contains the number of the power cycles."""

    power_on_hours: int
    """Contains the number of power-on hours."""

    unsafe_shutdowns: int
    """Contains the number of unsafe shutdowns."""

    media_and_data_integrity_errors: int
    """Contains the number of occurrences where the controller detected an unrecovered data integrity error."""

    error_information_log_entries: int
    """Contains the number of Error Information log entries over the life of the controller."""

    warning_composite_temperature_time: int
    """Contains the amount of time in minutes that the controller is operational and the Composite Temperature
    is greater than or equal to the Warning Composite Temperature Threshold."""

    critical_composite_temperature_time: int
    """Contains the amount of time in minutes that the controller is operational and the Composite Temperature
    is greater than or equal to the Critical Composite Temperature Threshold."""

    def __init__(self, critical_warning: int, temperature: int, available_spare: int,
                 available_spare_threshold: int, percentage_used: int, data_units_read: int,
                 data_units_written: int, host_read_commands: int, host_write_commands: int,
                 controller_busy_time: int, power_cycles: int, power_on_hours: int,
                 unsafe_shutdowns: int, media_and_data_integrity_errors: int,
                 error_information_log_entries: int, warning_composite_temperature_time: int,
                 critical_composite_temperature_time: int):
        """Initialize class properties."""
        self.critical_warning = critical_warning
        self.temperature = temperature
        self.available_spare = available_spare
        self.available_spare_threshold = available_spare_threshold
        self.percentage_used = percentage_used
        self.data_units_read = data_units_read
        self.data_units_written = data_units_written
        self.host_read_commands = host_read_commands
        self.host_write_commands = host_write_commands
        self.controller_busy_time = controller_busy_time
        self.power_cycles = power_cycles
        self.power_on_hours = power_on_hours
        self.unsafe_shutdowns = unsafe_shutdowns
        self.media_and_data_integrity_errors = media_and_data_integrity_errors
        self.error_information_log_entries = error_information_log_entries
        self.warning_composite_temperature_time = warning_composite_temperature_time
        self.critical_composite_temperature_time = critical_composite_temperature_time


class DiskSmartData:
    """This class presents all collected SMART data for a disk. This class is created by
    :meth:`~diskinfo.Disk.get_smart_data()` method. There are several disk type specific data attributes in this
    class, they are available only for a specific disk type(s).
    """

    smart_enabled: bool
    """SMART is enabled for the disk."""

    smart_capable: bool
    """The disk is SMART capable."""

    healthy: bool
    """The health status of the disk. Valid for all disk types. Meaning:

        - `True`: the disk is reported healthy (i.e. overall-health self-assessment test is PASSED).
        - `False`: the disk is reported failed (i.e. overall-health self-assessment test is FAILED).

    """

    standby_mode: bool
    """Standby flag for disk. Valid only for HDDs:

            - `True` means the disk is in STANDBY state
            - `False` means the disk is ACTIVE or IDLE

    .. warning::
        When an HDD is in STANDBY state (i.e. this flag is `True`) then other SMART attributes will not be updated!
    """

    smart_attributes: List[SmartAttribute]
    """List of the SMART attributes of a disk. Valid only for HDDs and SSDs, in case of NVME disk it will be
    empty. Methods :meth:`~diskinfo.DiskSmartData.find_smart_attribute_by_id()` and
    :meth:`~diskinfo.DiskSmartData.find_smart_attribute_by_name()` will find an item on this list based on an `id`
    or a `name`.
    """

    nvme_attributes: NvmeAttributes
    """NVME attributes for a disk. Valid only for NVME disks. See more details in
    :class:`~diskinfo.NvmeAttributes` class."""

    def find_smart_attribute_by_id(self, id_val: int) -> int:
        """Finds a SMART attribute by the `id` and returns its index in :attr:`~diskinfo.DiskSmartData.smart_attributes`
        list, or -1 if not found.

        Args:
            id_val (int): SMART attribute `id` value

        Returns:
            int: an index of the attribute in :attr:`~diskinfo.DiskSmartData.smart_attributes` list, or -1
            if not found

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk, DiskSmartData
                >>> d = Disk("sda")
                >>> sd = d.get_smart_data(sudo=True)
                >>> sd.find_smart_attribute_by_id(5)
                0

        """
        for index, item in enumerate(self.smart_attributes):
            if item.id == id_val:
                return index
        return -1

    def find_smart_attribute_by_name(self, name_val: str) -> int:
        """Finds an attribute by `name` and return with its index in :attr:`~diskinfo.DiskSmartData.smart_attributes`
        list.

        Args:
            name_val (int): SMART attribute name value

        Returns:
            int:  an index of the attribute in :attr:`~diskinfo.DiskSmartData.smart_attributes` list, or -1
            if not found

        Example:
            An example about the use of this function::

                >>> from diskinfo import Disk, DiskSmartData
                >>> d = Disk("sda")
                >>> sd = d.get_smart_data(sudo=True)
                >>> sd.find_smart_attribute_by_name("Power_On_Hours")
                1

        """
        for index, item in enumerate(self.smart_attributes):
            if name_val in item.attribute_name:
                return index
        return -1

# End
