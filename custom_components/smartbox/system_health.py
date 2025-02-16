"""Provide info to system health."""

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback
from typing import Any
from . import SmartboxConfigEntry
from .const import DOMAIN


async def system_health_info(hass: HomeAssistant) -> dict[str, Any]:
    """Get info for the info page."""
    config_entry: SmartboxConfigEntry = hass.config_entries.async_entries(DOMAIN)[0]

    return {
        "api_health_check": (await config_entry.runtime_data.client.health_check())[
            "message"
        ],
        "can_reach_web_resailer": system_health.async_check_can_reach_url(
            hass, config_entry.runtime_data.client.resailer.web_url
        ),
    }


@callback
def async_register(
    hass: HomeAssistant, register: system_health.SystemHealthRegistration
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info)
