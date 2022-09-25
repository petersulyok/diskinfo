#
#    Module `demo`: implements a simple demo for `diskinfo` package.
#    Peter Sulyok (C) 2022.
#
from diskinfo import DiskType, DiskInfo
RICH = True
# Import rich if installed
try:
    from rich import print as rprint
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    from rich.console import Group
except ImportError:
    RICH = False


def main():
    """Demo application for package `diskinfo`."""

    # Discover disks in the system.
    di = DiskInfo()

    # Count number of the different disk types.
    disk_num = di.get_disk_number()
    hdd_num = di.get_disk_number(included={DiskType.HDD}, excluded={DiskType.NVME, DiskType.SSD})
    ssd_num = di.get_disk_number(included={DiskType.SSD}, excluded={DiskType.NVME, DiskType.HDD})
    nvme_num = di.get_disk_number(included={DiskType.NVME}, excluded={DiskType.HDD})
    verb = "are"
    plural = "s"
    if disk_num <= 1:
        verb = "is"
        plural = ""

    # Rich demo.
    if RICH:
        panel = Panel(f"[markdown.strong]There {verb} [bold sky_blue2]{disk_num}[/] disk{plural} installed in this"
                      f" system :point_right: [bold sky_blue2]{hdd_num}[/] HDD(s), [bold sky_blue2]{ssd_num}[/]"
                      f" SSD(s), [bold sky_blue2]{nvme_num}[/] NVME(s)[/]", box=box.MINIMAL, expand=False)
        table = Table(border_style="gray30", box=box.MINIMAL)
        table.add_column("Name", justify="left", style="bold orange1")
        table.add_column("Type", justify="left", style="bold orchid")
        table.add_column("Model", justify="left", style="bold gray54")
        table.add_column("Path", justify="left", style="bold green")
        table.add_column("Temp", justify="right", style="bold orchid1")
        table.add_column("Serial", justify="left", style="bold purple3")
        table.add_column("Firmware", justify="left", style="bold slate_blue1")
        table.add_column("Size", justify="right", style="bold blue")
        disks = di.get_disk_list(sorting=True)
        for d in disks:
            s, u = d.get_size_in_hrf()
            table.add_row(d.get_name(), d.get_type_str(), d.get_model(), d.get_path(), f"{d.get_temperature():.1f} C",
                          d.get_serial_number(), d.get_firmware(), f"{s:.1f} {u}")
        group = Group(panel, table)
        rprint(Panel(group, title="diskinfo demo", title_align="left", border_style="gray30", expand=False))

    # Normal demo.
    else:
        # Print the attributes of the discovered disks.
        print(f"There {verb} {disk_num} disk{plural} installed in this system: {hdd_num} HDDs, {ssd_num} SSDs,"
              f" {nvme_num} NVMEs")
        disks = di.get_disk_list(sorting=True)
        for d in disks:
            print(f"[{d.get_name()}]")
            print(f"\tpath:                     {d.get_path()}")
            print(f"\tmodel:                    {d.get_model()}")
            s, u = d.get_size_in_hrf(units=2)
            print(f"\tsize:                     {s:.1f} {u}")
            print(f"\tserial:                   {d.get_serial_number()}")
            print(f"\tfirmware:                 {d.get_firmware()}")
            print(f"\ttemperature:              {d.get_temperature():.1f} C")
            print(f"\tdevice type:              {d.get_type_str()}")
            print(f"\tby-id path:               {d.get_byid_path()}")
            print(f"\tby-path path:             {d.get_bypath_path()}")
            print(f"\twwn id:                   {d.get_wwn()}")
            print(f"\tdevice id:                ({d.get_device_id()})")
            print(f"\tPhysical block size:      {d.get_physical_block_size()}")
            print(f"\tLogical block size:       {d.get_logical_block_size()}")
            print(f"\tPartition table type:     {d.get_partition_table_type()}")
            print(f"\tPartition table UUID:     {d.get_partition_table_uuid()}")


if __name__ == '__main__':
    main()

# End.
