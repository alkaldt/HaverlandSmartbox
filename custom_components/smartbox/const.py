"""Constants for the Smartbox integration."""

from datetime import timedelta
from enum import StrEnum

from smartbox.session import _DEFAULT_BACKOFF_FACTOR, _DEFAULT_RETRY_ATTEMPTS

DOMAIN = "smartbox"

CONF_API_NAME = "api_name"
CONF_BASIC_AUTH_CREDS = "basic_auth_creds"
CONF_PASSWORD = "password"
CONF_USERNAME = "username"
CONF_SESSION_RETRY_ATTEMPTS = "session_retry_attempts"
CONF_SESSION_BACKOFF_FACTOR = "session_backoff_factor"
CONF_SOCKET_RECONNECT_ATTEMPTS = "socket_reconnect_attempts"
CONF_SOCKET_BACKOFF_FACTOR = "socket_backoff_factor"

DEFAULT_SESSION_RETRY_ATTEMPTS = _DEFAULT_RETRY_ATTEMPTS
DEFAULT_SESSION_BACKOFF_FACTOR = _DEFAULT_BACKOFF_FACTOR
DEFAULT_SOCKET_RECONNECT_ATTEMPTS = 3
DEFAULT_SOCKET_BACKOFF_FACTOR = 0.1

GITHUB_ISSUES_URL = "https://github.com/ajtudela/hass-smartbox/issues"

HEATER_NODE_TYPE_ACM = "acm"
HEATER_NODE_TYPE_HTR = "htr"
HEATER_NODE_TYPE_HTR_MOD = "htr_mod"
HEATER_NODE_TYPES = [
    HEATER_NODE_TYPE_ACM,
    HEATER_NODE_TYPE_HTR,
    HEATER_NODE_TYPE_HTR_MOD,
]

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1)

PRESET_FROST = "frost"
PRESET_SCHEDULE = "schedule"
PRESET_SELF_LEARN = "self_learn"

SMARTBOX_DEVICES = "smartbox_devices"
SMARTBOX_NODES = "smartbox_nodes"
SMARTBOX_SESSIONS = "smartbox_sessions"

SMARTBOX_RESAILER = {
    "api-hjm": {
        "name": "HJM",
        "web_url": "https://api.calorhjm.com/",
        "api_url": "api-hjm",
    },
    "api-helki": {
        "name": "Helki",
        "web_url": "https://app.helki.com/",
        "api_url": "api-helki",
    },
    "api-haverland": {
        "name": "Haverland",
        "web_url": "https://i2control.haverland.com/",
        "api_url": "api-haverland",
    },
    "api-elnur": {
        "name": "Elnur",
        "web_url": "https://remotecontrol.elnur.es/",
        "api_url": "api-elnur",
    },
}

CONF_HISTORY_CONSUMPTION = "history_consumption"


class HistoryConsumptionStatus(StrEnum):
    """Consumption History Status."""

    START = "start"
    AUTO = "auto"
    OFF = "off"
