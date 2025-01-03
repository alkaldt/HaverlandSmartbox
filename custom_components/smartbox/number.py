from homeassistant.components.number import (
    NumberEntity,
)
from homeassistant.core import HomeAssistant
import logging
from typing import Union
from unittest.mock import MagicMock

from .const import DOMAIN, SMARTBOX_DEVICES
from .model import SmartboxDevice
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from .const import DEVICE_MANUFACTURER
from homeassistant.helpers.entity import DeviceInfo


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
    """Smartbox device power limit"""

    def __init__(self, device: Union[SmartboxDevice, MagicMock]) -> None:
        self._device = device
        self._device_id = list(device.get_nodes())[0].node_id

    native_max_value: float = _MAX_POWER_LIMIT

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device.name,
            manufacturer=DEVICE_MANUFACTURER,
            model=DOMAIN,
        )

    @property
    def name(self):
        """Return the name of the number."""
        return f"{self._device.name} Power Limit"

    @property
    def unique_id(self) -> str:
        return f"{self._device.dev_id}_power_limit"

    @property
    def native_value(self) -> float:
        return self._device.power_limit

    def set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._device.set_power_limit(int(value))
