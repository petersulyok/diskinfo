#
#    Unit tests for `disk` module (pytest style)
#    Peter Sulyok (C) 2022-2026.
#
# pylint: disable=redefined-outer-name
import os
import uuid
import random
import tempfile
import contextlib
from typing import List
from unittest.mock import patch, MagicMock, PropertyMock
import pytest
import pySMART
from pyudev import DeviceNotFoundAtPathError
from pySMART import Device
from diskinfo import Disk, DiskType


# ── mock device factories ─────────────────────────────────────────────────────


def _make_device(
    name: str,
    dev_id: str,
    size: int,
    phys_bs: int,
    log_bs: int,
    rotational: str = None,
    serial: str = None,
    firmware: str = None,
    wwn: str = None,
    model: str = None,
    part_table_type: str = 'gpt',
    part_table_uuid: str = None,
    byid_links: List[str] = None,
    bypath_links: List[str] = None,
    children: list = None,
) -> MagicMock:
    """Return a MagicMock satisfying all pyudev.Device access patterns in Disk.__init__."""
    dev = MagicMock()
    dev.sys_name = name
    dev.device_node = f'/dev/{name}'
    dev.device_type = 'disk'
    dev.parent = MagicMock()

    # .attributes.asint / .asstring
    int_attrs = {
        'size': size,
        'queue/physical_block_size': phys_bs,
        'queue/logical_block_size': log_bs,
    }
    str_attrs: dict = {'dev': dev_id}
    if rotational is not None:
        str_attrs['queue/rotational'] = rotational

    dev.attributes.asint.side_effect = lambda k: int_attrs[k]
    dev.attributes.asstring.side_effect = lambda k: str_attrs[k]

    # .get(key) – udev properties; include _ENC variant for model decoding
    model_enc = model.replace(' ', '\\x20') if (model and ' ' in model) else None
    props = {
        'ID_SERIAL_SHORT': serial,
        'ID_REVISION': firmware,
        'ID_WWN': wwn,
        'ID_PART_TABLE_TYPE': part_table_type,
        'ID_PART_TABLE_UUID': part_table_uuid,
        'ID_MODEL_ENC': model_enc,
        'ID_MODEL': model.replace(' ', '_') if model else None,
    }
    dev.get.side_effect = props.get

    # .device_links – by-id entries first, then by-path
    dev.device_links = list(byid_links or []) + list(bypath_links or [])

    # .children – partition child devices
    dev.children = list(children or [])
    return dev


def _make_partition_device(
    disk_dev_id: str, idx: int, disk_name: str, is_nvme: bool = False
) -> MagicMock:
    """Return a minimal MagicMock that satisfies Partition.__init__."""
    part_name = disk_name + (f'p{idx}' if is_nvme else str(idx))
    major = disk_dev_id.split(':')[0]
    part = MagicMock()
    part.sys_name = part_name
    part.device_node = f'/dev/{part_name}'
    part.device_type = 'partition'
    part.attributes.asstring.return_value = f'{major}:{idx}'
    part.device_links = []
    part.get.return_value = None
    return part


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def ssd_device():
    """Mock pyudev Device representing a SATA SSD (Samsung 850 PRO 1 TB, rotational=0)."""
    return _make_device(
        name='sda',
        dev_id='8:0',
        size=2000409264,
        phys_bs=512,
        log_bs=512,
        rotational='0',
        serial='ABC12345',
        firmware='EXM04B6Q',
        wwn='0x5002539c407255be',
        model='Samsung SSD 850 PRO 1TB',
        part_table_type='gpt',
        part_table_uuid=str(uuid.uuid4()),
        byid_links=[
            '/dev/disk/by-id/ata-Samsung_SSD_850_PRO_1TB_ABC12345',
            '/dev/disk/by-id/wwn-0x5002539c407255be',
        ],
        bypath_links=[
            '/dev/disk/by-path/pci-0000:00:17.0-ata-1',
            '/dev/disk/by-path/pci-0000:00:17.0-ata-1.0',
        ],
    )


@pytest.fixture
def hdd_device():
    """Mock pyudev Device representing a SATA HDD (WD 8 TB, rotational=1, 4K physical sectors)."""
    return _make_device(
        name='sdb',
        dev_id='8:16',
        size=15628053168,
        phys_bs=4096,
        log_bs=512,
        rotational='1',
        serial='WXB2345678',
        firmware='HAFBA',
        wwn='0x5000cca291d5aba5',
        model='WDC WD80FLAX-68VNTN0',
        part_table_type='gpt',
        part_table_uuid=str(uuid.uuid4()),
        byid_links=[
            '/dev/disk/by-id/ata-WDC_WD80FLAX-68VNTN0_WXB2345678',
            '/dev/disk/by-id/wwn-0x5000cca291d5aba5',
        ],
        bypath_links=[
            '/dev/disk/by-path/pci-0000:00:17.0-ata-2',
            '/dev/disk/by-path/pci-0000:00:17.0-ata-2.0',
        ],
    )


