"""Support for Smartbox sensor entities."""

import logging
from unittest.mock import MagicMock

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SMARTBOX_DEVICES
from .model import SmartboxDevice

_LOGGER = logging.getLogger(__name__)
_MAX_POWER_LIMIT = 9999


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up platform."""
    _LOGGER.debug("Setting up Smartbox number platform")

    async_add_entities(
        [DevicePowerLimit(device) for device in hass.data[DOMAIN][SMARTBOX_DEVICES]],
        True,
    )

    _LOGGER.debug("Finished setting up Smartbox number platform")


class DevicePowerLimit(NumberEntity):
    """Smartbox device power limit."""

    def __init__(self, device: SmartboxDevice | MagicMock) -> None:
        """Initialize the Entity."""
        self._device = device
        self._device_id = list(device.get_nodes())[0].node_id

    native_max_value: float = _MAX_POWER_LIMIT

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device.name,
            model_id=self._device.model_id,
            sw_version=self._device.sw_version,
            serial_number=self._device.serial_number,
        )

    @property
    def name(self):
        """Return the name of the number."""
        return f"{self._device.name} Power Limit"

    @property
    def unique_id(self) -> str:
        """Return the unique id of the number."""
        return f"{self._device.dev_id}_power_limit"

    @property
    def native_value(self) -> float:
        """Return the native value of the number."""
        return self._device.power_limit

    def set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._device.set_power_limit(int(value))
