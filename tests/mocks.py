"""Mocks for powerwall_control testing."""

from unittest.mock import AsyncMock

from custom_components.powerwall_control.netzero import EnergySite


async def _mock_energysite_get_config(config):
    """Mock netzero EnergySite."""
    energysite_mock = AsyncMock(EnergySite)
    # energysite_mock.__aenter__.return_value = energysite_mock

    energysite_mock.async_get_config.return_value = config

    return energysite_mock
