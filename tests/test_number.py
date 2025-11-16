"""Test number platform for powerwall_control integration."""

from datetime import timedelta

from pytest_homeassistant_custom_component.common import async_fire_time_changed

from homeassistant.components.number import (
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.util.dt import utcnow

control_cooldown_interval = timedelta(seconds=15)


async def test_number(hass, mock_energysite):
    """Test number platform initialisation."""

    state = hass.states.get("number.powerwall_backup_reserve")

    assert state
    assert state.state == "80"
    assert state.attributes["min"] == 0
    assert state.attributes["max"] == 100
    assert state.attributes["step"] == 1
    assert state.attributes["unit_of_measurement"] == "%"


async def test_number_set(hass, mock_energysite):
    """Test setting backup reserve."""

    state = hass.states.get("number.powerwall_backup_reserve")
    assert state
    assert state.state == "80"

    base_config = mock_energysite.async_set_config.return_value
    base_config.raw_data["backup_reserve_percent"] = 70
    mock_energysite.async_set_config.return_value = base_config

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_VALUE: 70.0, ATTR_ENTITY_ID: "number.powerwall_backup_reserve"},
        blocking=True,
    )
    await hass.async_block_till_done()

    # The update is only done after the coordinator returns
    async_fire_time_changed(hass, utcnow() + control_cooldown_interval)
    await hass.async_block_till_done()

    state = hass.states.get("number.powerwall_backup_reserve")
    assert state
    assert state.state == "70"
