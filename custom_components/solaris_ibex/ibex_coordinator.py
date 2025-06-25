"""Coordinator for Solaris Ibex integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, CONF_USERNAME, CONF_PASSWORD
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util import dt as dt_util

from .const import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)

class IbexCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch and manage electricity price data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Solaris Coordinator",
            update_interval=timedelta(minutes=5),
        )
        self._last_success = None

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        payload = {
            "size": 48,
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": "now/d",
                        "lte": "now+1d/d",
                        "time_zone": "+03:00",
                    }
                }
            },
            "sort": [{"@timestamp": {"order": "asc"}}],
        }
        headers = {"Content-Type": "application/json"}

        try:
            _LOGGER.debug("Sending request to API with payload: %s", payload)
            async with (
                async_timeout.timeout(10),
                aiohttp.ClientSession() as session,
                session.post(
                    API_URL,
                    json=payload,
                    headers=headers,
                    auth=aiohttp.BasicAuth(USERNAME, PASSWORD),
                ) as response,
            ):
                if response.status != 200:
                    raise UpdateFailed(f"HTTP error: {response.status}")
                data = await response.json()
                _LOGGER.debug("Received data from API: %s", data)
                self._last_success = (
                    dt_util.utcnow()
                )  # Use dt_util for the current UTC time
                return data
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}") from err

    @property
    def last_success_time(self):
        """Return the last successful update time."""
        return self._last_success


class IbexDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for Solaris Ibex data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Ibex data",
            update_interval=timedelta(seconds=60),
        )
        self.url: str = config_entry.data[CONF_URL]
        self.username: str = config_entry.data[CONF_USERNAME]
        self.password: str = config_entry.data[CONF_PASSWORD]

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Ibex HTTP API."""
        try:
            # Example async HTTP call using aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.url,
                    auth=aiohttp.BasicAuth(self.username, self.password),
                    timeout=10,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
            return data
        except aiohttp.ClientError as err:
            raise ConfigEntryNotReady from err
