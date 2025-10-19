"""Home Assistant Tesla Powerwall Control Integration.

This integration allows you to reconfigure your Powerwall via the
Netzero Developer API.

* Set operational mode (autonomous or self supporting).

* Set battery backup reserve.

* Enable grid charging.

* Set grid export mode (never, solar only, solar and battery).

This integration is intended to work together with the Tesla Powerwall
integration. The entities from that integration should be used to
monitor the Powerwall state. This integration is only intended to make
changes to the Powerwall configuration. The same changes can be made
via the Tesla App, Tesla Fleet API, or alternative integrations like
Teslemetry.
"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import PwCtrlCoordinator

# Temporarily use netzero directly to test in place within HA
from .netzero import Auth, EnergySite

# List of platforms to support.
PLATFORMS = [Platform.NUMBER, Platform.SELECT, Platform.SWITCH]

# Our ConfigEntry.runtime_data will hold PwCtrlData.
# Otherwise access the config entries via the .data[] dictionary.
type PwCtrlConfigEntry = ConfigEntry[PwCtrlData]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Called by Home Assistant when loading the integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: PwCtrlConfigEntry) -> bool:
    """Set up Powerwall Control from a config entry.

    The config entry is created by the Home Assistant config flow.
    """
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.data["system_id"])},
        manufacturer="Tesla",
        name="Powerwall",
    )
    session = async_get_clientsession(hass)
    # Create API connection
    auth = Auth(session, entry.data["api_token"])
    site = EnergySite(auth, entry.data["system_id"])
    config = await site.async_get_config()

    coordinator = PwCtrlCoordinator(hass, config)

    entry.runtime_data = PwCtrlData(hass, site, coordinator, device_info)

    # Creates a HA object for each platform required.
    # This calls `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Update all entities with initial values populated during
    # async_get_config() call
    coordinator.async_set_updated_data({})

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True


# Temp location. Move to appropriate file when we figure out what we
# want PwCtrlData to do. For now store hass and site.
class PwCtrlData:
    """Central class to store runtime state.

    This should eventually become a coordinator which talks to the
    Netzero servers.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        site: EnergySite,
        coordinator: PwCtrlCoordinator,
        device_info: DeviceInfo,
    ) -> None:
        """Store hass and site."""
        self._hass = hass
        self._site = site
        self.coordinator = coordinator
        self.device_info = device_info
