"""Data update coordinator."""

from datetime import timedelta

from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER
from .netzero import EnergySiteConfig

# This integration is making configuration data available, which
# generally shouldn't be changing, except where an automation is
# tweaking it. Set to check twice a day.
UPDATE_INTERVAL = timedelta(minutes=720)


class PwCtrlCoordinator(DataUpdateCoordinator[EnergySiteConfig]):
    """Class used to manage data collection.

    The Netzero API returns the status of multiple entities in a
    single call, so we want to do the update for all those entiries at
    once, and avoid swamping the server with many calls for each
    entity.

    In addition, the API allows all configs to be updated at
    once. Ideally this will accumulate these modifications into a
    single call.
    """

    def __init__(self, hass: HomeAssistant, config: EnergySiteConfig) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass, logger=LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL
        )
        # This object contains acceesors for all the data retreived,
        # and has an async_update call to refresh the data.
        self.config = config

    async def _async_update_data(self) -> None:
        """Refresh data."""
        try:
            await self.config.async_update()
        except ClientError as ex:
            raise UpdateFailed(f"The service is unavailable: {ex}") from ex
