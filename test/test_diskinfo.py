#
#    Unit tests for `diskinfo` module (pytest style)
#    Peter Sulyok (C) 2022-2026.
#
from unittest.mock import patch, MagicMock
import pytest
from diskinfo import Disk, DiskType
from diskinfo.diskinfo import DiskInfo


# ── helpers ───────────────────────────────────────────────────────────────────


def _make_disk(
    name: str, disk_type: int, serial: str = None, size: int = 10_000
) -> Disk:
    """Return a fully-initialised Disk stub (no pyudev required)."""
    d = Disk.__new__(Disk)
    d._Disk__name = name
    d._Disk__path = f'/dev/{name}'
    d._Disk__type = disk_type
    d._Disk__serial_number = serial or name
    d._Disk__size = size
    d._Disk__byid_path = []
    d._Disk__bypath_path = []
    d._Disk__wwn = None
    d._Disk__model = None
    d._Disk__firmware = None
    d._Disk__device_id = '8:0'
    d._Disk__physical_block_size = 512
    d._Disk__logical_block_size = 512
    d._Disk__part_table_type = 'gpt'
    d._Disk__part_table_uuid = None
    d._Disk__partitions = []
    return d


def _make_diskinfo(disks: list) -> DiskInfo:
    """Return a DiskInfo with a pre-populated disk list (no pyudev required)."""
    di = DiskInfo.__new__(DiskInfo)
    di._DiskInfo__disk_list = list(disks)
    return di


# ── DiskInfo.__init__ ────────────────────────────────────────────────────────


def test_diskinfo_init_discovers_disks():
    """DiskInfo.__init__() collects all non-empty block devices from pyudev."""
    ssd = _make_disk('sda', DiskType.SSD, serial='SSD001')
    hdd = _make_disk('sdb', DiskType.HDD, serial='HDD001')
    nvme = _make_disk('nvme0n1', DiskType.NVME, serial='NVM001')

    fake_devs = [MagicMock(), MagicMock(), MagicMock()]
    mock_ctx = MagicMock()
    mock_ctx.list_devices.return_value = fake_devs
    disk_queue = iter([ssd, hdd, nvme])

    with (
        patch('diskinfo.diskinfo.Context', return_value=mock_ctx),
        patch('diskinfo.diskinfo.Disk', side_effect=lambda _device: next(disk_queue)),
    ):
        di = DiskInfo()

    assert di.get_disk_number() == 3


def test_diskinfo_init_skips_empty_loop_devices():
    """DiskInfo.__init__() excludes loop devices whose size is 0."""
    ssd = _make_disk('sda', DiskType.SSD, serial='SSD001', size=10_000)
    empty_loop = _make_disk('loop0', DiskType.LOOP, serial='', size=0)

    fake_devs = [MagicMock(), MagicMock()]
    mock_ctx = MagicMock()
    mock_ctx.list_devices.return_value = fake_devs
    disk_queue = iter([ssd, empty_loop])

    with (
        patch('diskinfo.diskinfo.Context', return_value=mock_ctx),
        patch('diskinfo.diskinfo.Disk', side_effect=lambda _device: next(disk_queue)),
    ):
        di = DiskInfo()

    assert di.get_disk_number() == 1
    assert di.get_disk_list()[0].get_name() == 'sda'


def test_diskinfo_init_keeps_nonempty_loop():
    """DiskInfo.__init__() retains loop devices that have a non-zero size."""
    loop = _make_disk('loop0', DiskType.LOOP, serial='L0', size=204_800)

    mock_ctx = MagicMock()
    mock_ctx.list_devices.return_value = [MagicMock()]
    disk_queue = iter([loop])

    with (
        patch('diskinfo.diskinfo.Context', return_value=mock_ctx),
        patch('diskinfo.diskinfo.Disk', side_effect=lambda _device: next(disk_queue)),
    ):
        di = DiskInfo()

    assert di.get_disk_number() == 1


# ── DiskInfo.get_disk_number ──────────────────────────────────────────────────


