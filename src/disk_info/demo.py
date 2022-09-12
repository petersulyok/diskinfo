from disk_info import Disk, DiskType, DiskInfo

def main():

    di = DiskInfo()

    disk_num = di.get_disk_number()
    hdd_num = di.get_disk_number(included={DiskType.HDD}, excluded={DiskType.NVME, DiskType.SSD})
    ssd_num = di.get_disk_number(included={DiskType.SSD}, excluded={DiskType.NVME, DiskType.HDD})
    nvme_num = di.get_disk_number(included={DiskType.NVME}, excluded={DiskType.HDD})

    print(f"There are {disk_num} disks installed in this system ({hdd_num} HDDs, {ssd_num} SSDs, {nvme_num} NVMEs).")
    disks = di.get_disk_list(sorted=True)
    for d in disks:
        print(f"[{d.get_name()}]")
        print(f"\tpath:\t\t{d.get_path()}")
        print(f"\tmodel:\t\t{d.get_model()}")
        s, u = d.get_size_in_hrf(units=2)
        print(f"\tsize:\t\t{s:.1f} {u}")
        print(f"\tserial:\t\t{d.get_serial()}")
        print(f"\tfirmware:\t\t{d.get_firmware()}")
        print(f"\tdevice type:\t\t{d.get_type_str()}")
        print(f"\tby-id path:\t\t{d.get_byid_path()}")
        print(f"\tby-path path:\t\t{d.get_bypath_path()}")
        print(f"\twwn id:\t\t{d.get_wwn()}")
        print(f"\tdevice id:\t\t({d.get_dev_id()})")


if __name__ == '__main__':
    main()

# End.