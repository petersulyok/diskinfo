#
#    Unit tests for `partition` module (pytest style)
#    Peter Sulyok (C) 2022-2026.
#
import os
from unittest.mock import MagicMock, patch, mock_open
import pytest
from diskinfo.partition import Partition
from diskinfo.filesystem import FileSystem


# ── mock helpers ──────────────────────────────────────────────────────────────


def _make_part_device(
    name: str = "sda1",
    dev_id: str = "8:1",
    links: list = None,
    scheme: str = "gpt",
    part_label: str = "MyLabel",
    part_uuid: str = "acb8374d-fb60-4cb0-8ac4-273417c6f847",
    part_type: str = "ebd0a0a2-b9e5-4433-87c0-68b6b72699c7",
    part_number: str = "1",
    part_offset: str = "2048",
    part_size: str = "2097152",
    fs_label: str = "MyFS",
    fs_uuid: str = "d54d33ea-d892-44d9-ae24-e3c6216d7a32",
    fs_type: str = "ext4",
    fs_version: str = "1.0",
    fs_usage: str = "filesystem",
) -> MagicMock:
    """Return a MagicMock satisfying all pyudev.Device patterns in Partition.__init__."""
    dev = MagicMock()
    dev.sys_name = name
    dev.device_node = f"/dev/{name}"
    dev.attributes.asstring.return_value = dev_id
    dev.device_links = list(links or [])

    props = {
        "ID_PART_ENTRY_SCHEME": scheme,
        "ID_PART_ENTRY_NAME": part_label,
        "ID_PART_ENTRY_UUID": part_uuid,
        "ID_PART_ENTRY_TYPE": part_type,
        "ID_PART_ENTRY_NUMBER": part_number,
        "ID_PART_ENTRY_OFFSET": part_offset,
        "ID_PART_ENTRY_SIZE": part_size,
        # _pyudev_getenc tries ID_FS_LABEL_ENC first, falls back to ID_FS_LABEL
        "ID_FS_LABEL_ENC": None,
        "ID_FS_LABEL": fs_label,
        # same pattern for fs uuid
        "ID_FS_UUID_ENC": None,
        "ID_FS_UUID": fs_uuid,
        "ID_FS_TYPE": fs_type,
        "ID_FS_VERSION": fs_version,
        "ID_FS_USAGE": fs_usage,
    }
    dev.get.side_effect = props.get
    return dev


def _proc_mounts(*entries):
    """Return a mock_open for /proc/mounts with the given (device, mountpoint) entries."""
    lines = ""
    for dev_path, mount_point in entries:
        lines += f"{dev_path} {mount_point} ext4 rw,relatime 0 0\n"
    return mock_open(read_data=lines)


def _statvfs_result(f_bavail: int = 0, f_frsize: int = 512) -> os.statvfs_result:
    """Return an os.statvfs_result with the given f_bavail and f_frsize."""
    return os.statvfs_result((4096, f_frsize, 1000000, 500000, f_bavail, 100000, 90000, 90000, 0, 255))


# ── Partition.__init__ – basic attributes ─────────────────────────────────────


def test_partition_stores_name_and_path():
    """Partition stores the partition name and device path from pyudev."""
    dev = _make_part_device(name="sda1", dev_id="8:1")
    with patch("builtins.open", _proc_mounts()):
        p = Partition(dev)
    assert p.get_name() == "sda1"
    assert p.get_path() == "/dev/sda1"
    assert p.get_part_device_id() == "8:1"


def test_partition_stores_all_attributes():
    """Partition stores every attribute correctly from the pyudev device."""
    dev = _make_part_device(
        name="sda1",
        dev_id="8:1",
        scheme="gpt",
        part_label="Boot",
        part_uuid="abcd-1234",
        part_type="ebd0a0a2-b9e5-4433-87c0-68b6b72699c7",
        part_number="1",
        part_offset="2048",
        part_size="1048576",
        fs_label="BOOT",
        fs_uuid="6432-935A",
        fs_type="vfat",
        fs_version="FAT32",
        fs_usage="filesystem",
    )
    m = _proc_mounts(("/dev/sda1", "/boot/efi"))
    with (patch("builtins.open", m),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=512000))):
        p = Partition(dev)

    assert p.get_part_scheme() == "gpt"
    assert p.get_part_label() == "Boot"
    assert p.get_part_uuid() == "abcd-1234"
    assert p.get_part_type() == "ebd0a0a2-b9e5-4433-87c0-68b6b72699c7"
    assert p.get_part_number() == 1
    assert p.get_part_offset() == 2048
    assert p.get_part_size() == 1048576
    fs = p.get_filesystem()
    assert fs.get_fs_label() == "BOOT"
    assert fs.get_fs_uuid() == "6432-935A"
    assert fs.get_fs_type() == "vfat"
    assert fs.get_fs_version() == "FAT32"
    assert fs.get_fs_usage() == "filesystem"
    assert fs.get_fs_free_size() == 512000
    assert fs.get_fs_mounting_point() == "/boot/efi"


