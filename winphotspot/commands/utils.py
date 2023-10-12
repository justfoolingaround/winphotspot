import rich

from winphotspot import Hotspot


def rich_print_hotspot(console: "rich.Console", hotspot: Hotspot):
    connected = hotspot.is_running

    color = "green" if connected else "red"

    band = (
        "2.4GHz/5GHz (device decides)"
        if hotspot.band == "auto"
        else "2.4GHz"
        if hotspot.band == "2.4"
        else "5GHz"
    )

    console.print(
        f"[bold {color}]{hotspot.ssid}[/bold {color}] [dim]{band}, sharing from {hotspot.network_profile.profile_name}[/dim]"
    )
    console.print(f"passwd: {hotspot.password!r}")

    if connected:
        console.print(
            f"{hotspot.connection_count}/{hotspot.max_connection_count} connected."
        )

        if hotspot.will_disable_on_no_connections:
            console.print(
                "[dim]The hotspot will be disabled after a while when no devices are connected.[/dim]"
            )

        for n, device in enumerate(hotspot.iter_connected_devices(), 1):
            console.print(
                f"    {n}. {device.get_name() or '???'} ({device.mac_address}, {device.get_ip_address() or 'unknown IP address'})"
            )