def test_get_disk_number_no_filter_counts_all():
    """get_disk_number() with no filters returns the total disk count."""
    disks = [
        _make_disk('sda', DiskType.SSD),
        _make_disk('sdb', DiskType.HDD),
        _make_disk('nvme0n1', DiskType.NVME),
        _make_disk('loop0', DiskType.LOOP, size=204_800),
    ]
    di = _make_diskinfo(disks)
    assert di.get_disk_number() == 4


def test_get_disk_number_included_filter():
    """get_disk_number() counts only disks whose type is in the included set."""
    disks = [
        _make_disk('sda', DiskType.SSD),
        _make_disk('sdb', DiskType.SSD),
        _make_disk('sdc', DiskType.HDD),
        _make_disk('nvme0n1', DiskType.NVME),
    ]
    di = _make_diskinfo(disks)
    assert di.get_disk_number(included={DiskType.SSD}) == 2
    assert di.get_disk_number(included={DiskType.HDD}) == 1
    assert di.get_disk_number(included={DiskType.NVME}) == 1
    assert di.get_disk_number(included={DiskType.LOOP}) == 0


def test_get_disk_number_excluded_only_raises_valueerror():
    """get_disk_number(excluded=...) alone always raises ValueError.

    The default ``included`` contains all disk types, so it always intersects
    with any non-empty ``excluded`` set — violating the disjointness constraint.
    """
    di = _make_diskinfo([_make_disk('sda', DiskType.SSD)])
    with pytest.raises(ValueError):
        di.get_disk_number(excluded={DiskType.SSD})
    with pytest.raises(ValueError):
        di.get_disk_number(excluded={DiskType.HDD})


def test_get_disk_number_included_and_excluded_overlap_raises_valueerror():
    """get_disk_number() raises ValueError when included and excluded share an element."""
    di = _make_diskinfo([_make_disk('sda', DiskType.SSD)])
    with pytest.raises(ValueError):
        di.get_disk_number(
            included={DiskType.SSD, DiskType.HDD}, excluded={DiskType.HDD}
        )
    with pytest.raises(ValueError):
        di.get_disk_number(
            included={DiskType.HDD, DiskType.SSD}, excluded={DiskType.SSD}
        )


def test_get_disk_number_empty_list_returns_zero():
    """get_disk_number() returns 0 when no disks were discovered."""
    di = _make_diskinfo([])
    assert di.get_disk_number() == 0


def test_get_disk_number_invalid_filter_raises_valueerror():
    """get_disk_number() raises ValueError when the same type is in both filter sets."""
    di = _make_diskinfo([_make_disk('sda', DiskType.SSD)])
    with pytest.raises(ValueError):
        di.get_disk_number(included={DiskType.SSD}, excluded={DiskType.SSD})
    with pytest.raises(ValueError):
        di.get_disk_number(
            included={DiskType.HDD, DiskType.SSD}, excluded={DiskType.SSD}
        )


# ── DiskInfo.get_disk_list ────────────────────────────────────────────────────


def test_get_disk_list_no_filter_returns_all():
    """get_disk_list() with no filters returns all discovered disks."""
    disks = [_make_disk('sda', DiskType.SSD), _make_disk('sdb', DiskType.HDD)]
    di = _make_diskinfo(disks)
    result = di.get_disk_list()
    assert len(result) == 2


def test_get_disk_list_included_filter():
    """get_disk_list() returns only disks whose type is in the included set."""
    disks = [
        _make_disk('sda', DiskType.SSD),
        _make_disk('sdb', DiskType.HDD),
        _make_disk('nvme0n1', DiskType.NVME),
    ]
    di = _make_diskinfo(disks)
    result = di.get_disk_list(included={DiskType.SSD})
    assert len(result) == 1
    assert result[0].get_name() == 'sda'


def test_get_disk_list_excluded_only_raises_valueerror():
    """get_disk_list(excluded=...) alone always raises ValueError.

    The default ``included`` contains all disk types, so it always intersects
    with any non-empty ``excluded`` set — violating the disjointness constraint.
    """
    di = _make_diskinfo([_make_disk('sda', DiskType.SSD)])
    with pytest.raises(ValueError):
        di.get_disk_list(excluded={DiskType.HDD})
    with pytest.raises(ValueError):
        di.get_disk_list(excluded={DiskType.SSD})


