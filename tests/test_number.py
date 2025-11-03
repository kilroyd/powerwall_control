"""Test number platform for powerwall_control integration."""

from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.powerwall_control.const import DOMAIN
from custom_components.powerwall_control.netzero import EnergySiteConfig

DEFAULT_JSON = {
    "backup_reserve_percent": 80,
    "operational_mode": "autonomous",
    "energy_exports": "pv_only",
    "grid_charging": False,
}


async def test_number(hass):
    """Test number platform initialisation."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "api_token": "ABCDEFG",
            "system_id": "123456",
        },
    )

    # Patch async_get_config to return initial JSON
    with patch(
        "custom_components.powerwall_control.netzero.EnergySite.async_get_config",
        return_value=(EnergySiteConfig(123456, DEFAULT_JSON)),
    ):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("number.powerwall_backup_reserve")

    assert state
    assert state.state == "80"
    assert state.attributes["min"] == 0
    assert state.attributes["max"] == 100
    assert state.attributes["step"] == 1
    assert state.attributes["unit_of_measurement"] == "%"