@pytest.fixture
def nvme_device():
    """Mock pyudev Device representing an NVMe SSD (Samsung 970 EVO Plus 512 GB)."""
    return _make_device(
        name='nvme0n1',
        dev_id='259:0',
        size=1000215216,
        phys_bs=512,
        log_bs=512,
        serial='BTNYM23456',
        firmware='ADH00101',
        wwn='eui.0025385b914dc239',
        model='Samsung SSD 970 EVO Plus 512GB',
        part_table_type='gpt',
        part_table_uuid=str(uuid.uuid4()),
        byid_links=[
            '/dev/disk/by-id/nvme-Samsung_SSD_970_EVO_Plus_512GB_BTNYM23456',
            '/dev/disk/by-id/nvme-eui.0025385b914dc239',
        ],
        bypath_links=['/dev/disk/by-path/pci-0000:02:00.0-nvme-1'],
    )


@pytest.fixture
def loop_device():
    """Mock pyudev Device representing a loop device (loop0, major=7, 100 MiB)."""
    return _make_device(
        name='loop0',
        dev_id='7:0',
        size=204800,
        phys_bs=512,
        log_bs=512,
        part_table_type='gpt',
        part_table_uuid=str(uuid.uuid4()),
    )


# ── pyudev patch helper ───────────────────────────────────────────────────────


@contextlib.contextmanager
def pyudev_patched(mock_device, readlink_return: str = None):
    """Patch diskinfo.disk's pyudev imports so no real hardware is accessed.

    * ``Context()`` returns a mock whose ``list_devices(subsystem='block')``
      yields *mock_device*; ``list_devices(subsystem='hwmon')`` returns ``[]``
      (the resulting ``ValueError`` on unpacking is caught, leaving
      ``hwmon_path`` as the empty string).
    * ``Devices.from_name`` always returns *mock_device*.
    * ``os.readlink`` is patched when *readlink_return* is provided
      (required for by-id / by-path initialisation paths).
    """
    mock_ctx = MagicMock()

    def _list_devices(**kwargs):
        return [mock_device] if kwargs.get('subsystem') == 'block' else []

    mock_ctx.list_devices.side_effect = _list_devices

    with contextlib.ExitStack() as stack:
        stack.enter_context(patch('diskinfo.disk.Context', return_value=mock_ctx))
        mock_devs = stack.enter_context(patch('diskinfo.disk.Devices'))
        mock_devs.from_name.return_value = mock_device
        if readlink_return is not None:
            stack.enter_context(patch('os.readlink', return_value=readlink_return))
        yield mock_devs


# ── __init__ – positive ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    'fixture_name, expected_type',
    [
        ('nvme_device', DiskType.NVME),
        ('ssd_device', DiskType.SSD),
        ('hdd_device', DiskType.HDD),
        ('loop_device', DiskType.LOOP),
    ],
)
def test_init_by_disk_name(fixture_name, expected_type, request):
    """Disk(disk_name) creates an instance with the correct type and attributes."""
    mock_dev = request.getfixturevalue(fixture_name)
    with pyudev_patched(mock_dev):
        d = Disk(mock_dev.sys_name)

    assert d.get_name() == mock_dev.sys_name
    assert d.get_path() == mock_dev.device_node
    assert d.get_type() == expected_type
    assert d.get_size() == mock_dev.attributes.asint('size')
    assert d.get_device_id() == mock_dev.attributes.asstring('dev')
    assert d.get_physical_block_size() == mock_dev.attributes.asint(
        'queue/physical_block_size'
    )
    assert d.get_logical_block_size() == mock_dev.attributes.asint(
        'queue/logical_block_size'
    )
    assert d.get_partition_table_type() == mock_dev.get('ID_PART_TABLE_TYPE')
    assert d.get_partition_table_uuid() == mock_dev.get('ID_PART_TABLE_UUID')
    if expected_type != DiskType.LOOP:
        assert d.get_serial_number() == mock_dev.get('ID_SERIAL_SHORT')
        assert d.get_firmware() == mock_dev.get('ID_REVISION')
        assert d.get_wwn() == mock_dev.get('ID_WWN')
        byid = [lnk for lnk in mock_dev.device_links if '/by-id' in lnk]
        bypath = [lnk for lnk in mock_dev.device_links if '/by-path' in lnk]
        assert d.get_byid_path() == byid
        assert d.get_bypath_path() == bypath


@pytest.mark.parametrize('fixture_name', ['ssd_device', 'hdd_device', 'nvme_device'])
def test_init_by_byid_name(fixture_name, request):
    """Disk(byid_name=...) resolves the by-id symlink and finds the correct disk."""
    mock_dev = request.getfixturevalue(fixture_name)
    byid_link = next(lnk for lnk in mock_dev.device_links if '/by-id' in lnk)
    byid_name = os.path.basename(byid_link)
    link_target = f'../../{mock_dev.sys_name}'

    with pyudev_patched(mock_dev, readlink_return=link_target):
        d = Disk(byid_name=byid_name)
    assert d.get_name() == mock_dev.sys_name


