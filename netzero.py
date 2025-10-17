"""API library for access to Netzero Developer API."""

from enum import StrEnum
from typing import Any

from aiohttp import ClientResponse, ClientSession


class OperationalMode(StrEnum):
    """States that may be used by operational mode."""

    AUTONOMOUS = "autonomous"
    SELF_CONSUMPTION = "self_consumption"


class GridExportMode(StrEnum):
    """States that may be used by grid export mode."""

    NEVER = "never"
    PV_ONLY = "pv_only"
    BATTERY_OK = "battery_ok"


class Auth:
    """Class to make authenticated requests."""

    def __init__(self, websession: ClientSession, access_token: str):
        """Initialize the auth."""
        self.websession = websession
        self.host = "https://api.netzero.energy/api/v1"
        self.access_token = access_token

    async def request(self, method: str, path: str, **kwargs) -> ClientResponse:
        """Make a request."""
        if headers := kwargs.pop("headers", {}):
            headers = dict(headers)
        headers["authorization"] = f"Bearer {self.access_token}"

        return await self.websession.request(
            method,
            f"{self.host}/{path}",
            **kwargs,
            headers=headers,
        )


class EnergySiteConfig:
    """Class that represents an energy site's configuration."""

    def __init__(self, auth: Auth, id: str, raw_data: dict[str, Any] = {}):
        """Initialize a config object."""
        self.auth = auth
        self.id = id
        self.raw_data = raw_data

    @property
    def battery_charge(self) -> float:
        """Percentage charge of the batteries at the energy site."""
        return float(self.raw_data["percentage_charged"])

    @property
    def backup_reserve(self) -> int:
        """Return the backup reserve as a percentage."""
        return self.raw_data["backup_reserve_percent"]

    @property
    def operational_mode(self) -> OperationalMode:
        """Return the operational mode of the site.

        This may be either autonomous or self_supported.
        """
        return OperationalMode(self.raw_data["operational_mode"])

    @property
    def grid_export_mode(self) -> GridExportMode:
        """Return the grid export mode of the site.

        This may be one of never, pv_only, or battery_pl.
        """
        return GridExportMode(self.raw_data["energy_exports"])

    @property
    def grid_charging_enabled(self) -> bool:
        """Return whether grid charging is enabled."""
        return self.raw_data["grid_charging"]

    async def async_control(self, **kwargs):
        """Reconfigure the energy site with new parameters.

        Each parameter can be changed individually, or together.
        The response includes the updated state of the energy site.

        Accepted kwargs parameters are
        backup_reserve
        grid_charging_enabled
        grid_export_mode
        operational_mode
        """
        json = {}
        value = kwargs.get("backup_reserve")
        if value is not None:
            json["backup_reserve_percent"] = value
        value = kwargs.get("grid_charging_enabled")
        if value is not None:
            json["grid_charging"] = value
        value = kwargs.get("grid_export_mode")
        if value is not None:
            json["energy_exports"] = str(value)
        value = kwargs.get("operational_mode")
        if value is not None:
            json["operational_mode"] = str(value)
        resp = await self.auth.request("post", f"{self.id}/config", json=json)
        resp.raise_for_status()
        self.raw_data = await resp.json()

    async def async_update(self):
        """Update the energy site configuration."""
        resp = await self.auth.request("get", f"{self.id}/config")
        resp.raise_for_status()
        self.raw_data = await resp.json()


class EnergySite:
    """Class representing a single energy site."""

    def __init__(self, auth: Auth, id: str):
        """Initialize the API and store the auth so we can make requests."""
        self.auth = auth
        self.id = id

    async def async_get_config(self) -> EnergySiteConfig:
        """Return the energy site configuration."""
        resp = await self.auth.request("get", f"{self.id}/config")
        resp.raise_for_status()
        return EnergySiteConfig(self.auth, self.id, resp.json)
