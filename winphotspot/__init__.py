import typing

from winsdk.windows.networking import HostName, HostNameType
from winsdk.windows.networking.connectivity import NetworkInformation
from winsdk.windows.networking.networkoperators import (
    NetworkOperatorTetheringAccessPointConfiguration,
    NetworkOperatorTetheringManager,
    TetheringCapability,
    TetheringOperationalState,
    TetheringWiFiBand,
)


class Client:
    def __init__(self, hostnames: typing.List[HostName], mac_address: str):
        self.hostnames = hostnames
        self.mac_address = mac_address

    def get_ip_address(self, ipv4: bool = True, ipv6: bool = True):
        assert ipv4 or ipv6, "At least one of ipv4 or ipv6 must be True"

        for host in self.hostnames:
            if ipv4 and host.type == HostNameType.IPV4:
                return host.canonical_name

            if ipv6 and host.type == HostNameType.IPV6:
                return host.canonical_name

    def get_name(self):
        for host in self.hostnames:
            if host.type == HostNameType.DOMAIN_NAME:
                return host.display_name

    def __str__(self):
        return f"Client(name={self.get_name() or '?'!r}, ip={self.get_ip_address() or '?'!r}, mac={self.mac_address})"


class Hotspot:
    def __init__(self):
        self.network_profile = NetworkInformation.get_internet_connection_profile()
        capability = NetworkOperatorTetheringManager.get_tethering_capability_from_connection_profile(
            self.network_profile
        )

        if capability != TetheringCapability.ENABLED:
            raise RuntimeError(f"Tethering is unsupported on this device: {capability}")

        self.manager = NetworkOperatorTetheringManager.create_from_connection_profile(
            self.network_profile
        )

    @property
    def config(self):
        return self.manager.get_current_access_point_configuration()

    async def update_config(
        self,
        ssid: typing.Optional[str] = None,
        passphrase: typing.Optional[str] = None,
        band: typing.Optional[TetheringWiFiBand] = None,
    ):
        config = self.config or NetworkOperatorTetheringAccessPointConfiguration()

        if ssid is not None:
            if not 1 <= len(ssid) <= 32:
                raise ValueError("SSID must be between 1 and 32 characters.")

            config.ssid = ssid

        if passphrase is not None:
            if len(passphrase) < 8:
                raise ValueError("Passphrase must be at least 8 characters.")

            config.passphrase = passphrase

        if band is not None:
            # TODO: Add check for band support.
            config.band = band

        current_config = (
            self.config or NetworkOperatorTetheringAccessPointConfiguration()
        )

        if (
            current_config.ssid == config.ssid
            and current_config.passphrase == config.passphrase
            and current_config.band == config.band
        ):
            return

        await self.manager.configure_access_point_async(config)

    @property
    def ssid(self):
        return self.config.ssid

    @property
    def password(self):
        return self.config.passphrase

    @property
    def band(self):
        return self.config.band

    @property
    def will_disable_on_no_connections(self):
        return bool(self.manager.is_no_connections_timeout_enabled())

    @property
    def is_running(self):
        return bool(
            self.manager.tethering_operational_state == TetheringOperationalState.ON
        )

    async def start(self):
        if self.is_running:
            return

        await self.manager.start_tethering_async()

    async def stop(self):
        if not self.is_running:
            return

        await self.manager.stop_tethering_async()

    async def enable_auto_stop(self):
        if self.will_disable_on_no_connections:
            return

        await self.manager.enable_no_connections_timeout_async()

    async def disable_auto_stop(self):
        if not self.will_disable_on_no_connections:
            return

        await self.manager.disable_no_connections_timeout_async()

    def iter_connected_devices(self):
        clients = self.manager.get_tethering_clients()

        if clients is None:
            return

        for client in clients:
            yield Client(list(client.host_names or []), client.mac_address)

    @property
    def connection_count(self):
        return int(self.manager.client_count)

    @property
    def max_connection_count(self):
        return int(self.manager.max_client_count)
