"""Draft of generic entity"""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity

from custom_components.smartbox.const import CONF_DISPLAY_ENTITY_PICTURES, DOMAIN
from custom_components.smartbox.model import SmartboxDevice, SmartboxNode


class DefaultSmartBoxEntity(Entity):
    """Default Smartbox Entity."""

    _node: SmartboxNode
    _attr_key: str
    _attr_websocket_event: str

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the default Device Entity."""
        self._device_id = self._node.node_id
        self._attr_has_entity_name = True
        self._attr_translation_key = self._attr_key
        self._attr_unique_id = self._node.node_id
        self._resailer = self._node.session.resailer
        self._configuration_url = f"{self._resailer.web_url}#/{self._node.device.home['id']}/dev/{self._device_id}/{self._node.node_type}/{self._node.addr}/setup"
        if entry.options.get(CONF_DISPLAY_ENTITY_PICTURES, False) is True:
            self._attr_entity_picture = f"{self._resailer.web_url}img/favicon.ico"

    @property
    def unique_id(self) -> str:
        """Return Unique ID string."""
        return f"{self._device_id}_{self._attr_key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._node.name,
            manufacturer=self._resailer.name,
            model_id=self._node.device.model_id,
            sw_version=self._node.device.sw_version,
            serial_number=self._node.device.serial_number,
            configuration_url=self._configuration_url,
        )

    @callback
    def _async_update(self, data: Any) -> None:
        """Update the state."""
        self._attr_state = data
        self.async_write_ha_state()


class SmartBoxDeviceEntity(DefaultSmartBoxEntity):
    """BaseClass for SmartBoxDeviceEntity."""

    def __init__(self, device: SmartboxDevice, entry: ConfigEntry) -> None:
        """Initialize the Device Entity."""
        self._node = list(device.get_nodes())[0]
        self._device = device
        super().__init__(entry=entry)

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        async_dispatcher_connect(
            self.hass,
            f"{DOMAIN}_{self._node.device.dev_id}_{self._attr_websocket_event}",
            self._async_update,
        )


class SmartBoxNodeEntity(DefaultSmartBoxEntity):
    """BaseClass for SmartBoxNodeEntity."""

    def __init__(self, node: SmartboxNode, entry: ConfigEntry) -> None:
        """Initialize the Node Entity."""
        self._node = node
        super().__init__(entry=entry)

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        async_dispatcher_connect(
            self.hass,
            f"{DOMAIN}_{self._node.node_id}_{self._attr_websocket_event}",
            self._async_update,
        )