@pytest.mark.parametrize('fixture_name', ['ssd_device', 'hdd_device'])
def test_init_by_bypath_name(fixture_name, request):
    """Disk(bypath_name=...) resolves the by-path symlink and finds the correct disk."""
    mock_dev = request.getfixturevalue(fixture_name)
    bypath_link = next(lnk for lnk in mock_dev.device_links if '/by-path' in lnk)
    bypath_name = os.path.basename(bypath_link)
    link_target = f'../../{mock_dev.sys_name}'

    with pyudev_patched(mock_dev, readlink_return=link_target):
        d = Disk(bypath_name=bypath_name)
    assert d.get_name() == mock_dev.sys_name


@pytest.mark.parametrize('fixture_name', ['ssd_device', 'hdd_device'])
def test_init_by_serial_number(fixture_name, request):
    """Disk(serial_number=...) locates the disk by scanning udev properties."""
    mock_dev = request.getfixturevalue(fixture_name)
    serial = mock_dev.get('ID_SERIAL_SHORT')

    with pyudev_patched(mock_dev):
        d = Disk(serial_number=serial)
    assert d.get_name() == mock_dev.sys_name
    assert d.get_serial_number() == serial


# ── __init__ – negative ───────────────────────────────────────────────────────


def test_init_no_parameters_raises_valueerror():
    """Disk() with no arguments raises ValueError."""
    with pytest.raises(ValueError):
        Disk()


def test_init_unknown_disk_name_raises_valueerror():
    """Disk('nonexistent') raises ValueError when pyudev cannot find the device."""
    mock_ctx = MagicMock()
    mock_ctx.list_devices.return_value = []
    with (
        patch('diskinfo.disk.Context', return_value=mock_ctx),
        patch('diskinfo.disk.Devices') as mock_devs,
    ):
        mock_devs.from_name.side_effect = DeviceNotFoundAtPathError(
            '/sys/class/block/nonexistent'
        )
        with pytest.raises(ValueError):
            Disk('nonexistent')


def test_init_invalid_serial_raises_valueerror(ssd_device):
    """Disk(serial_number=...) raises ValueError when no device matches."""
    with pyudev_patched(ssd_device):
        with pytest.raises(ValueError):
            Disk(serial_number='XXXXXXXXXXXXXXXX')


def test_init_invalid_byid_name_raises_valueerror():
    """Disk(byid_name=...) raises ValueError when the by-id symlink is missing."""
    mock_ctx = MagicMock()
    mock_ctx.list_devices.return_value = []
    with (
        patch('diskinfo.disk.Context', return_value=mock_ctx),
        patch('diskinfo.disk.Devices'),
        patch('os.readlink', side_effect=OSError('no such file')),
    ):
        with pytest.raises(ValueError):
            Disk(byid_name='ata-nonexistent-disk')


def test_init_invalid_bypath_name_raises_valueerror():
    """Disk(bypath_name=...) raises ValueError when the by-path symlink is missing."""
    mock_ctx = MagicMock()
    mock_ctx.list_devices.return_value = []
    with (
        patch('diskinfo.disk.Context', return_value=mock_ctx),
        patch('diskinfo.disk.Devices'),
        patch('os.readlink', side_effect=FileNotFoundError('no such file')),
    ):
        with pytest.raises(ValueError):
            Disk(bypath_name='pci-0000:00:17.0-ata-99')


def test_init_wwn_bug_always_raises_valueerror(ssd_device):
    """Disk(wwn=...) always raises ValueError.

    This is a known bug in disk.py: the WWN lookup compares
    dev.get('ID_WWN') to ``serial_number`` (which is None) instead of
    the ``wwn`` argument, so no device is ever matched.
    """
    with pyudev_patched(ssd_device):
        with pytest.raises(ValueError):
            Disk(wwn=ssd_device.get('ID_WWN'))


# ── disk type predicates ──────────────────────────────────────────────────────


@pytest.mark.parametrize(
    'disk_type, is_ssd, is_hdd, is_nvme, is_loop, type_str',
    [
        (DiskType.SSD, True, False, False, False, DiskType.SSD_STR),
        (DiskType.HDD, False, True, False, False, DiskType.HDD_STR),
        (DiskType.NVME, False, False, True, False, DiskType.NVME_STR),
        (DiskType.LOOP, False, False, False, True, DiskType.LOOP_STR),
    ],
)
def test_disk_type_predicates(disk_type, is_ssd, is_hdd, is_nvme, is_loop, type_str):
    """Type-check helpers return the correct booleans and string for each disk type."""
    d = Disk.__new__(Disk)
    d._Disk__type = disk_type
    assert d.get_type() == disk_type
    assert d.is_ssd() is is_ssd
    assert d.is_hdd() is is_hdd
    assert d.is_nvme() is is_nvme
    assert d.is_loop() is is_loop
    assert d.get_type_str() == type_str


