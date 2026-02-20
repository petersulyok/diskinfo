#
#    Unit tests for `disksmart` module (pytest style)
#    Peter Sulyok (C) 2022-2026.
#
import pytest
from diskinfo.disksmart import SmartAttribute, NvmeAttributes, DiskSmartData


# ── SmartAttribute ────────────────────────────────────────────────────────────


def test_smart_attribute_stores_all_fields():
    """SmartAttribute.__init__() stores all ten field values correctly."""
    attr = SmartAttribute(
        5, 'Reallocated_Sector_Ct', 0x0033, 100, 100, 10, 'Pre-fail', 'Always', '-', 0
    )
    assert attr.id == 5
    assert attr.attribute_name == 'Reallocated_Sector_Ct'
    assert attr.flag == 0x0033
    assert attr.value == 100
    assert attr.worst == 100
    assert attr.thresh == 10
    assert attr.type == 'Pre-fail'
    assert attr.updated == 'Always'
    assert attr.when_failed == '-'
    assert attr.raw_value == 0


@pytest.mark.parametrize(
    '_id, name, flag, value, worst, thresh, _type, updated, when_failed, raw',
    [
        (9, 'Power_On_Hours', 0x0032, 95, 95, 0, 'Old_age', 'Always', '-', 23268),
        (12, 'Power_Cycle_Count', 0x0032, 92, 92, 0, 'Old_age', 'Always', '-', 7103),
        (177, 'Wear_Leveling_Count', 0x0013, 99, 99, 0, 'Pre-fail', 'Always', '-', 20),
        (
            241,
            'Total_LBAs_Written',
            0x0032,
            99,
            99,
            0,
            'Old_age',
            'Always',
            '-',
            9_869_978_356,
        ),
        (
            187,
            'Uncorrectable_Error_Cnt',
            0x0032,
            100,
            100,
            0,
            'Old_age',
            'Always',
            'now',
            1,
        ),
    ],
)
def test_smart_attribute_parametrized(
    _id, name, flag, value, worst, thresh, _type, updated, when_failed, raw
):
    """SmartAttribute correctly stores every parametrised combination of values."""
    attr = SmartAttribute(
        _id, name, flag, value, worst, thresh, _type, updated, when_failed, raw
    )
    assert attr.id == _id
    assert attr.attribute_name == name
    assert attr.flag == flag
    assert attr.value == value
    assert attr.worst == worst
    assert attr.thresh == thresh
    assert attr.type == _type
    assert attr.updated == updated
    assert attr.when_failed == when_failed
    assert attr.raw_value == raw


# ── NvmeAttributes ────────────────────────────────────────────────────────────


def test_nvme_attributes_stores_all_fields():
    """NvmeAttributes.__init__() stores all seventeen NVMe field values correctly."""
    na = NvmeAttributes(
        critical_warning=0,
        temperature=35,
        available_spare=100,
        available_spare_threshold=10,
        percentage_used=2,
        data_units_read=123_456,
        data_units_written=654_321,
        host_read_commands=9_999_999,
        host_write_commands=7_777_777,
        controller_busy_time=1_234,
        power_cycles=42,
        power_on_hours=1_565,
        unsafe_shutdowns=5,
        media_and_data_integrity_errors=0,
        error_information_log_entries=0,
        warning_composite_temperature_time=0,
        critical_composite_temperature_time=0,
    )
    assert na.critical_warning == 0
    assert na.temperature == 35
    assert na.available_spare == 100
    assert na.available_spare_threshold == 10
    assert na.percentage_used == 2
    assert na.data_units_read == 123_456
    assert na.data_units_written == 654_321
    assert na.host_read_commands == 9_999_999
    assert na.host_write_commands == 7_777_777
    assert na.controller_busy_time == 1_234
    assert na.power_cycles == 42
    assert na.power_on_hours == 1_565
    assert na.unsafe_shutdowns == 5
    assert na.media_and_data_integrity_errors == 0
    assert na.error_information_log_entries == 0
    assert na.warning_composite_temperature_time == 0
    assert na.critical_composite_temperature_time == 0


