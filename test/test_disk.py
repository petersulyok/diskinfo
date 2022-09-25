#
#    Unitest for `disk` module
#    Peter Sulyok (C) 2022.
#
import glob
import os
import shutil
import random
import unittest
from unittest.mock import patch, MagicMock
from test_data import TestData
from diskinfo import Disk, DiskType


class DiskTest(unittest.TestCase):
    """Unit tests for Disk() class."""

    def pt_init_p1(self, disk_name: str, disk_type: int, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - create TestData class
            - mock glob.glob(), os.readlink(), os.listdir(), os.path.exists() and builtins.open() functions
            - create Disk() class instance based on test data in all five ways
            - ASSERT: if any attribute of the class is different from the generated test data
            - delete all instance
        """

        # Mock function for glob.glob().
        def mocked_glob(file: str, *args, **kwargs):
            if file.startswith('/sys/block'):
                file = my_td.td_dir + file
            return original_glob(file, *args, **kwargs)

        # Mock function for os.readlink().
        def mocked_readlink(path: str,  *args, **kwargs):
            return original_readlink(my_td.td_dir + path, *args, **kwargs)

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
        my_td.create_disks([disk_name], [disk_type])
        original_glob = glob.glob
        mock_glob = MagicMock(side_effect=mocked_glob)
        original_readlink = os.readlink
        mock_readlink = MagicMock(side_effect=mocked_readlink)
        original_listdir = os.listdir
        mock_listdir = MagicMock(side_effect=mocked_listdir)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('glob.glob', mock_glob), \
             patch('os.readlink', mock_readlink), \
             patch('os.listdir', mock_listdir), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):

            for i in range(5):
                # Disk class creation with disk name
                if i == 0:
                    d = Disk(disk_name)
                # Disk class creation with disk by-id name
                elif i == 1:
                    name = os.path.basename(random.choice(my_td.disks[0].byid_path))
                    d = Disk(byid_name=name)
                # Disk class creation with disk by-path name
                elif i == 2:
                    name = os.path.basename(random.choice(my_td.disks[0].bypath_path))
                    d = Disk(bypath_name=name)
                # Disk class creation with disk serial number
                elif i == 3:
                    name = my_td.disks[0].serial
                    d = Disk(serial_number=name)
                # Disk class creation with disk wwn name
                else:  # if i == 4:
                    name = my_td.disks[0].wwn
                    d = Disk(wwn_name=name)

                # Check all disk attributes.
                self.assertEqual(d.get_name(), my_td.disks[0].name, error)
                self.assertEqual(d.get_path(), my_td.disks[0].path.replace(my_td.td_dir, ""), error)
                self.assertEqual(d.get_serial_number(), my_td.disks[0].serial, error)
                self.assertEqual(d.get_firmware(), my_td.disks[0].firmware, error)
                self.assertEqual(d.get_model(), my_td.disks[0].model, error)
                self.assertEqual(d.get_wwn(), my_td.disks[0].wwn, error)
                self.assertEqual(d.get_size(), my_td.disks[0].size, error)
                self.assertEqual(d.get_device_id(), my_td.disks[0].dev_id, error)
                self.assertEqual(d.get_logical_block_size(), my_td.disks[0].log_bs, error)
                self.assertEqual(d.get_physical_block_size(), my_td.disks[0].phys_bs, error)
                self.assertEqual(d.get_partition_table_type(), my_td.disks[0].part_table_type, error)
                self.assertEqual(d.get_partition_table_uuid(), my_td.disks[0].part_table_uuid, error)
                for index, item in enumerate(d.get_byid_path()):
                    self.assertEqual(item, my_td.disks[0].byid_path[index].replace(my_td.td_dir, ""), error)
                for index, item in enumerate(d.get_bypath_path()):
                    self.assertEqual(item, my_td.disks[0].bypath_path[index].replace(my_td.td_dir, ""), error)
                self.assertEqual(d.get_type(), my_td.disks[0].type, error)
                disk_type = d.get_type()
                if disk_type == DiskType.NVME:
                    self.assertTrue(d.is_nvme(), error)
                    self.assertFalse(d.is_ssd(), error)
                    self.assertFalse(d.is_hdd(), error)
                    self.assertEqual(d.get_type_str(), DiskType.NVME_STR, error)
                elif disk_type == DiskType.SSD:
                    self.assertTrue(d.is_ssd(), error)
                    self.assertFalse(d.is_nvme(), error)
                    self.assertFalse(d.is_hdd(), error)
                    self.assertEqual(d.get_type_str(), DiskType.SSD_STR, error)
                if disk_type == DiskType.HDD:
                    self.assertFalse(d.is_nvme(), error)
                    self.assertFalse(d.is_ssd(), error)
                    self.assertTrue(d.is_hdd(), error)
                    self.assertEqual(d.get_type_str(), DiskType.HDD_STR, error)
                del d
        del my_td

    def pt_init_n1(self, disk_name: str, disk_type: int, error: str) -> None:
        """Primitive negative test function. It contains the following steps:
            - create TestData class
            - mock os.readlink(), os.path.exists() and builtins.open() functions
            - create Disk() class instance based on test data
            - ASSERT: if assert not raised in case of missing system files/folders
            - delete all instance
        """

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            return original_exists(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks([disk_name], [disk_type])
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):

            # Exception 1: missing by-path path
            os.unlink(my_td.disks[0].bypath_path[0])
            with self.assertRaises(Exception) as cm:
                Disk(disk_name)
            self.assertEqual(type(cm.exception), RuntimeError, error)

            # Exception 2: missing by-id path
            os.unlink(my_td.disks[0].byid_path[0])
            with self.assertRaises(Exception) as cm:
                Disk(disk_name)
            self.assertEqual(type(cm.exception), RuntimeError, error)

            # Exception 3: missing file `/sys/block/name/queue/rotational`
            os.remove(my_td.td_dir + "/sys/block/" + my_td.disks[0].name + "/queue/rotational")
            with self.assertRaises(Exception) as cm:
                Disk(disk_name)
            self.assertEqual(type(cm.exception), RuntimeError, error)

            # Exception 3: missing file `/sys/block/name/queue/rotational`
            shutil.rmtree(my_td.td_dir + "/sys/block/" + my_td.disks[0].name)
            with self.assertRaises(Exception) as cm:
                Disk(disk_name)
            self.assertEqual(type(cm.exception), ValueError, error)

            # Exception 4: missing file `/dev/name`
            os.remove(my_td.td_dir + "/dev/" + my_td.disks[0].name)
            with self.assertRaises(Exception) as cm:
                Disk(disk_name)
            self.assertEqual(type(cm.exception), ValueError, error)

            # Exception 5: missing initialization paramaters
            with self.assertRaises(Exception) as cm:
                Disk()
            self.assertEqual(type(cm.exception), ValueError, error)
        del my_td

    def pt_init_n2(self, name: str, serial: bool, error: str) -> None:
        """Primitive negative test function. It contains the following steps:
            - create TestData class
            - mock os.listdir(), os.path.exists() and builtins.open() functions
            - create Disk() class instance with serial and wwn name
            - ASSERT: if assert not raised in case of invalid missing serial number or wwn name.
            - delete all instance
        """

        # Mock function for os.listdir().
        def mocked_listdir(path: str):
            return original_listdir(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks(["sda"], [DiskType.SSD])
        original_listdir = os.listdir
        mock_listdir = MagicMock(side_effect=mocked_listdir)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.listdir', mock_listdir), \
             patch('builtins.open', mock_open):
            with self.assertRaises(Exception) as cm:
                if serial:
                    Disk(serial_number=name)
                else:
                    Disk(wwn_name=name)
            self.assertEqual(type(cm.exception), ValueError, error)
        del my_td

    def test_init(self):
        """Unit test for Disk.__init__()"""

        # Test creation of all valid disk types.
        self.pt_init_p1("nvmep0n1", DiskType.NVME, "disk_init 1")
        self.pt_init_p1("sda", DiskType.SSD, "disk_init 2")
        self.pt_init_p1("sda", DiskType.HDD, "disk_init 3")

        # Test of asserts in __init__() in case of missing files.
        self.pt_init_n1("nvmep0n1", DiskType.NVME, "disk_init 4")
        self.pt_init_n1("sda", DiskType.SSD, "disk_init 5")
        self.pt_init_n1("sda", DiskType.HDD, "disk_init 6")

        # Test of asserts in __init__() in case of invalid serial number and wwn name.
        self.pt_init_n2("nonexisting_serial_0923409283408", True, "disk_init 7")
        self.pt_init_n2("nonexisting_wwn_0923409283408", False,  "disk_init 8")

    def pt_gsih_p1(self, size_in_512: int, calc_size: float, calc_unit: str, metric: int, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - create an empty Disk() class
            - setup __size attribute
            - call get_size_in_hrf() function
            - ASSERT: if the result is different from the expected ones
            - delete instance
        """
        d = Disk.__new__(Disk)
        d._Disk__size = size_in_512
        size, unit = d.get_size_in_hrf(metric)
        self.assertEqual(size, calc_size, error)
        self.assertEqual(unit, calc_unit, error)
        del d

    def test_get_size_in_hrf(self):
        """Unit test for function Disk.get_size_in_hrf()."""

        self.pt_gsih_p1(1, 512, "B", 0, "get_size_in_hrf 1")
        self.pt_gsih_p1(1, 512, "B", 1, "get_size_in_hrf 2")
        self.pt_gsih_p1(1, 512, "B", 2, "get_size_in_hrf 3")

        self.pt_gsih_p1(3, (3*512)/1000, "kB", 0, "get_size_in_hrf 4")
        self.pt_gsih_p1(3, (3*512)/1024, "KiB", 1, "get_size_in_hrf 5")
        self.pt_gsih_p1(3, (3*512)/1024, "KB", 2, "get_size_in_hrf 6")

        self.pt_gsih_p1(6144, (6144*512)/1000/1000, "MB", 0, "get_size_in_hrf 7")
        self.pt_gsih_p1(6144, (6144*512)/1024/1024, "MiB", 1, "get_size_in_hrf 8")
        self.pt_gsih_p1(6144, (6144*512)/1024/1024, "MB", 2, "get_size_in_hrf 9")

        self.pt_gsih_p1(16777216, (16777216*512)/1000/1000/1000, "GB", 0, "get_size_in_hrf 10")
        self.pt_gsih_p1(16777216, (16777216*512)/1024/1024/1024, "GiB", 1, "get_size_in_hrf 11")
        self.pt_gsih_p1(16777216, (16777216*512)/1024/1024/1024, "GB", 2, "get_size_in_hrf 12")

        self.pt_gsih_p1(8589934592, (8589934592*512)/1000/1000/1000/1000, "TB", 0, "get_size_in_hrf 13")
        self.pt_gsih_p1(8589934592, (8589934592*512)/1024/1024/1024/1024, "TiB", 1, "get_size_in_hrf 14")
        self.pt_gsih_p1(8589934592, (8589934592*512)/1024/1024/1024/1024, "TB", 2, "get_size_in_hrf 15")

        self.pt_gsih_p1(4398046511104, (4398046511104*512)/1000/1000/1000/1000/1000, "PB", 0, "get_size_in_hrf 16")
        self.pt_gsih_p1(4398046511104, (4398046511104*512)/1024/1024/1024/1024/1024, "PiB", 1, "get_size_in_hrf 17")
        self.pt_gsih_p1(4398046511104, (4398046511104*512)/1024/1024/1024/1024/1024, "PB", 2, "get_size_in_hrf 18")

    def pt_gt_p1(self, disk_name: str, disk_type: int, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - create TestData class
            - mock glob.glob(), os.path.exists() and builtins.open() functions
            - create Disk() class instance based on test data in all five ways
            - call get_temperature() method
            - ASSERT: if the returned temperature is different from the generated test data
            - delete all instance
        """

        # Mock function for glob.glob().
        def mocked_glob(file: str, *args, **kwargs):
            if file.startswith('/sys/block'):
                file = my_td.td_dir + file
            return original_glob(file, *args, **kwargs)

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            if not path.startswith(my_td.td_dir):
                path = my_td.td_dir + path
            return original_exists(path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            if not path.startswith(my_td.td_dir):
                path = my_td.td_dir + path
            return original_open(path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks([disk_name], [disk_type])
        original_glob = glob.glob
        mock_glob = MagicMock(side_effect=mocked_glob)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('glob.glob', mock_glob), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            d = Disk(disk_name)
            temp_str = Disk._read_file(my_td.disks[0].hwmon_path)
            temp_val = float(temp_str) / 1000.0
            self.assertEqual(d.get_temperature(), temp_val, error)
            del d
        del my_td

    def pt_gt_n1(self, disk_name: str, disk_type: int, error: str) -> None:
        """Primitive negative test function. It contains the following steps:
            - create TestData class
            - mock glob.glob(), os.path.exists() and builtins.open() functions
            - create Disk() class instance
            - call get_temperature() method
            - ASSERT: if assertion is not raised in case of missing hwmon_path
            - delete all instance
        """

        # Mock function for glob.glob().
        def mocked_glob(file: str, *args, **kwargs):
            if file.startswith('/sys/block'):
                file = my_td.td_dir + file
            return original_glob(file, *args, **kwargs)

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            if not path.startswith(my_td.td_dir):
                path = my_td.td_dir + path
            return original_exists(path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            if not path.startswith(my_td.td_dir):
                path = my_td.td_dir + path
            return original_open(path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks([disk_name], [disk_type])
        original_glob = glob.glob
        mock_glob = MagicMock(side_effect=mocked_glob)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('glob.glob', mock_glob), \
             patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            d = Disk(disk_name)
            d._Disk__hwmon_path = None
            with self.assertRaises(Exception) as cm:
                d.get_temperature()
            self.assertEqual(type(cm.exception), RuntimeError, error)
            del d
        del my_td

    def test_get_temperature(self):
        """Unit test for get_temperature method of Disk class."""

        # Test valid functionality.
        for i in range(20):
            self.pt_gt_p1("nvme0n1", DiskType.NVME, "get_temperature 1")
        self.pt_gt_p1("sda", DiskType.SSD, "get_temperature 2")
        self.pt_gt_p1("sdb", DiskType.HDD, "get_temperature 3")

        # Test assertino.
        self.pt_gt_n1("nvme0n1", DiskType.NVME, "get_temperature 4")
        self.pt_gt_n1("sda", DiskType.SSD, "get_temperature 5")
        self.pt_gt_n1("sdb", DiskType.HDD, "get_temperature 6")

    def test_read_files(self):
        """Unit test for invalid file names in case of _read_file(), _read_udev_property(), _read_udev_path()."""

        # Test if the following functions return empty string/list in case of invalid path.
        d = Disk.__new__(Disk)
        self.assertEqual(d._read_file("./nonexistent_dir/nonexistent_dir/nonexistent_file"), "", "_read_file 1")
        d._Disk__device_id = "104567:03490834"
        self.assertEqual(d._read_udev_property("NONEXISTENT_PROPERTY="), "", "_read_udev_property 1")
        self.assertEqual(d._read_udev_path(True), [], "_read_udev_path 1")
        self.assertEqual(d._read_udev_path(False), [], "_read_udev_path 2")
        del d

    def test_operators(self):
        """Unit test for operators implemented in Disk class"""
        d1 = Disk.__new__(Disk)
        d1._Disk__name = "sda"
        d2 = Disk.__new__(Disk)
        d2._Disk__name = "sda"
        d3 = Disk.__new__(Disk)
        d3._Disk__name = "sdb"
        self.assertTrue(d1 == d2)
        self.assertFalse(d1 != d2)
        self.assertTrue(d1 < d3)
        self.assertTrue(d3 > d1)
        self.assertFalse(d1 > d3)
        self.assertFalse(d3 < d1)
        del d3
        del d2
        del d1

    def test_repr(self):
        """Unit test for __repr__ in Disk class"""

        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            return original_exists(my_td.td_dir + path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(my_td.td_dir + path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks(["sda"], [DiskType.HDD])
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.path.exists', mock_exists), \
             patch('builtins.open', mock_open):
            d = Disk("sda")
            result = repr(d)
            self.assertTrue(d.get_name() in result, "repr 1")
            self.assertTrue(d.get_path() in result, "repr 2")
            self.assertTrue(repr(d.get_byid_path()) in result, "repr 3")
            self.assertTrue(repr(d.get_bypath_path()) in result, "repr 4")
            self.assertTrue(d.get_wwn() in result, "repr 5")
            self.assertTrue(d.get_model() in result, "repr 6")
            self.assertTrue(d.get_serial_number() in result, "repr 7")
            self.assertTrue(d.get_firmware() in result, "repr 8")
            self.assertTrue(d.get_type_str() in result, "repr 9")
            self.assertTrue(str(d.get_size()) in result, "repr 10")
            self.assertTrue(d.get_device_id() in result, "repr 11")
            self.assertTrue(str(d.get_physical_block_size()) in result, "repr 12")
            self.assertTrue(str(d.get_logical_block_size()) in result, "repr 13")
            self.assertTrue(d.get_partition_table_type() in result, "repr 14")
            self.assertTrue(d.get_partition_table_uuid() in result, "repr 15")
        del d
        del my_td


if __name__ == "__main__":
    unittest.main()
