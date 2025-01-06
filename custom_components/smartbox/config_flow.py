import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from smartbox import Session

from .const import (
    CONF_API_NAME,
    CONF_BASIC_AUTH_CREDS,
    CONF_PASSWORD,
    CONF_SESSION_BACKOFF_FACTOR,
    CONF_SESSION_RETRY_ATTEMPTS,
    CONF_SOCKET_BACKOFF_FACTOR,
    CONF_SOCKET_RECONNECT_ATTEMPTS,
    CONF_USERNAME,
    CONF_X_REFERER,
    CONF_X_SERIALID,
    DEFAULT_SESSION_RETRY_ATTEMPTS,
    DEFAULT_SOCKET_BACKOFF_FACTOR,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_NAME): str,
        vol.Required(CONF_USERNAME): TextSelector(
            TextSelectorConfig(type=TextSelectorType.EMAIL, autocomplete="username")
        ),
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD,
                autocomplete="current-password",
            )
        ),
        vol.Required(CONF_BASIC_AUTH_CREDS): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
        vol.Required(
            CONF_X_REFERER,
        ): str,
        vol.Required(CONF_X_SERIALID): str,
        vol.Required(
            CONF_SESSION_RETRY_ATTEMPTS,
            default=DEFAULT_SESSION_RETRY_ATTEMPTS,
        ): cv.positive_int,
        vol.Required(
            CONF_SESSION_BACKOFF_FACTOR,
            default=DEFAULT_SOCKET_BACKOFF_FACTOR,
        ): cv.small_float,
        vol.Required(CONF_SOCKET_RECONNECT_ATTEMPTS, default=3): cv.positive_int,
        vol.Required(CONF_SOCKET_BACKOFF_FACTOR, default=0.1): cv.small_float,
    },
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    try:
        hub = await hass.async_add_executor_job(
            Session,
            data[CONF_API_NAME],
            data[CONF_BASIC_AUTH_CREDS],
            data[CONF_X_REFERER],
            data[CONF_X_SERIALID],
            data[CONF_USERNAME],
            data[CONF_PASSWORD],
            data[CONF_SESSION_RETRY_ATTEMPTS],
            data[CONF_SESSION_BACKOFF_FACTOR],
        )
        if not await hass.async_add_executor_job(hub.get_access_token):
            raise InvalidAuth
    except requests.exceptions.ConnectionError:
        raise CannotConnect
    except Exception as e:
        raise InvalidAuth
    locations = [
        {"id": location["id"], "name": location["name"]}
        for location in await hass.async_add_executor_job(hub.get_grouped_devices)
    ]
    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": data[CONF_USERNAME], "hub": hub, "locations": locations}


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for test."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_USERNAME])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=STEP_USER_DATA_SCHEMA,
            )
        return await self.async_step_user()
