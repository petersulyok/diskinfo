#
#    Unit tests for `filesystem` module (pytest style)
#    Peter Sulyok (C) 2022-2026.
#
import os
from unittest.mock import MagicMock, patch, mock_open
import pytest
from diskinfo.filesystem import FileSystem


# ── mock helpers ──────────────────────────────────────────────────────────────


def _make_fs_device(
    path: str = "/dev/sdb",
    fs_label: str = "MyFS",
    fs_uuid: str = "d54d33ea-d892-44d9-ae24-e3c6216d7a32",
    fs_type: str = "ext4",
    fs_version: str = "1.0",
    fs_usage: str = "filesystem",
) -> MagicMock:
    """Return a MagicMock satisfying all pyudev.Device patterns in FileSystem.__init__."""
    dev = MagicMock()
    dev.device_node = path
    props = {
        # _pyudev_getenc tries _ENC first, falls back to plain key
        "ID_FS_LABEL_ENC": None,
        "ID_FS_LABEL": fs_label,
        "ID_FS_UUID_ENC": None,
        "ID_FS_UUID": fs_uuid,
        "ID_FS_TYPE": fs_type,
        "ID_FS_VERSION": fs_version,
        "ID_FS_USAGE": fs_usage,
    }
    dev.get.side_effect = props.get
    return dev


def _proc_mounts(*entries):
    """Return a mock_open for /proc/mounts with the given (device, mountpoint) entries.

    Each entry is a tuple of (device_path, mount_point). Extra fields are filled with defaults.
    If no entries are provided, an empty /proc/mounts is simulated.
    """
    lines = ""
    for dev_path, mount_point in entries:
        lines += f"{dev_path} {mount_point} ext4 rw,relatime 0 0\n"
    return mock_open(read_data=lines)


def _statvfs_result(f_bavail: int = 0, f_frsize: int = 512) -> os.statvfs_result:
    """Return an os.statvfs_result with the given f_bavail and f_frsize."""
    # os.statvfs_result takes a 10-tuple:
    # (f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, f_favail, f_flag, f_namemax)
    return os.statvfs_result((4096, f_frsize, 1000000, 500000, f_bavail, 100000, 90000, 90000, 0, 255))


# ── FileSystem.__init__ – basic attributes ───────────────────────────────


def test_filesystem_stores_all_attributes():
    """FileSystem stores every attribute correctly from the pyudev device."""
    dev = _make_fs_device(
        path="/dev/sdb",
        fs_label="DATA",
        fs_uuid="abcd-1234",
        fs_type="ext4",
        fs_version="1.0",
        fs_usage="filesystem",
    )
    m = _proc_mounts(("/dev/sdb", "/mnt/data"))
    with (patch("builtins.open", m),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=1000, f_frsize=512))):
        fs = FileSystem(dev)

    assert fs.get_fs_label() == "DATA"
    assert fs.get_fs_uuid() == "abcd-1234"
    assert fs.get_fs_type() == "ext4"
    assert fs.get_fs_version() == "1.0"
    assert fs.get_fs_usage() == "filesystem"
    assert fs.get_fs_free_size() == 1000
    assert fs.get_fs_mounting_point() == "/mnt/data"


# ── FileSystem.__init__ – /proc/mounts parsing ──────────────────────────


def test_filesystem_unmounted_leaves_defaults():
    """FileSystem leaves free_size=0 and mount_point='' when device is not mounted."""
    dev = _make_fs_device(path="/dev/sdb")
    m = _proc_mounts(("/dev/sda1", "/"))  # sda1, not sdb
    with patch("builtins.open", m):
        fs = FileSystem(dev)

    assert fs.get_fs_free_size() == 0
    assert fs.get_fs_mounting_point() == ""


def test_filesystem_empty_proc_mounts_leaves_defaults():
    """FileSystem handles empty /proc/mounts gracefully."""
    dev = _make_fs_device(path="/dev/sdb")
    m = _proc_mounts()
    with patch("builtins.open", m):
        fs = FileSystem(dev)

    assert fs.get_fs_free_size() == 0
    assert fs.get_fs_mounting_point() == ""


