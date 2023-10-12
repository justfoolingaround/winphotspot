import asyncio
import re

import click
import rich
from click import ParamType

from winphotspot import Hotspot, TetheringWiFiBand

from .utils import rich_print_hotspot


def escape(string, chars=';\\"'):
    return "".join(f"\\{char}" if char in chars else char for char in string)


class BandParamType(ParamType):
    name = "band"

    def convert(self, band: str, param, ctx) -> TetheringWiFiBand:
        band = re.sub(r"g(?:hz)?$", "", band, flags=re.IGNORECASE)

        if band == "auto":
            return TetheringWiFiBand.AUTO

        if band == "2.4":
            return TetheringWiFiBand.TWO_POINT_FOUR_GIGAHERTZ

        if band == "5":
            return TetheringWiFiBand.FIVE_GIGAHERTZ


@click.command(name="toggle")
@click.help_option("-h", "--help")
@click.option(
    "--disable",
    "-D",
    is_flag=True,
)
@click.option(
    "-s",
    "--ssid",
    type=str,
    help="SSID of the hotspot.",
)
@click.option(
    "-p",
    "--passphrase",
    type=str,
    help="Passphrase of the hotspot.",
)
@click.option(
    "-b",
    "--band",
    type=BandParamType(),
    default="auto",
    help="Band of the hotspot.",
)
@click.option(
    "-r",
    "--restart",
    is_flag=True,
    help="Restart the hotspot if it is already running.",
)
@click.option(
    "-A",
    "--auto-disable",
    is_flag=True,
    help="Automatically disable the hotspot when no devices are connected.",
)
@click.option(
    "-Q",
    "--qr-code",
    is_flag=True,
    help="Display the QR code for the hotspot.",
)
def main(
    disable: bool,
    ssid: str,
    passphrase: str,
    band: str,
    restart: bool,
    auto_disable: bool,
    qr_code: bool,
):
    console = rich.get_console()

    hotspot = Hotspot()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(hotspot.update_config(ssid, passphrase, band))

    if auto_disable:
        loop.run_until_complete(hotspot.enable_auto_stop())
    else:
        loop.run_until_complete(hotspot.disable_auto_stop())

    running = hotspot.is_running

    if running:
        if disable or restart:
            loop.run_until_complete(hotspot.stop())
        if restart:
            loop.run_until_complete(hotspot.start())
    else:
        if not disable:
            loop.run_until_complete(hotspot.start())

    rich_print_hotspot(console, hotspot)

    try:
        import qrcode
    except ImportError:
        qr_code = False

    if qr_code:
        data = f"WIFI:T:WPA;S:{escape(hotspot.ssid)};P:{escape(hotspot.password)};;"
        qr = qrcode.QRCode(border=4)
        qr.add_data(data)

        if not hotspot.is_running:
            console.print(
                "[dim]The hotspot is not running, you may be unable to connect.[/dim]"
            )

        qr.print_ascii(invert=True)
