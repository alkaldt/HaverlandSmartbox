"""The Smartbox integration."""

import logging

from smartbox import Session

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_API_NAME,
    CONF_BASIC_AUTH_CREDS,
    CONF_PASSWORD,
    CONF_SESSION_BACKOFF_FACTOR,
    CONF_SESSION_RETRY_ATTEMPTS,
    CONF_USERNAME,
    DOMAIN,
    SMARTBOX_DEVICES,
    SMARTBOX_NODES,
)
from .model import get_devices, is_supported_node

__version__ = "3.0"

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smartbox from a config entry."""
    session = await hass.async_add_executor_job(
        Session,
        entry.data[CONF_API_NAME],
        entry.data[CONF_BASIC_AUTH_CREDS],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_SESSION_RETRY_ATTEMPTS],
        entry.data[CONF_SESSION_BACKOFF_FACTOR],
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][SMARTBOX_DEVICES] = []
    hass.data[DOMAIN][SMARTBOX_NODES] = []

    devices = await get_devices(hass=hass, session=session, entry=entry)
    for device in devices:
        _LOGGER.info("Setting up configured device %s", device.dev_id)
        hass.data[DOMAIN][SMARTBOX_DEVICES].append(device)
    for device in hass.data[DOMAIN][SMARTBOX_DEVICES]:
        nodes = device.get_nodes()
        _LOGGER.debug("Configuring nodes for device %s %s", device.dev_id, nodes)
        for node in nodes:
            if not is_supported_node(node):
                _LOGGER.error(
                    'Nodes of type "%s" are not yet supported; no entities will be created. Please file an issue on GitHub',
                    node.node_type,
                )
        hass.data[DOMAIN][SMARTBOX_NODES].extend(nodes)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
