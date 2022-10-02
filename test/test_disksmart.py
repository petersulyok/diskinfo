#
#    Unitest for `disksmart` module
#    Peter Sulyok (C) 2022.
#
import unittest
from test_data_smart import TestSmartData


class DiskSmartDataTest(unittest.TestCase):
    """Unit test for DiskSmartData() class."""

    def test_find_smart_attribute_by_id(self):
        """Unit test for find_smart_attribute_by_id() method."""
        my_tsd = TestSmartData()
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(5), 0, "find_smart_attribute_by_id 1")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(9), 1, "find_smart_attribute_by_id 2")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(12), 2, "find_smart_attribute_by_id 3")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(177), 3, "find_smart_attribute_by_id 4")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(179), 4, "find_smart_attribute_by_id 5")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(181), 5, "find_smart_attribute_by_id 6")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(182), 6, "find_smart_attribute_by_id 7")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(183), 7, "find_smart_attribute_by_id 8")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(187), 8, "find_smart_attribute_by_id 9")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(190), 9, "find_smart_attribute_by_id 10")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(195), 10, "find_smart_attribute_by_id 11")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(199), 11, "find_smart_attribute_by_id 12")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(235), 12, "find_smart_attribute_by_id 13")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(241), 13, "find_smart_attribute_by_id 14")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_id(253), -1, "find_smart_attribute_by_id 15")
        del my_tsd

    def test_find_smart_attribute_by_name(self):
        """Unit test for find_smart_attribute_by_id() method."""
        my_tsd = TestSmartData()
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Reallocated_Sector"), 0,
                         "find_smart_attribute_by_name 1")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Power_On_Hours"), 1,
                         "find_smart_attribute_by_name 2")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Power_Cycle_Count"), 2,
                         "find_smart_attribute_by_name 3")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Wear_Leveling_Count"), 3,
                         "find_smart_attribute_by_name 4")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Used_Rsvd_Blk_Cnt_Tot"), 4,
                         "find_smart_attribute_by_name 5")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Program_Fail_Cnt_Total"), 5,
                         "find_smart_attribute_by_name 6")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Erase_Fail_Count_Total"), 6,
                         "find_smart_attribute_by_name 7")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Runtime_Bad_Block"), 7,
                         "find_smart_attribute_by_name 8")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Uncorrectable_Error"), 8,
                         "find_smart_attribute_by_name 9")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Airflow_Temperature"), 9,
                         "find_smart_attribute_by_name 10")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("ECC_Error_Rate"), 10,
                         "find_smart_attribute_by_name 12")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("CRC_Error_Count"), 11,
                         "find_smart_attribute_by_name 13")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("POR_Recovery_Count"), 12,
                         "find_smart_attribute_by_name 14")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("Total_LBAs_Written"), 13,
                         "find_smart_attribute_by_name 15")
        self.assertEqual(my_tsd.smart_results[0].find_smart_attribute_by_name("nonexistent_attribute"), -1,
                         "find_smart_attribute_by_name 16")
        del my_tsd


if __name__ == "__main__":
    unittest.main()

# End
