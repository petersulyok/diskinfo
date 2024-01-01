#
#    Unitest for `partition` module
#    Peter Sulyok (C) 2022-2024.
#
import os
import random
import subprocess
import unittest
from typing import List, Any
from unittest.mock import patch, MagicMock
from test_data import TestData, TestPartition
from diskinfo import DiskType, Partition, size_in_hrf


class PartitionTest(unittest.TestCase):
    """Unit test for utils module."""

    def pt_init_p1(self, part_name: str, part_devid: str, part_data: TestPartition, test_dir: str, error: str):
        """Primitive positive test function. It contains the following steps:
            - create TestData class
            - os.path.exists() and subprocess.run() open() functions
            - create Partition() class
            - ASSERT: if the partition attributes are different from the expected
            - delete all instances
        """
        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            if not path.startswith(test_dir):
                path = test_dir + path
            return original_exists(path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(test_dir + path, *args, **kwargs)

        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        mock_subprocess_run = MagicMock()
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=part_data.df_output
                )]
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.path.exists', mock_exists), \
             patch('subprocess.run', mock_subprocess_run), \
             patch('builtins.open', mock_open):
            part = Partition(part_name, part_devid)
        args = ["df", "--block-size", "512", "--output=source,avail,target"]
        mock_subprocess_run.assert_called_with(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               check=False, text=True)
        self.assertEqual(part.get_name(), part_data.name, error)
        self.assertEqual(part.get_path(), part_data.path, error)
        plist = part.get_byid_path()
        self.assertEqual(plist[0], part_data.byid_path[0], error)
        self.assertEqual(plist[1], part_data.byid_path[1], error)
        self.assertEqual(part.get_bypath_path(), part_data.bypath_path, error)
        self.assertEqual(part.get_bypartuuid_path(), part_data.bypartuuid_path, error)
        self.assertEqual(part.get_bypartlabel_path(), part_data.bypartlabel_path, error)
        self.assertEqual(part.get_byuuid_path(), part_data.byuuid_path, error)
        self.assertEqual(part.get_bylabel_path(), part_data.bylabel_path, error)
        self.assertEqual(part.get_part_device_id(), part_data.part_dev_id, error)
        self.assertEqual(part.get_part_scheme(), part_data.part_scheme, error)
        self.assertEqual(part.get_part_label(), part_data.part_label, error)
        self.assertEqual(part.get_part_uuid(), part_data.part_uuid, error)
        self.assertEqual(part.get_part_type(), part_data.part_type, error)
        self.assertEqual(part.get_part_number(), part_data.part_number, error)
        self.assertEqual(part.get_part_offset(), part_data.part_offset, error)
        self.assertEqual(part.get_part_size(), part_data.part_size, error)
        s1, u1 = part.get_part_size_in_hrf()
        s2, u2 = size_in_hrf(part_data.part_size * 512)
        self.assertEqual(s1, s2, error)
        self.assertEqual(u1, u2, error)
        self.assertEqual(part.get_fs_label(), part_data.fs_label, error)
        self.assertEqual(part.get_fs_uuid(), part_data.fs_uuid, error)
        self.assertEqual(part.get_fs_type(), part_data.fs_type, error)
        self.assertEqual(part.get_fs_version(), part_data.fs_version, error)
        self.assertEqual(part.get_fs_usage(), part_data.fs_usage, error)
        self.assertEqual(part.get_fs_free_size(), part_data.fs_free_size, error)
        s1, u1 = part.get_fs_free_size_in_hrf()
        s2, u2 = size_in_hrf(part_data.fs_free_size * 512)
        self.assertEqual(s1, s2, error)
        self.assertEqual(u1, u2, error)
        self.assertEqual(part.get_fs_mounting_point(), part_data.fs_mounting_point, error)

    def pt_init_n1(self, part_name: str, part_devid: str, test_dir: str, exceptions: List[Any], error: str):
        """Primitive negative test function. It contains the following steps:
            - create TestData class
            - os.path.exists() and subprocess.run() functions
            - create Partition() class
            - ASSERT: if no assertion will be raised for missing files
            - delete all instances
        """
        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            if not path.startswith(test_dir):
                path = test_dir + path
            return original_exists(path)

        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        mock_subprocess_run = MagicMock()
        mock_subprocess_run.side_effect = [subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=""
                )]
        with patch('os.path.exists', mock_exists), \
             patch('subprocess.run', mock_subprocess_run):
            with self.assertRaises(Exception) as cm:
                Partition(part_name, part_devid)
            self.assertTrue(type(cm.exception) in exceptions, error)

    def pt_init_n2(self, part_name: str, part_devid: str, test_dir: str, exceptions: List[Any], error: str):
        """Primitive negative test function. It contains the following steps:
            - create TestData class
            - os.path.exists(), subprocess.run(), open() functions
            - create Partition() class
            - ASSERT: if no assertion will be raised for missing `df` command
            - delete all instances
        """
        # Mock function for os.path.exists().
        def mocked_exists(path: str):
            if not path.startswith(test_dir):
                path = test_dir + path
            return original_exists(path)

        # Mock function for builtin.open().
        def mocked_open(path: str,  *args, **kwargs):
            return original_open(test_dir + path, *args, **kwargs)

        # Mock function for subprocess.run().
        def mocked_run(*args, **kwargs):
            raise random.choice([FileNotFoundError, ValueError])

        original_exists = os.path.exists
        mock_exists = MagicMock(side_effect=mocked_exists)
        mock_subprocess_run = MagicMock(side_effect=mocked_run)
        original_open = open
        mock_open = MagicMock(side_effect=mocked_open)
        with patch('os.path.exists', mock_exists), \
             patch('subprocess.run', mock_subprocess_run), \
             patch('builtins.open', mock_open):
            with self.assertRaises(Exception) as cm:
                Partition(part_name, part_devid)
            self.assertTrue(type(cm.exception) in exceptions, error)

    def test_init_file(self):
        """Unit test for Partition.__init__() method."""

        # Test an HDD with 4 partitions.
        my_td = TestData()
        my_td.create_disks(["sda"], [DiskType.HDD])
        part_number = 4
        my_td.create_partitions(0, part_number)
        for i in range(part_number):
            self.pt_init_p1(my_td.disks[0].partitions[i].name, my_td.disks[0].partitions[i].part_dev_id,
                            my_td.disks[0].partitions[i], my_td.td_dir, f"partition_init {i+1}")
        del my_td

        # Test an SSD with 5 partitions.
        my_td = TestData()
        my_td.create_disks(["sda"], [DiskType.SSD])
        part_number = 5
        my_td.create_partitions(0, part_number)
        for i in range(part_number):
            self.pt_init_p1(my_td.disks[0].partitions[i].name, my_td.disks[0].partitions[i].part_dev_id,
                            my_td.disks[0].partitions[i], my_td.td_dir, f"partition_init {i+1}")
        del my_td

        # Test an NVME with 9 partitions.
        my_td = TestData()
        my_td.create_disks(["nvme0n1"], [DiskType.NVME])
        part_number = 9
        my_td.create_partitions(0, part_number)
        for i in range(part_number):
            self.pt_init_p1(my_td.disks[0].partitions[i].name, my_td.disks[0].partitions[i].part_dev_id,
                            my_td.disks[0].partitions[i], my_td.td_dir, f"partition_init {i+1}")
        del my_td

        # Test exceptions for missing /dev/nvme0n1p1
        my_td = TestData()
        my_td.create_disks(["nvme0n1"], [DiskType.NVME])
        my_td.create_partitions(0, 1)
        os.remove(my_td.td_dir + my_td.disks[0].partitions[0].path)
        self.pt_init_n1(my_td.disks[0].partitions[0].name, my_td.disks[0].partitions[0].part_dev_id,
                        my_td.td_dir, [ValueError], "partition_init exception 1")
        del my_td

        # Test exceptions for missing /run/udev/data/b259:1
        my_td = TestData()
        my_td.create_disks(["nvme0n1"], [DiskType.NVME])
        my_td.create_partitions(0, 1)
        os.remove(my_td.td_dir + "/run/udev/data/b" + my_td.disks[0].partitions[0].part_dev_id)
        self.pt_init_n1(my_td.disks[0].partitions[0].name, my_td.disks[0].partitions[0].part_dev_id,
                        my_td.td_dir, [ValueError], "partition_init exception 2")
        del my_td

        # Test exceptions for missing `df` command
        my_td = TestData()
        my_td.create_disks(["nvme0n1"], [DiskType.NVME])
        my_td.create_partitions(0, 1)
        self.pt_init_n2(my_td.disks[0].partitions[0].name, my_td.disks[0].partitions[0].part_dev_id,
                        my_td.td_dir, [FileNotFoundError, ValueError], "partition_init exception 3")
        del my_td


if __name__ == "__main__":
    unittest.main()

# End
