#
#    Test data generation
#    Peter Sulyok (C) 2022.
#
import tempfile
import random
import shutil
import os
import uuid
import time
from typing import List
from diskinfo import DiskType


class TestDisk:
    """Test disk attributes."""
    name: str
    path: str
    serial: str
    firmware: str
    size: int
    type: int
    part_table_type: str
    part_table_uuid: str
    model: str
    wwn: str
    dev_id: str
    phys_bs: int
    log_bs: int
    byid_path: List[str]
    bypath_path: List[str]
    hwmon_path: str


class TestData:
    """Class for test data handling."""

    td_dir: str = ''        # Test data directory in /tmp
    disks: List[TestDisk]   # List of test disk data

    def __init__(self):
        """Initialize the class. It creates a temporary directory."""
        self.td_dir = tempfile.mkdtemp()
        self.disks = []

    def __del__(self):
        """Deletes the temporary directory with its all content."""
        shutil.rmtree(self.td_dir)

    def create_disks(self, disk_names: List[str], disks_types: List[int]) -> None:
        """Creates data for disks."""

        # Create high-level disk folders.
        random.seed(time.monotonic())
        os.makedirs(self.td_dir + "/dev/disk/by-id/", exist_ok=True)
        os.makedirs(self.td_dir + "/dev/disk/by-path/", exist_ok=True)
        os.makedirs(self.td_dir + "/sys/block/", exist_ok=True)
        os.makedirs(self.td_dir + "/run/udev/data/", exist_ok=True)

        for index, dt in enumerate(disks_types):

            # Create a new TestDisk() class
            td = TestDisk()

            # Create common disk attributes for all disk types.
            td.name = disk_names[index]
            td.path = self.td_dir + "/dev/" + td.name
            td.serial = self._get_random_alphanum_str(8)
            td.firmware = self._get_random_alphanum_str(6)
            tb = random.randint(1, 4)
            td.size = int((1099511627776 * tb) / 512)
            td.part_table_type = random.choice(["mbr", "gtp"])
            td.part_table_uuid = str(uuid.uuid4())

            # Create an NVME type disk attributes
            if dt == DiskType.NVME:
                td.model = "DPEKNW010T8"
                td.wwn = "eui." + self._get_random_alphanum_str(20).lower()
                td.dev_id = "259:" + str(index * 8)
                td.type = DiskType.NVME
                rotational = 0
                td.phys_bs = 512
                td.log_bs = 512
                td.byid_path = [self.td_dir + "/dev/disk/by-id/nvme-" + td.model.replace(" ", "_") +
                                "_" + td.serial, self.td_dir + "/dev/disk/by-id/nvme-" + td.wwn]
                td.bypath_path = [self.td_dir + "/dev/disk/by-path/pci-0000:00:17.0-nvme-" + str(1 + index)]
                td.hwmon_path = random.choice([self.td_dir + "/sys/block/" + td.name + "/device/device/hwmon/hwmon" +
                                               str(random.randint(0, 20)),
                                               self.td_dir + "/sys/block/" + td.name + "/device/hwmon" +
                                               str(random.randint(0, 20))])

            # Create an SSD type disk attributes
            elif dt == DiskType.SSD:
                td.model = "Samsung SSD 8" + str(random.randint(5, 9)) + "0 EVO " + str(tb) + "TB"
                td.wwn = "0x500" + self._get_random_alphanum_str(8).lower()
                td.dev_id = "8:" + str(index * 16)
                td.type = DiskType.SSD
                rotational = 0
                td.phys_bs = 512
                td.log_bs = 512
                td.byid_path = [self.td_dir + "/dev/disk/by-id/ata-" + td.model.replace(" ", "_") +
                                "_" + td.serial, self.td_dir + "/dev/disk/by-id/wwn-" + td.wwn]
                td.bypath_path = [self.td_dir + "/dev/disk/by-path/pci-0000:00:17.0-ata-" + str(1 + index),
                                  self.td_dir + "/dev/disk/by-path/pci-0000:00:17.0-ata-" + str(1 + index) + ".0"]
                td.hwmon_path = self.td_dir + "/sys/block/" + td.name + "/device/hwmon/hwmon" + \
                    str(random.randint(0, 20))

            # Create an HDD type disk attributes
            else:  # if dt == DiskType.HDD:
                td.model = "WDC WD100SLAX-69VNTN1"
                td.wwn = "0x500" + self._get_random_alphanum_str(8)
                td.dev_id = "8:" + str(index * 16)
                td.type = DiskType.HDD
                rotational = 1
                td.phys_bs = 4096
                td.log_bs = 512
                td.byid_path = [self.td_dir + "/dev/disk/by-id/ata-" + td.model.replace(" ", "_") +
                                "_" + td.serial, self.td_dir + "/dev/disk/by-id/wwn-" + td.wwn]
                td.bypath_path = [self.td_dir + "/dev/disk/by-path/pci-0000:00:17.0-ata-" + str(1 + index),
                                  self.td_dir + "/dev/disk/by-path/pci-0000:00:17.0-ata-" + str(1 + index) + ".0"]
                td.hwmon_path = self.td_dir + "/sys/block/" + td.name + "/device/hwmon/hwmon" + \
                    str(random.randint(0, 20))

            # Create further disk name based folders.
            os.makedirs(self.td_dir + "/sys/block/" + td.name + "/queue", exist_ok=True)
            os.makedirs(self.td_dir + "/sys/block/" + td.name + "/device", exist_ok=True)

            # Create data files for the disk.
            self._create_file(td.path)
            self._create_file(self.td_dir + "/sys/block/" + td.name + "/queue/rotational", str(rotational))
            self._create_file(self.td_dir + "/sys/block/" + td.name + "/size", str(td.size))
            self._create_file(self.td_dir + "/sys/block/" + td.name + "/device/model", td.model.replace(" ", "_"))
            self._create_file(self.td_dir + "/sys/block/" + td.name + "/dev", td.dev_id)
            self._create_file(self.td_dir + "/sys/block/" + td.name + "/queue/physical_block_size", str(td.phys_bs))
            self._create_file(self.td_dir + "/sys/block/" + td.name + "/queue/logical_block_size", str(td.log_bs))
            for item in td.byid_path:
                self._create_link(item, "../../" + td.name)
            for item in td.bypath_path:
                self._create_link(item, "../../" + td.name)
            os.makedirs(td.hwmon_path, exist_ok=True)
            td.hwmon_path += "/temp1_input"
            self._create_file(td.hwmon_path, str(random.randint(30, 65)*1000))

            # Create /run/udev/data/b"device:id" file.
            udev_content = \
                "S:disk/by-id/" + os.path.basename(td.byid_path[0]) + "\n" \
                "S:disk/by-path/" + os.path.basename(td.bypath_path[0]) + "\n" \
                "S:disk/by-id/" + os.path.basename(td.byid_path[1]) + "\n"
            if len(td.bypath_path) > 1:
                udev_content += "S:disk/by-path/" + os.path.basename(td.bypath_path[1]) + "\n"
            model_str = td.model
            if " " in model_str:
                model_str = model_str.replace(" ", "\\x20") + "\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20\\x20"
            udev_content += "E:ID_MODEL_ENC=" + model_str + "\n"
            udev_content += \
                "E:ID_SERIAL_SHORT=" + td.serial + "\n" \
                "E:ID_REVISION=" + td.firmware + "\n" \
                "E:ID_WWN=" + td.wwn + "\n" \
                "E:ID_PART_TABLE_TYPE=" + td.part_table_type + "\n" \
                "E:ID_PART_TABLE_UUID=" + td.part_table_uuid + "\n"
            self._create_file(self.td_dir + "/run/udev/data/b" + td.dev_id, udev_content)

            self.disks.append(td)

    @staticmethod
    def _get_random_alphanum_str(length: int) -> str:
        """Generates a random string of numbers and letters in a given length."""
        result = ""
        j = 0
        while j < length:
            result = result + random.choice('0123456789ABCDEFGHIJKLMOPQRSTUVWXYZ')
            j += 1
        return result

    @staticmethod
    def _create_file(path: str, content: str = None) -> None:
        """ Creates a file with the specified text content."""
        with open(path, "w+t", encoding="UTF-8") as f:
            if content:
                f.write(content)

    @staticmethod
    def _create_link(path: str, link: str) -> None:
        """ Creates a file with the specified text content."""
        os.symlink(link, path)

# End.