def test_get_type_str_unknown_raises_runtimeerror():
    """get_type_str() raises RuntimeError for an unrecognised type value."""
    d = Disk.__new__(Disk)
    d._Disk__type = 99999
    with pytest.raises(RuntimeError):
        d.get_type_str()


# ── get_size_in_hrf ───────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    'size_512, units, exp_value, exp_unit',
    [
        (1, 0, 512.0, 'B'),
        (1, 1, 512.0, 'B'),
        (1, 2, 512.0, 'B'),
        (3, 0, (3 * 512) / 1000, 'kB'),
        (3, 1, (3 * 512) / 1024, 'KiB'),
        (3, 2, (3 * 512) / 1024, 'KB'),
        (6144, 0, (6144 * 512) / 1e6, 'MB'),
        (6144, 1, (6144 * 512) / 1024**2, 'MiB'),
        (6144, 2, (6144 * 512) / 1024**2, 'MB'),
        (16777216, 0, (16777216 * 512) / 1e9, 'GB'),
        (16777216, 1, (16777216 * 512) / 1024**3, 'GiB'),
        (16777216, 2, (16777216 * 512) / 1024**3, 'GB'),
        (8589934592, 0, (8589934592 * 512) / 1e12, 'TB'),
        (8589934592, 1, (8589934592 * 512) / 1024**4, 'TiB'),
        (8589934592, 2, (8589934592 * 512) / 1024**4, 'TB'),
        (4398046511104, 0, (4398046511104 * 512) / 1e15, 'PB'),
        (4398046511104, 1, (4398046511104 * 512) / 1024**5, 'PiB'),
        (4398046511104, 2, (4398046511104 * 512) / 1024**5, 'PB'),
    ],
)
def test_get_size_in_hrf(size_512, units, exp_value, exp_unit):
    """get_size_in_hrf() returns correct (value, unit) for every unit system."""
    d = Disk.__new__(Disk)
    d._Disk__size = size_512
    value, unit = d.get_size_in_hrf(units)
    assert value == pytest.approx(exp_value)
    assert unit == exp_unit


# ── get_temperature ───────────────────────────────────────────────────────────


def test_get_temperature_reads_hwmon_sysfs_file():
    """get_temperature() divides milli-degrees from an hwmon sysfs file by 1000."""
    d = Disk.__new__(Disk)
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='_temp1_input', delete=False
    ) as f:
        f.write('43000')
        hwmon_file = f.name
    try:
        d._Disk__hwmon_path = hwmon_file
        assert d.get_temperature() == 43.0
    finally:
        os.unlink(hwmon_file)


@pytest.mark.parametrize('fixture_name', ['ssd_device', 'hdd_device', 'nvme_device'])
def test_get_temperature_via_pysmart(fixture_name, request):
    """get_temperature() falls back to pySMART when hwmon path is absent."""
    mock_dev = request.getfixturevalue(fixture_name)
    with pyudev_patched(mock_dev):
        d = Disk(mock_dev.sys_name)

    # hwmon lookup found nothing → hwmon_path is ''
    assert d._Disk__hwmon_path == ''

    with (
        patch.object(Device, '__init__', return_value=None),
        patch('pySMART.Device.temperature', new_callable=PropertyMock) as mock_temp,
    ):
        mock_temp.return_value = 38
        temp = d.get_temperature(sudo=random.choice([True, False]))
    assert temp == 38.0


def test_get_temperature_loop_returns_none(loop_device):
    """get_temperature() returns None for a LOOP disk (pySMART finds no temperature)."""
    with pyudev_patched(loop_device):
        d = Disk(loop_device.sys_name)

    with (
        patch.object(Device, '__init__', return_value=None),
        patch('pySMART.Device.temperature', new_callable=PropertyMock) as mock_temp,
    ):
        mock_temp.return_value = None
        assert d.get_temperature() is None


def test_get_temperature_none_from_pysmart_returns_none(ssd_device):
    """get_temperature() returns None when pySMART reports no temperature."""
    with pyudev_patched(ssd_device):
        d = Disk(ssd_device.sys_name)

    with (
        patch.object(Device, '__init__', return_value=None),
        patch('pySMART.Device.temperature', new_callable=PropertyMock) as mock_temp,
    ):
        mock_temp.return_value = None
        assert d.get_temperature() is None


def test_get_temperature_none_hwmon_path_falls_through_to_pysmart(ssd_device):
    """get_temperature() skips hwmon when __hwmon_path is None and uses pySMART."""
    with pyudev_patched(ssd_device):
        d = Disk(ssd_device.sys_name)
    d._Disk__hwmon_path = None

    with (
        patch.object(Device, '__init__', return_value=None),
        patch('pySMART.Device.temperature', new_callable=PropertyMock) as mock_temp,
    ):
        mock_temp.return_value = 35
        assert d.get_temperature() == 35.0


