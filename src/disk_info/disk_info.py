"""

    disk_info.py (C) 2022, Peter Sulyok
    Disk information Python Package for Linux.

"""
import os
from typing import List
from disk_info.disk import Disk, DiskType


class DiskInfo:
    """ Disks class implementation."""
    __disks: int                      # Number of disks
    __disk_list: List[Disk]           # List of Disk() instances

    def __init__(self):

        # Initialize class variables.
        self.__disks = 0
        self.__disk_list = []

        # Iterate on list of block devices.
        for f in os.listdir('/sys/block'):
            new_disk = Disk(disk_name=f)
            self.__disk_list.append(new_disk)
            self.__disks += 1
        return

    def get_disk_number(self, included: set = None, excluded: set = None) -> int:
        number: int = 0

        if not included:
            included = {DiskType.HDD, DiskType.SSD, DiskType.NVME}
        if not excluded:
            excluded = set()

        if included.intersection(excluded):
            ValueError("Parameter error: same value on included and excluded list.")

        for d in self.__disk_list:
            if d.get_type().intersection(included) and not d.get_type().intersection(excluded):
                number += 1
        return number

    def get_disk_list(self, included: set = None, excluded: set = None, sorted: bool = False, rev_order: bool = False) -> List[Disk]:

        result: List[Disk] = []

        if not included:
            included = {DiskType.HDD, DiskType.SSD, DiskType.NVME}
        if not excluded:
            excluded = set()

        if included.intersection(excluded):
            ValueError("Parameter error: same value on included and excluded list.")

        for i, d in enumerate(self.__disk_list):
            if d.get_type().intersection(included) and not d.get_type().intersection(excluded):
                result.append(d)

        if sorted:
            result.sort(reverse = rev_order)

        return result

# End