# ── Partition.__init__ – device links ─────────────────────────────────────────


def test_partition_classifies_all_link_types():
    """Partition correctly routes each device link to the right path attribute."""
    dev = _make_part_device(
        links=[
            "/dev/disk/by-id/ata-Samsung-part1",
            "/dev/disk/by-id/wwn-0xabc-part1",
            "/dev/disk/by-path/pci-0000:00:17.0-ata-1-part1",
            "/dev/disk/by-partuuid/acb8374d-fb60-4cb0-8ac4-273417c6f847",
            "/dev/disk/by-partlabel/EFI",
            "/dev/disk/by-label/SYSTEM",
            "/dev/disk/by-uuid/6432-935A",
        ]
    )
    with patch("builtins.open", _proc_mounts()):
        p = Partition(dev)

    assert p.get_byid_path() == [
        "/dev/disk/by-id/ata-Samsung-part1",
        "/dev/disk/by-id/wwn-0xabc-part1",
    ]
    assert p.get_bypath_path() == "/dev/disk/by-path/pci-0000:00:17.0-ata-1-part1"
    assert p.get_bypartuuid_path() == "/dev/disk/by-partuuid/acb8374d-fb60-4cb0-8ac4-273417c6f847"
    assert p.get_bypartlabel_path() == "/dev/disk/by-partlabel/EFI"
    assert p.get_bylabel_path() == "/dev/disk/by-label/SYSTEM"
    assert p.get_byuuid_path() == "/dev/disk/by-uuid/6432-935A"


def test_partition_multiple_byid_links():
    """Partition accumulates multiple by-id links into a list."""
    dev = _make_part_device(
        links=[
            "/dev/disk/by-id/ata-Samsung-part1",
            "/dev/disk/by-id/wwn-0x5002539c-part1",
            "/dev/disk/by-id/nvme-Samsung-part1",
        ]
    )
    with patch("builtins.open", _proc_mounts()):
        p = Partition(dev)

    assert len(p.get_byid_path()) == 3


def test_partition_no_device_links_returns_defaults():
    """Partition sets empty/'' path attributes when no device links are present."""
    dev = _make_part_device(links=[])
    with patch("builtins.open", _proc_mounts()):
        p = Partition(dev)

    assert not p.get_byid_path()
    assert p.get_bypath_path() == ""
    assert p.get_bypartuuid_path() == ""
    assert p.get_bypartlabel_path() == ""
    assert p.get_bylabel_path() == ""
    assert p.get_byuuid_path() == ""


# ── Partition.__init__ – mount/free space parsing ─────────────────────────────


def test_partition_mounted_path_is_extracted():
    """Partition reads free_size and mounting_point from /proc/mounts + statvfs."""
    dev = _make_part_device(name="sdb1")
    m = _proc_mounts(("/dev/sdb1", "/home"))
    with (patch("builtins.open", m),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=2_097_152))):
        p = Partition(dev)

    assert p.get_filesystem().get_fs_free_size() == 2_097_152
    assert p.get_filesystem().get_fs_mounting_point() == "/home"


def test_partition_unmounted_leaves_defaults():
    """Partition leaves free_size=0 and mount_point='' when device is not in /proc/mounts."""
    dev = _make_part_device(name="sda2")
    m = _proc_mounts(("/dev/sda1", "/"))  # sda1, not sda2
    with patch("builtins.open", m):
        p = Partition(dev)

    assert p.get_filesystem().get_fs_free_size() == 0
    assert p.get_filesystem().get_fs_mounting_point() == ""


def test_partition_multiple_mounts_matches_correct_one():
    """Partition picks the matching entry when /proc/mounts has many lines."""
    dev = _make_part_device(name="sda3")
    m = _proc_mounts(("/dev/sda1", "/"), ("/dev/sda2", "/boot"), ("/dev/sda3", "/data"))
    with (patch("builtins.open", m),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=999999))):
        p = Partition(dev)

    assert p.get_filesystem().get_fs_free_size() == 999999
    assert p.get_filesystem().get_fs_mounting_point() == "/data"


def test_partition_empty_proc_mounts_leaves_defaults():
    """Partition handles empty /proc/mounts gracefully (free_size=0, mount='')."""
    dev = _make_part_device(name="sda1")
    with patch("builtins.open", _proc_mounts()):
        p = Partition(dev)

    assert p.get_filesystem().get_fs_free_size() == 0
    assert p.get_filesystem().get_fs_mounting_point() == ""