# ── get_smart_data helpers ────────────────────────────────────────────────────

# Minimal valid smartctl --info output (5 lines; line[3] is empty = not standby)
_SMART_INFO_OK = ['smartctl 7.2', '', '', '', '# output']

# smartctl --info output signalling STANDBY at line[3]
_SMART_INFO_STANDBY = ['smartctl 7.2', '', '', 'Device is in STANDBY mode, exiting', '']


def _make_nvme_if_attrs() -> MagicMock:
    """Return a MagicMock with all NVMe if_attributes consumed by disk.py."""
    a = MagicMock()
    a.criticalWarning = 0
    a._temperature = 35
    a.availableSpare = 100
    a.availableSpareThreshold = 10
    a.percentageUsed = 2
    a.dataUnitsRead = 123_456
    a.dataUnitsWritten = 654_321
    a.hostReadCommands = 9_999_999
    a.hostWriteCommands = 7_777_777
    a.controllerBusyTime = 1_234
    a.powerCycles = 42
    a.powerOnHours = 1_565
    a.unsafeShutdowns = 5
    a.integrityErrors = 0
    a.errorEntries = 0
    a.warningTemperatureTime = 0
    a.criticalTemperatureTime = 0
    return a


def _make_hdd_legacy_attrs() -> list:
    """Return a list of MagicMocks representing pySMART legacy SMART attributes."""
    raw = [
        (
            5,
            'Reallocated_Sector_Ct',
            0x0033,
            100,
            100,
            10,
            'Pre-fail',
            'Always',
            '-',
            0,
        ),
        (9, 'Power_On_Hours', 0x0032, 95, 95, 0, 'Old_age', 'Always', '-', 23268),
        (12, 'Power_Cycle_Count', 0x0032, 92, 92, 0, 'Old_age', 'Always', '-', 7103),
        (
            190,
            'Airflow_Temperature_Cel',
            0x0032,
            72,
            45,
            0,
            'Old_age',
            'Always',
            '-',
            28,
        ),
    ]
    attrs = []
    for (
        num,
        name,
        flags,
        value_int,
        worst,
        thresh,
        _type,
        updated,
        when_failed,
        raw_int,
    ) in raw:
        a = MagicMock()
        a.num = num
        a.name = name
        a.flags = flags
        a.value_int = value_int
        a.worst = worst
        a.thresh = thresh
        a.type = _type
        a.updated = updated
        a.when_failed = when_failed
        a.raw_int = raw_int
        attrs.append(a)
    return attrs


# ── get_smart_data ────────────────────────────────────────────────────────────


def test_get_smart_data_nvme():
    """get_smart_data() returns all expected NVMe SMART attributes."""
    d = Disk.__new__(Disk)
    d._Disk__path = '/dev/nvme0n1'
    d._Disk__type = DiskType.NVME

    mock_if = _make_nvme_if_attrs()
    mock_sd = MagicMock()
    mock_sd.interface = 'nvme'
    mock_sd.smart_enabled = True
    mock_sd.smart_capable = True
    mock_sd.assessment = 'PASS'
    mock_sd.if_attributes = mock_if

    with (
        patch.object(pySMART.SMARTCTL, 'info', return_value=_SMART_INFO_OK),
        patch('pySMART.Device', return_value=mock_sd),
    ):
        sd = d.get_smart_data(nocheck=True, sudo=True)

    assert sd is not None
    assert sd.healthy is True
    assert sd.smart_enabled is True
    assert sd.smart_capable is True

    na = sd.nvme_attributes
    assert na.critical_warning == mock_if.criticalWarning
    assert na.temperature == mock_if._temperature
    assert na.available_spare == mock_if.availableSpare
    assert na.available_spare_threshold == mock_if.availableSpareThreshold
    assert na.percentage_used == mock_if.percentageUsed
    assert na.data_units_read == mock_if.dataUnitsRead
    assert na.data_units_written == mock_if.dataUnitsWritten
    assert na.host_read_commands == mock_if.hostReadCommands
    assert na.host_write_commands == mock_if.hostWriteCommands
    assert na.controller_busy_time == mock_if.controllerBusyTime
    assert na.power_cycles == mock_if.powerCycles
    assert na.power_on_hours == mock_if.powerOnHours
    assert na.unsafe_shutdowns == mock_if.unsafeShutdowns
    assert na.media_and_data_integrity_errors == mock_if.integrityErrors
    assert na.error_information_log_entries == mock_if.errorEntries
    assert na.warning_composite_temperature_time == mock_if.warningTemperatureTime
    assert na.critical_composite_temperature_time == mock_if.criticalTemperatureTime


