#
#    Module `demo`: implements a simple demo for `diskinfo` package.
#    Peter Sulyok (C) 2022.
#
from diskinfo import DiskType, DiskInfo


def main():
    """Demo application for package `disk_info`."""

    # Discover disks in the system.
    di = DiskInfo()
    # Count number of the different disk types.
    disk_num = di.get_disk_number()
    hdd_num = di.get_disk_number(included={DiskType.HDD}, excluded={DiskType.NVME, DiskType.SSD})
    ssd_num = di.get_disk_number(included={DiskType.SSD}, excluded={DiskType.NVME, DiskType.HDD})
    nvme_num = di.get_disk_number(included={DiskType.NVME}, excluded={DiskType.HDD})
    # Print the attributes of the discovered disks.
    print(f"There are {disk_num} disks installed in this system ({hdd_num} HDDs, {ssd_num} SSDs, {nvme_num} NVMEs).")
    disks = di.get_disk_list(sorting=True)
    for d in disks:
        print(f"[{d.get_name()}]")
        print(f"\tpath:                     {d.get_path()}")
        print(f"\tmodel:                    {d.get_model()}")
        s, u = d.get_size_in_hrf(units=2)
        print(f"\tsize:                     {s:.1f} {u}")
        print(f"\tserial:                   {d.get_serial()}")
        print(f"\tfirmware:                 {d.get_firmware()}")
        print(f"\tdevice type:              {d.get_type_str()}")
        print(f"\tby-id path:               {d.get_byid_path()}")
        print(f"\tby-path path:             {d.get_bypath_path()}")
        print(f"\twwn id:                   {d.get_wwn()}")
        print(f"\tdevice id:                ({d.get_dev_id()})")
        print(f"\tPhysical block size:      {d.get_physical_block_size()}")
        print(f"\tLogical block size:       {d.get_logical_block_size()}")
        print(f"\tPartition table type:     {d.get_partition_table_type()}")
        print(f"\tPartition table UUID:     {d.get_partition_table_uuid()}")


if __name__ == '__main__':
    main()

# End.
