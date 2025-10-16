from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import PwCtrlConfigEntry


class PwCtrlOperationalModeSelectEntity(SelectEntity):
    """Operational mode select entity class."""

    _attr_name = "Operational mode"
    _attr_options: list[str] = ["Autonomous",
                                "Self consumption"]


    def __init__(self):
        """Initialize the number entity."""
        self._attr_current_option = "Autonomous"


    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
#        self.async_write_ha_state()


class PwCtrlExportModeSelectEntity(SelectEntity):
    """Export mode select entity class."""

    _attr_name = "Export mode"
    _attr_options: list[str] = ["Never",
                                "PV only",
                                "Battery ok"]


    def __init__(self):
        """Initialize the select entity."""
        self._attr_current_option = "PV only"


    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
#        self.async_write_ha_state()


async def async_setup_entry(hass: HomeAssistant,
                            entry: PwCtrlConfigEntry,
                            async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Set up select platform from a config entry."""
    entities: list[SelectEntity] = []
    entities.append(PwCtrlOperationalModeSelectEntity())
    entities.append(PwCtrlExportModeSelectEntity())
    async_add_entities(entities)
