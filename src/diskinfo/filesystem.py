#
#    Module `filesystem`: implements `FileSystem` class.
#    Peter Sulyok (C) 2022-2026.
#
import os
from typing import Tuple
from pyudev import Device
from diskinfo.utils import size_in_hrf, _pyudev_getenc

# Path to the kernel mount table.
_PROC_MOUNTS = "/proc/mounts"


class FileSystem:
    """This class encapsulates filesystem-related information read from a block device's udev properties.
    It is used by both :class:`~diskinfo.Partition` and :class:`~diskinfo.Disk` to represent filesystem data.

    .. note::

        1. The mounting point and available space are determined by reading ``/proc/mounts`` and calling
           :func:`os.statvfs`. If the file system is not mounted, the mounting point will be empty and the
           free size will be ``0``.
        2. Instances are created internally by :class:`~diskinfo.Partition` and :class:`~diskinfo.Disk`.

    Args:
        _device (pyudev.Device): pyudev.Device class

    """

    __fs_label: str             # File system label
    __fs_uuid: str              # File system UUID
    __fs_type: str              # File system type
    __fs_version: str           # File system version
    __fs_usage: str             # File system usage
    __fs_free_size: int         # File system free/available 512-bytes blocks
    __fs_mounting_point: str    # File system mounting folder

    def __init__(self, _device: Device) -> None:
        # Read filesystem attributes from udev properties.
        self.__fs_label = _pyudev_getenc(_device, "ID_FS_LABEL")
        self.__fs_uuid = _pyudev_getenc(_device, "ID_FS_UUID")
        self.__fs_type = _device.get("ID_FS_TYPE")
        self.__fs_version = _device.get("ID_FS_VERSION")
        self.__fs_usage = _device.get("ID_FS_USAGE")
        self.__fs_mounting_point = ""
        self.__fs_free_size = 0

        # Find mounting point from /proc/mounts and free space via os.statvfs().
        path = _device.device_node
        try:
            with open(_PROC_MOUNTS, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    if parts[0] == path:
                        self.__fs_mounting_point = parts[1]
                        try:
                            st = os.statvfs(parts[1])
                            self.__fs_free_size = (st.f_bavail * st.f_frsize) // 512
                        except OSError:
                            # statvfs can fail if the mount point becomes stale or inaccessible
                            # between reading /proc/mounts and calling statvfs (race condition),
                            # or if the filesystem does not support statvfs. In this case, the
                            # mounting point is still valid but free size remains 0.
                            pass
                        break
        except OSError:
            # /proc/mounts may not be available (e.g. in a minimal container or chroot
            # without /proc mounted). In this case, both mounting point and free size
            # remain at their defaults (empty string and 0 respectively).
            pass

    def get_fs_label(self) -> str:
        """Returns the label of the file system. The result could be empty if the file system does not have a label.
        """
        return self.__fs_label

    def get_fs_uuid(self) -> str:
        """Returns the UUID of the file system. The result could be empty if the device does not contain a
        file system.
        """
        return self.__fs_uuid

    def get_fs_type(self) -> str:
        """Returns the type of the file system. The result could be empty if the device does not contain a
        file system.
        """
        return self.__fs_type

    def get_fs_version(self) -> str:
        """Returns the version of the file system. The result could be empty if the device does not contain a
        file system or does not have a version.
        """
        return self.__fs_version

    def get_fs_usage(self) -> str:
        """Returns the usage of the file system. The result could be empty if the device does not contain a
        file system. Valid values are ``filesystem`` or ``other`` for special devices (e.g. for a swap partition).
        """
        return self.__fs_usage

    def get_fs_free_size(self) -> int:
        """Returns the free size of the file system in 512-byte blocks. The result could be 0 if the device does not
        contain a file system or if the file system is not mounted.
        """
        return self.__fs_free_size

    def get_fs_free_size_in_hrf(self, units: int = 0) -> Tuple[float, str]:
        """Returns the free size of the file system in human-readable form. The result could be 0 if the device
        does not contain a file system or if the file system is not mounted.

        Args:
            units (int): unit system will be used for the calculation and in the result:

                            - 0 metric units (default)
                            - 1 IEC units
                            - 2 legacy units

                         Read more about `units here <https://en.wikipedia.org/wiki/Byte>`_.

        Returns:
            Tuple[float, str]: size in human-readable form, proper unit

        """
        return size_in_hrf(self.__fs_free_size * 512, units)

    def get_fs_mounting_point(self) -> str:
        """Returns the mounting point of the file system. The result could be empty if the device does not
        contain any file system, or it is not mounted.
        """
        return self.__fs_mounting_point

    def __repr__(self):
        """String representation of the FileSystem class."""
        return (f"FileSystem(fs_label={self.__fs_label}, "
                f"fs_uuid={self.__fs_uuid}, "
                f"fs_type={self.__fs_type}, "
                f"fs_version={self.__fs_version}, "
                f"fs_usage={self.__fs_usage}, "
                f"fs_free_size={self.__fs_free_size}, "
                f"fs_mounting_point={self.__fs_mounting_point})")


# End
