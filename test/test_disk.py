#
#    Unitest for `disk` module
#    Peter Sulyok (C) 2022-2024.
#
import glob
import os
import shutil
import random
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from typing import List, Tuple
from test_data import TestData
from pySMART import Device
from test_data_smart import TestSmartData
from diskinfo import Disk, DiskType, _read_file


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
                d = None

                # Disk class creation with disk name
                if i == 0:
                    d = Disk(disk_name)
                # Disk class creation with disk by-id name
                elif not disk_type == DiskType.LOOP and i == 1:
                    name = os.path.basename(random.choice(my_td.disks[0].byid_path))
                    d = Disk(byid_name=name)
                # Disk class creation with disk by-path name
                elif not disk_type == DiskType.LOOP and i == 2:
                    name = os.path.basename(random.choice(my_td.disks[0].bypath_path))
                    d = Disk(bypath_name=name)
                # Disk class creation with disk serial number
                elif not disk_type == DiskType.LOOP and i == 3:
                    name = my_td.disks[0].serial
                    d = Disk(serial_number=name)
                # Disk class creation with disk wwn name
                elif not disk_type == DiskType.LOOP and i == 4:
                    name = my_td.disks[0].wwn
                    d = Disk(wwn=name)

                if not d:
                    continue

                # Check all disk attributes.
                self.assertEqual(d.get_name(), my_td.disks[0].name, error)
                self.assertEqual(d.get_path(), my_td.disks[0].path.replace(my_td.td_dir, ""), error)
                if not disk_type == DiskType.LOOP:
                    self.assertEqual(d.get_serial_number(), my_td.disks[0].serial, error)
                    self.assertEqual(d.get_firmware(), my_td.disks[0].firmware, error)
                    self.assertEqual(d.get_model(), my_td.disks[0].model, error)
                    self.assertEqual(d.get_wwn(), my_td.disks[0].wwn, error)
                self.assertEqual(d.get_device_id(), my_td.disks[0].dev_id, error)
                self.assertEqual(d.get_size(), my_td.disks[0].size, error)
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
                    self.assertFalse(d.is_loop(), error)
                    self.assertEqual(d.get_type_str(), DiskType.NVME_STR, error)
                elif disk_type == DiskType.SSD:
                    self.assertTrue(d.is_ssd(), error)
                    self.assertFalse(d.is_nvme(), error)
                    self.assertFalse(d.is_hdd(), error)
                    self.assertFalse(d.is_loop(), error)
                    self.assertEqual(d.get_type_str(), DiskType.SSD_STR, error)
                if disk_type == DiskType.HDD:
                    self.assertTrue(d.is_hdd(), error)
                    self.assertFalse(d.is_nvme(), error)
                    self.assertFalse(d.is_ssd(), error)
                    self.assertFalse(d.is_loop(), error)
                    self.assertEqual(d.get_type_str(), DiskType.HDD_STR, error)
                if disk_type == DiskType.LOOP:
                    self.assertTrue(d.is_loop(), error)
                    self.assertFalse(d.is_nvme(), error)
                    self.assertFalse(d.is_ssd(), error)
                    self.assertFalse(d.is_hdd(), error)
                    self.assertEqual(d.get_type_str(), DiskType.LOOP_STR, error)
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
            if not disk_type == DiskType.LOOP:
                os.unlink(my_td.disks[0].bypath_path[0])
                with self.assertRaises(Exception) as cm:
                    Disk(disk_name)
                self.assertEqual(type(cm.exception), RuntimeError, error)

            # Exception 2: missing by-id path
            if not disk_type == DiskType.LOOP:
                os.unlink(my_td.disks[0].byid_path[0])
                with self.assertRaises(Exception) as cm:
                    Disk(disk_name)
                self.assertEqual(type(cm.exception), RuntimeError, error)

            # Exception 3: missing file `/sys/block/name/queue/rotational`
            if not disk_type == DiskType.LOOP:
                os.remove(my_td.td_dir + "/sys/block/" + my_td.disks[0].name + "/queue/rotational")
                with self.assertRaises(Exception) as cm:
                    Disk(disk_name)
                self.assertEqual(type(cm.exception), RuntimeError, error)

            # Exception 4: missing file `/sys/block/name`
            shutil.rmtree(my_td.td_dir + "/sys/block/" + my_td.disks[0].name)
            with self.assertRaises(Exception) as cm:
                Disk(disk_name)
            self.assertEqual(type(cm.exception), ValueError, error)

            # Exception 5: missing file `/dev/name`
            os.remove(my_td.td_dir + "/dev/" + my_td.disks[0].name)
            with self.assertRaises(Exception) as cm:
                Disk(disk_name)
            self.assertEqual(type(cm.exception), ValueError, error)

            # Exception 6: missing initialization parameters
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
                    Disk(wwn=name)
            self.assertEqual(type(cm.exception), ValueError, error)
        del my_td

    def test_init(self):
        """Unit test for Disk.__init__()"""

        # Test creation of all valid disk types.
        self.pt_init_p1("nvmep0n1", DiskType.NVME, "disk_init 1")
        self.pt_init_p1("sda", DiskType.SSD, "disk_init 2")
        self.pt_init_p1("sda", DiskType.HDD, "disk_init 3")
        self.pt_init_p1("loop0", DiskType.LOOP, "disk_init 4")

        # Test of asserts in __init__() in case of missing files.
        self.pt_init_n1("nvmep0n1", DiskType.NVME, "disk_init 5")
        self.pt_init_n1("sda", DiskType.SSD, "disk_init 6")
        self.pt_init_n1("sda", DiskType.HDD, "disk_init 7")
        self.pt_init_n1("loop0", DiskType.LOOP, "disk_init 8")

        # Test of asserts in __init__() in case of invalid serial number and wwn name.
        self.pt_init_n2("nonexisting_serial_0923409283408", True, "disk_init 9")
        self.pt_init_n2("nonexisting_wwn_0923409283408", False,  "disk_init 10")

    def test_get_type(self):
        """Unit test for function Disk.get_type and Disk.get_type_str."""
        d = Disk.__new__(Disk)
        d._Disk__type = DiskType.SSD
        self.assertTrue(d.get_type() == DiskType.SSD, "get_type 1")
        self.assertTrue(d.is_ssd(), "get_type 2")
        self.assertTrue(d.get_type_str() == DiskType.SSD_STR, "get_type 3")
        d._Disk__type = DiskType.HDD
        self.assertTrue(d.get_type() == DiskType.HDD, "get_type 4")
        self.assertTrue(d.is_hdd(), "get_type 5")
        self.assertTrue(d.get_type_str() == DiskType.HDD_STR, "get_type 6")
        d._Disk__type = DiskType.NVME
        self.assertTrue(d.get_type() == DiskType.NVME, "get_type 7")
        self.assertTrue(d.is_nvme(), "get_type 8")
        self.assertTrue(d.get_type_str() == DiskType.NVME_STR, "get_type 9")
        d._Disk__type = DiskType.LOOP
        self.assertTrue(d.get_type() == DiskType.LOOP, "get_type 10")
        self.assertTrue(d.is_loop(), "get_type 11")
        self.assertTrue(d.get_type_str() == DiskType.LOOP_STR, "get_type 12")

        d._Disk__type = 10345
        with self.assertRaises(Exception) as cm:
            d.get_type_str()
        self.assertEqual(type(cm.exception), RuntimeError, "get_type 13")

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
            - mock glob.glob(), os.path.exists(), builtins.open(), Device.__init__(), Device.temperature() functions
            - create Disk() class instance
            - call get_temperature() method
            - ASSERT: if the returned temperature is different from the generated test data
            - delete all instance
        """
        temp_val: float = 0.0

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
        def mocked_open(path: str, *args, **kwargs):
            if not path.startswith(my_td.td_dir):
                path = my_td.td_dir + path
            return original_open(path, *args, **kwargs)

        my_td = TestData()
        my_td.create_disks([disk_name], [disk_type])
        if disk_type != DiskType.LOOP:
            temp_str = _read_file(my_td.disks[0].hwmon_path)
            temp_val = float(temp_str) / 1000
        original_glob = glob.glob
        mock_glob = MagicMock(side_effect=mocked_glob)
        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('glob.glob', mock_glob), \
                patch('os.path.exists', mock_exists), \
                patch('builtins.open', mock_open), \
                patch.object(Device, '__init__', return_value=None), \
                patch('pySMART.Device.temperature', new_callable=PropertyMock) as mock_device_temp:
            if disk_type == DiskType.LOOP:
                mock_device_temp.return_value = None
            else:
                mock_device_temp.return_value = int(temp_val)
            d = Disk(disk_name)
            if d.is_loop():
                self.assertEqual(None, d.get_temperature(sudo=random.choice([True, False])), error)
            else:
                if d.is_hdd() and random.choice([0, 1]):
                    os.unlink(my_td.disks[0].hwmon_path)
                self.assertEqual(temp_val, d.get_temperature(sudo=random.choice([True, False])), error)
            del d
        del my_td

    def pt_gt_n1(self, disk_name: str, disk_type: int, error: str) -> None:
        """Primitive negative test function. It contains the following steps:
            - create TestData class
            - mock glob.glob(), os.path.exists() and builtins.open() functions
            - create Disk() class instance
            - call get_temperature() method
            - ASSERT: if the return value is not None
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
        def mocked_open(path: str, *args, **kwargs):
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
            if disk_type != DiskType.LOOP:
                os.system("echo 'something' > " + my_td.disks[0].hwmon_path)
                self.assertEqual(d.get_temperature(sudo=True, smartctl_path="./non-existing-folder/smartctl"),
                                 None, error)
                d._Disk__hwmon_path = None
                self.assertEqual(d.get_temperature(sudo=True, smartctl_path="./non-existing-folder/smartctl"),
                                 None, error)
            else:
                self.assertEqual(d.get_temperature(sudo=True, smartctl_path="./non-existing-folder/smartctl"),
                                 None, error)
            del d
        del my_td

    def test_get_temperature(self):
        """Unit test for get_temperature() method of Disk class."""

        # Test reading temperature.
        for i in range(20):
            self.pt_gt_p1("nvme0n1", DiskType.NVME, f"get_temperature {(i * 4) + 1}")
            self.pt_gt_p1("sda", DiskType.SSD, f"get_temperature {(i * 4) + 2}")
            self.pt_gt_p1("sdb", DiskType.HDD, f"get_temperature {(i * 4) + 3}")
            self.pt_gt_p1("loop0", DiskType.LOOP, f"get_temperature {(i * 4) + 4}")

        # Test error conditions.
        self.pt_gt_n1("nvme0n1", DiskType.NVME, "get_temperature 81")
        self.pt_gt_n1("sda", DiskType.SSD, "get_temperature 82")
        self.pt_gt_n1("sdb", DiskType.HDD, "get_temperature 83")
        self.pt_gt_n1("loop0", DiskType.LOOP, "get_temperature 84")

    def pt_gsd_p1(self, disk: Disk, nocheck: bool, sudo: bool, smartctrl_path: str, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - mock pySMART.SMARTCTL.generic_call() function
            - call get_smart_data() method for a given Disk class
            - ASSERT: if SMART attributes are different from test data
        """
        tsd: TestSmartData

        # Mock function for pySMART.SMARTCLT.generic_call()
        # pylint: disable=R0911,W0613
        def mocked_smartctl_generic_call(params: List[str], pass_options: bool = False) -> Tuple[List[str], int]:
            if "--info" in params:
                if disk.is_nvme():
                    return tsd.tsd[0].input_info, 0
                return tsd.tsd[1].input_info, 0
            if "background" in params:
                return tsd.tsd[1].input_background, 0
            if "test" in params:
                if disk.is_nvme():
                    return tsd.tsd[0].input_test, 0
                return tsd.tsd[1].input_test, 0
            if disk.is_nvme():
                return tsd.tsd[0].input_all, 0
            return tsd.tsd[1].input_all, 0

        tsd = TestSmartData()
        mock_smartctl_generic_call = MagicMock(side_effect=mocked_smartctl_generic_call)
        with patch('pySMART.SMARTCTL.generic_call', mock_smartctl_generic_call):
            sd = disk.get_smart_data(nocheck=nocheck, sudo=sudo, smartctl_path=smartctrl_path)
            self.assertTrue(sd, error)
            if disk.is_nvme():
                # Check NVME attributes.
                self.assertEqual(sd.nvme_attributes.critical_warning,
                                 tsd.tsd[0].result.nvme_attributes.critical_warning, error)
                self.assertEqual(sd.nvme_attributes.temperature,
                                 tsd.tsd[0].result.nvme_attributes.temperature, error)
                self.assertEqual(sd.nvme_attributes.available_spare,
                                 tsd.tsd[0].result.nvme_attributes.available_spare, error)
                self.assertEqual(sd.nvme_attributes.available_spare_threshold,
                                 tsd.tsd[0].result.nvme_attributes.available_spare_threshold, error)
                self.assertEqual(sd.nvme_attributes.percentage_used,
                                 tsd.tsd[0].result.nvme_attributes.percentage_used, error)
                self.assertEqual(sd.nvme_attributes.data_units_read,
                                 tsd.tsd[0].result.nvme_attributes.data_units_read, error)
                self.assertEqual(sd.nvme_attributes.data_units_written,
                                 tsd.tsd[0].result.nvme_attributes.data_units_written, error)
                self.assertEqual(sd.nvme_attributes.host_read_commands,
                                 tsd.tsd[0].result.nvme_attributes.host_read_commands, error)
                self.assertEqual(sd.nvme_attributes.host_write_commands,
                                 tsd.tsd[0].result.nvme_attributes.host_write_commands, error)
                self.assertEqual(sd.nvme_attributes.controller_busy_time,
                                 tsd.tsd[0].result.nvme_attributes.controller_busy_time, error)
                self.assertEqual(sd.nvme_attributes.power_cycles,
                                 tsd.tsd[0].result.nvme_attributes.power_cycles, error)
                self.assertEqual(sd.nvme_attributes.power_on_hours,
                                 tsd.tsd[0].result.nvme_attributes.power_on_hours, error)
                self.assertEqual(sd.nvme_attributes.unsafe_shutdowns,
                                 tsd.tsd[0].result.nvme_attributes.unsafe_shutdowns, error)
                self.assertEqual(sd.nvme_attributes.media_and_data_integrity_errors,
                                 tsd.tsd[0].result.nvme_attributes.media_and_data_integrity_errors, error)
                self.assertEqual(sd.nvme_attributes.error_information_log_entries,
                                 tsd.tsd[0].result.nvme_attributes.error_information_log_entries, error)
                self.assertEqual(sd.nvme_attributes.warning_composite_temperature_time,
                                 tsd.tsd[0].result.nvme_attributes.warning_composite_temperature_time, error)
                self.assertEqual(sd.nvme_attributes.critical_composite_temperature_time,
                                 tsd.tsd[0].result.nvme_attributes.critical_composite_temperature_time, error)

            else:
                # Check SMART attributes.
                for j, item in enumerate(sd.smart_attributes):
                    self.assertEqual(item.id, tsd.tsd[1].result.smart_attributes[j].id, error)
                    self.assertEqual(item.attribute_name, tsd.tsd[1].result.smart_attributes[j].attribute_name,
                                     error)
                    self.assertEqual(item.flag, tsd.tsd[1].result.smart_attributes[j].flag, error)
                    self.assertEqual(item.value, tsd.tsd[1].result.smart_attributes[j].value, error)
                    self.assertEqual(item.worst, tsd.tsd[1].result.smart_attributes[j].worst, error)
                    self.assertEqual(item.thresh, tsd.tsd[1].result.smart_attributes[j].thresh, error)
                    self.assertEqual(item.type, tsd.tsd[1].result.smart_attributes[j].type, error)
                    self.assertEqual(item.updated, tsd.tsd[1].result.smart_attributes[j].updated, error)
                    self.assertEqual(item.when_failed, tsd.tsd[1].result.smart_attributes[j].when_failed,
                                     error)
                    self.assertEqual(item.raw_value, tsd.tsd[1].result.smart_attributes[j].raw_value, error)
        del sd
        del tsd

    def pt_gsd_p2(self, disk: Disk, nocheck: bool, sudo: bool, smartctrl_path: str, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - mock pySMART.SMARTCTL.generic_call() function
            - call get_smart_data() method for a given Disk class
            - ASSERT: if assessment is not FAIL
        """
        tsd: TestSmartData

        # Mock function for pySMART.SMARTCLT.generic_call()
        # pylint: disable=R0911,W0613
        def mocked_smartctl_generic_call(params: List[str], pass_options: bool = False) -> Tuple[List[str], int]:
            if "--info" in params:
                return tsd.tsd[2].input_info, 0
            if "test" in params:
                return tsd.tsd[2].input_test, 0
            return tsd.tsd[2].input_all, 0

        tsd = TestSmartData()
        mock_smartctl_generic_call = MagicMock(side_effect=mocked_smartctl_generic_call)
        with patch('pySMART.SMARTCTL.generic_call', mock_smartctl_generic_call):
            sd = disk.get_smart_data(nocheck=nocheck, sudo=sudo, smartctl_path=smartctrl_path)
            self.assertEqual(False, sd.healthy, error)
        del sd
        del tsd

    def pt_gsd_p3(self, disk: Disk, nocheck: bool, sudo: bool, smartctrl_path: str, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - mock pySMART.SMARTCTL.generic_call() function
            - call get_smart_data() method for a given Disk class
            - ASSERT: if disk is not in STANDBY mode
        """
        tsd: TestSmartData

        # Mock function for pySMART.SMARTCLT.generic_call()
        # pylint: disable=R0911,W0613
        def mocked_smartctl_generic_call(params: List[str], pass_options: bool = False) -> Tuple[List[str], int]:
            return tsd.tsd[3].input_info, 2

        tsd = TestSmartData()
        mock_smartctl_generic_call = MagicMock(side_effect=mocked_smartctl_generic_call)
        with patch('pySMART.SMARTCTL.generic_call', mock_smartctl_generic_call):
            sd = disk.get_smart_data(nocheck=nocheck, sudo=sudo, smartctl_path=smartctrl_path)
            self.assertEqual(True, sd.standby_mode, error)
        del sd
        del tsd

    def pt_gsd_n1(self, disk: Disk, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - mock pySMART.SMARTCTL.generic_call() function
            - call get_smart_data() with empty output from `smartctl`
            - ASSERT: if not None return value will be provided
        """

        # Mock function for pySMART.SMARTCLT.generic_call()
        # pylint: disable=R0911,W0613
        def mocked_smartctl_generic_call(params: List[str], pass_options: bool = False) -> Tuple[List[str], int]:
            return [], 1

        mock_smartctl_generic_call = MagicMock(side_effect=mocked_smartctl_generic_call)
        with patch('pySMART.SMARTCTL.generic_call', mock_smartctl_generic_call):
            sd = disk.get_smart_data()
            self.assertEqual(None, sd, error)
            del sd

    def pt_gsd_n2(self, disk: Disk, tc: int, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - mock pySMART.SMARTCTL.generic_call() function
            - call get_smart_data() for a loop disk
            - ASSERT: if not None return value will be provided
        """
        tsd: TestSmartData

        # Mock function for pySMART.SMARTCLT.generic_call()
        # pylint: disable=R0911,W0613
        def mocked_smartctl_generic_call(params: List[str], pass_options: bool = False) -> Tuple[List[str], int]:
            if "--info" in params:
                return tsd.tsd[tc].input_info, 1
            return tsd.tsd[tc].input_all, 1

        tsd = TestSmartData()
        mock_smartctl_generic_call = MagicMock(side_effect=mocked_smartctl_generic_call)
        with patch('pySMART.SMARTCTL.generic_call', mock_smartctl_generic_call):
            sd = disk.get_smart_data()
            self.assertEqual(None, sd, error)
            del sd
        del tsd

    def test_get_smart_data(self):
        """Unit test for get_smart_data() method of Disk class."""
        d = Disk.__new__(Disk)

        # Test all combination of the input parameters
        d._Disk__path = "/dev/nvme0"
        d._Disk__type = DiskType.NVME
        self.pt_gsd_p1(d, True, True, "/usr/sbin/smartctl", "get_smart_data 1")

        d._Disk__path = "/dev/sda"
        d._Disk__type = DiskType.HDD
        self.pt_gsd_p1(d, False, False, "/usr/sbin/smartctl", "get_smart_data 2")

        # Test a FAIL disk
        d._Disk__path = "/dev/nvme0"
        d._Disk__type = DiskType.NVME
        self.pt_gsd_p2(d, False, False, "/usr/sbin/smartctl", "get_smart_data 3")

        # Test a disk in standby mode
        d._Disk__path = "/dev/sda"
        d._Disk__type = DiskType.HDD
        self.pt_gsd_p3(d, False, False, "/usr/sbin/smartctl", "get_smart_data 4")

        # Test if `smartctl` cannot be executed
        d._Disk__path = "/dev/sda"
        d._Disk__type = DiskType.HDD
        self.pt_gsd_n1(d, "get_smart_data 5")

        # Test if `smartctl` is executed on a LOOP disk
        d._Disk__path = "/dev/loop0"
        d._Disk__type = DiskType.LOOP
        self.pt_gsd_n2(d, 4, "get_smart_data 6")

        # Test if `smartctl` cannot identify the interface of the disk.
        d._Disk__path = "/dev/xyz"
        d._Disk__type = DiskType.SSD
        self.pt_gsd_n2(d, 5, "get_smart_data 7")

    def pt_gpl_p1(self, disk_name: str, disk_type: int, part_num: int, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - create TestData class
            - mock glob.glob(), os.path.exists() and builtins.open() functions
            - create Disk() class instance
            - create partitions for Disk() class
            - call get_partition_list() method
            - ASSERT: if number of identified partitions are different from the expected number
            - delete all instances
        """
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
        my_td.create_partitions(0, part_num)
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
            plist = d.get_partition_list()
            self.assertEqual(len(plist), part_num, error)
            del d
        del my_td

    def test_get_partition_list(self):
        """Unit test for get_partition_list() method of Disk class."""

        # Test all disk types.
        self.pt_gpl_p1("sda", DiskType.HDD, 0, "get_partition_list 1")
        self.pt_gpl_p1("sda", DiskType.HDD, 2, "get_partition_list 2")
        self.pt_gpl_p1("sda", DiskType.SSD, 3, "get_partition_list 3")
        self.pt_gpl_p1("nvme0n1", DiskType.NVME, 6, "get_partition_list 4")

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

# End
