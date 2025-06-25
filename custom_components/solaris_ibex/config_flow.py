"""Config flow for Solaris integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SolarisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solaris integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Solaris IBEX", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_url"): str,
                    vol.Required("username"): str,
                    vol.Required("password"): str,
                }
            ),
        )

    def _get_reconfigure_entry(self) -> config_entries.ConfigEntry:
        """Get the current config entry being reconfigured."""
        return self.hass.config_entries.async_get_entry(self.context["entry_id"])
