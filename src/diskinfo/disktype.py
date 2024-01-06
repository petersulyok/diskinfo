#
#    Module `disktype`: implements `DiskType` class.
#    Peter Sulyok (C) 2022-2024.
#

class DiskType:
    """Constant values for disk types and for their names."""
    HDD = 1
    """Hard disk type."""
    SSD = 2
    """SSD disk type."""
    NVME = 4
    """NVME disk type."""
    LOOP = 8
    """LOOP disk type."""
    HDD_STR = "HDD"
    """Name of the hard disk type."""
    SSD_STR = "SSD"
    """Name of the SSD disk type."""
    NVME_STR = "NVME"
    """Name of the NVME disk type."""
    LOOP_STR = "LOOP"
    """Name of the LOOP disk type."""

# End
