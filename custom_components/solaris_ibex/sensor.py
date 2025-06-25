"""Platform for Solaris sensors."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .ibex_coordinator import IbexCoordinator
from .sensors.current_price_sensor import CurrentPriceSensorKWH
from .sensors.ibex_energy_price_sensor import IbexEnergyPriceSensor
from .sensors.ibex_prices_last_updated_sensor import IbexPricesLastUpdatedSensor


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Solaris sensors from a config entry."""
    # Retrieve the coordinator from hass.data
    coordinator: IbexCoordinator = hass.data["solaris_ibex"][entry.entry_id]

    # Add sensors
    price_sensors = [IbexEnergyPriceSensor(coordinator)]
    async_add_entities(
        [
            *price_sensors,
            IbexPricesLastUpdatedSensor(coordinator),
            CurrentPriceSensorKWH(hass),
        ]
    )
