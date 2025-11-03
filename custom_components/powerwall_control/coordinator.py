"""Data update coordinator."""

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER
from .netzero import EnergySite, EnergySiteConfig

# This integration is making configuration data available, which
# generally shouldn't be changing, except where an automation is
# tweaking it. Set to check twice a day.
UPDATE_INTERVAL = timedelta(minutes=720)

REQUEST_CONTROL_DEFAULT_COOLDOWN = 15
REQUEST_CONTROL_DEFAULT_IMMEDIATE = False


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

    def __init__(self, hass: HomeAssistant, site: EnergySite) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            # Filter out no-op updates
            always_update=False,
        )
        # This object contains async functions to get updated data,
        # and set desired state.
        self.site = site

        # List of things we want to set on the next config call
        self._reconfig_dict = {}

        self._debounced_control = Debouncer(
            hass,
            logger=LOGGER,
            cooldown=REQUEST_CONTROL_DEFAULT_COOLDOWN,
            immediate=REQUEST_CONTROL_DEFAULT_IMMEDIATE,
            function=self._async_control,
        )

    async def _async_update_data(self) -> EnergySiteConfig:
        """Refresh data."""
        # ClientErrors are caught by DataUpdateCoordinator.  Netzero
        # isn't raising any more specific errors, so just allow the
        # default handling to take care of it.
        return await self.site.async_get_config()

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
        updated_config = await self.config.async_set_config(**self._reconfig_dict)
        self._reconfig_dict.clear()

        # Update listeners with any new values
        self.async_set_updated_data(updated_config)
