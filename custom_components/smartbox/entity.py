"""Draft of generic entity"""

# from unittest.mock import MagicMock

# from custom_components.smartbox.const import DOMAIN
# from custom_components.smartbox.model import SmartboxNode
# from homeassistant.helpers.entity import DeviceInfo, Entity


# class SmartBoxEntity(Entity):
#     """BaseClass for entities."""

#     def __init__(self, node: SmartboxNode | MagicMock) -> None:
#         """Initialize the away Entity."""
#         self._node = node
#         self._device = self._node.device
#         self._device_id = self._node.node_id
#         self._attr_has_entity_name = True

#     @property
#     def unique_id(self) -> str:
#         """Return the unique id of the switch."""
#         return f"{self._device_id}_{self._attr_translation_key}"

#     @property
#     def device_info(self) -> DeviceInfo:
#         """Return the device info."""
#         return DeviceInfo(
#             identifiers={(DOMAIN, self._device_id)},
#             name=self._device.name,
#             model_id=self._device.model_id,
#             sw_version=self._device.sw_version,
#             serial_number=self._device.serial_number,
#         )
