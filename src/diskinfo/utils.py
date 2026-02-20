#
#    Module `utils`: implements utility functions.
#    Peter Sulyok (C) 2022-2026.
#
from typing import List, Tuple, Union
from pyudev import Device


def _read_file(path, encoding: str = 'utf-8') -> str:
    """Reads the text content of the specified file. The function will hide :py:obj:`IOError` and
    :py:obj:`FileNotFound` exceptions during the file operations. The result bytes will be read with the specified
    encoding and stripped.

    Args:
        path (str): file path
        encoding (str): encoding (default is `utf-8`)

    Returns:
        str: file content text

    Example:
        An example about the use of the function::

            >>> from diskinfo import *
            >>> _read_file("/sys/block/sda/dev")
            '8:0'

    """
    result: str = ''
    try:
        with open(path, 'rt', encoding=encoding) as file:
            result = file.read().strip()
    except (IOError, FileNotFoundError):
        pass
    return result


def size_in_hrf(size_value: int, units: int = 0) -> Tuple[float, str]:
    """Returns the size in a human-readable form.

    Args:
        size_value (int): number of bytes
        units (int): unit system will be used for the calculation and in the result:

                        - 0 metric units (default)
                        - 1 IEC units
                        - 2 legacy units

                     Read more about `units here <https://en.wikipedia.org/wiki/Byte>`_.

    Returns:
        Tuple[float, str]: size in human-readable form, proper unit

    Raises:
        ValueError: in case of invalid input parameters (negative size, invalid units)

    Example:
        An example about the use of the function::

            >>> from diskinfo import *
            >>> size = 12839709879873
            >>> s, u = size_in_hrf(size)
            >>> print(f"{s:.1f} {u}")
            12.8 TB
            >>> s, u = size_in_hrf(size, units=1)
            >>> print(f"{s:.1f} {u}")
            11.7 TiB

    """
    metric_units: List[str] = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB']
    iec_units: List[str] = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']
    legacy_units: List[str] = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    divider: int  # Divider for the specified unit.
    hrf_size: float  # Result size
    hfr_unit: str  # Result unit
    index: int = 0  # Unit index

    # Validate input parameters.
    if units not in (0, 1, 2):
        raise ValueError(f'Invalid units parameter ({units}).')
    if size_value < 0:
        raise ValueError(f'Invalid size value ({size_value}).')

    # Set up the proper divider.
    if units == 0:
        divider = 1000
    elif units == 1:
        divider = 1024
    else:
        divider = 1024

    # Calculate the proper size.
    hrf_size = size_value
    number_of_units = len(metric_units)
    for index in range(number_of_units):
        if hrf_size < divider:
            break
        hrf_size /= divider

    # Identify the proper unit for the calculated size.
    if units == 0:
        hfr_unit = metric_units[index]
    elif units == 1:
        hfr_unit = iec_units[index]
    else:
        hfr_unit = legacy_units[index]

    return hrf_size, hfr_unit


def time_in_hrf(time: int, unit: int = 0, short_format: bool = False) -> Tuple[float, str]:
    """Returns the amount of time in a human-readable form.

    Args:
        time (int): time value
        unit (int): unit of the input time value

            - 0 seconds
            - 1 minutes
            - 2 hours
            - 3 days
            - 4 years

        short_format (bool): result unit in short format (e.g. `min` instead of `minute`)

    Returns:
        Tuple[float, str]: time in human-readable form, proper unit

    Raises:
        ValueError: in case of invalid input parameters (negative time, invalid unit)

    Example:
        An example about the use of the function::

            >>> from diskinfo import *
            >>> hours = 6517
            >>> t, u = time_in_hrf(hours, unit=2)
            >>> print(f"{t:.1f} {u}")
            271.5 day
            >>> days = 2401
            >>> t, u = time_in_hrf(hours, unit=3, short_format=True)
            >>> print(f"{t:.1f} {u}")
            6.6 yr

    """
    time_long_units: List[str] = ['second', 'minute', 'hour', 'day', 'year']
    time_short_units: List[str] = ['s', 'min', 'h', 'd', 'yr']
    time_dividers: List[int] = [60, 60, 24, 365, 1]

    divider: int  # Divider for the specified unit.
    hrf_time: float  # Result size
    hfr_unit: str  # Result unit
    index: int  # Unit index

    # Validate input parameters.
    if time < 0:
        raise ValueError(f'Invalid input time value ({time}).')
    length = len(time_long_units) - 1
    if unit < 0 or unit > length:
        raise ValueError(f'Invalid input unit ({unit}).')

    # Calculate the proper time.
    hrf_time = time
    index = unit
    while index < length:
        divider = time_dividers[index]
        if hrf_time < divider:
            break
        hrf_time /= divider
        index += 1

    # Identify the proper unit for the calculated time.
    if short_format:
        hfr_unit = time_short_units[index]
    else:
        hfr_unit = time_long_units[index]

    return hrf_time, hfr_unit


def _pyudev_getint(device: Device, key: str, default_value: int = None) -> Union[int, None]:
    """Returns an integer attribute value of a pyudev.Device() class. The function hides the ValueError exception
    in case of conversion error and returns the `default_value`.

    Args:
        device (pyudev.Device): pyudev.Device() class
        key (str): attribute key
        default_value (int): default int value in case of missing attribute

    Returns:
        Union[int, None]: int attribute value or None

    Example:
        An example about the use of the function::

            >>> from diskinfo import *
            >>> from pyudev import *
            >>> c = Context()
            >>> d = Devices.from_name(c, 'block', 'sda1')
            >>> print(_pyudev_getint(d, 'ID_PART_ENTRY_SIZE'))
            20000409264

    """
    value: str

    # Read the value for the specified device attribute.
    value = device.get(key)
    # Convert the value string to integer if the key exists.
    if value:
        try:
            return int(value)
        except ValueError:
            pass
    # Otherwise return the default value.
    return default_value


def _pyudev_getenc(dev: Device, key: str) -> Union[str, None]:
    """Returns one of the device attribute key pairs. There are udev attributes key pairs (e.g. `ID_MODEL` and
    `ID_MODEL_ENC`), where this function first tries to read and decode the `_ENC` version of the key then the simple
    key if the previous one does not exist.

    Args:
        device (pyudev.Device): pyudev.Device() class
        key (str): attribute key

    Returns:
        Union[str, None]: str attribute value or None

    Example:
        An example about the use of the function::

            >>> from diskinfo import *
            >>> from pyudev import *
            >>> c = Context()
            >>> d = Devices.from_name(c, 'block', 'sda')
            >>> print(_pyudev_getenc(d, 'ID_MODEL'))
            Samsung SSD 850 PRO 1TB

    """
    value: str

    # Read and decode the `_ENC` key.
    value = dev.get(key + '_ENC')
    if value:
        if '\\x20' in value:
            return value.replace('\\x20', ' ').strip()
    # Read the simple key.
    return dev.get(key)


# End
