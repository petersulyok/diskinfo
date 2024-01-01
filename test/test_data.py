#
#    Test data generation
#    Peter Sulyok (C) 2022-2024.
#
import tempfile
import random
import shutil
import os
import uuid
import time
from typing import List
from diskinfo import DiskType


class TestPartition:
    """Test data for a partition entry."""
    name: str
    path: str
    byid_path: List[str]
    bypath_path: str
    bypartuuid_path: str
    bypartlabel_path: str
    bylabel_path: str
    byuuid_path: str
    part_dev_id: str
    part_scheme: str
    part_label: str
    part_uuid: str
    part_type: str
    part_number: int
    part_offset: int
    part_size: int
    fs_label: str
    fs_uuid: str
    fs_type: str
    fs_version: str
    fs_usage: str
    fs_free_size: int
    fs_mounting_point: str
    df_output: str


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
    partitions: List[TestPartition]


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

    def create_partitions(self, disk_idx: int, part_num: int) -> None:
        """Creates partitions for disks."""

        self.disks[disk_idx].partitions = []
        p_offset = 2048
        index = 1
        while index <= part_num:
            part = TestPartition()
            part.name = self.disks[disk_idx].name
            if self.disks[disk_idx].type == DiskType.NVME:
                part.name += "p"
            part.name += str(index)
            os.makedirs(self.td_dir + "/sys/block/" + self.disks[disk_idx].name + "/" + part.name, exist_ok=True)
            dev_ids = self.disks[disk_idx].dev_id.split(':')
            part.part_dev_id = dev_ids[0] + ":" + str(int(dev_ids[1]) + index)
            self._create_file(self.td_dir + "/sys/block/" + self.disks[disk_idx].name + "/" + part.name + "/dev",
                              part.part_dev_id)
            part.path = "/dev/" + part.name
            self._create_file(self.td_dir + part.path, " ")

            part.byid_path = [
                "/dev/disk/by-id/" + os.path.basename(self.disks[disk_idx].byid_path[0]) + "-part" + str(index),
                "/dev/disk/by-id/" + os.path.basename(self.disks[disk_idx].byid_path[1]) + "-part" + str(index)
            ]
            part.bypath_path = "/dev/disk/by-path/" + os.path.basename(self.disks[disk_idx].bypath_path[0]) + \
                               "-part" + str(index)
            part.part_uuid = str(uuid.uuid4())
            part.bypartuuid_path = "/dev/disk/by-partuuid/" + part.part_uuid
            part.part_label = random.choice(["EFI system partition", "Microsoft reserved partition",
                                             "Basic data partition", ""])
            part_label = part.part_label
            if " " in part_label:
                part_label = part_label.replace(" ", "\\x20")
            if part_label:
                part.bypartlabel_path = "/dev/disk/by-partlabel/" + part.part_label
            else:
                part.bypartlabel_path = ""
            part.part_scheme = random.choice(["gtp", "mbr"])
            part.part_type = str(uuid.uuid4())
            part.part_number = index
            part.part_offset = p_offset
            # Partition size is random between 100MiB - 500GiB in 512-byte block
            part.part_size = random.randint(204800, 1048576000)
            p_offset += part.part_size

            # If the partition has a filesystem
            is_fs = random.choice([False, True, True, True])
            if is_fs:
                part.fs_uuid = str(uuid.uuid4())
                part.fs_label = random.choice(["System", "", "Windows", "Recovery tools", "", "Data", "Debian",
                                               "Arch Linux", ""])
                fs_label = part.fs_label
                fs_label_enc = part.fs_label
                if " " in fs_label:
                    fs_label = fs_label.replace(" ", "_")
                    fs_label_enc = fs_label_enc.replace(" ", "\\x20")
                if fs_label:
                    part.bylabel_path = "/dev/disk/by-label/" + part.fs_label
                else:
                    part.bylabel_path = ""
                part.fs_uuid = str(uuid.uuid4())
                part.byuuid_path = "/dev/disk/by-uuid/" + part.fs_uuid
                part.fs_type = random.choice(["ntfs", "vfat", "ext3", "ext4"])
                part.fs_version = random.choice(["", "1.0", "FAT32", "500", ""])
                part.fs_usage = "filesystem"
                part.fs_mounting_point = random.choice(["", "/", "/mnt/data", "/home", "/mnt/system"])
                if part.fs_mounting_point:
                    part.fs_free_size = round(part.part_size * random.random())
                else:
                    part.fs_free_size = 0
            else:
                fs_label = ""
                fs_label_enc = ""
                part.fs_label = ""
                part.bylabel_path = ""
                part.fs_uuid = ""
                part.byuuid_path = ""
                part.fs_type = ""
                part.fs_version = ""
                part.fs_usage = ""
                part.fs_free_size = 0
                part.fs_mounting_point = ""

            udev_content = \
                "S:disk/by-id/" + os.path.basename(part.byid_path[0]) + "\n" \
                "S:disk/by-id/" + os.path.basename(part.byid_path[1]) + "\n" \
                "S:disk/by-path/" + os.path.basename(part.bypath_path) + "\n" \
                "S:disk/by-partuuid/" + part.part_uuid + "\n"
            if part_label:
                udev_content += "S:disk/by-partlabel/" + part_label + "\n"
            if is_fs:
                udev_content += "S:disk/by-uuid/" + part.fs_uuid + "\n"
                if fs_label:
                    udev_content += \
                        "S:disk/by-label/" + fs_label_enc + "\n" \
                        "E:ID_FS_LABEL=" + fs_label + "\n" \
                        "E:ID_FS_LABEL_ENC=" + fs_label_enc + "\n"
                udev_content += \
                    "E:ID_FS_UUID=" + part.fs_uuid + "\n" \
                    "E:ID_FS_UUID_ENC=" + part.fs_uuid + "\n"
                if part.fs_version:
                    udev_content += "E:ID_FS_VERSION=" + part.fs_version + "\n"
                udev_content += \
                    "E:ID_FS_TYPE=" + part.fs_type + "\n" \
                    "E:ID_FS_USAGE=" + part.fs_usage + "\n"
            udev_content += \
                "E:ID_PART_ENTRY_SCHEME=" + part.part_scheme + "\n"
            if part_label:
                udev_content += "E:ID_PART_ENTRY_NAME=" + part.part_label + "\n"
            udev_content += \
                "E:ID_PART_ENTRY_UUID=" + part.part_uuid + "\n" \
                "E:ID_PART_ENTRY_TYPE=" + part.part_type + "\n" \
                "E:ID_PART_ENTRY_NUMBER=" + str(part.part_number) + "\n" \
                "E:ID_PART_ENTRY_OFFSET=" + str(part.part_offset) + "\n" \
                "E:ID_PART_ENTRY_SIZE=" + str(part.part_size) + "\n"
            self._create_file(self.td_dir + "/run/udev/data/b" + part.part_dev_id, udev_content)
            part.df_output = \
                "Filesystem          Avail Mounted on\n" \
                "udev             65571944 /dev\n" \
                "tmpfs            13125008 /run\n"
            if part.fs_mounting_point:
                part.df_output += part.path + "  " + str(part.fs_free_size) + " " + part.fs_mounting_point + "\n"
            self.disks[disk_idx].partitions.append(part)
            index += 1

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
