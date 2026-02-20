#
#    Unit tests for `utils` module (pytest style)
#    Peter Sulyok (C) 2022-2026.
#
import os
import tempfile
from unittest.mock import MagicMock
import pytest
from diskinfo.utils import (
    _read_file,
    size_in_hrf,
    time_in_hrf,
    _pyudev_getint,
    _pyudev_getenc,
)


# ── _read_file ────────────────────────────────────────────────────────────────


def test_read_file_returns_stripped_content():
    """_read_file() reads a file, strips surrounding whitespace, and returns it."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write('  hello world  \n')
        path = f.name
    try:
        assert _read_file(path) == 'hello world'
    finally:
        os.unlink(path)


def test_read_file_missing_returns_empty_string():
    """_read_file() returns '' for a non-existent file (no exception raised)."""
    assert _read_file('/no/such/file/exists') == ''


def test_read_file_directory_returns_empty_string(tmp_path):
    """_read_file() returns '' when given a directory path (IOError suppressed)."""
    assert _read_file(str(tmp_path)) == ''


def test_read_file_empty_file_returns_empty_string():
    """_read_file() returns '' for an existing but empty file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        path = f.name
    try:
        assert _read_file(path) == ''
    finally:
        os.unlink(path)


def test_read_file_multiline_returns_stripped():
    """_read_file() strips but does not split multi-line file content."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('line1\nline2\n')
        path = f.name
    try:
        assert _read_file(path) == 'line1\nline2'
    finally:
        os.unlink(path)


# ── size_in_hrf ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    'size, units, exp_value, exp_unit',
    [
        # Stays in Bytes (below any threshold)
        (0, 0, 0.0, 'B'),
        (0, 1, 0.0, 'B'),
        (0, 2, 0.0, 'B'),
        (999, 0, 999.0, 'B'),
        (512, 1, 512.0, 'B'),
        # Metric (units=0): divider=1000
        (1_000, 0, 1.0, 'kB'),
        (1_000_000, 0, 1.0, 'MB'),
        (1_000_000_000, 0, 1.0, 'GB'),
        (1_000_000_000_000, 0, 1.0, 'TB'),
        (1_000_000_000_000_000, 0, 1.0, 'PB'),
        # IEC (units=1): divider=1024
        (1_024, 1, 1.0, 'KiB'),
        (1_048_576, 1, 1.0, 'MiB'),
        (1_073_741_824, 1, 1.0, 'GiB'),
        (1_099_511_627_776, 1, 1.0, 'TiB'),
        (1_125_899_906_842_624, 1, 1.0, 'PiB'),
        # Legacy (units=2): same divider as IEC but different unit names
        (1_024, 2, 1.0, 'KB'),
        (1_048_576, 2, 1.0, 'MB'),
        (1_073_741_824, 2, 1.0, 'GB'),
        (1_099_511_627_776, 2, 1.0, 'TB'),
        (1_125_899_906_842_624, 2, 1.0, 'PB'),
    ],
)
def test_size_in_hrf_unit_thresholds(size, units, exp_value, exp_unit):
    """size_in_hrf() produces the correct magnitude and unit for each unit system."""
    value, unit = size_in_hrf(size, units)
    assert value == pytest.approx(exp_value)
    assert unit == exp_unit


def test_size_in_hrf_fractional_result():
    """size_in_hrf() returns a fractional value when size is not an exact multiple."""
    value, unit = size_in_hrf(1_500_000, units=0)
    assert value == pytest.approx(1.5)
    assert unit == 'MB'


def test_size_in_hrf_invalid_units_raises_valueerror():
    """size_in_hrf() raises ValueError for units outside {0, 1, 2}."""
    with pytest.raises(ValueError):
        size_in_hrf(1024, units=3)
    with pytest.raises(ValueError):
        size_in_hrf(1024, units=-1)


def test_size_in_hrf_negative_size_raises_valueerror():
    """size_in_hrf() raises ValueError for a negative byte count."""
    with pytest.raises(ValueError):
        size_in_hrf(-1)
    with pytest.raises(ValueError):
        size_in_hrf(-1_000_000)


@pytest.mark.parametrize(
    'size, units, exp_value, exp_unit',
    [
        # 1000^7 bytes exhausts the metric loop (7 iterations, no break) → index=6 → "EB"
        (10**21, 0, 1.0, 'EB'),
        # 1024^7 bytes exhausts the IEC loop → index=6 → "EiB"
        (2**70, 1, 1.0, 'EiB'),
        # same value, legacy units → "EB"
        (2**70, 2, 1.0, 'EB'),
    ],
)
def test_size_in_hrf_loop_exhausted(size, units, exp_value, exp_unit):
    """size_in_hrf() handles values so large the inner loop is fully exhausted (branch 95->101)."""
    value, unit = size_in_hrf(size, units)
    assert value == pytest.approx(exp_value)
    assert unit == exp_unit


# ── time_in_hrf ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    'time, unit, short_format, exp_value, exp_unit',
    [
        # Stays in input unit (below threshold)
        (30, 0, False, 30.0, 'second'),
        (30, 0, True, 30.0, 's'),
        (45, 1, False, 45.0, 'minute'),
        (45, 1, True, 45.0, 'min'),
        (20, 2, False, 20.0, 'hour'),
        (20, 2, True, 20.0, 'h'),
        (100, 3, False, 100.0, 'day'),
        (100, 3, True, 100.0, 'd'),
        (3, 4, False, 3.0, 'year'),
        (3, 4, True, 3.0, 'yr'),
        # Seconds → minutes
        (120, 0, False, 2.0, 'minute'),
        (90, 0, True, 1.5, 'min'),
        # Minutes → hours
        (180, 1, False, 3.0, 'hour'),
        (90, 1, True, 1.5, 'h'),
        # Hours → days
        (48, 2, False, 2.0, 'day'),
        (36, 2, True, 1.5, 'd'),
        # Days → years
        (730, 3, False, 2.0, 'year'),
        (365, 3, True, 1.0, 'yr'),
    ],
)
def test_time_in_hrf_conversions(time, unit, short_format, exp_value, exp_unit):
    """time_in_hrf() converts time values to correct magnitude and unit string."""
    value, u = time_in_hrf(time, unit, short_format)
    assert value == pytest.approx(exp_value)
    assert u == exp_unit


def test_time_in_hrf_zero_seconds():
    """time_in_hrf() handles time=0 correctly (stays in seconds)."""
    value, u = time_in_hrf(0)
    assert value == pytest.approx(0.0)
    assert u == 'second'


def test_time_in_hrf_negative_time_raises_valueerror():
    """time_in_hrf() raises ValueError for a negative time value."""
    with pytest.raises(ValueError):
        time_in_hrf(-1)


def test_time_in_hrf_invalid_unit_raises_valueerror():
    """time_in_hrf() raises ValueError for a unit outside 0–4."""
    with pytest.raises(ValueError):
        time_in_hrf(10, unit=5)
    with pytest.raises(ValueError):
        time_in_hrf(10, unit=-1)


# ── _pyudev_getint ────────────────────────────────────────────────────────────


def test_pyudev_getint_converts_string_to_int():
    """_pyudev_getint() returns an int when the attribute is a valid numeric string."""
    dev = MagicMock()
    dev.get.return_value = '42'
    assert _pyudev_getint(dev, 'some_key') == 42


def test_pyudev_getint_large_value():
    """_pyudev_getint() handles large integer strings correctly."""
    dev = MagicMock()
    dev.get.return_value = '20000409264'
    assert _pyudev_getint(dev, 'ID_PART_ENTRY_SIZE') == 20_000_409_264


def test_pyudev_getint_missing_key_returns_none():
    """_pyudev_getint() returns None when the key is absent and no default given."""
    dev = MagicMock()
    dev.get.return_value = None
    assert _pyudev_getint(dev, 'no_such_key') is None


def test_pyudev_getint_missing_key_returns_default():
    """_pyudev_getint() returns default_value when the key is absent."""
    dev = MagicMock()
    dev.get.return_value = None
    assert _pyudev_getint(dev, 'no_such_key', default_value=99) == 99


def test_pyudev_getint_non_integer_string_returns_default():
    """_pyudev_getint() returns default_value when the value cannot be cast to int."""
    dev = MagicMock()
    dev.get.return_value = 'not-a-number'
    assert _pyudev_getint(dev, 'bad_key', default_value=0) == 0


def test_pyudev_getint_non_integer_no_default_returns_none():
    """_pyudev_getint() returns None when value is non-integer and no default given."""
    dev = MagicMock()
    dev.get.return_value = 'bad'
    assert _pyudev_getint(dev, 'key') is None


# ── _pyudev_getenc ────────────────────────────────────────────────────────────


def test_pyudev_getenc_decodes_x20_escapes():
    """_pyudev_getenc() decodes \\x20 in the _ENC variant into spaces."""
    dev = MagicMock()
    props = {'ID_MODEL_ENC': 'Samsung\\x20SSD\\x20850', 'ID_MODEL': 'Samsung_SSD_850'}
    dev.get.side_effect = props.get
    assert _pyudev_getenc(dev, 'ID_MODEL') == 'Samsung SSD 850'


def test_pyudev_getenc_falls_back_when_enc_is_none():
    """_pyudev_getenc() returns the plain key value when _ENC key is absent."""
    dev = MagicMock()
    props = {'ID_MODEL_ENC': None, 'ID_MODEL': 'Samsung_SSD_850'}
    dev.get.side_effect = props.get
    assert _pyudev_getenc(dev, 'ID_MODEL') == 'Samsung_SSD_850'


def test_pyudev_getenc_enc_without_x20_falls_back_to_plain_key():
    """_pyudev_getenc() uses the plain key when _ENC exists but has no \\x20."""
    dev = MagicMock()
    props = {'ID_MODEL_ENC': 'SamsungSSD850', 'ID_MODEL': 'SamsungSSD850_plain'}
    dev.get.side_effect = props.get
    # ENC has no \x20, so falls through to plain key
    assert _pyudev_getenc(dev, 'ID_MODEL') == 'SamsungSSD850_plain'


def test_pyudev_getenc_returns_none_when_both_keys_absent():
    """_pyudev_getenc() returns None when neither _ENC nor plain key exists."""
    dev = MagicMock()
    dev.get.return_value = None
    assert _pyudev_getenc(dev, 'ID_MODEL') is None


def test_pyudev_getenc_strips_whitespace_after_decode():
    """_pyudev_getenc() strips leading/trailing whitespace after \\x20 decoding."""
    dev = MagicMock()
    props = {'ID_FS_LABEL_ENC': '\\x20My\\x20Label\\x20', 'ID_FS_LABEL': 'raw'}
    dev.get.side_effect = props.get
    assert _pyudev_getenc(dev, 'ID_FS_LABEL') == 'My Label'


# End
