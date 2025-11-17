"""Powerwall Control integration config flow.

This is a Home Assistant defined file for defining the GUI driven
configuration for an integration.

Powerwall Control needs the user to provide an API token and an energy
system ID which we can then use to talk to the Netzero servers.
"""

import re
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from . import async_get_config
from .const import DOMAIN

# Regular expressions to validate user input
API_TOKEN_RE = re.compile(r"[0-9A-z]{40,}$")
SYSTEM_ID_RE = re.compile(r"[0-9]+$")


async def validate_input(data: dict, hass: HomeAssistant) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    if not API_TOKEN_RE.match(data["api_token"]):
        raise InvalidToken

    if not SYSTEM_ID_RE.match(data["system_id"]):
        raise InvalidSystemId

    # Verify we can connect to Netzero with the key and id
    try:
        _, _ = await async_get_config(hass, data["api_token"], data["system_id"])
    except aiohttp.ClientResponseError as e:
        raise CannotConnect from e

    # Return info we want stored in the config entry
    return {"title": "Energy site " + data["system_id"], "system_id": data["system_id"]}


class PwCtrlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Powerwall Control config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle a flow initiated by the user."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(user_input, self.hass)
                # Input validated, set the unique id and create the config entries
                await self.async_set_unique_id(info["system_id"])

                # Abort the flow if a config entry with the same unique ID exists
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidToken:
                errors["base"] = "invalid_token"
            except InvalidSystemId:
                errors["base"] = "invalid_system_id"
            except CannotConnect:
                errors["base"] = "cannot_connect"

        # Either initial call or validation failed.
        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_token"): str,
                    vol.Required("system_id"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Handle reconfiguration flow initiated by the user."""
        errors = {}
        if user_input is not None:
            try:
                _ = await validate_input(user_input, self.hass)

                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(), data_updates=user_input
                )
            except InvalidToken:
                errors["base"] = "invalid_token"
            except InvalidSystemId:
                errors["base"] = "invalid_system_id"
            except CannotConnect:
                errors["base"] = "cannot_connect"

        # Get defaults from the existing entry. System ID is the unique ID,
        # so don't allow that to change.
        config_entry = self._get_reconfigure_entry()

        # Either initial call or validation failed.
        # Show the form
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "api_token", default=config_entry.data["api_token"]
                    ): str,
                    vol.Optional(
                        "system_id", default=config_entry.data["system_id"]
                    ): TextSelector(TextSelectorConfig(read_only=True)),
                }
            ),
            errors=errors,
        )


class InvalidToken(exceptions.HomeAssistantError):
    """Error to indicate the API token is invalid."""


class InvalidSystemId(exceptions.HomeAssistantError):
    """Error to indicate the System ID is invalid."""


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we can't connect to Netzero."""
