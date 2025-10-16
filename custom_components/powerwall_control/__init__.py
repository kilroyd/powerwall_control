from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# Our ConfigEntry.runtime_data will hold PwCtrlData.
# Otherwise access the config entries the the .data[] dictionary.
type PwCtrlConfigEntry = ConfigEntry[PwCtrlData]


async def async_setup_entry(hass: HomeAssistant, entry: PwCtrlConfigEntry) -> bool:
    """
    Set up Powerwall Control from a config entry .
    """
    # TODO: initialize class that will do the talking to Netzero?
    entry.runtime_data = PwCtrlData(hass, entry.data["api_token"], entry.data["system_id"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Unload a config entry.
    """
    return True


# Temp location. Move to appropriate file when we figure out what we
# want PwCtrlData to do. For now store the token and system id.
class PwCtrlData:
    def __init__(self, hass: HomeAssistant, api_token:str, system_id: str) -> None:
        """Init dummy hub."""
        self._hass = hass
        self._api_token = api_token
        self._system_id = system_id
