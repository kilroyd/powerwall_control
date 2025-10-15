from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PwCtrlConfigEntry

class PwCtrlGridChargingSwitch(SwitchEntity):
    _attr_has_entity_name = True
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_name = "Grid charging"

    def __init__(self):
        self._is_on = False
        #self._attr_device_info = ...  # For automatic device registration
        #self._attr_unique_id = ...

    @property
    def is_on(self) -> bool:
        """If the switch is currently on or off."""
        return self._is_on

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False


async def async_setup_entry(hass: HomeAssistant,
                            entry: PwCtrlConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback,
                            ) -> None:
    """Set up switch platform from a config entry."""

    entities: list[SwitchEntity] = []

    entities.append(PwCtrlGridChargingSwitch())

    async_add_entities(entities)
