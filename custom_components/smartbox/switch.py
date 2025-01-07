"""Support for Smartbox switch entities."""

import logging
from unittest.mock import MagicMock

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SMARTBOX_DEVICES, SMARTBOX_NODES
from .model import (
    SmartboxDevice,
    SmartboxNode,
    true_radiant_available,
    window_mode_available,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up platform."""
    _LOGGER.debug("Setting up Smartbox switch platform")

    switch_entities: list[SwitchEntity] = []
    for device in hass.data[DOMAIN][SMARTBOX_DEVICES]:
        _LOGGER.debug("Creating away switch for device %s", device.name)
        switch_entities.append(AwaySwitch(device))

    for node in hass.data[DOMAIN][SMARTBOX_NODES]:
        if window_mode_available(node):
            _LOGGER.debug("Creating window_mode switch for node %s", node.name)
            switch_entities.append(WindowModeSwitch(node))
        else:
            _LOGGER.info("Window mode not available for node %s", node.name)
        if true_radiant_available(node):
            _LOGGER.debug("Creating true_radiant switch for node %s", node.name)
            switch_entities.append(TrueRadiantSwitch(node))
        else:
            _LOGGER.info("True radiant not available for node %s", node.name)

    async_add_entities(switch_entities, True)

    _LOGGER.debug("Finished setting up Smartbox switch platform")


class AwaySwitch(SwitchEntity):
    """Smartbox device away switch."""

    def __init__(self, device: SmartboxDevice | MagicMock) -> None:
        """Initialize the away Entity."""
        self._device = device
        self._device_id = list(device.get_nodes())[0].node_id

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
        """Return the name of the switch."""
        return f"{self._device.name} Away Status"

    @property
    def unique_id(self) -> str:
        """Return the unique id of the switch."""
        return f"{self._device.dev_id}_away_status"

    def turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        return self._device.set_away_status(True)

    def turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        return self._device.set_away_status(False)

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._device.away


class WindowModeSwitch(SwitchEntity):
    """Smartbox node window mode switch."""

    def __init__(self, node: SmartboxNode | MagicMock) -> None:
        """Initialize the window mode Entity."""
        self._node = node
        self._device_id = self._node.node_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._node.name,
            model_id=self._node.device.model_id,
            sw_version=self._node.device.sw_version,
            serial_number=self._node.device.serial_number,
        )

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self._node.name} Window Mode"

    @property
    def unique_id(self) -> str:
        """Return the unique id of the switch."""
        return f"{self._node.node_id}_window_mode"

    def turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        return self._node.set_window_mode(True)

    def turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        return self._node.set_window_mode(False)

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._node.window_mode


class TrueRadiantSwitch(SwitchEntity):
    """Smartbox node true radiant switch."""

    def __init__(self, node: SmartboxNode | MagicMock) -> None:
        """Initialize the radiant Entity."""
        self._node = node
        self._device_id = self._node.node_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._node.name,
            model_id=self._node.device.model_id,
            sw_version=self._node.device.sw_version,
            serial_number=self._node.device.serial_number,
        )

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self._node.name} True Radiant"

    @property
    def unique_id(self) -> str:
        """Return the unique id of the switch."""
        return f"{self._node.node_id}_true_radiant"

    def turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        return self._node.set_true_radiant(True)

    def turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        return self._node.set_true_radiant(False)

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._node.true_radiant