# ── Partition size helpers ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "units, exp_unit",
    [
        (0, "GB"),  # metric
        (1, "GiB"),  # IEC
        (2, "GB"),  # legacy
    ],
)
def test_partition_get_part_size_in_hrf(units, exp_unit):
    """get_part_size_in_hrf() returns the size in the requested unit system."""
    # part_size='2097152' → 2097152 × 512 bytes = 1 GiB exactly
    dev = _make_part_device(part_size="2097152")
    with patch("builtins.open", _proc_mounts()):
        p = Partition(dev)

    value, unit = p.get_part_size_in_hrf(units=units)
    assert unit == exp_unit
    if units == 1:
        assert value == pytest.approx(1.0)
    else:
        assert value == pytest.approx(
            2_097_152 * 512 / (1_000**3 if units == 0 else 1_024**3)
        )


@pytest.mark.parametrize(
    "units, exp_unit",
    [
        (0, "GB"),
        (1, "GiB"),
        (2, "GB"),
    ],
)
def test_partition_get_fs_free_size_in_hrf(units, exp_unit):
    """get_fs_free_size_in_hrf() returns free space in the requested unit system."""
    # statvfs returns 2097152 blocks × 512 bytes = 1 GiB free
    dev = _make_part_device(name="sda1")
    m = _proc_mounts(("/dev/sda1", "/mnt"))
    with (patch("builtins.open", m),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=2_097_152))):
        p = Partition(dev)

    value, unit = p.get_filesystem().get_fs_free_size_in_hrf(units=units)
    assert unit == exp_unit
    if units == 1:
        assert value == pytest.approx(1.0)
    else:
        assert value == pytest.approx(
            2_097_152 * 512 / (1_000**3 if units == 0 else 1_024**3)
        )


# ── Partition – NVMe naming convention ───────────────────────────────────────


def test_partition_nvme_partition_name():
    """Partition handles nvme0n1p1 style names correctly."""
    dev = _make_part_device(name="nvme0n1p1", dev_id="259:1")
    with patch("builtins.open", _proc_mounts()):
        p = Partition(dev)

    assert p.get_name() == "nvme0n1p1"
    assert p.get_path() == "/dev/nvme0n1p1"


# ── additional branch-coverage tests ─────────────────────────────────────────


def test_partition_unknown_link_prefix_is_ignored():
    """A device link with an unrecognised prefix falls through all checks (branch 109->90)."""
    dev = _make_part_device(
        links=[
            "/dev/disk/by-id/ata-Samsung-part1",
            "/dev/disk/by-diskseq/123",  # unrecognised prefix → skipped
            "/dev/disk/by-uuid/6432-935A",
        ]
    )
    with patch("builtins.open", _proc_mounts()):
        p = Partition(dev)

    assert p.get_byid_path() == ["/dev/disk/by-id/ata-Samsung-part1"]
    assert p.get_byuuid_path() == "/dev/disk/by-uuid/6432-935A"


# ── Partition.get_filesystem() ────────────────────────────────────────────────


def test_partition_get_filesystem_returns_filesystem_info():
    """get_filesystem() returns a FileSystem instance with correct data."""
    dev = _make_part_device(
        name="sda1",
        fs_type="ext4",
        fs_label="ROOT",
        fs_uuid="d54d33ea-d892-44d9-ae24-e3c6216d7a32",
    )
    m = _proc_mounts(("/dev/sda1", "/"))
    with (patch("builtins.open", m),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=500000))):
        p = Partition(dev)

    fs = p.get_filesystem()
    assert isinstance(fs, FileSystem)
    assert fs.get_fs_type() == "ext4"
    assert fs.get_fs_label() == "ROOT"
    assert fs.get_fs_free_size() == 500000
    assert fs.get_fs_mounting_point() == "/"


# ── Partition.__repr__ ─────────────────────────────────────────────────────


def test_partition_repr():
    """repr() output contains all partition attribute values."""
    dev = _make_part_device(
        name="sda1",
        dev_id="8:1",
        scheme="gpt",
        part_label="Boot",
        part_uuid="abcd-1234",
        part_type="ebd0a0a2-b9e5-4433-87c0-68b6b72699c7",
        part_number="1",
        part_offset="2048",
        part_size="1048576",
    )
    with patch("builtins.open", _proc_mounts()):
        p = Partition(dev)

    result = repr(p)
    assert "Partition(" in result
    assert "sda1" in result
    assert "/dev/sda1" in result
    assert "8:1" in result
    assert "gpt" in result
    assert "Boot" in result
    assert "abcd-1234" in result
    assert "1048576" in result
    assert "filesystem=" in result


# End
