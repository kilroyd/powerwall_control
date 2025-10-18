"""API library for access to Netzero Developer API."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from aiohttp import ClientResponse, ClientSession


class OperationalMode(StrEnum):
    """States that may be used by operational mode."""

    AUTONOMOUS = "autonomous"
    SELF_CONSUMPTION = "self_consumption"


class EnergyExportMode(StrEnum):
    """States that may be used by energy export mode."""

    NEVER = "never"
    PV_ONLY = "pv_only"
    BATTERY_OK = "battery_ok"


class GridStatus(StrEnum):
    """States that may be used by grid status."""

    ACTIVE = "Active"
    INACTIVE = "Inactive"


class IslandStatus(StrEnum):
    """States that may be used by island status."""

    ON_GRID = "on_grid"
    OFF_GRID = "off_grid"


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


class EnergySiteStatus:
    """Class that represents an energy site's current status."""

    def __init__(self, auth: Auth, id: str, raw_data: dict[str, Any] = {}):
        """Initialize a config object."""
        self.auth = auth
        self.id = id
        self.raw_data = raw_data

    @property
    def percentage_charged(self) -> float:
        """Percentage charge of the batteries at the energy site."""
        return float(self.raw_data["percentage_charged"])

    @property
    def solar_power(self) -> int:
        """Current solar power generation in W."""
        return self.raw_data["solar_power"]

    @property
    def battery_power(self) -> int:
        """Current battery power output in W.

        While charging, this value will be negative.
        """
        return self.raw_data["battery_power"]

    @property
    def load_power(self) -> int:
        """Current site load in W.

        Energy consumption of the site, ignoring any local power generation
        and battery usage (for power or storage).
        """
        return self.raw_data["load_power"]

    @property
    def grid_power(self) -> int:
        """Current grid power usage in W.

        Positive when importing energy from the grid, and negative
        when exporting energy to the grid.
        """
        return self.raw_data["grid_power"]

    @property
    def generator_power(self) -> int:
        """Current generator power in W.

        Power from other energy generation sources.
        """
        return self.raw_data["generator_power"]

    @property
    def grid_status(self) -> GridStatus:
        """Current grid status.

        Either active or inactive.
        """
        return GridStatus(self.raw_data["grid_status"])

    @property
    def island_status(self) -> IslandStatus:
        """Current island status.

        Either on grid or off grid.
        """
        return IslandStatus(self.raw_data["island_status"])

    @property
    def storm_mode_active(self) -> bool:
        """Whether storm mode is currently active."""
        return self.raw_data["storm_mode_active"]

    @property
    def timestamp(self) -> str:
        """Time associated with current site readings."""
        return datetime.fromisoformat(self.raw_data["timestamp"])

    # TODO: support for wall connectors

    async def async_update(self):
        """Update the energy site status.

        Note that this retreives the full configuration.
        """
        resp = await self.auth.request("get", f"{self.id}/config")
        resp.raise_for_status()
        self.raw_data = await resp.json()["live_status"]


class EnergySiteConfig:
    """Class that represents an energy site's configuration."""

    def __init__(self, auth: Auth, id: str, raw_data: dict[str, Any] = {}):
        """Initialize a config object."""
        self.auth = auth
        self.id = id
        self.raw_data = raw_data

    @property
    def backup_reserve_percent(self) -> int:
        """The backup reserve as a percentage."""
        return self.raw_data["backup_reserve_percent"]

    @property
    def operational_mode(self) -> OperationalMode:
        """The operational mode of the site.

        This may be either autonomous or self_supported.
        """
        return OperationalMode(self.raw_data["operational_mode"])

    @property
    def energy_exports(self) -> EnergyExportMode:
        """The grid export mode of the site.

        This may be one of never, pv_only, or battery_ok.
        """
        return EnergyExportMode(self.raw_data["energy_exports"])

    @property
    def grid_charging(self) -> bool:
        """Whether grid charging is enabled."""
        return self.raw_data["grid_charging"]

    @property
    def live_status(self) -> EnergySiteStatus:
        """A class from which live status of the site can be queried."""
        return EnergySiteStatus(self.auth, self.id, self.raw_data["live_status"])

    async def async_control(self, **kwargs):
        """Reconfigure the energy site with new parameters.

        Each parameter can be changed individually, or together.
        The response includes the updated state of the energy site.

        Accepted kwargs parameters are
        backup_reserve_percent
        grid_charging
        energy_exports
        operational_mode
        """
        json = {}
        value = kwargs.get("backup_reserve_percent")
        if value is not None:
            json["backup_reserve_percent"] = value
        value = kwargs.get("grid_charging")
        if value is not None:
            json["grid_charging"] = value
        value = kwargs.get("energy_exports")
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
