"""Define Powerwall Control number entities.

This is a Home Assistant defined file that specifies all number
entities for an integration. A number entity has a numerical value.

Powerwall Control defines a single number entity for selecting the
battery backup reserve value.
"""

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.const import PERCENTAGE, PRECISION_WHOLE, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.icon import icon_for_battery_level
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PwCtrlConfigEntry
from .coordinator import PwCtrlCoordinator


class PwCtrlBackupReserveNumberEntity(CoordinatorEntity, NumberEntity):
    """Backup Reserve number entity class."""

    _attr_native_step = PRECISION_WHOLE
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_device_class = NumberDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_name = "Backup reserve"
    _attr_unique_id = "backup_reserve"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: PwCtrlCoordinator, device_info: DeviceInfo) -> None:
        """Initialize the number entity."""
        self._attr_device_info = device_info
        super().__init__(coordinator)

        # Need initial values
        self._attr_native_value = 20
        self._attr_icon = icon_for_battery_level(self._attr_native_value)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.config.backup_reserve_percent
        self._attr_icon = icon_for_battery_level(self._attr_native_value)
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        value = int(value)
        await self.coordinator.async_request_control(backup_reserve_percent=value)
        # When set the coordinator will call _handle_coordinator_update


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PwCtrlConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up number platform from a config entry."""
    entities: list[NumberEntity] = []
    entities.append(
        PwCtrlBackupReserveNumberEntity(
            entry.runtime_data.coordinator, entry.runtime_data.device_info
        )
    )
    async_add_entities(entities)
