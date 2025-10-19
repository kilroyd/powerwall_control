"""Define Powerwall Control select entities.

This is a Home Assistant defined file that specifies all select
entities for an integration. A select entity can take one value from a
discrete set of options.

Powerwall Control defines a two select entities for selecting the
operation mode, and the grid export mode.
"""

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PwCtrlConfigEntry
from .coordinator import PwCtrlCoordinator
from .netzero import EnergyExportMode, OperationalMode


class PwCtrlOperationalModeSelectEntity(CoordinatorEntity, SelectEntity):
    """Operational mode select entity class."""

    _attr_name = "Operational mode"
    _attr_options: list[str] = ["Autonomous", "Self consumption"]

    def __init__(self, coordinator: PwCtrlCoordinator):
        """Initialize the number entity."""
        super().__init__(coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        mode = self.coordinator.config.operational_mode
        if mode == OperationalMode.AUTONOMOUS:
            self._attr_current_option = "Autonomous"
        elif mode == OperationalMode.SELF_CONSUMPTION:
            self._attr_current_option = "Self consumption"
        else:
            # TODO: set unavailable?
            self._attr_current_option = "Autonomous"
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option == "Autonomous":
            mode = OperationalMode.AUTONOMOUS
        elif option == "Self consumption":
            mode = OperationalMode.SELF_CONSUMPTION
        else:
            # TODO: ?
            mode = OperationalMode.AUTONOMOUS
        await self.coordinator.async_request_control(operational_mode=mode)
        # When set the coordinator will call _handle_coordinator_update


class PwCtrlExportModeSelectEntity(CoordinatorEntity, SelectEntity):
    """Export mode select entity class."""

    _attr_name = "Export mode"
    _attr_options: list[str] = ["Never", "PV only", "Battery ok"]

    def __init__(self, coordinator: PwCtrlCoordinator):
        """Initialize the select entity."""
        super().__init__(coordinator)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        mode = self.coordinator.config.energy_exports
        if mode == EnergyExportMode.BATTERY_OK:
            self._attr_current_option = "Battery ok"
        elif mode == EnergyExportMode.PV_ONLY:
            self._attr_current_option = "PV only"
        else:
            self._attr_current_option = "Never"
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option == "Battery ok":
            exports = EnergyExportMode.BATTERY_OK
        elif option == "PV only":
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
    entities.append(PwCtrlOperationalModeSelectEntity(entry.runtime_data.coordinator))
    entities.append(PwCtrlExportModeSelectEntity(entry.runtime_data.coordinator))
    async_add_entities(entities)
