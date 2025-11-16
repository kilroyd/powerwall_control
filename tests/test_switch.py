"""Test switch platform for powerwall_control integration."""

from datetime import timedelta

from pytest_homeassistant_custom_component.common import async_fire_time_changed

from homeassistant.components.switch import (
    DOMAIN as SWITCH_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.util.dt import utcnow

control_cooldown_interval = timedelta(seconds=15)


async def test_switch(hass, mock_energysite):
    """Test switch platform initialisation."""

    state = hass.states.get("switch.powerwall_grid_charging")

    assert state
    assert state.state == "off"


async def test_switch_turn_on_and_off(hass, mock_energysite):
    """Test grid charging on and off."""

    state = hass.states.get("switch.powerwall_grid_charging")
    assert state
    assert state.state == "off"

    base_config = mock_energysite.async_set_config.return_value
    base_config.raw_data["grid_charging"] = True
    mock_energysite.async_set_config.return_value = base_config

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "switch.powerwall_grid_charging"},
        blocking=True,
    )
    await hass.async_block_till_done()

    # The update is only done after the coordinator returns
    async_fire_time_changed(hass, utcnow() + control_cooldown_interval)
    await hass.async_block_till_done()

    state = hass.states.get("switch.powerwall_grid_charging")
    assert state
    assert state.state == "on"

    base_config.raw_data["grid_charging"] = False
    mock_energysite.async_set_config.return_value = base_config

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "switch.powerwall_grid_charging"},
        blocking=True,
    )
    await hass.async_block_till_done()

    # The update is only done after the coordinator returns
    async_fire_time_changed(hass, utcnow() + control_cooldown_interval)
    await hass.async_block_till_done()

    state = hass.states.get("switch.powerwall_grid_charging")
    assert state
    assert state.state == "off"
