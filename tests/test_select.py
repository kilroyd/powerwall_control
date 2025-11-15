"""Test select platform for powerwall_control integration."""


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
