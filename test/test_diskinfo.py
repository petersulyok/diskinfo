#
#    Unitest for `diskinfo` module
#    Peter Sulyok (C) 2022.
#
import os
import unittest
from typing import List
from unittest.mock import patch, MagicMock
from test_data import TestData
from diskinfo import DiskType, Disk, DiskInfo


class DiskInfoTest(unittest.TestCase):
    """Unit tests for DiskInfo() class."""

    # Test data: pre-defined disk lists.
    test_disks_list = [
        # Test data for 1 disk.
        [["nvme0n1"], [DiskType.NVME]],
        [["sda"], [DiskType.SSD]],
        [["sda"], [DiskType.HDD]],
        # Test data for 2 disks.
        [["nvme0n1", "sda"], [DiskType.NVME, DiskType.SSD]],
        [["nvme0n1", "sda"], [DiskType.NVME, DiskType.HDD]],
        [["sda", "sdb"], [DiskType.SSD, DiskType.HDD]],
        [["sda", "nvme0n1"], [DiskType.SSD, DiskType.NVME]],
        [["sda", "sdb"], [DiskType.HDD, DiskType.SSD]],
        [["sda", "nvme0n1"], [DiskType.HDD, DiskType.NVME]],
        # Tests data for 3 disks.
        [["nvme0n1", "nvme0n2", "nvme0n3"], [DiskType.NVME, DiskType.NVME, DiskType.NVME]],
        [["nvme0n1", "nvme0n2", "sda"], [DiskType.NVME, DiskType.NVME, DiskType.SSD]],
        [["nvme0n1", "nvme0n2", "sda"], [DiskType.NVME, DiskType.NVME, DiskType.HDD]],
        [["nvme0n1", "sda", "sdb"], [DiskType.NVME, DiskType.SSD, DiskType.HDD]],
        [["nvme0n1", "sda", "sdb"], [DiskType.NVME, DiskType.HDD, DiskType.SSD]],
        [["sda", "sdb", "sdc"], [DiskType.SSD, DiskType.SSD, DiskType.SSD]],
        [["sda", "sdb", "nvme0n1"], [DiskType.SSD, DiskType.SSD, DiskType.NVME]],
        [["sda", "sdb", "sdc"], [DiskType.SSD, DiskType.SSD, DiskType.HDD]],
        [["sda", "nvme0n1", "sdb"], [DiskType.SSD, DiskType.NVME, DiskType.HDD]],
        [["sda", "sdb", "nvme0n1"], [DiskType.SSD, DiskType.HDD, DiskType.NVME]],
        [["sda", "sdb", "sdc"], [DiskType.HDD, DiskType.HDD, DiskType.HDD]],
        [["sda", "sdb", "nvme0n1"], [DiskType.HDD, DiskType.HDD, DiskType.NVME]],
        [["sda", "sdb", "sdc"], [DiskType.HDD, DiskType.HDD, DiskType.SSD]],
        [["sda", "nvme0n1", "sdb"], [DiskType.HDD, DiskType.NVME, DiskType.SSD]],
        [["sda", "sdb", "nvme0n1"], [DiskType.HDD, DiskType.SSD, DiskType.NVME]],
        # Test data for 4 disks.
        [["sda", "sdb", "sdc", "nvme0n1"], [DiskType.HDD, DiskType.SSD, DiskType.SSD, DiskType.NVME]],
        # Test data for 5 disks.
        [["sda", "sdb", "sdc", "nvme0n1", "nvme0n2"],
         [DiskType.HDD, DiskType.SSD, DiskType.SSD, DiskType.NVME, DiskType.NVME]],
        # Test data for 8 disks.
        [["sda", "sdb", "sdc", "nvme0n1", "nvme0n2", "sdd", "nvme0n3", "sde"],
         [DiskType.HDD, DiskType.SSD, DiskType.SSD, DiskType.NVME, DiskType.NVME, DiskType.HDD,
          DiskType.NVME, DiskType.SSD]],
    ]

    def pt_init_p1(self, disk_names: List[str], disk_types: List[int], error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - create TestData class
            - mock os.listdir(), os.path.exists() and builtins.open() functions
            - create DiskInfo() class instance
            - ASSERT: if proper amount disks are discovered
            - delete all instance
        """

        # Mock function for os.listdir().
        def mocked_listdir(path: str):
            return original_listdir(my_td.td_dir + path)

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            return original_exists(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks(disk_names, disk_types)
        original_listdir = os.listdir
        mock_listdir = MagicMock(side_effect=mocked_listdir)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.listdir', mock_listdir), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            di = DiskInfo()
            self.assertEqual(di.get_disk_number(), len(disk_names), error)
            del di
        del my_td

    def test_init(self):
        """Unit test for DiskInfo.__init__()."""

        # Test valid disk list combinations.
        for i, tdl in enumerate(self.test_disks_list):
            self.pt_init_p1(tdl[0], tdl[1], "diskinfo_init " + str(i + 1))

    def pt_gdn_p1(self, disk_names: List[str], disk_types: List[int], error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - create TestData class
            - mock os.listdir(), os.path.exists() and builtins.open() functions
            - create DiskInfo() class instance and call get_disk_number() function
            - ASSERT: if the filtered result is different that  calculated
            - delete all instance
        """

        # Mock function for os.listdir().
        def mocked_listdir(path: str):
            return original_listdir(my_td.td_dir + path)

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            return original_exists(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks(disk_names, disk_types)
        original_listdir = os.listdir
        mock_listdir = MagicMock(side_effect=mocked_listdir)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.listdir', mock_listdir), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            di = DiskInfo()
            count_nvme = disk_types.count(DiskType.NVME)
            count_ssd = disk_types.count(DiskType.SSD)
            count_hdd = disk_types.count(DiskType.HDD)
            self.assertEqual(di.get_disk_number(included={DiskType.NVME, DiskType.SSD, DiskType.HDD}),
                             count_nvme + count_ssd + count_hdd, error)
            self.assertEqual(di.get_disk_number(included={DiskType.NVME}, excluded={DiskType.SSD, DiskType.HDD}),
                             count_nvme, error)
            self.assertEqual(di.get_disk_number(included={DiskType.NVME, DiskType.SSD}, excluded={DiskType.HDD}),
                             count_nvme + count_ssd, error)
            self.assertEqual(di.get_disk_number(included={DiskType.NVME, DiskType.HDD}, excluded={DiskType.SSD}),
                             count_nvme + count_hdd, error)
            self.assertEqual(di.get_disk_number(included={DiskType.SSD}, excluded={DiskType.NVME, DiskType.HDD}),
                             count_ssd, error)
            self.assertEqual(di.get_disk_number(included={DiskType.SSD, DiskType.NVME}, excluded={DiskType.HDD}),
                             count_ssd + count_nvme, error)
            self.assertEqual(di.get_disk_number(included={DiskType.SSD, DiskType.HDD}, excluded={DiskType.NVME}),
                             count_ssd + count_hdd, error)
            self.assertEqual(di.get_disk_number(included={DiskType.HDD}, excluded={DiskType.SSD, DiskType.NVME}),
                             count_hdd, error)
            self.assertEqual(di.get_disk_number(included={DiskType.HDD, DiskType.NVME}, excluded={DiskType.SSD}),
                             count_hdd + count_nvme, error)
            self.assertEqual(di.get_disk_number(included={DiskType.HDD, DiskType.SSD}, excluded={DiskType.NVME}),
                             count_hdd + count_ssd, error)
            # This case will not work: if included list is empty then everything will be included and it will be a
            # conflict with the excluded list.
            # self.assertEqual(di.get_disk_number(excluded={DiskType.NVME, DiskType.SSD, DiskType.HDD}), 0, error)
            del di
        del my_td

    def pt_gdn_n1(self, disk_names: List[str], disk_types: List[int], incl: set, excl: set, error: str) -> None:
        """Primitive negative test function. It contains the following steps:
            - create TestData class
            - mock os.listdir(), os.path.exists() and builtins.open() functions
            - create DiskInfo() class instance and call get_disk_number()
            - ASSERT: if no assertion will be raised in case of invalid included and excluded lists
            - delete all instance
        """

        # Mock function for os.listdir().
        def mocked_listdir(path: str):
            return original_listdir(my_td.td_dir + path)

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            return original_exists(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks(disk_names, disk_types)
        original_listdir = os.listdir
        mock_listdir = MagicMock(side_effect=mocked_listdir)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.listdir', mock_listdir), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            di = DiskInfo()
            with self.assertRaises(Exception) as cm:
                di.get_disk_number(included=incl, excluded=excl)
            self.assertEqual(type(cm.exception), ValueError, error)
            del di
        del my_td

    def test_get_disk_number(self):
        """Unit test for DiskInfo.get_disk_number()"""

        # Test with pre-defined disk lists.
        for i, tdl in enumerate(self.test_disks_list):
            self.pt_gdn_p1(tdl[0], tdl[1], "get_disk_number " + str(i + 1))

        # Test for asserts for invalid filters.
        self.pt_gdn_n1(["sda", "sdb", "nvme0n1"], [DiskType.HDD, DiskType.SSD, DiskType.NVME],
                       {DiskType.HDD}, {DiskType.HDD, DiskType.SSD}, "get_disk_number 30")

    def pt_gdl_p1(self, disk_names: List[str], disk_types: List[int], error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - create TestData class
            - mock os.listdir(), os.path.exists() and builtins.open() functions
            - create DiskInfo() class instance and call det_disk_list() function
            - ASSERT: if length of the filtered result list is different from calculated size
            - delete all instance
        """

        # Mock function for os.listdir().
        def mocked_listdir(path: str):
            return original_listdir(my_td.td_dir + path)

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            return original_exists(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks(disk_names, disk_types)
        original_listdir = os.listdir
        mock_listdir = MagicMock(side_effect=mocked_listdir)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.listdir', mock_listdir), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            di = DiskInfo()
            count_nvme = disk_types.count(DiskType.NVME)
            count_ssd = disk_types.count(DiskType.SSD)
            count_hdd = disk_types.count(DiskType.HDD)
            self.assertEqual(len(di.get_disk_list(included={DiskType.NVME, DiskType.SSD, DiskType.HDD})),
                             count_nvme + count_ssd + count_hdd, error)
            self.assertEqual(len(di.get_disk_list(included={DiskType.NVME}, excluded={DiskType.SSD, DiskType.HDD})),
                             count_nvme, error)
            self.assertEqual(len(di.get_disk_list(included={DiskType.NVME, DiskType.SSD}, excluded={DiskType.HDD})),
                             count_nvme + count_ssd, error)
            self.assertEqual(len(di.get_disk_list(included={DiskType.NVME, DiskType.HDD}, excluded={DiskType.SSD})),
                             count_nvme + count_hdd, error)
            self.assertEqual(len(di.get_disk_list(included={DiskType.SSD}, excluded={DiskType.NVME, DiskType.HDD})),
                             count_ssd, error)
            self.assertEqual(len(di.get_disk_list(included={DiskType.SSD, DiskType.NVME}, excluded={DiskType.HDD})),
                             count_ssd + count_nvme, error)
            self.assertEqual(len(di.get_disk_list(included={DiskType.SSD, DiskType.HDD}, excluded={DiskType.NVME})),
                             count_ssd + count_hdd, error)
            self.assertEqual(len(di.get_disk_list(included={DiskType.HDD}, excluded={DiskType.SSD, DiskType.NVME})),
                             count_hdd, error)
            self.assertEqual(len(di.get_disk_list(included={DiskType.HDD, DiskType.NVME}, excluded={DiskType.SSD})),
                             count_hdd + count_nvme, error)
            self.assertEqual(len(di.get_disk_list(included={DiskType.HDD, DiskType.SSD}, excluded={DiskType.NVME})),
                             count_hdd + count_ssd, error)
            # This case will not work: if included list is empty then everything will be included, and it will be
            # conflicting with the excluded list.
            # self.assertEqual(di.get_disk_list(excluded={DiskType.NVME, DiskType.SSD, DiskType.HDD})), 0, error)
            del di
        del my_td

    def pt_gdl_p2(self, disk_names: List[str], expected_name: List[str], so: bool, ro: bool, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - create TestData class
            - mock os.listdir(), os.path.exists() and builtins.open() functions
            - create DiskInfo() class instance and call get_disk_list()
            - ASSERT: if sorted result list will be different from the expected list.
            - delete all instance
        """

        # Mock function for os.listdir().
        def mocked_listdir(path: str):
            return original_listdir(my_td.td_dir + path)

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            return original_exists(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks(disk_names, [DiskType.SSD] * len(disk_names))
        original_listdir = os.listdir
        mock_listdir = MagicMock(side_effect=mocked_listdir)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.listdir', mock_listdir), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            di = DiskInfo()
            sorted_list = di.get_disk_list(sorting=so, rev_order=ro)
            for index, disk in enumerate(sorted_list):
                self.assertEqual(disk.get_name(), expected_name[index], error)
            del di
        del my_td

    def pt_gdl_n1(self, disk_names: List[str], disk_types: List[int], incl: set, excl: set, error: str) -> None:
        """Primitive negative test function. It contains the following steps:
            - create TestData class
            - mock os.listdir(), os.path.exists() and builtins.open() functions
            - create DiskInfo() class instance and call get_disk_list()
            - ASSERT: if no assertion will be raised in case of invalid filters (included and excluded lists)
            - delete all instance
        """

        # Mock function for os.listdir().
        def mocked_listdir(path: str):
            return original_listdir(my_td.td_dir + path)

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            return original_exists(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks(disk_names, disk_types)
        original_listdir = os.listdir
        mock_listdir = MagicMock(side_effect=mocked_listdir)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.listdir', mock_listdir), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            di = DiskInfo()
            with self.assertRaises(Exception) as cm:
                di.get_disk_list(included=incl, excluded=excl)
            self.assertEqual(type(cm.exception), ValueError, error)
            del di
        del my_td

    def test_get_disk_list(self):
        """Unit test for DiskInfo.get_disk_list()"""

        # Test with pre-defined disk lists.
        for i, tdl in enumerate(self.test_disks_list):
            self.pt_gdl_p1(tdl[0], tdl[1], "get_disk_list " + str(i + 1))

        # Test list sorting.
        self.pt_gdl_p2(["sda", "sdb", "sdc"], ["sda", "sdb", "sdc"], True, False, "get_disk_list 31")
        self.pt_gdl_p2(["sda", "sdb", "sdc"], ["sdc", "sdb", "sda"], True, True, "get_disk_list 32")
        self.pt_gdl_p2(["sdb", "sda", "sdc"], ["sda", "sdb", "sdc"], True, False, "get_disk_list 33")
        self.pt_gdl_p2(["sdb", "sda", "sdc"], ["sdc", "sdb", "sda"], True, True, "get_disk_list 34")
        self.pt_gdl_p2(["sdb", "sda", "sdc", "nvme0n1"], ["nvme0n1", "sda", "sdb", "sdc"], True, False,
                       "get_disk_list 35")
        self.pt_gdl_p2(["sdb", "sda", "sdc", "nvme0n1"], ["sdc", "sdb", "sda", "nvme0n1"], True, True,
                       "get_disk_list 36")

        # Test for asserts in case of invalid filters.
        self.pt_gdl_n1(["sda", "sdb", "nvme0n1"], [DiskType.HDD, DiskType.SSD, DiskType.NVME],
                       {DiskType.HDD}, {DiskType.HDD, DiskType.SSD}, "get_disk_list 37")

    def pt_con_p1(self, disk_names: List[str], disk_types: List[int], error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - create TestData class
            - mock os.listdir(), os.path.exists() and builtins.open() functions
            - create DiskInfo() class instance and call __contains__()
            - ASSERT: if a disk is not found in the identified list of disks
            - delete all instance
        """

        # Mock function for os.listdir().
        def mocked_listdir(path: str):
            return original_listdir(my_td.td_dir + path)

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            return original_exists(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks(disk_names, disk_types)
        original_listdir = os.listdir
        mock_listdir = MagicMock(side_effect=mocked_listdir)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.listdir', mock_listdir), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            di = DiskInfo()
            for name in disk_names:
                disk = Disk(name)
                self.assertTrue(disk in di, error)
            unknown_disk = Disk.__new__(Disk)
            unknown_disk._Disk__serial_number = my_td._get_random_alphanum_str(8)
            self.assertFalse(unknown_disk in di, error)
            del di
        del my_td

    def test_contains(self):
        """Unit test for DiskInfo.__contains__()"""

        # Test with pre-defined disk lists.
        for i, tdl in enumerate(self.test_disks_list):
            self.pt_con_p1(tdl[0], tdl[1], "contains " + str(i + 1))

    def test_rep(self):
        """Unit test for __repr__ function of DiskInfo class."""

        # Mock function for os.listdir().
        def mocked_listdir(path: str):
            return original_listdir(my_td.td_dir + path)

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            return original_exists(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks(["sda", "sdb"], [DiskType.SSD, DiskType.HDD])
        original_listdir = os.listdir
        mock_listdir = MagicMock(side_effect=mocked_listdir)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.listdir', mock_listdir), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            di = DiskInfo()
            self.assertEqual(di.get_disk_number(), 2, "diskinfo repr 1")
            disk_list = di.get_disk_list()
            self.assertTrue(repr(disk_list[0]) in repr(di), "diskinfo repr 2")
            self.assertTrue(repr(disk_list[1]) in repr(di), "diskinfo repr 3")
            del di
        del my_td


if __name__ == "__main__":
    unittest.main()
