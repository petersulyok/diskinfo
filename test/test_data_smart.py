#
#    Test data generation for SMART.
#    Peter Sulyok (C) 2022.
#
from typing import List
from diskinfo import DiskType, DiskSmartData, SmartAttribute, NvmeAttributes


class TestSmartData:
    """Class to generate test data for testing Disk.get_smart_data() method."""
    smart_results: List[DiskSmartData]
    disk_types: List[int]
    input_texts: List[str] = [
        (
            "smartctl 7.2 2020-12-30 r5155 [x86_64-linux-5.19.0-2-amd64] (local build)\n"
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n"
            "\n"
            "=== START OF READ SMART DATA SECTION ===\n"
            "SMART overall-health self-assessment test result: PASSED\n"
            "\n"
            "SMART Attributes Data Structure revision number: 1\n"
            "Vendor Specific SMART Attributes with Thresholds:\n"
            "ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE\n"
            "  5 Reallocated_Sector_Ct   0x0033   100   100   010    Pre-fail  Always       -       0\n"
            "  9 Power_On_Hours          0x0032   096   096   000    Old_age   Always       -       18329\n"
            " 12 Power_Cycle_Count       0x0032   094   094   000    Old_age   Always       -       5233\n"
            "177 Wear_Leveling_Count     0x0013   099   099   000    Pre-fail  Always       -       5\n"
            "179 Used_Rsvd_Blk_Cnt_Tot   0x0013   100   100   010    Pre-fail  Always       -       0\n"
            "181 Program_Fail_Cnt_Total  0x0032   100   100   010    Old_age   Always       -       0\n"
            "182 Erase_Fail_Count_Total  0x0032   100   100   010    Old_age   Always       -       0\n"
            "183 Runtime_Bad_Block       0x0013   100   100   010    Pre-fail  Always       -       0\n"
            "187 Uncorrectable_Error_Cnt 0x0032   100   100   000    Old_age   Always       -       0\n"
            "190 Airflow_Temperature_Cel 0x0032   074   058   000    Old_age   Always       -       26\n"
            "195 ECC_Error_Rate          0x001a   200   200   000    Old_age   Always       -       0\n"
            "199 CRC_Error_Count         0x003e   100   100   000    Old_age   Always       -       0\n"
            "235 POR_Recovery_Count      0x0012   099   099   000    Old_age   Always       -       183\n"
            "241 Total_LBAs_Written      0x0032   099   099   000    Old_age   Always       -       11201446014\n"
            "\n"
        ),

        (
            "smartctl 7.2 2020-12-30 r5155 [x86_64-linux-5.19.0-2-amd64] (local build)\n"
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n"
            "\n"
            "=== START OF SMART DATA SECTION ===\n"
            "SMART overall-health self-assessment test result: PASSED\n"
            "\n"
            "SMART/Health Information (NVMe Log 0x02)\n"
            "Critical Warning:                   0x00\n"
            "Temperature:                        39 Celsius\n"
            "Available Spare:                    100%\n"
            "Available Spare Threshold:          10%\n"
            "Percentage Used:                    0%\n"
            "Data Units Read:                    11,921,669 [6.10 TB]\n"
            "Data Units Written:                 6,761,542 [3.46 TB]\n"
            "Host Read Commands:                 141,804,273\n"
            "Host Write Commands:                121,286,435\n"
            "Controller Busy Time:               150\n"
            "Power Cycles:                       97\n"
            "Power On Hours:                     1,329\n"
            "Unsafe Shutdowns:                   39\n"
            "Media and Data Integrity Errors:    0\n"
            "Error Information Log Entries:      0\n"
            "Warning  Comp. Temperature Time:    0\n"
            "Critical Comp. Temperature Time:    0\n"
            "\n"
        ),

        (
            "smartctl 7.2 2020-12-30 r5155 [x86_64-linux-5.10.0-14-amd64] (local build)\n"
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n"
            "\n"
            "=== START OF SMART DATA SECTION ===\n"
            "SMART overall-health self-assessment test result: FAILED!\n"
            "\n"
            "SMART/Health Information (NVMe Log 0x02)\n"
            "Critical Warning:                   0x15\n"
            "Temperature:                        31 Celsius\n"
            "Available Spare:                    100%\n"
            "Available Spare Threshold:          10%\n"
            "Percentage Used:                    0%\n"
            "Data Units Read:                    2,853,403 [1.46 TB]\n"
            "Data Units Written:                 3,332,923 [1.70 TB]\n"
            "Host Read Commands:                 24,401,281\n"
            "Host Write Commands:                51,396,029\n"
            "Controller Busy Time:               179\n"
            "Power Cycles:                       266\n"
            "Power On Hours:                     608\n"
            "Unsafe Shutdowns:                   43\n"
            "Media and Data Integrity Errors:    0\n"
            "Error Information Log Entries:      36\n"
            "Warning  Comp. Temperature Time:    0\n"
            "Critical Comp. Temperature Time:    0\n"
            "Temperature Sensor 1:               31 Celsius\n"
            "Temperature Sensor 2:               28 Celsius\n"
            "\n"
        ),

        (
            "smartctl 7.2 2020-12-30 r5155 [x86_64-linux-5.10.0-14-amd64] (local build)\n"
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n"
            "\n"
            "Device is in STANDBY mode, exit(2)\n"
        ),

        (
            "smartctl 7.2 2020-12-30 r5155 [x86_64-linux-5.19.0-2-amd64] (local build)\n"
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n"
            "\n"
            "Smartctl open device: /dev/sda failed: Permission denied\n"
        ),

        (
            "smartctl 7.2 2020-12-30 r5155 [x86_64-linux-5.19.0-2-amd64] (local build)\n"
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n"
            "\n"
            "Smartctl open device: /dev/sdx failed: No such device\n"
        )
    ]

    def __init__(self) -> None:

        self.smart_results = []
        self.disk_types = [DiskType.SSD, DiskType.NVME, DiskType.NVME, DiskType.HDD, DiskType.HDD, DiskType.HDD]

        # input_texts[0] - SSD
        sd = DiskSmartData()
        sd.healthy = True
        sd.standby_mode = False
        sd.return_code = 0
        sd.raw_output = self.input_texts[0]
        sd.smart_attributes = []

        sa = SmartAttribute()
        sa.id = 5
        sa.attribute_name = "Reallocated_Sector_Ct"
        sa.flag = "0x0033"
        sa.value = 100
        sa.worst = 100
        sa.thresh = 10
        sa.type = "Pre-fail"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 0
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 9
        sa.attribute_name = "Power_On_Hours"
        sa.flag = "0x0032"
        sa.value = 96
        sa.worst = 96
        sa.thresh = 0
        sa.type = "Old_age"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 18329
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 12
        sa.attribute_name = "Power_Cycle_Count"
        sa.flag = "0x0032"
        sa.value = 94
        sa.worst = 94
        sa.thresh = 0
        sa.type = "Old_age"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 5233
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 177
        sa.attribute_name = "Wear_Leveling_Count"
        sa.flag = "0x0013"
        sa.value = 99
        sa.worst = 99
        sa.thresh = 0
        sa.type = "Pre-fail"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 5
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 179
        sa.attribute_name = "Used_Rsvd_Blk_Cnt_Tot"
        sa.flag = "0x0013"
        sa.value = 100
        sa.worst = 100
        sa.thresh = 10
        sa.type = "Pre-fail"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 0
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 181
        sa.attribute_name = "Program_Fail_Cnt_Total"
        sa.flag = "0x0032"
        sa.value = 100
        sa.worst = 100
        sa.thresh = 10
        sa.type = "Old_age"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 0
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 182
        sa.attribute_name = "Erase_Fail_Count_Total"
        sa.flag = "0x0032"
        sa.value = 100
        sa.worst = 100
        sa.thresh = 10
        sa.type = "Old_age"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 0
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 183
        sa.attribute_name = "Runtime_Bad_Block"
        sa.flag = "0x0013"
        sa.value = 100
        sa.worst = 100
        sa.thresh = 10
        sa.type = "Pre-fail"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 0
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 187
        sa.attribute_name = "Uncorrectable_Error_Cnt"
        sa.flag = "0x0032"
        sa.value = 100
        sa.worst = 100
        sa.thresh = 0
        sa.type = "Old_age"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 0
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 190
        sa.attribute_name = "Airflow_Temperature_Cel"
        sa.flag = "0x0032"
        sa.value = 74
        sa.worst = 58
        sa.thresh = 0
        sa.type = "Old_age"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 26
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 195
        sa.attribute_name = "ECC_Error_Rate"
        sa.flag = "0x001a"
        sa.value = 200
        sa.worst = 200
        sa.thresh = 0
        sa.type = "Old_age"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 0
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 199
        sa.attribute_name = "CRC_Error_Count"
        sa.flag = "0x003e"
        sa.value = 100
        sa.worst = 100
        sa.thresh = 0
        sa.type = "Old_age"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 0
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 235
        sa.attribute_name = "POR_Recovery_Count"
        sa.flag = "0x0012"
        sa.value = 99
        sa.worst = 99
        sa.thresh = 0
        sa.type = "Old_age"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 183
        sd.smart_attributes.append(sa)

        sa = SmartAttribute()
        sa.id = 241
        sa.attribute_name = "Total_LBAs_Written"
        sa.flag = "0x0032"
        sa.value = 99
        sa.worst = 99
        sa.thresh = 0
        sa.type = "Old_age"
        sa.updated = "Always"
        sa.when_failed = "-"
        sa.raw_value = 11201446014
        sd.smart_attributes.append(sa)

        self.smart_results.append(sd)

        # input_texts[1] - NVME
        sd = DiskSmartData()
        sd.healthy = True
        sd.standby_mode = False
        sd.return_code = 0
        sd.raw_output = self.input_texts[1]
        sd.nvme_attributes = NvmeAttributes()
        sd.nvme_attributes.critical_warning = 0
        sd.nvme_attributes.temperature = 39
        sd.nvme_attributes.data_units_read = 11921669
        sd.nvme_attributes.data_units_written = 6761542
        sd.nvme_attributes.power_cycles = 97
        sd.nvme_attributes.power_on_hours = 1329
        sd.nvme_attributes.unsafe_shutdowns = 39
        sd.nvme_attributes.media_and_data_integrity_errors = 0
        sd.nvme_attributes.error_information_log_entries = 0
        self.smart_results.append(sd)

        # input_texts[2] - NVME / FAILED
        sd = DiskSmartData()
        sd.healthy = False
        sd.standby_mode = False
        sd.return_code = 0
        sd.raw_output = self.input_texts[2]
        sd.nvme_attributes = NvmeAttributes()
        sd.nvme_attributes.critical_warning = 21
        sd.nvme_attributes.temperature = 31
        sd.nvme_attributes.data_units_read = 2853403
        sd.nvme_attributes.data_units_written = 3332923
        sd.nvme_attributes.power_cycles = 266
        sd.nvme_attributes.power_on_hours = 608
        sd.nvme_attributes.unsafe_shutdowns = 43
        sd.nvme_attributes.media_and_data_integrity_errors = 0
        sd.nvme_attributes.error_information_log_entries = 36
        self.smart_results.append(sd)

        # input_texts[3] - HDD
        sd = DiskSmartData()
        sd.healthy = True
        sd.standby_mode = True
        sd.return_code = 2
        sd.raw_output = self.input_texts[3]
        self.smart_results.append(sd)

        # input_texts[4] - ERROR
        sd = DiskSmartData()
        sd.standby_mode = False
        sd.return_code = 2
        sd.raw_output = self.input_texts[4]
        self.smart_results.append(sd)

        # input_texts[5] - ERROR
        sd = DiskSmartData()
        sd.standby_mode = False
        sd.return_code = 2
        sd.raw_output = self.input_texts[5]
        self.smart_results.append(sd)

# End
