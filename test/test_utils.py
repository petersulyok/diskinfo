#
#    Unitest for `utils` module
#    Peter Sulyok (C) 2022-2024.
#
import unittest
from test_data import TestData
from diskinfo import DiskType, _read_file, _read_udev_property, _read_udev_path, size_in_hrf, time_in_hrf


class UtilsTest(unittest.TestCase):
    """Unit test for utils module."""

    def test_read_file(self):
        """Unit test for _read_file() function."""
        my_td = TestData()
        content = "Some content\nin a text file."
        path = my_td.td_dir + "/tmp-" + my_td._get_random_alphanum_str(6)
        TestData._create_file(path, content)
        self.assertEqual(_read_file(path), content, "test_read_file 1")
        self.assertEqual(_read_file("./nonexistent_dir/nonexistent_dir/nonexistent_file"), "", "test_read_file 2")
        self.assertEqual(_read_file(""), "", "test_read_file 3")
        del my_td

    def test_read_udev_property(self):
        """Unit test for _read_udev_property() function."""
        my_td = TestData()
        my_td.create_disks(["sda"], [DiskType.SSD])
        path = my_td.td_dir + "/run/udev/data/b" + my_td.disks[0].dev_id

        # Test valid values.
        self.assertEqual(_read_udev_property(path, "ID_WWN="), my_td.disks[0].wwn, "test_read_udev_property 1")
        self.assertEqual(_read_udev_property(path, "NONEXISTENT_PROPERTY="), "", "test_read_udev_property 2")
        self.assertEqual(_read_udev_property("./NON-EXISTING_FILE#", "ID_WWN="), "", "test_read_udev_property 3")

        # Test exceptions.
        with self.assertRaises(Exception) as cm:
            # Empty property.
            _read_udev_property(path, "")
        self.assertEqual(type(cm.exception), ValueError, "test_read_udev_property assert-1")
        with self.assertRaises(Exception) as cm:
            # Empty path.
            _read_udev_property("", "ID_WWN=")
        self.assertEqual(type(cm.exception), ValueError, "test_read_udev_property assert-2")

        del my_td

    def test_read_udev_path(self):
        """Unit test for _read_udev_path() function."""
        my_td = TestData()
        my_td.create_disks(["sda"], [DiskType.SSD])
        path = my_td.td_dir + "/run/udev/data/b" + my_td.disks[0].dev_id

        # Test valid values.
        plist = _read_udev_path(path, 0)
        self.assertEqual(plist[0], my_td.disks[0].byid_path[0].replace(my_td.td_dir, ""), "test_read_udev_path 1")
        self.assertEqual(plist[1], my_td.disks[0].byid_path[1].replace(my_td.td_dir, ""), "test_read_udev_path 2")
        plist = _read_udev_path(path, 1)
        self.assertEqual(plist[0], my_td.disks[0].bypath_path[0].replace(my_td.td_dir, ""), "test_read_udev_path 3")
        self.assertEqual(plist[1], my_td.disks[0].bypath_path[1].replace(my_td.td_dir, ""), "test_read_udev_path 4")
        self.assertEqual(_read_udev_path("./NON-EXISTING_FILE#", 0), [], "test_read_udev_path 5")

        # Test exceptions.
        with self.assertRaises(Exception) as cm:
            # Invalid path type.
            _read_udev_path(path, 12)
        self.assertEqual(type(cm.exception), ValueError, "test_read_udev_path assert-1")
        with self.assertRaises(Exception) as cm:
            # Empty path.
            _read_udev_path("", 0)
        self.assertEqual(type(cm.exception), ValueError, "test_read_udev_path assert-2")

        del my_td

    def test_size_in_hrf(self):
        """Unit test for size_in_hrf() function."""

        test_data = [
            (0, 0, 0.0, "B"),
            # Bytes.
            (1, 0, 1.0, "B"),
            (1, 1, 1.0, "B"),
            (1, 2, 1.0, "B"),
            # Kilobytes.
            (1 * 1000, 0, 1.0, "kB"),
            (1 * 1024, 1, 1.0, "KiB"),
            (1 * 1024, 2, 1.0, "KB"),
            # Megabytes.
            (1 * 1000 * 1000, 0, 1.0, "MB"),
            (1 * 1024 * 1024, 1, 1.0, "MiB"),
            (1 * 1024 * 1024, 2, 1.0, "MB"),
            # Gigabytes.
            (1 * 1000 * 1000 * 1000, 0, 1.0, "GB"),
            (1 * 1024 * 1024 * 1024, 1, 1.0, "GiB"),
            (1 * 1024 * 1024 * 1024, 2, 1.0, "GB"),
            # Terrabytes.
            (1 * 1000 * 1000 * 1000 * 1000, 0, 1.0, "TB"),
            (1 * 1024 * 1024 * 1024 * 1024, 1, 1.0, "TiB"),
            (1 * 1024 * 1024 * 1024 * 1024, 2, 1.0, "TB"),
            # Petabytes.
            (1 * 1000 * 1000 * 1000 * 1000 * 1000, 0, 1.0, "PB"),
            (1 * 1024 * 1024 * 1024 * 1024 * 1024, 1, 1.0, "PiB"),
            (1 * 1024 * 1024 * 1024 * 1024 * 1024, 2, 1.0, "PB"),
            # Exabytes.
            (1 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000, 0, 1.0, "EB"),
            (1 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024, 1, 1.0, "EiB"),
            (1 * 1024 * 1024 * 1024 * 1024 * 1024 * 1024, 2, 1.0, "EB"),
        ]

        # Test calculations and compare with expected results.
        for idx, td in enumerate(test_data):
            s, u = size_in_hrf(td[0], td[1])
            self.assertEqual(s, td[2], f"test_size_in_hrf {idx}/1")
            self.assertEqual(u, td[3], f"test_size_in_hrf {idx}/2")

        # Test exceptions.
        with self.assertRaises(Exception) as cm:
            # Negative value.
            size_in_hrf(-1, 0)
        self.assertEqual(type(cm.exception), ValueError, "test_size_in_hrf assert-1")
        with self.assertRaises(Exception) as cm:
            # Negative units.
            size_in_hrf(1, -1)
        self.assertEqual(type(cm.exception), ValueError, "test_size_in_hrf assert-2")
        with self.assertRaises(Exception) as cm:
            # Invalid units.
            size_in_hrf(1, 6)
        self.assertEqual(type(cm.exception), ValueError, "test_size_in_hrf assert-3")

    def test_time_in_hfr(self):
        """Unit test for time_in_hrf() function."""

        test_data = [
            # Convert seconds.
            (1, 0, False, 1.0, "second"),
            (1 * 60, 0, False, 1.0, "minute"),
            (1 * 60 * 60, 0, False, 1.0, "hour"),
            (1 * 60 * 60 * 24, 0, False, 1.0, "day"),
            (1 * 60 * 60 * 24 * 365, 0, False, 1.0, "year"),
            (1, 0, True, 1.0, "s"),
            (1 * 60, 0, True, 1.0, "min"),
            (1 * 60 * 60, 0, True, 1.0, "h"),
            (1 * 60 * 60 * 24, 0, True, 1.0, "d"),
            (1 * 60 * 60 * 24 * 365, 0, True, 1.0, "yr"),
            # Convert minutes
            (1, 1, False, 1.0, "minute"),
            (1 * 60, 1, False, 1.0, "hour"),
            (1 * 60 * 24, 1, False, 1.0, "day"),
            (1 * 60 * 24 * 365, 1, False, 1.0, "year"),
            (1, 1, True, 1.0, "min"),
            (1 * 60, 1, True, 1.0, "h"),
            (1 * 60 * 24, 1, True, 1.0, "d"),
            (1 * 60 * 24 * 365, 1, True, 1.0, "yr"),
            # Convert hours
            (1, 2, False, 1.0, "hour"),
            (1 * 24, 2, False, 1.0, "day"),
            (1 * 24 * 365, 2, False, 1.0, "year"),
            (1, 2, True, 1.0, "h"),
            (1 * 24, 2, True, 1.0, "d"),
            (1 * 24 * 365, 2, True, 1.0, "yr"),
            # Convert days
            (1, 3, False, 1.0, "day"),
            (1 * 365, 3, False, 1.0, "year"),
            (1, 3, True, 1.0, "d"),
            (1 * 365, 3, True, 1.0, "yr"),
            # Convert years
            (1, 4, False, 1.0, "year"),
            (1, 4, True, 1.0, "yr"),
            # Special cases
            (0, 0, False, 0.0, "second"),
            (0, 1, False, 0.0, "minute"),
            (0, 2, False, 0.0, "hour"),
            (0, 3, False, 0.0, "day"),
            (0, 4, False, 0.0, "year"),
        ]

        # Test calculations and compare with expected results.
        for idx, td in enumerate(test_data):
            t, u = time_in_hrf(td[0], td[1], td[2])
            self.assertEqual(t, td[3], f"test_time_in_hrf {idx}/1")
            self.assertEqual(u, td[4], f"test_time_in_hrf {idx}/2")

        # Test exceptions.
        with self.assertRaises(Exception) as cm:
            # Negative value.
            time_in_hrf(-1, 0)
        self.assertEqual(type(cm.exception), ValueError, "test_time_in_hrf assert-1")
        with self.assertRaises(Exception) as cm:
            # Negative units.
            time_in_hrf(1, -1)
        self.assertEqual(type(cm.exception), ValueError, "test_time_in_hrf assert-2")
        with self.assertRaises(Exception) as cm:
            # Invalid units.
            time_in_hrf(1, 6)
        self.assertEqual(type(cm.exception), ValueError, "test_time_in_hrf assert-3")


if __name__ == "__main__":
    unittest.main()

# End