def test_filesystem_short_proc_mounts_line_skipped():
    """FileSystem skips /proc/mounts lines with fewer than 2 fields."""
    dev = _make_fs_device(path="/dev/sdb")
    data = "\n/dev/sdb /mnt ext4 rw,relatime 0 0\n"
    with (patch("builtins.open", mock_open(read_data=data)),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=500, f_frsize=512))):
        fs = FileSystem(dev)

    assert fs.get_fs_mounting_point() == "/mnt"
    assert fs.get_fs_free_size() == 500


def test_filesystem_multiple_mounts_matches_correct_one():
    """FileSystem picks the matching entry when /proc/mounts has many lines."""
    dev = _make_fs_device(path="/dev/sdb")
    m = _proc_mounts(("/dev/sda1", "/"), ("/dev/sdb", "/data"), ("/dev/sdc1", "/boot"))
    with (patch("builtins.open", m),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=999999, f_frsize=512))):
        fs = FileSystem(dev)

    assert fs.get_fs_free_size() == 999999
    assert fs.get_fs_mounting_point() == "/data"


def test_filesystem_statvfs_computes_free_size_correctly():
    """FileSystem correctly computes free size from statvfs f_bavail and f_frsize."""
    dev = _make_fs_device(path="/dev/sdb")
    # f_bavail=1024, f_frsize=4096 → (1024 * 4096) / 512 = 8192 blocks of 512 bytes
    m = _proc_mounts(("/dev/sdb", "/mnt"))
    with (patch("builtins.open", m),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=1024, f_frsize=4096))):
        fs = FileSystem(dev)

    assert fs.get_fs_free_size() == 8192


# ── FileSystem.__init__ – error handling ─────────────────────────────────


def test_filesystem_statvfs_oserror_leaves_free_size_zero():
    """FileSystem keeps mount point but leaves free_size=0 when statvfs raises OSError."""
    dev = _make_fs_device(path="/dev/sdb")
    m = _proc_mounts(("/dev/sdb", "/mnt"))
    with (patch("builtins.open", m),
          patch("os.statvfs", side_effect=OSError("stale mount"))):
        fs = FileSystem(dev)

    assert fs.get_fs_mounting_point() == "/mnt"
    assert fs.get_fs_free_size() == 0


def test_filesystem_proc_mounts_oserror_leaves_defaults():
    """FileSystem leaves defaults when /proc/mounts cannot be read."""
    dev = _make_fs_device(path="/dev/sdb")
    with patch("builtins.open", side_effect=OSError("no /proc")):
        fs = FileSystem(dev)

    assert fs.get_fs_mounting_point() == ""
    assert fs.get_fs_free_size() == 0


# ── FileSystem – human-readable size ─────────────────────────────────────


@pytest.mark.parametrize(
    "units, exp_unit",
    [
        (0, "GB"),
        (1, "GiB"),
        (2, "GB"),
    ],
)
def test_filesystem_get_fs_free_size_in_hrf(units, exp_unit):
    """get_fs_free_size_in_hrf() returns free space in the requested unit system."""
    dev = _make_fs_device(path="/dev/sdb")
    # 2_097_152 blocks × 512 bytes = 1 GiB
    m = _proc_mounts(("/dev/sdb", "/mnt"))
    with (patch("builtins.open", m),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=2_097_152, f_frsize=512))):
        fs = FileSystem(dev)

    value, unit = fs.get_fs_free_size_in_hrf(units=units)
    assert unit == exp_unit
    if units == 1:
        assert value == pytest.approx(1.0)
    else:
        assert value == pytest.approx(
            2_097_152 * 512 / (1_000**3 if units == 0 else 1_024**3)
        )


# ── FileSystem – __repr__ ────────────────────────────────────────────────


def test_filesystem_repr():
    """repr() output contains all filesystem attribute values."""
    dev = _make_fs_device(
        path="/dev/sdb",
        fs_label="DATA",
        fs_uuid="abcd-1234",
        fs_type="ext4",
        fs_version="1.0",
        fs_usage="filesystem",
    )
    m = _proc_mounts(("/dev/sdb", "/mnt"))
    with (patch("builtins.open", m),
          patch("os.statvfs", return_value=_statvfs_result(f_bavail=100, f_frsize=512))):
        fs = FileSystem(dev)

    result = repr(fs)
    assert "FileSystem(" in result
    assert "DATA" in result
    assert "abcd-1234" in result
    assert "ext4" in result
    assert "1.0" in result
    assert "filesystem" in result
    assert "/mnt" in result


# End