def test_nvme_attributes_none_values():
    """NvmeAttributes accepts None for any field (as disk.py passes None when attr absent)."""
    na = NvmeAttributes(
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    assert na.critical_warning is None
    assert na.temperature is None
    assert na.power_on_hours is None


# ── DiskSmartData – helpers ───────────────────────────────────────────────────


def _make_smart_data() -> DiskSmartData:
    """Return a DiskSmartData with four representative SMART attributes."""
    sd = DiskSmartData()
    sd.smart_attributes = [
        SmartAttribute(
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
        SmartAttribute(
            9, 'Power_On_Hours', 0x0032, 95, 95, 0, 'Old_age', 'Always', '-', 23268
        ),
        SmartAttribute(
            12, 'Power_Cycle_Count', 0x0032, 92, 92, 0, 'Old_age', 'Always', '-', 7103
        ),
        SmartAttribute(
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
    return sd


# ── DiskSmartData.find_smart_attribute_by_id ─────────────────────────────────


def test_find_by_id_returns_correct_index():
    """find_smart_attribute_by_id() returns the correct list index for each id."""
    sd = _make_smart_data()
    assert sd.find_smart_attribute_by_id(5) == 0
    assert sd.find_smart_attribute_by_id(9) == 1
    assert sd.find_smart_attribute_by_id(12) == 2
    assert sd.find_smart_attribute_by_id(190) == 3


def test_find_by_id_returns_minus_one_when_not_found():
    """find_smart_attribute_by_id() returns -1 when the id is absent."""
    sd = _make_smart_data()
    assert sd.find_smart_attribute_by_id(99) == -1
    assert sd.find_smart_attribute_by_id(0) == -1
    assert sd.find_smart_attribute_by_id(255) == -1


def test_find_by_id_empty_list_returns_minus_one():
    """find_smart_attribute_by_id() returns -1 when smart_attributes is empty."""
    sd = DiskSmartData()
    sd.smart_attributes = []
    assert sd.find_smart_attribute_by_id(9) == -1


# ── DiskSmartData.find_smart_attribute_by_name ───────────────────────────────


def test_find_by_name_exact_match_returns_index():
    """find_smart_attribute_by_name() returns the index on an exact name match."""
    sd = _make_smart_data()
    assert sd.find_smart_attribute_by_name('Reallocated_Sector_Ct') == 0
    assert sd.find_smart_attribute_by_name('Power_On_Hours') == 1
    assert sd.find_smart_attribute_by_name('Power_Cycle_Count') == 2
    assert sd.find_smart_attribute_by_name('Airflow_Temperature_Cel') == 3


def test_find_by_name_substring_match():
    """find_smart_attribute_by_name() finds attributes by substring (in operator)."""
    sd = _make_smart_data()
    assert sd.find_smart_attribute_by_name('Power_On') == 1  # prefix of Power_On_Hours
    assert sd.find_smart_attribute_by_name('Cycle') == 2  # infix of Power_Cycle_Count
    assert (
        sd.find_smart_attribute_by_name('Airflow') == 3
    )  # prefix of Airflow_Temperature_Cel


def test_find_by_name_not_found_returns_minus_one():
    """find_smart_attribute_by_name() returns -1 when no attribute name matches."""
    sd = _make_smart_data()
    assert sd.find_smart_attribute_by_name('Nonexistent_Attr') == -1
    assert sd.find_smart_attribute_by_name('') == 0  # empty string is in every string


def test_find_by_name_empty_list_returns_minus_one():
    """find_smart_attribute_by_name() returns -1 when smart_attributes is empty."""
    sd = DiskSmartData()
    sd.smart_attributes = []
    assert sd.find_smart_attribute_by_name('Power_On_Hours') == -1


# End
