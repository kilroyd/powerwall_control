"""Data update coordinator."""

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER
from .netzero import EnergySiteConfig

# This integration is making configuration data available, which
# generally shouldn't be changing, except where an automation is
# tweaking it. Set to check twice a day.
UPDATE_INTERVAL = timedelta(minutes=720)

REQUEST_CONTROL_DEFAULT_COOLDOWN = 15
REQUEST_CONTROL_DEFAULT_IMMEDIATE = False


class PwCtrlCoordinator(DataUpdateCoordinator):
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
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            # The API updates the data in config, and we don't return json in _async_update_data.
            # So tell the DataUpdateCoordinator to always update all entities.
            always_update=True,
        )
        # This object contains acceesors for all the data retreived,
        # and has an async_update call to refresh the data.
        self.config = config

        # List of things we want to set on the next config call
        self._reconfig_dict = {}

        self._debounced_control = Debouncer(
            hass,
            logger=LOGGER,
            cooldown=REQUEST_CONTROL_DEFAULT_COOLDOWN,
            immediate=REQUEST_CONTROL_DEFAULT_IMMEDIATE,
            function=self._async_control,
        )

    async def _async_update_data(self) -> None:
        """Refresh data."""
        # ClientErrors are caught by DataUpdateCoordinator.  Netzero
        # isn't raising any more specific errors, so just allow the
        # default handling to take care of it.
        await self.config.async_update()

    async def async_request_control(self, **kwargs) -> None:
        """Pass requests for control to netzero.

        Add the request to a list, and then set a debounce to actually
        make the change.
        """
        self._reconfig_dict.update(kwargs)
        await self._debounced_control.async_call()
        # TODO: cancel scheduled calls on shutdown

    async def _async_control(self) -> None:
        """Invoke the control call, and update listeners with result."""
        # Pass the accumulated configuration changes to netzero
        await self.config.async_control(**self._reconfig_dict)
        self._reconfig_dict.clear()

        # Update listeners with any new values
        await self.async_set_updated_data(None)
