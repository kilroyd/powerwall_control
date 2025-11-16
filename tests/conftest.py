"""Fixtures for testing."""

from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.powerwall_control.const import DOMAIN
from custom_components.powerwall_control.netzero import EnergySiteConfig
from homeassistant.core import HomeAssistant

from .mocks import _mock_energysite_get_config


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations.

    This fixture is required so pytest-homeassistant-custom-component
    loads the custom components in independent repositories.
    """
    return


DEFAULT_GET_CONFIG = {
    "backup_reserve_percent": 80,
    "operational_mode": "autonomous",
    "energy_exports": "pv_only",
    "grid_charging": False,
}
DEFAULT_SET_CONFIG = {
    "backup_reserve_percent": 70,
    "operational_mode": "self_consumption",
    "energy_exports": "pv_only",
    "grid_charging": False,
}


@pytest.fixture(name="mock_energysite")
async def mock_energysite_fixture(hass: HomeAssistant) -> AsyncMock:
    """This fixture provides a mock EnergySite, returning constant EnergySiteConfig."""
    mock_energysite = await _mock_energysite_get_config(
        EnergySiteConfig(123456, DEFAULT_GET_CONFIG),
        EnergySiteConfig(123456, DEFAULT_SET_CONFIG),
    )

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "api_token": "ABCDEFG",
            "system_id": "123456",
        },
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.powerwall_control.netzero.EnergySite",
        return_value=mock_energysite,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        yield mock_energysite
