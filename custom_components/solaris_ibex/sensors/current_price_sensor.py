"""Sensors for current energy prices."""

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)
import logging

_LOGGER = logging.getLogger(__name__)


class CurrentPriceSensorKWH(SensorEntity):
    """Sensor for the current energy price per kWh."""

    _attr_has_entity_name = True
    _attr_name = "Price Now in kWh (DA)"
    _attr_unique_id = "ibex_dayahead_price_kwh_now"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "BGN/kWh"

    def __init__(self, hass: HomeAssistant):
        """Initialize the Current Price Sensor for kWh."""
        self.hass = hass

        # Update hourly
        async_track_time_change(hass, self._update, minute=0, second=0)

        # Update when any of the hourly sensors change
        async_track_state_change_event(hass, self._watched_entities(), self._update)

    def _watched_entities(self) -> list[str]:
        """Return the list of hourly price sensors to watch."""
        return ["sensor.ibex_dayahead_price_now"]

    async def _update(self, *args):
        """Trigger an update and write the new state."""
        self.async_write_ha_state()

    @property
    def state(self) -> float | None:
        """Return the current price per kWh."""
        entity_id = "sensor.ibex_dayahead_price_now"
        state = self.hass.states.get(entity_id)
        if state and state.state not in (None, "unknown", "unavailable"):
            try:
                return float(state.state) / 1000
            except ValueError:
                return None
        return None

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._attr_unique_id

    @property
    def should_poll(self) -> bool:
        """Indicate that this sensor does not require polling."""
        return False

    @property
    def device_info(self):
        """Return device information for the sensor."""
        return {
            "identifiers": {("solaris_ibex", "mynkow")},
            "name": "Solar1s IBEX",
            "manufacturer": "1SoftwareCompany",
            "model": "ibex",
            "entry_type": "service",
        }
