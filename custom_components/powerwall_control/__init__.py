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

# List of platforms to support.
PLATFORMS = [Platform.NUMBER, Platform.SELECT, Platform.SWITCH]

# Our ConfigEntry.runtime_data will hold PwCtrlData.
# Otherwise access the config entries the the .data[] dictionary.
type PwCtrlConfigEntry = ConfigEntry[PwCtrlData]


async def async_setup_entry(hass: HomeAssistant, entry: PwCtrlConfigEntry) -> bool:
    """Set up Powerwall Control from a config entry."""
    # TODO: initialize class that will do the talking to Netzero?
    entry.runtime_data = PwCtrlData(
        hass, entry.data["api_token"], entry.data["system_id"]
    )

    # Creates a HA object for each platform required.
    # This calls `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True


# Temp location. Move to appropriate file when we figure out what we
# want PwCtrlData to do. For now store the token and system id.
class PwCtrlData:
    """Central class to store runtime state.

    This should eventually become a coordinator which talks to the
    Netzero servers.
    """

    def __init__(self, hass: HomeAssistant, api_token: str, system_id: str) -> None:
        """Init dummy hub."""
        self._hass = hass
        self._api_token = api_token
        self._system_id = system_id
