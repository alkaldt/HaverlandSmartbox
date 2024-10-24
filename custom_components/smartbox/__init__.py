"""The Smartbox integration."""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import async_load_platform

# from smartbox import __version__ as SMARTBOX_VERSION

from .const import (
    DOMAIN,
    CONF_ACCOUNTS,
    CONF_API_NAME,
    CONF_BASIC_AUTH_CREDS,
    CONF_X_REFERER,
    CONF_X_SERIALID,
    CONF_DEVICE_IDS,
    CONF_PASSWORD,
    CONF_SESSION_RETRY_ATTEMPTS,
    CONF_SESSION_BACKOFF_FACTOR,
    CONF_SOCKET_RECONNECT_ATTEMPTS,
    CONF_SOCKET_BACKOFF_FACTOR,
    CONF_USERNAME,
    DEFAULT_SESSION_RETRY_ATTEMPTS,
    DEFAULT_SESSION_BACKOFF_FACTOR,
    DEFAULT_SOCKET_RECONNECT_ATTEMPTS,
    DEFAULT_SOCKET_BACKOFF_FACTOR,
    SMARTBOX_DEVICES,
    SMARTBOX_NODES,
)
from .model import get_devices, is_supported_node

__version__ = "3.0"

_LOGGER = logging.getLogger(__name__)


DEVICE_IDS_SCHEMA = vol.Schema([cv.string])

ACCOUNT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_NAME): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_DEVICE_IDS): DEVICE_IDS_SCHEMA,
        vol.Required(
            CONF_SESSION_RETRY_ATTEMPTS, default=DEFAULT_SESSION_RETRY_ATTEMPTS
        ): cv.positive_int,
        vol.Required(
            CONF_SESSION_BACKOFF_FACTOR, default=DEFAULT_SESSION_BACKOFF_FACTOR
        ): cv.small_float,
                vol.Required(
            CONF_SOCKET_RECONNECT_ATTEMPTS, default=DEFAULT_SOCKET_RECONNECT_ATTEMPTS
        ): cv.positive_int,
        vol.Required(
            CONF_SOCKET_BACKOFF_FACTOR, default=DEFAULT_SOCKET_BACKOFF_FACTOR
        ): cv.small_float,


    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_ACCOUNTS): vol.All(cv.ensure_list, [ACCOUNT_SCHEMA]),
                vol.Required(CONF_BASIC_AUTH_CREDS): cv.string,
                vol.Required(CONF_X_REFERER): cv.string,
                vol.Required(CONF_X_SERIALID): cv.string
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = ["climate", "number", "sensor", "switch"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Smartbox component."""
    hass.data.setdefault(DOMAIN, {})

    _LOGGER.info(
        f"Setting up Smartbox integration v{__version__}"
 #       f" (using smartbox v{SMARTBOX_VERSION})"
    )

    accounts_cfg = config[DOMAIN][CONF_ACCOUNTS]
    _LOGGER.debug(f"accounts: {accounts_cfg}")
    basic_auth_creds = config[DOMAIN][CONF_BASIC_AUTH_CREDS]
    _LOGGER.debug(f"basic_auth_creds: {basic_auth_creds}")
    x_referer = config[DOMAIN][CONF_X_REFERER]
    _LOGGER.debug(f"x_referer: {x_referer}")
    x_serialid = config[DOMAIN][CONF_X_SERIALID]
    _LOGGER.debug(f" x_serialid: {x_serialid}")

    hass.data[DOMAIN][SMARTBOX_DEVICES] = []
    hass.data[DOMAIN][SMARTBOX_NODES] = []

    for account in accounts_cfg:
        devices = await get_devices(
            hass,
            account[CONF_API_NAME],
            basic_auth_creds,
            x_referer, 
            x_serialid, 
            account[CONF_USERNAME],
            account[CONF_PASSWORD],
            account[CONF_SESSION_RETRY_ATTEMPTS],
            account[CONF_SESSION_BACKOFF_FACTOR],
        )

        found_dev_ids = frozenset(dev.dev_id for dev in devices)
        for dev_id in found_dev_ids.difference(account[CONF_DEVICE_IDS]):
            _LOGGER.warning(
                f"Found device {dev_id} which was not configured - ignoring"
            )

        for device in devices:
            if device.dev_id in account[CONF_DEVICE_IDS]:
                _LOGGER.info(f"Setting up configured device {device.dev_id}")
                hass.data[DOMAIN][SMARTBOX_DEVICES].append(device)

        setup_dev_ids = frozenset(
            dev.dev_id for dev in hass.data[DOMAIN][SMARTBOX_DEVICES]
        )
        for dev_id in frozenset(account[CONF_DEVICE_IDS]) - setup_dev_ids:
            _LOGGER.error(f"Configured device {dev_id} was not found")

    for device in hass.data[DOMAIN][SMARTBOX_DEVICES]:
        nodes = device.get_nodes()
        _LOGGER.debug(f"Configuring nodes for device {device.dev_id} {nodes}")
        for node in nodes:
            if not is_supported_node(node):
                _LOGGER.error(
                    f'Nodes of type "{node.node_type}" are not yet supported; '
                    "no entities will be created. Please file an issue on GitHub."
                )
        hass.data[DOMAIN][SMARTBOX_NODES].extend(nodes)

    if hass.data[DOMAIN][SMARTBOX_DEVICES]:
        for component in PLATFORMS:
            await async_load_platform(hass, component, DOMAIN, {}, config)

    _LOGGER.debug("Finished setting up Smartbox integration")

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Smartbox from a config entry."""
    # TODO: implement
    return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # TODO: implement
    return False