def test_get_disk_list_sorting_ascending():
    """get_disk_list() returns disks in alphabetical order when sorting=True."""
    disks = [
        _make_disk('sdc', DiskType.HDD),
        _make_disk('sda', DiskType.HDD),
        _make_disk('sdb', DiskType.HDD),
    ]
    di = _make_diskinfo(disks)
    result = di.get_disk_list(sorting=True)
    assert [d.get_name() for d in result] == ['sda', 'sdb', 'sdc']


def test_get_disk_list_sorting_descending():
    """get_disk_list() returns disks in reverse alphabetical order with rev_order=True."""
    disks = [
        _make_disk('sda', DiskType.HDD),
        _make_disk('sdb', DiskType.HDD),
        _make_disk('sdc', DiskType.HDD),
    ]
    di = _make_diskinfo(disks)
    result = di.get_disk_list(sorting=True, rev_order=True)
    assert [d.get_name() for d in result] == ['sdc', 'sdb', 'sda']


def test_get_disk_list_no_sort_preserves_discovery_order():
    """get_disk_list() preserves discovery order when sorting=False."""
    disks = [
        _make_disk('sdc', DiskType.HDD),
        _make_disk('sda', DiskType.HDD),
        _make_disk('sdb', DiskType.HDD),
    ]
    di = _make_diskinfo(disks)
    result = di.get_disk_list()
    assert [d.get_name() for d in result] == ['sdc', 'sda', 'sdb']


def test_get_disk_list_invalid_filter_raises_valueerror():
    """get_disk_list() raises ValueError on conflicting included/excluded filters."""
    di = _make_diskinfo([_make_disk('sda', DiskType.SSD)])
    with pytest.raises(ValueError):
        di.get_disk_list(included={DiskType.SSD}, excluded={DiskType.SSD})


def test_get_disk_list_empty_returns_empty():
    """get_disk_list() returns an empty list when no disks were discovered."""
    di = _make_diskinfo([])
    assert not di.get_disk_list()


# ── DiskInfo.__contains__ ─────────────────────────────────────────────────────


def test_contains_found_by_serial_number():
    """'disk in di' returns True when the disk's serial number is in the list."""
    registered = _make_disk('sda', DiskType.SSD, serial='SN12345')
    di = _make_diskinfo([registered])

    query = _make_disk('sda', DiskType.SSD, serial='SN12345')
    assert query in di


def test_contains_not_found():
    """'disk in di' returns False when no disk in the list has the same serial."""
    registered = _make_disk('sda', DiskType.SSD, serial='SN12345')
    di = _make_diskinfo([registered])

    query = _make_disk('sdb', DiskType.SSD, serial='SN99999')
    assert query not in di


def test_contains_empty_list_returns_false():
    """'disk in di' returns False when the disk list is empty."""
    di = _make_diskinfo([])
    query = _make_disk('sda', DiskType.SSD, serial='SN12345')
    assert query not in di


def test_contains_multiple_disks_correct_match():
    """'disk in di' matches by serial number among multiple disks."""
    disks = [
        _make_disk('sda', DiskType.SSD, serial='AAA'),
        _make_disk('sdb', DiskType.HDD, serial='BBB'),
        _make_disk('sdc', DiskType.NVME, serial='CCC'),
    ]
    di = _make_diskinfo(disks)

    assert _make_disk('x', DiskType.SSD, serial='AAA') in di
    assert _make_disk('x', DiskType.HDD, serial='BBB') in di
    assert _make_disk('x', DiskType.NVME, serial='CCC') in di
    assert _make_disk('x', DiskType.SSD, serial='ZZZ') not in di


# ── DiskInfo.__repr__ ─────────────────────────────────────────────────────────


def test_repr_contains_disk_count():
    """repr(DiskInfo) includes the total number of discovered disks."""
    disks = [_make_disk('sda', DiskType.SSD), _make_disk('sdb', DiskType.HDD)]
    di = _make_diskinfo(disks)
    result = repr(di)
    assert 'DiskInfo' in result
    assert 'number_of_disks=2' in result


def test_repr_empty_diskinfo():
    """repr(DiskInfo) with no disks shows number_of_disks=0."""
    di = _make_diskinfo([])
    assert 'number_of_disks=0' in repr(di)


# End
