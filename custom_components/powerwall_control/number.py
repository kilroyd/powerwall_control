from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.const import PERCENTAGE, PRECISION_WHOLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.icon import icon_for_battery_level

from . import PwCtrlConfigEntry


class PwCtrlBackupReserveNumberEntity(NumberEntity):
    """Backup Reserve number entity class."""

    _attr_native_step = PRECISION_WHOLE
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_device_class = NumberDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_name = "Backup reserve"

    def __init__(self):
        """Initialize the number entity."""
        self._attr_native_value = 100

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        value = int(value)
        self._attr_native_value = value
        #        self.async_write_ha_state()
        self._attr_icon = icon_for_battery_level(self.native_value)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PwCtrlConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up number platform from a config entry."""
    entities: list[NumberEntity] = []
    entities.append(PwCtrlBackupReserveNumberEntity())
    async_add_entities(entities)
