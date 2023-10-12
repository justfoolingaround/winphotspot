<h1><center>Pythonic Windows Portable Hotspot API</center></h1>

<p align="center">For Windows 10 and 11 only.</p>

> **Note**: This project automatically selects the network adapter with internet access to share from.

## Installation

Given that Python and Git are installed and are on PATH, his project can be installed on your device with the following command:

```sh
pip install git+https://github.com/justfoolingaround/winphotspot
```

If Git isn't installed on your device, you can also use the following command to download the latest commit:

```sh
pip install https://github.com/justfoolingaround/winphotspot/archive/refs/heads/master.zip
```

## Usage

After installation, you will get a console-entry point (given that Python is in PATH). For library usage, you can simply import `winphotspot`.

- Console-entry point usage:

    ```sh
    $ hotspot
    Usage: hotspot [OPTIONS]

    Options:
    -h, --help             Show this message and exit.
    -D, --disable
    -s, --ssid TEXT        SSID of the hotspot.
    -p, --passphrase TEXT  Passphrase of the hotspot.
    -b, --band BAND        Band of the hotspot.
    -r, --restart          Restart the hotspot if it is already running.
    -A, --auto-disable     Automatically disable the hotspot when no devices are
                            connected.
    -Q, --qr-code          Display the QR code for the hotspot.
    ```

    > **Note**: `-Q` / `--qr-code` requires [`qrcode==7.3.1`](https://github.com/lincolnloop/python-qrcode/tree/v7.3.1) to be installed on your Python installation. If not, it'll automatically be toggled off.

- Library usage:

    ```py
    import asyncio

    import winphotspot

    hotspot = winphotspot.Hotspot()
    loop = asyncio.new_event_loop()

    print(hotspot.ssid, hotspot.password)
    
    loop.run_until_complete(hotspot.start())
    ```

## Known issues

Since Microsoft is a totally poor indie company, you will face the following issue(s):

- If re-configured or activated and deactivated rapidly, your hotspot will cease to share internet from your network adapter. Rebooting seems to fix this issue.
- If you haven't updated your Windows in a while and have `KB5014697` or `KB5014699` installed, your hotspot will not share internet from your network adapter.

## Console-entry point use-cases

The `hotspot` entry point runs an executable that safely toggles your hotspot on and off. 

- If your hotspot is off and you'd like to keep it that way but would also like to inquire the credentials, you can safely run `hotspot -D`. 
- If your hotspot is on and you'd like to safely view newly connected devices or even just inquire the credentials, you can safely run `hotspot`.
- If you'd like to change credentials, simply run `hotspot --ssid [SSID] --passphrase [PASSWORD]`
    - If `-D` is in use, your credentials will be silently changed.
    - If hotspot is in use, Windows will automatically reload the hotspot.
