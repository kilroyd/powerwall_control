"""Fixtures for testing."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations.

    This fixture is required so pytest-homeassistant-custom-component
    loads the custom components in independent repositories.
    """
    return
