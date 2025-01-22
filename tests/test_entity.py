import unittest
from unittest.mock import MagicMock, patch
from homeassistant.config_entries import ConfigEntry
from custom_components.smartbox.entity import (
    DefaultSmartBoxEntity,
    SmartBoxDeviceEntity,
    SmartBoxNodeEntity,
)
from custom_components.smartbox.model import SmartboxDevice, SmartboxNode
from custom_components.smartbox.const import DOMAIN, SMARTBOX_RESAILER, CONF_API_NAME


class TestSmartBoxEntities(unittest.TestCase):

    def setUp(self):
        self.entry = MagicMock(spec=ConfigEntry)
        self.entry.data = {CONF_API_NAME: "test_api"}
        self.device = MagicMock(spec=SmartboxDevice)
        self.node = MagicMock(spec=SmartboxNode)
        self.node.node_id = "node_1"
        self.node.name = "Test Node"
        self.node.device.home = {"id": "home_1"}
        self.node.device.model_id = "model_1"
        self.node.device.sw_version = "1.0"
        self.node.device.serial_number = "serial_1"
        self.node.node_type = "type_1"
        self.node.addr = "addr_1"
        self.device.get_nodes.return_value = [self.node]
        SMARTBOX_RESAILER["test_api"] = {
            "web_url": "http://test.com",
            "name": "Test Resailer",
        }

    def test_default_smartbox_entity(self):
        entity = DefaultSmartBoxEntity(self.entry)
        entity._node = self.node
        entity._attr_key = "test_key"
        self.assertEqual(entity.unique_id, "node_1_test_key")
        self.assertEqual(entity.device_info["identifiers"], {(DOMAIN, "node_1")})
        self.assertEqual(entity.device_info["name"], "Test Node")
        self.assertEqual(entity.device_info["manufacturer"], "Test Resailer")
        self.assertEqual(entity.device_info["model_id"], "model_1")
        self.assertEqual(entity.device_info["sw_version"], "1.0")
        self.assertEqual(entity.device_info["serial_number"], "serial_1")
        self.assertEqual(
            entity.device_info["configuration_url"],
            "http://test.com#/home_1/dev/node_1/type_1/addr_1/setup",
        )

    def test_smartbox_device_entity(self):
        entity = SmartBoxDeviceEntity(self.device, self.entry)
        self.assertEqual(entity._node, self.node)
        self.assertEqual(entity._device, self.device)

    def test_smartbox_node_entity(self):
        entity = SmartBoxNodeEntity(self.node, self.entry)
        self.assertEqual(entity._node, self.node)


if __name__ == "__main__":
    unittest.main()
