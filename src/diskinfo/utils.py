#
#    Module `utils`: implements utility functions.
#    Peter Sulyok (C) 2022-2024.
#
from typing import List, Tuple


def _read_file(path) -> str:
    """Reads the text content of the specified file. The function will hide :py:obj:`IOError` and
    :py:obj:`FileNotFound` exceptions during the file operations. The result string will be decoded and stripped.

    Args:
        path (str): file path

    Returns:
        str: file content text

    Example:
        An example aboout the use of the function::

            >>> from diskinfo import *
            >>> _read_file("/sys/block/sda/dev")
            '8:0'

    """
    result: str = ""
    try:
        with open(path, "rt", encoding="UTF-8") as file:
            result = file.read()
    except (IOError, FileNotFoundError):
        pass
    return result.strip()


def _read_udev_property(path: str, udev_property: str) -> str:
    """Reads a property from an `udev` data file. The function will hide :py:obj:`IOError` and py:obj:`FileNotFound`
    exceptions during the file operations. The result string will be decoded and stripped.

    Args:
        path (str): path of the udev data file (e.g. `/run/udev/data/b8:0`)
        udev_property (str): udev property string

    Returns:
        str: udev property value

    Raises:
        ValueError: in case of empty input parameters

    Example:
        An example about the use of the function::

            >>> from diskinfo import *
            >>> _read_udev_property("/run/udev/data/b259:0", "ID_MODEL=")
            'WDS100T1X0E-00AFY0'

    """
    file_content: List[str] = []
    result: str = ""

    # Validate input parameters.
    if not path:
        raise ValueError("Invalid empty path.")
    if not udev_property:
        raise ValueError("Invalid empty property.")

    # Read proper udev data file.
    try:
        with open(path, "rt", encoding="unicode_escape") as file:
            file_content = file.read().splitlines()
    except (IOError, FileNotFoundError):
        pass

    # Find the specified udev_property and copy its value.
    for lines in file_content:
        pos = lines.find(udev_property)
        if pos != -1:
            result = lines[pos + len(udev_property):]

    return result.strip()


def _read_udev_path(path: str, path_type: int) -> List[str]:
    """Reads one or more path elements from an udev data file. It will hide :py:obj:`IOError` and
    :py:obj:`FileNotFound` exceptions during the file operations. The result path elements will be
    decoded and stripped.

    Args:
        path (str): path of the udev data file (e.g. `/run/udev/data/b8:0`)
        path_type (int): type of the path to find/load from udev data file. Valid values are:

            - 0 `by-id` path
            - 1 `by-path` path
            - 2 `by-partuuid` path
            - 3 `by-partlabel` path
            - 4 `by-label` path
            - 5 `by-uuid` path

    Returns:
        List[str]: path elements

    Raises:
        ValueError: in case of empty or invalid input parameters

    Example:
        An example about the use of the function::

            >>> from diskinfo import *
            >>> _read_udev_path("/run/udev/data/b259:0", 1)
            ['/dev/disk/by-path/pci-0000:02:00.0-nvme-1']

    """
    file_content: List[str] = []
    result: List[str] = []
    udev_property: str = ""

    # Validate input parameters.
    if not path:
        raise ValueError("Invalid empty path.")
    if path_type not in (0, 1, 2, 3, 4, 5):
        raise ValueError(f"Invalid path type ({path_type}).")

    # Read proper udev data file.
    try:
        with open(path, "rt", encoding="unicode_escape") as file:
            file_content = file.read().splitlines()
    except (IOError, FileNotFoundError):
        pass

    # Find the specified path elements and collect their value.
    if path_type == 0:
        udev_property = "disk/by-id/"
    elif path_type == 1:
        udev_property = "disk/by-path/"
    elif path_type == 2:
        udev_property = "disk/by-partuuid/"
    elif path_type == 3:
        udev_property = "disk/by-partlabel/"
    elif path_type == 4:
        udev_property = "disk/by-label/"
    elif path_type == 5:
        udev_property = "disk/by-uuid/"
    for lines in file_content:
        pos = lines.find(udev_property)
        if pos != -1:
            result.append("/dev/" + lines[pos:].strip())

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
            >>> s, u = size_in_hrf()
            >>> print(f"{s:.1f} {u}")
            12.8 TB
            >>> s, u = size_in_hrf(size, units=1)
            >>> print(f"{s:.1f} {u}")
            11.7 TiB

    """
    metric_units: List[str] = ["B", "kB", "MB", "GB", "TB", "PB", "EB"]
    iec_units: List[str] = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"]
    legacy_units: List[str] = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    divider: int        # Divider for the specified unit.
    hrf_size: float     # Result size
    hfr_unit: str       # Result unit
    index: int = 0      # Unit index

    # Validate input parameters.
    if units not in (0, 1, 2):
        raise ValueError(f"Invalid units parameter ({units}).")
    if size_value < 0:
        raise ValueError(f"Invalid size value ({size_value}).")

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
            >>> hours=6517
            >>> t, u = time_in_hrf(hours, unit=2)
            >>> print(f"{t:.1f} {u}")
            271.5 day
            >>> days=2401
            >>> t, u = time_in_hrf(hours, unit=3, short_format=True)
            >>> print(f"{t:.1f} {u}")
            6.6 yr

    """
    time_long_units: List[str] = ["second", "minute", "hour", "day", "year"]
    time_short_units: List[str] = ["s", "min", "h", "d", "yr"]
    time_dividers: List[int] = [60, 60, 24, 365, 1]

    divider: int        # Divider for the specified unit.
    hrf_time: float     # Result size
    hfr_unit: str       # Result unit
    index: int          # Unit index

    # Validate input parameters.
    if time < 0:
        raise ValueError(f"Invalid input time value ({time}).")
    length = len(time_long_units) - 1
    if unit < 0 or unit > length:
        raise ValueError(f"Invalid input unit ({unit}).")

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

# End
