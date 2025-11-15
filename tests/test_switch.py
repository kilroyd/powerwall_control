"""Test switch platform for powerwall_control integration."""


async def test_switch(hass, mock_energysite):
    """Test switch platform initialisation."""

    state = hass.states.get("switch.powerwall_grid_charging")

    assert state
    assert state.state == "off"
