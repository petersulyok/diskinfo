"""
    Module `disk_info`: implements class `DiskInfo`.
    Copyright (c) 2022 Peter Sulyok.
"""
import os
from typing import List
from disk_info.disk import Disk, DiskType


class DiskInfo:
    """ DisksInfo class implementation."""

    __disk_list: List[Disk]           # List of discovered disks.

    def __init__(self):
        """At class initialization time all existing disks will be discovered in the system. After this,
        the number of identified disk can be queried with method `get_disk_number()` and the list of the identified
        disks can be also queried with method `get_disk_list()`. In both cases disk type filters can be
        applied to query only the subset of the discovered disks."""

        # Initialize class variables.
        self.__disk_list = []

        # Iterate on list of block devices.
        for file_name in os.listdir('/sys/block'):
            new_disk = Disk(disk_name=file_name)
            self.__disk_list.append(new_disk)

    def get_disk_number(self, included: set = None, excluded: set = None) -> int:
        """Returns the number of the disks. The caller can specify inclusive and exclusice filters for disk types.
        If no filters are specified then the default behaviour is to include all disk types and to exclude nothing.

        Args:
            included (set): filter set for included disk types
            excluded (set): filter set for excluded disk types
        Returns:
            int: number of the (filtered) disks
        Raises:
            ValueError: if there are common disk types on included and excluded filter sets
        Example:
            A code example about using filters: it counts the number of SSDs excluding NVME disks.

            >>> from disk_info import DiskType, DiskInfo
            >>> di = DiskInfo()
            >>> n = di.get_disk_number(included={DiskType.SSD}, excluded={DiskType.NVME})
            >>> print(f"Number of SSDs: {n}")
            Number of SSDs: 3
        """
        disk_number: int    # Number of disk counted

        # Set default filters if not specified.
        if not included:
            included = {DiskType.HDD, DiskType.SSD, DiskType.NVME}
        if not excluded:
            excluded = set()

        # Check invalid filters.
        if included.intersection(excluded):
            ValueError("Parameter error: same value on included and excluded list.")

        # Count number of disks based on the specified filters.
        disk_number = 0
        for disk in self.__disk_list:
            if disk.get_type().intersection(included) and not disk.get_type().intersection(excluded):
                disk_number += 1

        return disk_number

    def get_disk_list(self, included: set = None, excluded: set = None, sorting: bool = False,
                      rev_order: bool = False) -> List[Disk]:
        """Returns the list of identified disks. The caller can specify inclusive and exclusice filters for disk types.
        If no filters are specified the default behaviour is to include all disk types and to exclude nothing.
        The list can be sorted based on the disk `name` in alphabetical order. Caller can also request sorting
        in reverse order.

        Args:
            included (set): filter set for included disk types
            excluded (set): filter set for excluded disk types
            sorting (bool): disk list will be sorted based on `name` string
            rev_order (bool): sorting in reverse order
        Returns:
            List[Disk]: list of the (filtered) disks
        Raises:
            ValueError: if there are common disk types on included and excluded filter sets
        Example:
            A code example about using filters and sorting: it will list the device path of the sorted list
            of the HDDs:

            >>> from disk_info import DiskType, DiskInfo
            >>> di = DiskInfo()
            >>> disks = di.get_disk_list(included={DiskType.HDD}, sorting=True)
            >>> for d in disks:
            ...     print(d.get_path())
            ...
            /dev/sda
            /dev/sdb
            /dev/sdc
        """
        result: List[Disk] = []

        # Set default filters if not specified.
        if not included:
            included = {DiskType.HDD, DiskType.SSD, DiskType.NVME}
        if not excluded:
            excluded = set()

        # Check invalid filters.
        if included.intersection(excluded):
            ValueError("Parameter error: same value on included and excluded list.")

        # Collect selected disks based on the specified filters.
        for disk in self.__disk_list:
            if disk.get_type().intersection(included) and not disk.get_type().intersection(excluded):
                result.append(disk)

        # Sort the result list if needed.
        if sorting:
            result.sort(reverse=rev_order)

        return result

# End
