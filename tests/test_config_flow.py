"""Tests for the config flow."""

from unittest.mock import patch

import aiohttp
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.powerwall_control.const import DOMAIN
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

VALID_INPUT = {
    "api_token": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCD",
    "system_id": "1234567",
}


async def test_show_form(hass: HomeAssistant) -> None:
    """Test that the form is served with no input."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_flow_user_step_valid_input(hass: HomeAssistant) -> None:
    """Test that on valid input we proceed to async_create_entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    # Patch async_get_config - this verifies that we can talk to the
    # servers.  Just return without error, which should allow the
    # config flow to get to the next step.
    with patch(
        "custom_components.powerwall_control.config_flow.async_get_config",
        return_value=(None, None),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=VALID_INPUT
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Energy site 1234567"
    assert result["data"] == VALID_INPUT


async def test_flow_user_step_bad_api_token(hass: HomeAssistant) -> None:
    """Test that with an invalid API token, we report an appropriate error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    # Patch async_get_config - this verifies that we can talk to the
    # servers.  Just return without error, which should allow the
    # config flow to get to the next step.
    with patch(
        "custom_components.powerwall_control.config_flow.async_get_config",
        return_value=(None, None),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={"api_token": "ABCD", "system_id": "1234567"}
        )
        await hass.async_block_till_done()

    assert result["errors"] == {"base": "invalid_token"}


async def test_flow_user_step_bad_system_id(hass: HomeAssistant) -> None:
    """Test that with an invalid System ID, we report an appropriate error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    # Patch async_get_config - this verifies that we can talk to the
    # servers.  Just return without error, which should allow the
    # config flow to get to the next step.
    with patch(
        "custom_components.powerwall_control.config_flow.async_get_config",
        return_value=(None, None),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "api_token": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCD",
                "system_id": "ab12345",
            },
        )
        await hass.async_block_till_done()

    assert result["errors"] == {"base": "invalid_system_id"}


async def test_flow_user_step_cannot_connect(hass: HomeAssistant) -> None:
    """Test that with invalid token and ID, we report an appropriate error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    # Patch async_get_config - this verifies that we can talk to the
    # servers. Return an error, preventing the config flow getting to
    # the next step.
    with patch(
        "custom_components.powerwall_control.config_flow.async_get_config",
        side_effect=aiohttp.ClientResponseError(
            "Can't connect", status=400, history=()
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "api_token": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCD",
                "system_id": "1234567",
            },
        )
        await hass.async_block_till_done()

    assert result["errors"] == {"base": "cannot_connect"}


async def test_flow_reconfigure_step_valid_input(hass: HomeAssistant) -> None:
    """Test reconfigure with valid input proceeds to async_update_reload_and_abort."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "api_token": "ABCDEFG",
            "system_id": "1234567",
        },
    )
    entry.add_to_hass(hass)
    result = await entry.start_reconfigure_flow(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    # Patch async_get_config - this verifies that we can talk to the
    # servers.  Just return without error, which should allow the
    # config flow to get to the next step.
    with patch(
        "custom_components.powerwall_control.config_flow.async_get_config",
        return_value=(None, None),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=VALID_INPUT
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data["api_token"] == VALID_INPUT["api_token"]
    assert entry.data["system_id"] == VALID_INPUT["system_id"]


async def test_flow_reconfigure_step_bad_api_token(hass: HomeAssistant) -> None:
    """Test reconfigure with bad API token."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "api_token": "ABCDEFG",
            "system_id": "1234567",
        },
    )
    entry.add_to_hass(hass)
    result = await entry.start_reconfigure_flow(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    # Patch async_get_config - this verifies that we can talk to the
    # servers.  Just return without error, which should allow the
    # config flow to get to the next step.
    with patch(
        "custom_components.powerwall_control.config_flow.async_get_config",
        return_value=(None, None),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={"api_token": "short", "system_id": "1234567"}
        )
        await hass.async_block_till_done()

    assert result["errors"] == {"base": "invalid_token"}


async def test_flow_reconfigure_step_bad_system_id(hass: HomeAssistant) -> None:
    """Test reconfigure with bad system id."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "api_token": "ABCDEFG",
            "system_id": "1234567",
        },
    )
    entry.add_to_hass(hass)
    result = await entry.start_reconfigure_flow(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    # Patch async_get_config - this verifies that we can talk to the
    # servers.  Just return without error, which should allow the
    # config flow to get to the next step.
    with patch(
        "custom_components.powerwall_control.config_flow.async_get_config",
        return_value=(None, None),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "api_token": "abcdefghijklmnopqrstuvwxyz0123456789abcd",
                "system_id": "alpha",
            },
        )
        await hass.async_block_till_done()

    assert result["errors"] == {"base": "invalid_system_id"}


async def test_flow_reconfigure_step_cannot_connect(hass: HomeAssistant) -> None:
    """Test reconfigure with invalid token and system ID."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "api_token": "ABCDEFG",
            "system_id": "1234567",
        },
    )
    entry.add_to_hass(hass)
    result = await entry.start_reconfigure_flow(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    # Patch async_get_config - this verifies that we can talk to the
    # servers. Return an error, preventing the config flow getting to
    # the next step.
    with patch(
        "custom_components.powerwall_control.config_flow.async_get_config",
        side_effect=aiohttp.ClientResponseError(
            "Can't connect", status=400, history=()
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=VALID_INPUT
        )
        await hass.async_block_till_done()

    assert result["errors"] == {"base": "cannot_connect"}
