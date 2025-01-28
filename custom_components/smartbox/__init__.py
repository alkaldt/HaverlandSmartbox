"""The Smartbox integration."""

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from smartbox import AsyncSmartboxSession
from smartbox.error import APIUnavailable, InvalidAuth, SmartboxError
from .const import (
    CONF_API_NAME,
    CONF_BASIC_AUTH_CREDS,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    SMARTBOX_DEVICES,
    SMARTBOX_NODES,
)
from .model import get_devices, is_supported_node


__version__ = "2.1.0"

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def create_smartbox_session_from_entry(
    hass: HomeAssistant, entry: ConfigEntry | dict[str, Any] | None = None
) -> AsyncSmartboxSession:
    """Create a Session class from smartbox."""
    data = {}
    if type(entry) is dict:
        data = entry
    else:
        data = entry.data
    try:
        websession = async_get_clientsession(hass)
        session = AsyncSmartboxSession(
            data[CONF_API_NAME],
            data[CONF_BASIC_AUTH_CREDS],
            data[CONF_USERNAME],
            data[CONF_PASSWORD],
            websession,
        )
        await session.health_check()
        await session.check_refresh_auth()
    except APIUnavailable as ex:
        raise APIUnavailable from ex
    except InvalidAuth as ex:
        raise InvalidAuth from ex
    except SmartboxError as ex:
        raise SmartboxError from ex
    else:
        return session


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smartbox from a config entry."""
    try:
        session = await create_smartbox_session_from_entry(hass, entry)
    except Exception as ex:
        raise ConfigEntryAuthFailed from ex

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][SMARTBOX_DEVICES] = []
    hass.data[DOMAIN][SMARTBOX_NODES] = []

    devices = await get_devices(session=session)
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
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entity from config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