def test_get_smart_data_hdd():
    """get_smart_data() returns all expected legacy SMART attributes for an HDD."""
    d = Disk.__new__(Disk)
    d._Disk__path = '/dev/sdb'
    d._Disk__type = DiskType.HDD

    legacy = _make_hdd_legacy_attrs()
    mock_sd = MagicMock()
    mock_sd.interface = 'ata'
    mock_sd.smart_enabled = True
    mock_sd.smart_capable = True
    mock_sd.assessment = 'PASS'
    mock_sd.if_attributes.legacyAttributes = legacy

    with (
        patch.object(pySMART.SMARTCTL, 'info', return_value=_SMART_INFO_OK),
        patch('pySMART.Device', return_value=mock_sd),
    ):
        sd = d.get_smart_data(nocheck=False, sudo=False)

    assert sd is not None
    assert sd.healthy is True
    assert len(sd.smart_attributes) == len(legacy)
    for j, attr in enumerate(sd.smart_attributes):
        exp = legacy[j]
        assert attr.id == exp.num
        assert attr.attribute_name == exp.name
        assert attr.flag == exp.flags
        assert attr.value == exp.value_int
        assert attr.worst == exp.worst
        assert attr.thresh == exp.thresh
        assert attr.type == exp.type
        assert attr.updated == exp.updated
        assert attr.when_failed == exp.when_failed
        assert attr.raw_value == exp.raw_int


def test_get_smart_data_fail_assessment():
    """get_smart_data() sets healthy=False when the SMART assessment is not PASS."""
    d = Disk.__new__(Disk)
    d._Disk__path = '/dev/sda'
    d._Disk__type = DiskType.SSD

    mock_sd = MagicMock()
    mock_sd.interface = 'ata'
    mock_sd.smart_enabled = True
    mock_sd.smart_capable = True
    mock_sd.assessment = 'FAIL'

    with (
        patch.object(pySMART.SMARTCTL, 'info', return_value=_SMART_INFO_OK),
        patch('pySMART.Device', return_value=mock_sd),
    ):
        sd = d.get_smart_data()

    assert sd is not None
    assert sd.healthy is False


def test_get_smart_data_standby_mode():
    """get_smart_data() sets standby_mode=True when smartctl reports STANDBY."""
    d = Disk.__new__(Disk)
    d._Disk__path = '/dev/sdb'
    d._Disk__type = DiskType.HDD

    with patch.object(pySMART.SMARTCTL, 'info', return_value=_SMART_INFO_STANDBY):
        sd = d.get_smart_data()

    assert sd is not None
    assert sd.standby_mode is True


def test_get_smart_data_empty_output_returns_none():
    """get_smart_data() returns None when smartctl produces no output."""
    d = Disk.__new__(Disk)
    d._Disk__path = '/dev/sda'
    d._Disk__type = DiskType.HDD

    with patch.object(pySMART.SMARTCTL, 'info', return_value=[]):
        assert d.get_smart_data() is None


def test_get_smart_data_loop_returns_none():
    """get_smart_data() returns None immediately for LOOP disks (no smartctl call)."""
    d = Disk.__new__(Disk)
    d._Disk__path = '/dev/loop0'
    d._Disk__type = DiskType.LOOP
    assert d.get_smart_data() is None


def test_get_smart_data_unknown_interface_returns_none():
    """get_smart_data() returns None when the device interface cannot be identified."""
    d = Disk.__new__(Disk)
    d._Disk__path = '/dev/sda'
    d._Disk__type = DiskType.SSD

    mock_sd = MagicMock()
    mock_sd.interface = None

    with (
        patch.object(pySMART.SMARTCTL, 'info', return_value=_SMART_INFO_OK),
        patch('pySMART.Device', return_value=mock_sd),
    ):
        assert d.get_smart_data() is None


# ── get_partition_list ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    'fixture_name, part_num, is_nvme',
    [
        ('hdd_device', 0, False),
        ('hdd_device', 2, False),
        ('ssd_device', 3, False),
        ('nvme_device', 6, True),
    ],
)
def test_get_partition_list(fixture_name, part_num, is_nvme, request):
    """get_partition_list() returns a list with the correct partition count."""
    mock_dev = request.getfixturevalue(fixture_name)
    mock_dev.children = [
        _make_partition_device(
            mock_dev.attributes.asstring('dev'),
            i + 1,
            mock_dev.sys_name,
            is_nvme=is_nvme,
        )
        for i in range(part_num)
    ]
    df_result = MagicMock()
    df_result.stdout = 'Filesystem Avail Mounted on\n'

    with (
        patch('diskinfo.partition.subprocess.run', return_value=df_result),
        pyudev_patched(mock_dev),
    ):
        d = Disk(mock_dev.sys_name)

    assert len(d.get_partition_list()) == part_num


# ── comparison operators ──────────────────────────────────────────────────────


def test_operator_equality():
    """== / != compare two Disk instances by name."""
    d1, d2 = Disk.__new__(Disk), Disk.__new__(Disk)
    d1._Disk__name = d2._Disk__name = 'sda'
    assert d1 == d2
    assert (d1 != d2) is False


