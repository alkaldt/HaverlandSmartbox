"""Support for Smartbox sensor entities."""

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.const import EntityCategory, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SmartboxConfigEntry
from .entity import SmartBoxDeviceEntity

_LOGGER = logging.getLogger(__name__)
_MAX_POWER_LIMIT = 9999


async def async_setup_entry(
    _: HomeAssistant,
    entry: SmartboxConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up platform."""
    _LOGGER.debug("Setting up Smartbox number platform")

    async_add_entities(
        [
            PowerLimit(device, entry)
            for device in entry.runtime_data.devices
            if device.power_limit != 0
        ],
        update_before_add=True,
    )
    _LOGGER.debug("Finished setting up Smartbox number platform")


class PowerLimit(SmartBoxDeviceEntity, NumberEntity):
    """Smartbox device power limit."""

    _attr_key = "power_limit"
    _attr_websocket_event = "power_limit"
    _websocket_event = "power_limit"
    native_max_value: float = _MAX_POWER_LIMIT
    _attr_entity_category = EntityCategory.CONFIG
    native_unit_of_measurement = UnitOfPower.WATT

    @property
    def native_value(self) -> float:
        """Return the native value of the number."""
        return self._device.power_limit

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self._device.set_power_limit(int(value))
        self.async_write_ha_state()
