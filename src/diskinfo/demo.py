#
#    Module `demo`: implements demos for `diskinfo` package.
#    Peter Sulyok (C) 2022-2024.
#
import sys
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.console import Group
from diskinfo import DiskType, Disk, DiskInfo, size_in_hrf, time_in_hrf


def disklist_demo():
    """Disk exploring demo."""

    # Explore disks in the system.
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
    rprint(Panel(group, title="diskinfo demo: disks", title_align="left", border_style="gray30", expand=False))


def disk_demo(name: str):
    """Disk attributes demo."""

    d = Disk(name)

    panel = Panel(f"[markdown.strong]Standard disk attributes:[/] [bold green]{name}[/]", box=box.MINIMAL, expand=False)
    table = Table(border_style="gray30", box=box.MINIMAL)
    table.add_column("Attribute", justify="left", style="steel_blue1")
    table.add_column("Value", justify="left", style="orchid")

    table.add_row("name", f"[bold royal_blue1]{d.get_name()}[/]")
    table.add_row("path", f"[bold chartreuse4]{d.get_path()}[/]")
    table.add_row("by-id path", f"[gray54]{str(d.get_byid_path())}[/]")
    table.add_row("by-path path", f"[gray54]{str(d.get_bypath_path())}[/]")
    table.add_row("model", f"[bold orange3]{str(d.get_model())}[/]")
    s, u = d.get_size_in_hrf(units=0)
    size_str = f"[bold slate_blue1]{s:.1f} {u}[/]"
    table.add_row("size", size_str)
    table.add_row("serial", f"[bold light_salmon1]{d.get_serial_number()}[/]")
    table.add_row("firmware", f"[bold light_coral]{d.get_firmware()}[/]")
    table.add_row("wwn id", f"[bold sky_blue3]{d.get_wwn()}[/]")
    table.add_row("disk type", f"[bold sea_green2]{d.get_type_str()}[/]")
    table.add_row("device id", f"[bold blue1]{d.get_device_id()}[/]")
    temp_str = f"[bold bright_magenta]{d.get_temperature()} C[/]"
    table.add_row("temperature", temp_str)
    table.add_row("physical block size", f"[bold wheat4]{str(d.get_physical_block_size())} bytes [/]")
    table.add_row("logical block size", f"[bold wheat4]{str(d.get_logical_block_size())} bytes[/]")
    table.add_row("partition table type", f"[bold gray62]{d.get_partition_table_type()}[/]")
    table.add_row("partition table uuid", f"[bold green3]{d.get_partition_table_uuid()}[/]")
    try:
        sd = d.get_smart_data(sudo="/usr/bin/sudo")
        panel2 = Panel("[markdown.strong]SMART attributes[/]", box=box.MINIMAL, expand=False)
        table2 = Table(border_style="gray30", box=box.MINIMAL)
        table2.add_column("Attribute", justify="left", style="steel_blue1")
        table2.add_column("Value", justify="left", style="bold orchid")
        if sd.healthy:
            hstate = "[bold green]HEALTHY[/]"
        else:
            hstate = "[bold red]FAILED[/]"
        table2.add_row("health status", hstate)
        if d.is_nvme():
            table2.add_row("critical warning", f"[bold blue_violet]{str(sd.nvme_attributes.critical_warning)}[/]")
            t, u = time_in_hrf(sd.nvme_attributes.power_on_hours, 2)
            poh = f"[bold medium_purple3]{t:.1f} {u}[/]"
            table2.add_row("power on time", poh)
            table2.add_row("power cycles", f"[bold orange4]{str(sd.nvme_attributes.power_cycles)}[/]")
            s, u = size_in_hrf(sd.nvme_attributes.data_units_read * 1000 * 512)
            size_str = f"[bold wheat4]{s:.1f} {u}[/]"
            table2.add_row("data units read", size_str)
            s, u = size_in_hrf(sd.nvme_attributes.data_units_written * 1000 * 512)
            size_str = f"[bold wheat4]{s:.1f} {u}[/]"
            table2.add_row("data units written", size_str)
            table2.add_row("error information log entries",
                           f"[bold blue]{str(sd.nvme_attributes.error_information_log_entries)}[/]")
            table2.add_row("media and data integrity errors",
                           f"[bold blue]{str(sd.nvme_attributes.media_and_data_integrity_errors)}[/]")
            table2.add_row("unsafe shutdowns",
                           f"[bold indian_red1]{str(sd.nvme_attributes.unsafe_shutdowns)}[/]")
        else:
            index = sd.find_smart_attribute_by_name("Power_On_Hours")
            if index != -1:
                t, u = time_in_hrf(sd.smart_attributes[index].raw_value, 2)
                poh = f"[bold medium_purple3]{t:.1f} {u}[/]"
                table2.add_row("power on time", poh)
            index = sd.find_smart_attribute_by_name("Power_Cycle_Count")
            if index != -1:
                pcc = str(sd.smart_attributes[index].raw_value)
                table2.add_row("power cycles", f"[bold orange4]{pcc}[/]")
            index = sd.find_smart_attribute_by_name("LBAs_Written")
            if index != -1:
                lbaw = sd.smart_attributes[index].raw_value
                s, u = size_in_hrf(lbaw * 512)
                size_str = f"[bold medium_violet_red]{s:.1f} {u}[/]"
                table2.add_row("total LBAs written", size_str)
    except RuntimeError:
        panel2 = Panel("[markdown.strong]SMART attributes cannot be read[/]", box=box.MINIMAL, expand=False)
        table2 = None
    group = Group(panel, table, panel2, table2)
    rprint(Panel(group, title="diskinfo demo: disk attributes", title_align="left", border_style="gray30",
                 expand=False))


