#
#    Package `diskinfo`
#    Peter Sulyok (C) 2022.
#
from diskinfo.disktype import DiskType
from diskinfo.disk import Disk
from diskinfo.disksmart import DiskSmartData, SmartAttribute, NvmeAttributes
from diskinfo.diskinfo import DiskInfo

__all__ = ["Disk", "DiskType", "DiskSmartData", "SmartAttribute", "NvmeAttributes", "DiskInfo"]
