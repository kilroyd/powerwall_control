"""Define Powerwall Control select entities.

This is a Home Assistant defined file that specifies all select
entities for an integration. A select entity can take one value from a
discrete set of options.

Powerwall Control defines a two select entities for selecting the
operation mode, and the grid export mode.
"""

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PwCtrlConfigEntry
from .coordinator import PwCtrlCoordinator
from .netzero import EnergyExportMode, OperationalMode


class PwCtrlOperationalModeSelectEntity(CoordinatorEntity, SelectEntity):
    """Operational mode select entity class."""

    _attr_has_entity_name = True
    _attr_unique_id = "operational_mode"
    _attr_translation_key = _attr_unique_id
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options: list[str] = ["auto", "backup", "self"]

    def __init__(self, coordinator: PwCtrlCoordinator, device_info: DeviceInfo) -> None:
        """Initialize the number entity."""
        self._attr_device_info = device_info
        super().__init__(coordinator)

        # Need an initial value
        self._attr_current_option = "auto"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        mode = self.coordinator.data.operational_mode
        if mode == OperationalMode.AUTONOMOUS:
            self._attr_current_option = "auto"
        elif mode == OperationalMode.BACKUP:
            self._attr_current_option = "backup"
        elif mode == OperationalMode.SELF_CONSUMPTION:
            self._attr_current_option = "self"
        else:
            # TODO: set unavailable?
            self._attr_current_option = "auto"
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option == "auto":
            mode = OperationalMode.AUTONOMOUS
        elif option == "backup":
            mode = OperationalMode.BACKUP
        elif option == "self":
            mode = OperationalMode.SELF_CONSUMPTION
        else:
            # TODO: ?
            mode = OperationalMode.AUTONOMOUS
        await self.coordinator.async_request_control(operational_mode=mode)
        # When set the coordinator will call _handle_coordinator_update


class PwCtrlExportModeSelectEntity(CoordinatorEntity, SelectEntity):
    """Export mode select entity class."""

    _attr_has_entity_name = True
    _attr_unique_id = "export_mode"
    _attr_translation_key = _attr_unique_id
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options: list[str] = ["never", "pv_only", "battery_ok"]

    def __init__(self, coordinator: PwCtrlCoordinator, device_info: DeviceInfo) -> None:
        """Initialize the select entity."""
        self._attr_device_info = device_info
        super().__init__(coordinator)

        # Need an initial value
        self._attr_current_option = "never"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        mode = self.coordinator.data.energy_exports
        if mode == EnergyExportMode.BATTERY_OK:
            self._attr_current_option = "battery_ok"
        elif mode == EnergyExportMode.PV_ONLY:
            self._attr_current_option = "pv_only"
        else:
            self._attr_current_option = "never"
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option == "battery_ok":
            exports = EnergyExportMode.BATTERY_OK
        elif option == "pv_only":
            exports = EnergyExportMode.PV_ONLY
        else:
            exports = EnergyExportMode.NEVER
        await self.coordinator.async_request_control(energy_exports=exports)
        # When set the coordinator will call _handle_coordinator_update


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PwCtrlConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up select platform from a config entry."""
    entities: list[SelectEntity] = []
    entities.append(
        PwCtrlOperationalModeSelectEntity(
            entry.runtime_data.coordinator, entry.runtime_data.device_info
        )
    )
    entities.append(
        PwCtrlExportModeSelectEntity(
            entry.runtime_data.coordinator, entry.runtime_data.device_info
        )
    )
    async_add_entities(entities)
