"""Test select platform for powerwall_control integration."""

from datetime import timedelta

from pytest_homeassistant_custom_component.common import async_fire_time_changed

from homeassistant.components.select import (
    ATTR_OPTION,
    DOMAIN as SELECT_DOMAIN,
    SERVICE_SELECT_OPTION,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.util.dt import utcnow

control_cooldown_interval = timedelta(seconds=15)


async def test_select(hass, mock_energysite):
    """Test select platform initialisation."""

    state = hass.states.get("select.powerwall_operational_mode")

    assert state
    assert state.state == "auto"
    assert "auto" in state.attributes["options"]
    assert "backup" in state.attributes["options"]
    assert "self" in state.attributes["options"]

    state = hass.states.get("select.powerwall_energy_export_mode")

    assert state
    assert state.state == "pv_only"
    assert "pv_only" in state.attributes["options"]
    assert "never" in state.attributes["options"]
    assert "battery_ok" in state.attributes["options"]


async def test_select_operational_mode(hass, mock_energysite):
    """Test operational_mode value selection."""
    test_values = [
        # JSON input val, HA state
        ("self_consumption", "self"),
        ("backup", "backup"),
        ("autonomous", "auto"),
    ]

    state = hass.states.get("select.powerwall_operational_mode")
    assert state
    assert state.state == "auto"

    base_config = mock_energysite.async_set_config.return_value

    for val in test_values:
        base_config.raw_data["operational_mode"] = val[0]
        mock_energysite.async_set_config.return_value = base_config

        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            {ATTR_ENTITY_ID: "select.powerwall_operational_mode", ATTR_OPTION: val[1]},
            blocking=True,
        )
        await hass.async_block_till_done()

        # The update is only done after the coordinator returns
        async_fire_time_changed(hass, utcnow() + control_cooldown_interval)
        await hass.async_block_till_done()

        state = hass.states.get("select.powerwall_operational_mode")
        assert state
        assert state.state == val[1]


async def test_select_energy_export_mode(hass, mock_energysite):
    """Test energy_export value selection."""
    test_values = [
        # JSON input val, HA state
        ("never", "never"),
        ("pv_only", "pv_only"),
        ("battery_ok", "battery_ok"),
    ]

    state = hass.states.get("select.powerwall_energy_export_mode")
    assert state
    assert state.state == "pv_only"

    base_config = mock_energysite.async_set_config.return_value

    for val in test_values:
        base_config.raw_data["energy_exports"] = val[0]
        mock_energysite.async_set_config.return_value = base_config

        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            {
                ATTR_ENTITY_ID: "select.powerwall_energy_export_mode",
                ATTR_OPTION: val[1],
            },
            blocking=True,
        )
        await hass.async_block_till_done()

        # The update is only done after the coordinator returns
        async_fire_time_changed(hass, utcnow() + control_cooldown_interval)
        await hass.async_block_till_done()

        state = hass.states.get("select.powerwall_energy_export_mode")
        assert state
        assert state.state == val[1]