def partition_demo(name: str):
    """Partition demo."""

    d = Disk(name)
    plist = d.get_partition_list()

    panel = Panel(f"[markdown.strong]There are {len(plist)} partitions on disk[/] [bold green]{name}[/]\n"
                  f"[markdown.strong]Partition table type is[/] [bold green]{d.get_partition_table_type()}[/]",
                  box=box.MINIMAL, expand=False)
    table = Table(border_style="gray30", box=box.MINIMAL)
    table.add_column("Name", justify="left", style="bold orange1")
    table.add_column("Type", justify="left", style="bold orchid")
    table.add_column("Start", justify="right", style="bold gray54")
    table.add_column("Size", justify="right", style="bold gray54")
    table.add_column("Label", justify="left", style="bold purple3")
    table.add_column("Mounting point", justify="left", style="bold green")
    table.add_column("Free", justify="right", style="bold blue")
    for p in plist:
        free_size_str = f"{round(float(p.get_fs_free_size() / p.get_part_size() * 100)):>3d} %"
        table.add_row(p.get_name(), p.get_fs_type(), str(p.get_part_offset()), str(p.get_part_size()),
                      p.get_fs_label(), p.get_fs_mounting_point(), free_size_str)
    group = Group(panel, table)
    rprint(Panel(group, title="[markdown.strong]diskinfo demo: partitions[/]", title_align="left",
                 border_style="gray30", expand=False))


def usage():
    """Prints usage help text."""
    print("Usage: python -m diskinfo.demo [device] [-p]\n"
          "Examples:\n"
          "\tpython -m diskinfo.demo\n"
          "\tpython -m diskinfo.demo sda\n"
          "\tpython -m diskinfo.demo sda -p\n")


def main():
    """Demo application for package `diskinfo`."""

    if len(sys.argv) == 1:
        disklist_demo()
    elif len(sys.argv) == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        usage()
    elif len(sys.argv) == 2:
        disk_demo(sys.argv[1])
    elif len(sys.argv) == 3 and sys.argv[2] == "-p":
        partition_demo(sys.argv[1])
    else:
        usage()


if __name__ == '__main__':
    main()

# End.
