"""Define Powerwall Control switches.

This is a Home Assistant defined file that specifies all switch
entities for an integration. A switch can be on or off.

Powerwall Control defines a single switch for selecting whether grid
charging is enabled.
"""

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PwCtrlConfigEntry
from .coordinator import PwCtrlCoordinator


class PwCtrlGridChargingSwitch(CoordinatorEntity, SwitchEntity):
    """Grid Charging switch entity class."""

    _attr_has_entity_name = True
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_name = "Grid charging"

    def __init__(self, coordinator: PwCtrlCoordinator, device_info: DeviceInfo):
        """Initialize the switch entity."""
        self._attr_device_info = device_info
        super().__init__(coordinator)

        # Need an initial value
        self._is_on = False

    @property
    def is_on(self) -> bool:
        """If the switch is currently on or off."""
        return self._is_on

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._is_on = self.coordinator.config.grid_charging
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self.coordinator.async_request_control(grid_charging=True)
        # When set the coordinator will call _handle_coordinator_update

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self.coordinator.async_request_control(grid_charging=False)
        # When set the coordinator will call _handle_coordinator_update


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PwCtrlConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switch platform from a config entry."""

    entities: list[SwitchEntity] = []

    entities.append(
        PwCtrlGridChargingSwitch(
            entry.runtime_data.coordinator, entry.runtime_data.device_info
        )
    )

    async_add_entities(entities)
