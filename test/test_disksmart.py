#
#    Unitest for `disksmart` module
#    Peter Sulyok (C) 2022-2024.
#
import unittest
from test_data_smart import TestSmartData


class DiskSmartDataTest(unittest.TestCase):
    """Unit test for DiskSmartData() class."""

    def test_find_smart_attribute_by_id(self):
        """Unit test for find_smart_attribute_by_id() method."""
        my_tsd = TestSmartData()
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(1), 0,
                         "find_smart_attribute_by_id 1")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(5), 3,
                         "find_smart_attribute_by_id 2")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(9), 5,
                         "find_smart_attribute_by_id 3")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(12), 7,
                         "find_smart_attribute_by_id 4")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(187), 8,
                         "find_smart_attribute_by_id 5")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(188), 9,
                         "find_smart_attribute_by_id 6")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(195), 14,
                         "find_smart_attribute_by_id 7")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(199), 17,
                         "find_smart_attribute_by_id 8")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(200), 18,
                         "find_smart_attribute_by_id 9")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(241), 20,
                         "find_smart_attribute_by_id 10")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_id(253), -1,
                         "find_smart_attribute_by_id 11")
        del my_tsd

    def test_find_smart_attribute_by_name(self):
        """Unit test for find_smart_attribute_by_id() method."""
        my_tsd = TestSmartData()
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_name("Reallocated_Sector"), 3,
                         "find_smart_attribute_by_name 1")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_name("Power_On_Hours"), 5,
                         "find_smart_attribute_by_name 2")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_name("Power_Cycle_Count"), 7,
                         "find_smart_attribute_by_name 3")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_name("Airflow_Temperature"), 10,
                         "find_smart_attribute_by_name 4")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_name("Hardware_ECC_Recovered"), 14,
                         "find_smart_attribute_by_name 5")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_name("Total_LBAs_Written"), 20,
                         "find_smart_attribute_by_name 6")
        self.assertEqual(my_tsd.tsd[1].result.find_smart_attribute_by_name("nonexistent_attribute"), -1,
                         "find_smart_attribute_by_name 7")
        del my_tsd


if __name__ == "__main__":
    unittest.main()

# End
