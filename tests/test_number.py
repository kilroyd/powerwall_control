"""Test number platform for powerwall_control integration."""


async def test_number(hass, mock_energysite):
    """Test number platform initialisation."""

    state = hass.states.get("number.powerwall_backup_reserve")

    assert state
    assert state.state == "80"
    assert state.attributes["min"] == 0
    assert state.attributes["max"] == 100
    assert state.attributes["step"] == 1
    assert state.attributes["unit_of_measurement"] == "%"
