"""Test powerwall_control init."""

from custom_components.powerwall_control.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


async def test_async_setup(hass: HomeAssistant) -> None:
    """Test async setup."""
    assert await async_setup_component(hass, DOMAIN, {})
