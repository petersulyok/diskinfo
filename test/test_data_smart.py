#
#    Test data generation for SMART.
#    Peter Sulyok (C) 2022-2024.
#
from typing import List
from diskinfo import DiskType, DiskSmartData, SmartAttribute, NvmeAttributes


class SmartTestCase:
    """Class to store test data for a single SMART test case."""

    disk_type: int                  # Disk type
    input_info: List[str]           # input text for "smartctl --info ..." command
    input_test: List[str]           # input text for "smartctl -d test ..." command
    input_background: List[str]     # input text for "smartctl -l background ..." command
    input_all: List[str]            # input text for "smartctl --all ..." command
    result: DiskSmartData           # result SMART attributes


class TestSmartData:
    """Class to store SMART test data for testing Disk.get_smart_data() method."""

    tsd: List[SmartTestCase]

    def __init__(self) -> None:

        self.tsd = []

        # Test scenario 1: NVME disk
        d = SmartTestCase()
        d.disk_type = DiskType.NVME
        d.input_info = [
            "smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.5.0-0.deb12.4-amd64] (local build)\n",
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n",
            "\n",
            "this is a test for --info input parameters, content is irrelevant\n",
            "\n"
        ]
        d.input_test = [
            "smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.5.0-0.deb12.4-amd64] (local build)\n",
            "Copyright (C) 2002-22, Bruce Allen, Christian Franke, www.smartmontools.org\n"
            "\n",
            "/dev/nvme0: Device of type 'nvme' [NVMe] detected\n",
            "/dev/nvme0: Device of type 'nvme' [NVMe] opened\n",
            "\n"
        ]
        d.input_all = [
            "smartctl 7.2 2021-01-17 r5171 [x86_64-linux-5.13.4-200.fc34.x86_64] (local build)\n",
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n",
            "\n",
            "=== START OF INFORMATION SECTION ===\n",
            "Model Number:                       KBG30ZMV256G TOSHIBA\n",
            "Serial Number:                      XXXXXXXXXXXX\n",
            "Firmware Version:                   ADHA0101\n",
            "PCI Vendor/Subsystem ID:            0x1179\n",
            "IEEE OUI Identifier:                0x00080d\n",
            "Controller ID:                      0\n",
            "NVMe Version:                       1.2.1\n",
            "Number of Namespaces:               1\n",
            "Namespace 1 Size/Capacity:          256.060.514.304 [256 GB]\n",
            "Namespace 1 Formatted LBA Size:     512\n",
            "Namespace 1 IEEE EUI-64:            00080d 040017b710\n",
            "Local Time is:                      Mon Jul 26 14:38:41 2021 CEST\n",
            "Firmware Updates (0x12):            1 Slot, no Reset required\n",
            "Optional Admin Commands (0x0017):   Security Format Frmw_DL Self_Test\n",
            "Optional NVM Commands (0x0017):     Comp Wr_Unc DS_Mngmt Sav/Sel_Feat\n",
            "Log Page Attributes (0x02):         Cmd_Eff_Lg\n",
            "Maximum Data Transfer Size:         512 Pages\n",
            "Warning  Comp. Temp. Threshold:     82 Celsius\n",
            "Critical Comp. Temp. Threshold:     85 Celsius\n",
            "Supported Power States\n",
            "St Op     Max   Active     Idle   RL RT WL WT  Ent_Lat  Ex_Lat\n",
            " 0 +     3.30W       -        -    0  0  0  0        0       0\n",
            " 1 +     2.70W       -        -    1  1  1  1        0       0\n",
            " 2 +     2.30W       -        -    2  2  2  2        0       0\n",
            " 3 -   0.0500W       -        -    4  4  4  4     8000   32000\n",
            " 4 -   0.0050W       -        -    4  4  4  4     8000   40000\n",
            "Supported LBA Sizes (NSID 0x1)\n",
            "Id Fmt  Data  Metadt  Rel_Perf\n",
            " 0 -    4096       0         0\n",
            " 1 +     512       0         3\n",
            "\n",
            "=== START OF SMART DATA SECTION ===\n",
            "SMART overall-health self-assessment test result: PASSED\n",
            "SMART/Health Information (NVMe Log 0x02)\n",
            "Critical Warning:                   0x00\n",
            "Temperature:                        42 Celsius\n",
            "Available Spare:                    100%\n",
            "Available Spare Threshold:          10%\n",
            "Percentage Used:                    28%\n",
            "Data Units Read:                    29.426.647 [15,0 TB]\n",
            "Data Units Written:                 24.664.736 [12,6 TB]\n",
            "Host Read Commands:                 570.575.528\n",
            "Host Write Commands:                700.150.454\n",
            "Controller Busy Time:               8.134\n",
            "Power Cycles:                       997\n",
            "Power On Hours:                     5.809\n",
            "Unsafe Shutdowns:                   67\n",
            "Media and Data Integrity Errors:    0\n",
            "Error Information Log Entries:      1.356\n",
            "Warning Comp. Temperature Time:     0\n",
            "Critical Comp. Temperature Time:    0\n",
            "Temperature Sensor 1:               42 Celsius\n",
            "Thermal Temp. 1 Transition Count:   5261\n",
            "Thermal Temp. 2 Transition Count:   3302\n",
            "Thermal Temp. 1 Total Time:         56184\n",
            "Thermal Temp. 2 Total Time:         6980\n",
            "\n",
            "Error Information (NVMe Log 0x01, 16 of 64 entries)\n",
            "Num   ErrCount  SQId   CmdId  Status  PELoc          LBA  NSID    VS\n",
            "  0       1356     0  0x0012  0xc005  0x028            -     0     -\n",
            "\n"
        ]
        d.result = DiskSmartData()
        d.result.healthy = True
        d.result.standby_mode = False
        d.result.nvme_attributes = NvmeAttributes(0, 42, 100,
                                                  10, 28, 29426647,
                                                  24664736, 570575528,
                                                  700150454, 8134, 997,
                                                  5809, 67, 0,
                                                  1356, 0,
                                                  0)
        self.tsd.append(d)

        # Test scenario 1: SATA HDD disk
        d = SmartTestCase()
        d.disk_type = DiskType.HDD
        d.input_info = self.tsd[0].input_info
        d.input_test = [
            "smartctl 7.2 2021-01-17 r5171 [x86_64-linux-5.13.4-200.fc34.x86_64] (local build)\n",
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n",
            "\n",
            "/dev/sda: Device of type 'scsi'[SCSI] detected",
            "/dev/sda [SAT]: Device open changed type from 'scsi' to 'sat'"
            "/dev/sda [SAT]: Device of type 'sat'[ATA] opened",
            "\n"
        ]
        d.input_background = [
            "smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.5.0-0.deb12.4-amd64] (local build)\n",
            "Copyright (C) 2002-22, Bruce Allen, Christian Franke, www.smartmontools.org\n",
            "\n",
            "ATA device successfully opened\n",
            "\n",
            "Use 'smartctl -a' (or '-x') to print SMART (and more) information\n",
            "\n"
        ]
        d.input_all = [
            "smartctl 7.1 2019-12-30 r5022 [x86_64-linux-5.4.0-80-generic] (local build)\n",
            "Copyright (C) 2002-19, Bruce Allen, Christian Franke, www.smartmontools.org\n",
            "=== START OF INFORMATION SECTION ===\n",
            "Device Model:     OOS12000G\n",
            "Serial Number:    00008AXB\n",
            "LU WWN Device Id: 5 000c50 0a4847915\n",
            "Firmware Version: OOS1\n",
            "User Capacity:    12,000,138,625,024 bytes [12.0 TB]\n",
            "Sector Sizes:     512 bytes logical, 4096 bytes physical\n",
            "Rotation Rate:    7200 rpm\n",
            "Form Factor:      3.5 inches\n",
            "Device is:        Not in smartctl database [for details use: -P showall]\n",
            "ATA Version is:   ACS-3 T13/2161-D revision 5\n",
            "SATA Version is:  SATA 3.1, 6.0 Gb/s (current: 6.0 Gb/s)\n",
            "Local Time is:    Sat Jul 24 16:19:15 2021 PDT\n",
            "SMART support is: Available - device has SMART capability.\n",
            "SMART support is: Enabled\n",
            "=== START OF READ SMART DATA SECTION ===\n",
            "SMART overall-health self-assessment test result: PASSED\n",
            "General SMART Values:\n",
            "Offline data collection status:  (0x82) Offline data collection activity\n",
            "                                        was completed without error.\n",
            "                                        Auto Offline Data Collection: Enabled.\n",
            "Self-test execution status:      ( 243) Self-test routine in progress...\n",
            "                                        30% of test remaining.\n",
            "Total time to complete Offline \n",
            "data collection:                (  567) seconds.\n",
            "Offline data collection\n",
            "capabilities:                    (0x7b) SMART execute Offline immediate.\n",
            "                                        Auto Offline data collection on/off support.\n",
            "                                        Suspend Offline collection upon new\n",
            "                                        command.\n",
            "                                        Offline surface scan supported.\n",
            "                                        Self-test supported.\n",
            "                                        Conveyance Self-test supported.\n",
            "                                        Selective Self-test supported.\n",
            "SMART capabilities:            (0x0003) Saves SMART data before entering\n",
            "                                        power-saving mode.\n",
            "                                        Supports SMART auto save timer.\n",
            "Error logging capability:        (0x01) Error logging supported.\n",
            "                                        General Purpose Logging supported.\n",
            "Short self-test routine \n",
            "recommended polling time:        (   1) minutes.\n",
            "Extended self-test routine\n",
            "recommended polling time:        (1082) minutes.\n",
            "Conveyance self-test routine\n",
            "recommended polling time:        (   2) minutes.\n",
            "SCT capabilities:              (0x50bd) SCT Status supported.\n",
            "                                        SCT Error Recovery Control supported.\n",
            "                                        SCT Feature Control supported.\n",
            "                                        SCT Data Table supported.\n",
            "SMART Attributes Data Structure revision number: 10\n",
            "Vendor Specific SMART Attributes with Thresholds:\n",
            "ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE\n",
            "  1 Raw_Read_Error_Rate     0x000f   082   066   044    Pre-fail  Always       -       176373483\n",
            "  3 Spin_Up_Time            0x0003   090   089   000    Pre-fail  Always       -       0\n",
            "  4 Start_Stop_Count        0x0032   100   100   020    Old_age   Always       -       10\n",
            "  5 Reallocated_Sector_Ct   0x0033   100   100   010    Pre-fail  Always       -       0\n",
            "  7 Seek_Error_Rate         0x000f   068   060   045    Pre-fail  Always       -       5849609\n",
            "  9 Power_On_Hours          0x0032   100   100   000    Old_age   Always       -       252\n",
            " 10 Spin_Retry_Count        0x0013   100   100   097    Pre-fail  Always       -       0\n",
            " 12 Power_Cycle_Count       0x0032   100   100   020    Old_age   Always       -       9\n",
            "187 Reported_Uncorrect      0x0032   100   100   000    Old_age   Always       -       0\n",
            "188 Command_Timeout         0x0032   100   100   000    Old_age   Always       -       0\n",
            "190 Airflow_Temperature_Cel 0x0022   062   060   040    Old_age   Always       -       38 (Min/Max 22/40)\n",
            "192 Power-Off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       8\n",
            "193 Load_Cycle_Count        0x0032   100   100   000    Old_age   Always       -       1230\n",
            "194 Temperature_Celsius     0x0022   038   040   000    Old_age   Always       -       38 (0 16 0 0 0)\n",
            "195 Hardware_ECC_Recovered  0x001a   032   015   000    Old_age   Always       -       176373483\n",
            "197 Current_Pending_Sector  0x0012   100   100   000    Old_age   Always       -       0\n",
            "198 Offline_Uncorrectable   0x0010   100   100   000    Old_age   Offline      -       0\n",
            "199 UDMA_CRC_Error_Count    0x003e   200   200   000    Old_age   Always       -       0\n",
            "200 Multi_Zone_Error_Rate   0x0023   100   100   001    Pre-fail  Always       -       0\n",
            "240 Head_Flying_Hours       0x0000   100   253   000    Old_age   Offline      -       17 (198 87 0)\n",
            "241 Total_LBAs_Written      0x0000   100   253   000    Old_age   Offline      -       3625709712\n",
            "242 Total_LBAs_Read         0x0000   100   253   000    Old_age   Offline      -       1041293\n",
            "SMART Error Log Version: 1\n",
            "No Errors Logged\n",
            "SMART Self-test log structure revision number 1\n",
            "Num  Test_Description    Status                  Remaining  LifeTime(hours)  LBA_of_first_error\n",
            "# 1  Extended offline    Self-test routine in progress 30%       252         -\n",
            "# 2  Short offline       Completed without error       00%       238         -\n",
            "# 3  Short offline       Completed without error       00%       214         -\n",
            "# 4  Short offline       Completed without error       00%       190         -\n",
            "# 5  Short offline       Completed without error       00%       166         -\n",
            "# 6  Short offline       Completed without error       00%       142         -\n",
            "# 7  Short offline       Completed without error       00%       118         -\n",
            "# 8  Short offline       Completed without error       00%        94         -\n",
            "SMART Selective self-test log data structure revision number 1\n",
            " SPAN  MIN_LBA  MAX_LBA  CURRENT_TEST_STATUS\n",
            "    1        0        0  Not_testing\n",
            "    2        0        0  Not_testing\n",
            "    3        0        0  Not_testing\n",
            "    4        0        0  Not_testing\n",
            "    5        0        0  Not_testing\n",
            "Selective self-test flags (0x0):\n",
            "  After scanning selected spans, do NOT read-scan remainder of disk.\n",
            "If Selective self-test is pending on power-up, resume after 0 minute delay.\n",
            "\n"
        ]
        d.result = DiskSmartData()
        d.result.healthy = True
        d.result.standby_mode = False
        d.result.smart_attributes = []
        d.result.smart_attributes.append(SmartAttribute(1, "Raw_Read_Error_Rate", 0x000f, 82,
                                                        66,  44, "Pre-fail", "Always",
                                                        "-", 176373483))
        d.result.smart_attributes.append(SmartAttribute(3, "Spin_Up_Time", 0x0003, 90,
                                                        89, 0, "Pre-fail", "Always",
                                                        "-", 0))
        d.result.smart_attributes.append(SmartAttribute(4, "Start_Stop_Count", 0x0032, 100,
                                                        100, 20, "Old_age", "Always",
                                                        "-", 10))
        d.result.smart_attributes.append(SmartAttribute(5, "Reallocated_Sector_Ct", 0x0033,
                                                        100, 100, 10, "Pre-fail",
                                                        "Always", "-", 0))
        d.result.smart_attributes.append(SmartAttribute(7, "Seek_Error_Rate", 0x000f, 68,
                                                        60, 45, "Pre-fail", "Always",
                                                        "-", 5849609))
        d.result.smart_attributes.append(SmartAttribute(9, "Power_On_Hours", 0x0032, 100,
                                                        100, 0, "Old_age", "Always",
                                                        "-", 252))
        d.result.smart_attributes.append(SmartAttribute(10, "Spin_Retry_Count", 0x0013, 100,
                                                        100, 97, "Pre-fail", "Always",
                                                        "-", 0))
        d.result.smart_attributes.append(SmartAttribute(12, "Power_Cycle_Count", 0x0032, 100,
                                                        100, 20, "Old_age", "Always",
                                                        "-", 9))
        d.result.smart_attributes.append(SmartAttribute(187, "Reported_Uncorrect", 0x0032,
                                                        100, 100, 0, "Old_age",
                                                        "Always", "-", 0))
        d.result.smart_attributes.append(SmartAttribute(188, "Command_Timeout", 0x0032, 100,
                                                        100, 0, "Old_age", "Always",
                                                        "-", 0))
        d.result.smart_attributes.append(SmartAttribute(190, "Airflow_Temperature_Cel", 0x0022,
                                                        62, 60, 40, "Old_age", "Always",
                                                        "-", 38))
        d.result.smart_attributes.append(SmartAttribute(192, "Power-Off_Retract_Count", 0x0032,
                                                        100, 100, 0, "Old_age", "Always",
                                                        "-", 8))
        d.result.smart_attributes.append(SmartAttribute(193, "Load_Cycle_Count", 0x0032, 100,
                                                        100, 0, "Old_age", "Always",
                                                        "-", 1230))
        d.result.smart_attributes.append(SmartAttribute(194, "Temperature_Celsius", 0x0022,
                                                        38, 40, 0, "Old_age", "Always",
                                                        "-", 38))
        d.result.smart_attributes.append(SmartAttribute(195, "Hardware_ECC_Recovered", 0x001a,
                                                        32, 15, 0, "Old_age", "Always",
                                                        "-", 176373483))
        d.result.smart_attributes.append(SmartAttribute(197, "Current_Pending_Sector", 0x0012,
                                                        100, 100, 0, "Old_age", "Always",
                                                        "-", 0))
        d.result.smart_attributes.append(SmartAttribute(198, "Offline_Uncorrectable", 0x0010,
                                                        100, 100, 0, "Old_age",
                                                        "Offline", "-", 0))
        d.result.smart_attributes.append(SmartAttribute(199, "UDMA_CRC_Error_Count", 0x003e,
                                                        200, 200, 0, "Old_age", "Always",
                                                        "-", 0))
        d.result.smart_attributes.append(SmartAttribute(200, "Multi_Zone_Error_Rate", 0x0023,
                                                        100, 100, 1, "Pre-fail",
                                                        "Always", "-", 0))
        d.result.smart_attributes.append(SmartAttribute(240, "Head_Flying_Hours", 0x0000, 100,
                                                        253, 0, "Old_age", "Offline",
                                                        "-", 17))
        d.result.smart_attributes.append(SmartAttribute(241, "Total_LBAs_Written", 0x0000, 100,
                                                        253, 000, "Old_age", "Offline",
                                                        "-", 3625709712))
        d.result.smart_attributes.append(SmartAttribute(242, "Total_LBAs_Read", 0x0000, 100,
                                                        253, 0, "Old_age", "Offline",
                                                        "-", 1041293))
        self.tsd.append(d)

        # Test scenario 3: FAILED NVME disk
        d = SmartTestCase()
        d.disk_type = DiskType.NVME
        d.input_info = [
            "smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.5.0-0.deb12.4-amd64] (local build)\n",
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n",
            "\n",
            "this is a test for --info input parameters, content is irrelevant\n",
            "\n"
        ]
        d.input_test = [
            "smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.5.0-0.deb12.4-amd64] (local build)\n",
            "Copyright (C) 2002-22, Bruce Allen, Christian Franke, www.smartmontools.org\n"
            "\n",
            "/dev/nvme0: Device of type 'nvme' [NVMe] detected\n",
            "/dev/nvme0: Device of type 'nvme' [NVMe] opened\n",
            "\n"
        ]
        d.input_all = [
            "smartctl 7.2 2021-01-17 r5171 [x86_64-linux-5.13.4-200.fc34.x86_64] (local build)\n",
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n",
            "\n",
            "=== START OF INFORMATION SECTION ===\n",
            "Model Number:                       KBG30ZMV256G TOSHIBA\n",
            "Serial Number:                      XXXXXXXXXXXX\n",
            "Firmware Version:                   ADHA0101\n",
            "PCI Vendor/Subsystem ID:            0x1179\n",
            "IEEE OUI Identifier:                0x00080d\n",
            "Controller ID:                      0\n",
            "NVMe Version:                       1.2.1\n",
            "Number of Namespaces:               1\n",
            "Namespace 1 Size/Capacity:          256.060.514.304 [256 GB]\n",
            "Namespace 1 Formatted LBA Size:     512\n",
            "Namespace 1 IEEE EUI-64:            00080d 040017b710\n",
            "Local Time is:                      Mon Jul 26 14:38:41 2021 CEST\n",
            "Firmware Updates (0x12):            1 Slot, no Reset required\n",
            "Optional Admin Commands (0x0017):   Security Format Frmw_DL Self_Test\n",
            "Optional NVM Commands (0x0017):     Comp Wr_Unc DS_Mngmt Sav/Sel_Feat\n",
            "Log Page Attributes (0x02):         Cmd_Eff_Lg\n",
            "Maximum Data Transfer Size:         512 Pages\n",
            "Warning  Comp. Temp. Threshold:     82 Celsius\n",
            "Critical Comp. Temp. Threshold:     85 Celsius\n",
            "Supported Power States\n",
            "St Op     Max   Active     Idle   RL RT WL WT  Ent_Lat  Ex_Lat\n",
            " 0 +     3.30W       -        -    0  0  0  0        0       0\n",
            " 1 +     2.70W       -        -    1  1  1  1        0       0\n",
            " 2 +     2.30W       -        -    2  2  2  2        0       0\n",
            " 3 -   0.0500W       -        -    4  4  4  4     8000   32000\n",
            " 4 -   0.0050W       -        -    4  4  4  4     8000   40000\n",
            "Supported LBA Sizes (NSID 0x1)\n",
            "Id Fmt  Data  Metadt  Rel_Perf\n",
            " 0 -    4096       0         0\n",
            " 1 +     512       0         3\n",
            "\n",
            "=== START OF SMART DATA SECTION ===\n",
            "SMART overall-health self-assessment test result: FAILED\n",
            "SMART/Health Information (NVMe Log 0x02)\n",
            "Critical Warning:                   0x05\n",
            "Temperature:                        42 Celsius\n",
            "Available Spare:                    100%\n",
            "Available Spare Threshold:          10%\n",
            "Percentage Used:                    28%\n",
            "Data Units Read:                    29.426.647 [15,0 TB]\n",
            "Data Units Written:                 24.664.736 [12,6 TB]\n",
            "Host Read Commands:                 570.575.528\n",
            "Host Write Commands:                700.150.454\n",
            "Controller Busy Time:               8.134\n",
            "Power Cycles:                       997\n",
            "Power On Hours:                     5.809\n",
            "Unsafe Shutdowns:                   67\n",
            "Media and Data Integrity Errors:    0\n",
            "Error Information Log Entries:      1.356\n",
            "Warning Comp. Temperature Time:     0\n",
            "Critical Comp. Temperature Time:    0\n",
            "Temperature Sensor 1:               42 Celsius\n",
            "Thermal Temp. 1 Transition Count:   5261\n",
            "Thermal Temp. 2 Transition Count:   3302\n",
            "Thermal Temp. 1 Total Time:         56184\n",
            "Thermal Temp. 2 Total Time:         6980\n",
            "\n",
            "Error Information (NVMe Log 0x01, 16 of 64 entries)\n",
            "Num   ErrCount  SQId   CmdId  Status  PELoc          LBA  NSID    VS\n",
            "  0       1356     0  0x0012  0xc005  0x028            -     0     -\n",
            "\n"
        ]
        d.result = DiskSmartData()
        d.result.healthy = True
        d.result.standby_mode = False
        d.result.nvme_attributes = NvmeAttributes(5, 42, 100,
                                                  10, 28, 29426647,
                                                  24664736, 570575528,
                                                  700150454, 8134, 997,
                                                  5809, 67, 0,
                                                  1356, 0,
                                                  0)
        self.tsd.append(d)

        # Test scenario 4: HDD in standby mode
        d = SmartTestCase()
        d.disk_type = DiskType.HDD
        d.input_info = [
            "smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.5.0-0.deb12.4-amd64] (local build)\n",
            "Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org\n",
            "\n",
            "Device is in STANDBY mode, exit(2)\n",
            "\n"
        ]
        d.result = DiskSmartData()
        d.result.healthy = True
        d.result.standby_mode = True
        self.tsd.append(d)

        # Test scenario 5: LOOP disk
        d = SmartTestCase()
        d.disk_type = DiskType.LOOP
        d.input_info = [
            "smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.5.0-0.deb12.4-amd64] (local build)\n",
            "Copyright (C) 2002-22, Bruce Allen, Christian Franke, www.smartmontools.org\n",
            "\n",
            "/dev/loop0: Unable to detect device type\n",
            "Please specify device type with the -d option.\n",
            "\n",
            "Use smartctl -h to get a usage summary\n",
            "\n"
        ]
        d.input_all = d.input_info
        self.tsd.append(d)

        # Test scenario 6: disk without known interface.
        d = SmartTestCase()
        d.disk_type = DiskType.SSD
        d.input_info = [
            "smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.5.0-0.deb12.4-amd64] (local build)\n",
            "Copyright (C) 2002-22, Bruce Allen, Christian Franke, www.smartmontools.org\n",
            "\n",
            "/dev/xyz: Unable to detect device type\n",
            "Please specify device type with the -d option.\n",
            "\n",
            "Use smartctl -h to get a usage summary\n",
            "\n"
        ]
        d.input_all = d.input_info
        self.tsd.append(d)


# End
