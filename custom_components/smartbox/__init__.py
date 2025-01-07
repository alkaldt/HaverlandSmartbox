"""The Smartbox integration."""

import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from smartbox import Session
from .const import (
    DOMAIN,
    CONF_API_NAME,
    CONF_BASIC_AUTH_CREDS,
    CONF_X_REFERER,
    CONF_X_SERIALID,
    CONF_PASSWORD,
    CONF_SESSION_RETRY_ATTEMPTS,
    CONF_SESSION_BACKOFF_FACTOR,
    CONF_USERNAME,
    SMARTBOX_DEVICES,
    SMARTBOX_NODES,
)
from .model import get_devices, is_supported_node

__version__ = "3.0"

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.NUMBER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smartbox from a config entry."""
    # entry.runtime_data
    session = await hass.async_add_executor_job(
        Session,
        entry.data[CONF_API_NAME],
        entry.data[CONF_BASIC_AUTH_CREDS],
        # entry.data[CONF_X_REFERER],
        # entry.data[CONF_X_SERIALID],
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
        _LOGGER.info(f"Setting up configured device {device.dev_id}")
        hass.data[DOMAIN][SMARTBOX_DEVICES].append(device)
    for device in hass.data[DOMAIN][SMARTBOX_DEVICES]:
        nodes = device.get_nodes()
        _LOGGER.debug(f"Configuring nodes for device {device.dev_id} {nodes}")
        for node in nodes:
            if not is_supported_node(node):
                _LOGGER.error(
                    f'Nodes of type "{node.node_type}" are not yet supported; no entities will be created. Please file an issue on GitHub.'
                )
        hass.data[DOMAIN][SMARTBOX_NODES].extend(nodes)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
