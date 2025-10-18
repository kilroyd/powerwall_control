"""Define Powerwall Control switches.

This is a Home Assistant defined file that specifies all switch
entities for an integration. A switch can be on or off.

Powerwall Control defines a single switch for selecting whether grid
charging is enabled.
"""

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PwCtrlConfigEntry


class PwCtrlGridChargingSwitch(SwitchEntity):
    """Grid Charging switch entity class."""

    _attr_has_entity_name = True
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_name = "Grid charging"

    def __init__(self):
        """Initialize the switch entity."""
        self._is_on = False
        # self._attr_device_info = ...  # For automatic device registration
        # self._attr_unique_id = ...

    @property
    def is_on(self) -> bool:
        """If the switch is currently on or off."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PwCtrlConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switch platform from a config entry."""

    entities: list[SwitchEntity] = []

    entities.append(PwCtrlGridChargingSwitch())

    async_add_entities(entities)
