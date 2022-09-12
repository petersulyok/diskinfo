import unittest
from disk_info import Disk

class DiskTest(unittest.TestCase):

    def test_init(self):

        d = Disk("sda")
        self.assertEqual(d.get_name(), "sda")

if __name__ == "__main__":
    unittest.main()