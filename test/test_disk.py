#
#    Unitest for `disk` module
#    Peter Sulyok (C) 2022.
#
import glob
import os
import re
import shutil
import random
import subprocess
import unittest
from unittest.mock import patch, MagicMock
from test_data import TestData
from test_data_smart import TestSmartData
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
                    d = Disk(wwn=name)

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
                    Disk(wwn=name)
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
            temp_val = int(int(temp_str) / 1000)
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
        """Unit test for get_temperature() method of Disk class."""

        # Test valid functionality.
        for i in range(20):
            self.pt_gt_p1("nvme0n1", DiskType.NVME, "get_temperature 1")
        self.pt_gt_p1("sda", DiskType.SSD, "get_temperature 2")
        self.pt_gt_p1("sdb", DiskType.HDD, "get_temperature 3")

        # Test assertion.
        self.pt_gt_n1("nvme0n1", DiskType.NVME, "get_temperature 4")
        self.pt_gt_n1("sda", DiskType.SSD, "get_temperature 5")
        self.pt_gt_n1("sdb", DiskType.HDD, "get_temperature 6")

    def pt_gsd_p1(self, disk: Disk, nocheck: bool, sudo: str, smartctrl_path: str, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - mock subprocess.run() function
            - call get_smart_data() method for a given Disk class
            - ASSERT: if the subprocess.run (i.e. smartctl) received different arguments than needed
        """
        test_str: str = (
            "smartctl 7.2 2020-12-30 r5155 [x86_64-linux-5.10.0-14-amd64] (local build)\n"
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n"
            "\n"
            "this is a test of input parameters\n"
        )
        mock_subprocess_run = MagicMock()
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=test_str
                )]
        if not smartctrl_path:
            smartctrl_path = "/usr/sbin/smartctl"
        with patch('subprocess.run', mock_subprocess_run):
            sd = disk.get_smart_data(nocheck=nocheck, sudo=sudo, smartctl_path=smartctrl_path)
        args = []
        if sudo:
            args.append(sudo)
        args.append(smartctrl_path)
        if nocheck:
            args.append("-n")
            args.append("standby")
        args.append("-H")
        args.append("-A")
        args.append(disk._Disk__path)
        mock_subprocess_run.assert_called_with(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               text=True)
        self.assertTrue(sd, error)
        self.assertEqual(sd.return_code, 0, error)
        self.assertEqual(sd.raw_output, test_str, error)

    def pt_gsd_n1(self, disk: Disk, smartctl_path: str, error: str) -> None:
        """Primitive negative test function. It contains the following steps:
            - mock subprocess.run() function
            - call get_smart_data() method for a given Disk class
            - ASSERT: if no exception raised on an invalid smartctl_path value
        """
        with self.assertRaises(Exception) as cm:
            disk.get_smart_data(smartctl_path=smartctl_path)
        self.assertTrue(type(cm.exception) in (FileNotFoundError, ValueError), error)

    def pt_gsd_p2(self, disk: Disk, index: int, error: str) -> None:
        """Primitive positive test function. It contains the following steps:
            - mock subprocess.run() function
            - call get_smart_data() method for a given Disk class
            - ASSERT: if parsed values are different from expected ones
        """
        my_tsd = TestSmartData()
        mock_subprocess_run = MagicMock()
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
                args=[],
                returncode=my_tsd.smart_results[index].return_code,
                stdout=my_tsd.input_texts[index]
                )]
        disk._Disk__type = my_tsd.disk_types[index]
        with patch('subprocess.run', mock_subprocess_run):
            sd = disk.get_smart_data()
        self.assertTrue(sd, error)
        self.assertEqual(sd.raw_output, my_tsd.input_texts[index], error)
        self.assertEqual(sd.return_code, my_tsd.smart_results[index].return_code, error)
        self.assertEqual(sd.standby_mode, my_tsd.smart_results[index].standby_mode, error)
        if "smart_attributes" in dir(sd):
            for j, item in enumerate(sd.smart_attributes):
                self.assertEqual(item.id, my_tsd.smart_results[index].smart_attributes[j].id, error)
                self.assertEqual(item.attribute_name, my_tsd.smart_results[index].smart_attributes[j].attribute_name,
                                 error)
                self.assertEqual(item.flag, my_tsd.smart_results[index].smart_attributes[j].flag, error)
                self.assertEqual(item.value, my_tsd.smart_results[index].smart_attributes[j].value, error)
                self.assertEqual(item.worst, my_tsd.smart_results[index].smart_attributes[j].worst, error)
                self.assertEqual(item.thresh, my_tsd.smart_results[index].smart_attributes[j].thresh, error)
                self.assertEqual(item.type, my_tsd.smart_results[index].smart_attributes[j].type, error)
                self.assertEqual(item.updated, my_tsd.smart_results[index].smart_attributes[j].updated, error)
                self.assertEqual(item.when_failed, my_tsd.smart_results[index].smart_attributes[j].when_failed, error)
                self.assertEqual(item.raw_value, my_tsd.smart_results[index].smart_attributes[j].raw_value, error)
        if "nvme_attributes" in dir(sd):
            self.assertEqual(sd.nvme_attributes.critical_warning,
                             my_tsd.smart_results[index].nvme_attributes.critical_warning,
                             error)
            self.assertEqual(sd.nvme_attributes.temperature,
                             my_tsd.smart_results[index].nvme_attributes.temperature,
                             error)
            self.assertEqual(sd.nvme_attributes.data_units_read,
                             my_tsd.smart_results[index].nvme_attributes.data_units_read,
                             error)
            self.assertEqual(sd.nvme_attributes.data_units_written,
                             my_tsd.smart_results[index].nvme_attributes.data_units_written,
                             error)
            self.assertEqual(sd.nvme_attributes.power_cycles,
                             my_tsd.smart_results[index].nvme_attributes.power_cycles,
                             error)
            self.assertEqual(sd.nvme_attributes.power_on_hours,
                             my_tsd.smart_results[index].nvme_attributes.power_on_hours,
                             error)
            self.assertEqual(sd.nvme_attributes.unsafe_shutdowns,
                             my_tsd.smart_results[index].nvme_attributes.unsafe_shutdowns,
                             error)
            self.assertEqual(sd.nvme_attributes.media_and_data_integrity_errors,
                             my_tsd.smart_results[index].nvme_attributes.media_and_data_integrity_errors,
                             error)
            self.assertEqual(sd.nvme_attributes.error_information_log_entries,
                             my_tsd.smart_results[index].nvme_attributes.error_information_log_entries,
                             error)
        del my_tsd

    def pt_gsd_n2(self, disk: Disk, index: int, error: str) -> None:
        """Primitive negative test function. It contains the following steps:
            - mock subprocess.run() function
            - call get_smart_data() method for a given Disk class
            - ASSERT: if no RuntimeError exception is raised for parsing errors of the NVME smart values
        """
        # Critical Warning
        mock_subprocess_run = MagicMock()
        my_tsd = TestSmartData()
        disk._Disk__type = my_tsd.disk_types[index]
        bad_input = re.sub(r"Critical Warning:\s+[\dxX]+\n",
                           r"Critical Warning:\n",
                           my_tsd.input_texts[index])
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
            args=[],
            returncode=my_tsd.smart_results[index].return_code,
            stdout=bad_input
        )]
        with patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                disk.get_smart_data()
            self.assertEqual(type(cm.exception), RuntimeError, error)
        del my_tsd

        # Temperature
        my_tsd = TestSmartData()
        disk._Disk__type = my_tsd.disk_types[index]
        bad_input = re.sub(r"Temperature:\s+\d+\s\w+\n",
                           r"Temperature:\n",
                           my_tsd.input_texts[index])
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
            args=[],
            returncode=my_tsd.smart_results[index].return_code,
            stdout=bad_input
        )]
        with patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                disk.get_smart_data()
            self.assertEqual(type(cm.exception), RuntimeError, error)
        del my_tsd

        # Data Units Read
        my_tsd = TestSmartData()
        disk._Disk__type = my_tsd.disk_types[index]
        bad_input = re.sub(r"Data Units Read:\s+[\d,]+\s\[[\d.\s\w]+\]\n",
                           r"Data Units Read:\n",
                           my_tsd.input_texts[index])
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
            args=[],
            returncode=my_tsd.smart_results[index].return_code,
            stdout=bad_input
        )]
        with patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                disk.get_smart_data()
            self.assertEqual(type(cm.exception), RuntimeError, error)
        del my_tsd

        # Data Units Written
        my_tsd = TestSmartData()
        disk._Disk__type = my_tsd.disk_types[index]
        bad_input = re.sub(r"Data Units Written:\s+[\d,]+\s\[[\d.\s\w]+\]\n",
                           r"Data Units Written:\n",
                           my_tsd.input_texts[index])
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
            args=[],
            returncode=my_tsd.smart_results[index].return_code,
            stdout=bad_input
        )]
        with patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                disk.get_smart_data()
            self.assertEqual(type(cm.exception), RuntimeError, error)
        del my_tsd

        # Power Cycles
        my_tsd = TestSmartData()
        disk._Disk__type = my_tsd.disk_types[index]
        bad_input = re.sub(r"Power Cycles:\s+[\d,]+\n",
                           r"Power Cycles:\n",
                           my_tsd.input_texts[index])
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
            args=[],
            returncode=my_tsd.smart_results[index].return_code,
            stdout=bad_input
        )]
        with patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                disk.get_smart_data()
            self.assertEqual(type(cm.exception), RuntimeError, error)
        del my_tsd

        # Power On Hours
        my_tsd = TestSmartData()
        disk._Disk__type = my_tsd.disk_types[index]
        bad_input = re.sub(r"Power On Hours:\s+[\d,]+\n",
                           r"Power On Hours:\n",
                           my_tsd.input_texts[index])
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
            args=[],
            returncode=my_tsd.smart_results[index].return_code,
            stdout=bad_input
        )]
        with patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                disk.get_smart_data()
            self.assertEqual(type(cm.exception), RuntimeError, error)
        del my_tsd

        # Unsafe Shutdowns
        my_tsd = TestSmartData()
        disk._Disk__type = my_tsd.disk_types[index]
        bad_input = re.sub(r"Unsafe Shutdowns:\s+[\d,]+\n",
                           r"Unsafe Shutdowns:\n",
                           my_tsd.input_texts[index])
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
            args=[],
            returncode=my_tsd.smart_results[index].return_code,
            stdout=bad_input
        )]
        with patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                disk.get_smart_data()
            self.assertEqual(type(cm.exception), RuntimeError, error)
        del my_tsd

        # Media and Data Integrity Errors
        my_tsd = TestSmartData()
        disk._Disk__type = my_tsd.disk_types[index]
        bad_input = re.sub(r"Media and Data Integrity Errors:\s+[\d,]+\n",
                           r"Media and Data Integrity Errors:\n",
                           my_tsd.input_texts[index])
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
            args=[],
            returncode=my_tsd.smart_results[index].return_code,
            stdout=bad_input
        )]
        with patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                disk.get_smart_data()
            self.assertEqual(type(cm.exception), RuntimeError, error)
        del my_tsd

        # Error Information Log Entries
        my_tsd = TestSmartData()
        disk._Disk__type = my_tsd.disk_types[index]
        bad_input = re.sub(r"Error Information Log Entries:\s+[\d,]+\n",
                           r"Error Information Log Entries:\n",
                           my_tsd.input_texts[index])
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
            args=[],
            returncode=my_tsd.smart_results[index].return_code,
            stdout=bad_input
        )]
        with patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                disk.get_smart_data()
            self.assertEqual(type(cm.exception), RuntimeError, error)
        del my_tsd

    def pt_gsd_n3(self, disk: Disk, index: int, error: str) -> None:
        """Primitive negative test function. It contains the following steps:
            - mock subprocess.run() function
            - call get_smart_data() method for a given Disk class
            - ASSERT: if no RuntimeError exception raised
        """
        my_tsd = TestSmartData()
        mock_subprocess_run = MagicMock()
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
                args=[],
                returncode=my_tsd.smart_results[index].return_code,
                stdout=my_tsd.input_texts[index]
                )]
        disk._Disk__type = my_tsd.disk_types[index]
        with patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                disk.get_smart_data()
            self.assertEqual(type(cm.exception), RuntimeError, error)
        del my_tsd

    def test_get_smart_data(self):
        """Unit test for get_smart_data() method of Disk class."""

        d = Disk.__new__(Disk)
        d._Disk__path = "/dev/sda"

        # Test all combination of the input parameters
        self.pt_gsd_p1(d, True, None, None, "get_smart_data 1")
        self.pt_gsd_p1(d, False, None, None, "get_smart_data 2")
        self.pt_gsd_p1(d, True, "sudopath", None, "get_smart_data 3")
        self.pt_gsd_p1(d, False, "sudopath", None, "get_smart_data 4")
        self.pt_gsd_p1(d, True, None, "smartctlpath", "get_smart_data 5")
        self.pt_gsd_p1(d, False, None, "smartctlpath", "get_smart_data 6")
        self.pt_gsd_p1(d, True, "sudopath", "smartctlpath", "get_smart_data 7")
        self.pt_gsd_p1(d, False, "sudopath", "smartctlpath", "get_smart_data 8")

        # Test exception for invalid `smartctl_path` value
        self.pt_gsd_n1(d, "./non_existent_dir$//non_existent_file_97541", "get_smart_data 10")

        # Test of smart data parsing
        self.pt_gsd_p2(d, 0, "get_smart_data 11")
        self.pt_gsd_p2(d, 1, "get_smart_data 12")
        self.pt_gsd_p2(d, 2, "get_smart_data 13")
        self.pt_gsd_p2(d, 3, "get_smart_data 14")

        # Test of NVME parsing errors -> RuntimeError exceptions
        self.pt_gsd_n2(d, 1, "get_smart_data 15")

        # Test of RuntimeError exceptions for `smartctl` errors
        self.pt_gsd_n3(d, 4, "get_smart_data 16")
        self.pt_gsd_n3(d, 5, "get_smart_data 17")

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

# End