def test_operator_less_than_greater_than():
    """< and > compare Disk instances lexicographically by name."""
    d_a, d_b = Disk.__new__(Disk), Disk.__new__(Disk)
    d_a._Disk__name, d_b._Disk__name = 'sda', 'sdb'
    assert d_a < d_b
    assert d_b > d_a
    assert (d_a > d_b) is False
    assert (d_b < d_a) is False


# ── __repr__ ──────────────────────────────────────────────────────────────────


def test_repr_contains_all_attributes(ssd_device):
    """repr() output contains every disk attribute value."""
    with pyudev_patched(ssd_device):
        d = Disk(ssd_device.sys_name)
    result = repr(d)
    assert d.get_name() in result
    assert d.get_path() in result
    assert repr(d.get_byid_path()) in result
    assert repr(d.get_bypath_path()) in result
    assert d.get_wwn() in result
    assert d.get_model() in result
    assert d.get_serial_number() in result
    assert d.get_firmware() in result
    assert d.get_type_str() in result
    assert str(d.get_size()) in result
    assert d.get_device_id() in result
    assert str(d.get_physical_block_size()) in result
    assert str(d.get_logical_block_size()) in result
    assert d.get_partition_table_type() in result
    assert d.get_partition_table_uuid() in result


# ── additional branch-coverage tests ─────────────────────────────────────────


def test_init_wwn_matches_device_with_null_wwn():
    """Disk(wwn=...) succeeds when the device's ID_WWN is None.

    Due to a bug in disk.py the lookup compares dev.get('ID_WWN') == serial_number
    (which is None).  A device whose ID_WWN property is also None therefore matches,
    covering lines 124-125 and the 'device found' branch at 126->160.
    """
    dev = _make_device(
        name='sda',
        dev_id='8:0',
        size=2000409264,
        phys_bs=512,
        log_bs=512,
        rotational='0',
        serial='ABC12345',
        firmware='EXM04B6Q',
        wwn=None,
        model='No-WWN Disk',
        part_table_type='gpt',
        part_table_uuid=str(uuid.uuid4()),
    )
    with pyudev_patched(dev):
        d = Disk(wwn='0x5002539c407255be')
    assert d.get_name() == 'sda'


def test_init_byid_name_device_not_found_raises_valueerror():
    """Disk(byid_name=...) raises ValueError when Devices.from_name raises DeviceNotFoundAtPathError."""
    mock_ctx = MagicMock()
    mock_ctx.list_devices.return_value = []
    with (
        patch('diskinfo.disk.Context', return_value=mock_ctx),
        patch('diskinfo.disk.Devices') as mock_devs,
        patch('os.readlink', return_value='../../sda'),
    ):
        mock_devs.from_name.side_effect = DeviceNotFoundAtPathError(
            '/sys/class/block/sda'
        )
        with pytest.raises(ValueError):
            Disk(byid_name='ata-Samsung_SSD_850_PRO_1TB_ABC12345')


def test_init_bypath_name_device_not_found_raises_valueerror():
    """Disk(bypath_name=...) raises ValueError when Devices.from_name raises DeviceNotFoundAtPathError."""
    mock_ctx = MagicMock()
    mock_ctx.list_devices.return_value = []
    with (
        patch('diskinfo.disk.Context', return_value=mock_ctx),
        patch('diskinfo.disk.Devices') as mock_devs,
        patch('os.readlink', return_value='../../sda'),
    ):
        mock_devs.from_name.side_effect = DeviceNotFoundAtPathError(
            '/sys/class/block/sda'
        )
        with pytest.raises(ValueError):
            Disk(bypath_name='pci-0000:00:17.0-ata-99')


def test_init_with_device_parameter(ssd_device):
    """Disk(_device=...) initialises directly from a pyudev Device object (line 153)."""
    with pyudev_patched(ssd_device):
        d = Disk(_device=ssd_device)
    assert d.get_name() == ssd_device.sys_name


def test_init_unknown_rotational_raises_runtimeerror():
    """Disk() raises RuntimeError when queue/rotational is not '0' or '1' (line 184)."""
    dev = _make_device(
        name='sda',
        dev_id='8:0',
        size=2000409264,
        phys_bs=512,
        log_bs=512,
        rotational='X',
    )
    with pyudev_patched(dev):
        with pytest.raises(RuntimeError):
            Disk('sda')


def test_init_non_byid_bypath_link_is_skipped(ssd_device):
    """A device link that is neither by-id nor by-path is silently ignored (branch 201->197)."""
    ssd_device.device_links = list(ssd_device.device_links) + [
        '/dev/disk/by-uuid/6432-935A'
    ]
    with pyudev_patched(ssd_device):
        d = Disk(ssd_device.sys_name)
    assert '/dev/disk/by-uuid/6432-935A' not in d.get_byid_path()
    assert '/dev/disk/by-uuid/6432-935A' not in d.get_bypath_path()


