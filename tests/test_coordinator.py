"""Tests for the control coordinator.

This does not re-test the functionality inheritted from the
DataUpdatecoordinator.
"""

from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.powerwall_control import netzero
from custom_components.powerwall_control.coordinator import PwCtrlCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import utcnow


def get_crd(
    hass: HomeAssistant,
) -> PwCtrlCoordinator:
    """Make coordinator mocks."""
    site = netzero.EnergySite(None, 123456)

    return PwCtrlCoordinator(hass, site)


@pytest.fixture
def crd(hass: HomeAssistant, mock_energysite: netzero.EnergySite) -> PwCtrlCoordinator:
    """Coordinator mock with default update interval."""
    return get_crd(hass)


async def test_async_request_control(
    hass: HomeAssistant,
    crd: PwCtrlCoordinator,
) -> None:
    """Test async_request_control for coordinator."""
    assert crd.data is None
    await crd.async_refresh()
    assert crd.last_update_success is True

    update_interval = crd.update_interval

    # Check initial values
    assert crd.data.backup_reserve_percent == 80
    assert crd.data.operational_mode == netzero.OperationalMode.AUTONOMOUS
    assert crd.data.energy_exports == netzero.EnergyExportMode.PV_ONLY
    assert not crd.data.grid_charging

    updates = []

    def update_callback():
        updates.append(crd.data)

    unsub = crd.async_add_listener(update_callback)
    await crd.async_request_control(backup_reserve_percent=50)

    # Nothing should have changed yet
    assert len(updates) == 0

    # Wait for the update interval
    async_fire_time_changed(hass, utcnow() + update_interval)
    await hass.async_block_till_done()

    # Check we've had an update from the set_config call
    assert len(updates) == 1
    assert updates[0].backup_reserve_percent == 70
    assert updates[0].operational_mode == netzero.OperationalMode.SELF_CONSUMPTION
    assert updates[0].energy_exports == netzero.EnergyExportMode.PV_ONLY
    assert not updates[0].grid_charging

    # Unsubscribe
    unsub()


async def test_shutdown(hass: HomeAssistant, crd: PwCtrlCoordinator) -> None:
    """Test async_shutdown for coordinator."""
    assert crd.data is None
    await crd.async_refresh()
    assert crd.last_update_success is True

    # Check initial values
    assert crd.data.backup_reserve_percent == 80
    assert crd.data.operational_mode == netzero.OperationalMode.AUTONOMOUS
    assert crd.data.energy_exports == netzero.EnergyExportMode.PV_ONLY
    assert not crd.data.grid_charging

    updates = []

    def update_callback():
        updates.append(crd.data)

    _ = crd.async_add_listener(update_callback)
    await crd.async_request_control()

    # Nothing updated yet
    assert len(updates) == 0

    # Test shutdown through function
    # ruff: noqa: SLF001 allow use of private _debounced_control
    with patch.object(crd._debounced_control, "async_shutdown") as mock_shutdown:
        await crd.async_shutdown()

    # Test we shutdown the debouncer and cleared the subscriptions
    assert len(mock_shutdown.mock_calls) == 1

    # Wait for the update interval
    async_fire_time_changed(hass, utcnow() + crd.update_interval)
    await hass.async_block_till_done()

    # No updates
    assert len(updates) == 0