def test_init_hwmon_device_found(ssd_device):
    """Disk.__init__() sets __hwmon_path when an hwmon device is present (line 210)."""
    mock_hwmon_dev = MagicMock()
    mock_hwmon_dev.sys_path = '/sys/class/hwmon/hwmon2'

    mock_ctx = MagicMock()
    mock_ctx.list_devices.return_value = [mock_hwmon_dev]

    with (
        patch('diskinfo.disk.Context', return_value=mock_ctx),
        patch('diskinfo.disk.Devices') as mock_devs,
    ):
        mock_devs.from_name.return_value = ssd_device
        d = Disk(ssd_device.sys_name)

    assert d._Disk__hwmon_path == '/sys/class/hwmon/hwmon2/temp1_input'


def test_init_non_partition_child_is_ignored(hdd_device):
    """Non-partition children of a disk are skipped (branch 217->216)."""
    non_part = MagicMock()
    non_part.device_type = 'disk'  # NOT 'partition'

    part = _make_partition_device(
        hdd_device.attributes.asstring('dev'), 1, hdd_device.sys_name
    )
    hdd_device.children = [non_part, part]

    df_result = MagicMock()
    df_result.stdout = 'Filesystem Avail Mounted on\n'

    with (
        patch('diskinfo.partition.subprocess.run', return_value=df_result),
        pyudev_patched(hdd_device),
    ):
        d = Disk(hdd_device.sys_name)

    assert len(d.get_partition_list()) == 1


def test_get_temperature_hwmon_invalid_content_falls_to_pysmart(ssd_device):
    """get_temperature() falls through to pySMART when hwmon file has non-numeric content (lines 611-612)."""
    with pyudev_patched(ssd_device):
        d = Disk(ssd_device.sys_name)

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='_temp1_input', delete=False
    ) as f:
        f.write('not-a-number')
        hwmon_file = f.name
    try:
        d._Disk__hwmon_path = hwmon_file
        with (
            patch.object(Device, '__init__', return_value=None),
            patch('pySMART.Device.temperature', new_callable=PropertyMock) as mock_temp,
        ):
            mock_temp.return_value = 40
            assert d.get_temperature() == 40.0
    finally:
        os.unlink(hwmon_file)


def test_get_smart_data_nvme_no_if_attributes():
    """get_smart_data() skips NvmeAttributes when if_attributes is absent (branch 737->786)."""
    d = Disk.__new__(Disk)
    d._Disk__path = '/dev/nvme0n1'
    d._Disk__type = DiskType.NVME

    mock_sd = MagicMock()
    mock_sd.interface = 'nvme'
    mock_sd.smart_enabled = True
    mock_sd.smart_capable = True
    mock_sd.assessment = 'PASS'
    del mock_sd.if_attributes  # hasattr → False

    with (
        patch.object(pySMART.SMARTCTL, 'info', return_value=_SMART_INFO_OK),
        patch('pySMART.Device', return_value=mock_sd),
    ):
        sd = d.get_smart_data()

    assert sd is not None
    assert not hasattr(sd, 'nvme_attributes')


def test_get_smart_data_sata_no_legacy_attributes():
    """get_smart_data() skips smart_attributes when legacyAttributes is absent (branch 777->786)."""
    d = Disk.__new__(Disk)
    d._Disk__path = '/dev/sda'
    d._Disk__type = DiskType.SSD

    mock_sd = MagicMock()
    mock_sd.interface = 'ata'
    mock_sd.smart_enabled = True
    mock_sd.smart_capable = True
    mock_sd.assessment = 'PASS'
    del mock_sd.if_attributes.legacyAttributes  # hasattr → False

    with (
        patch.object(pySMART.SMARTCTL, 'info', return_value=_SMART_INFO_OK),
        patch('pySMART.Device', return_value=mock_sd),
    ):
        sd = d.get_smart_data()

    assert sd is not None
    assert not hasattr(sd, 'smart_attributes')


def test_get_smart_data_sata_none_entry_in_legacy_attributes():
    """get_smart_data() skips None entries within legacyAttributes (branch 780->779)."""
    d = Disk.__new__(Disk)
    d._Disk__path = '/dev/sdb'
    d._Disk__type = DiskType.HDD

    legacy = _make_hdd_legacy_attrs()
    legacy_with_none = [legacy[0], None, legacy[1]]  # None in the middle

    mock_sd = MagicMock()
    mock_sd.interface = 'ata'
    mock_sd.smart_enabled = True
    mock_sd.smart_capable = True
    mock_sd.assessment = 'PASS'
    mock_sd.if_attributes.legacyAttributes = legacy_with_none

    with (
        patch.object(pySMART.SMARTCTL, 'info', return_value=_SMART_INFO_OK),
        patch('pySMART.Device', return_value=mock_sd),
    ):
        sd = d.get_smart_data()

    assert sd is not None
    assert len(sd.smart_attributes) == 2  # None entry was skipped


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

# End
