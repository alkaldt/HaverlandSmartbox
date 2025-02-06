"""Constants for the Smartbox integration."""

from datetime import timedelta
from enum import StrEnum

from smartbox.session import _DEFAULT_BACKOFF_FACTOR, _DEFAULT_RETRY_ATTEMPTS
from smartbox import SmartboxNodeType

DOMAIN = "smartbox"

CONF_API_NAME = "api_name"
CONF_DISPLAY_ENTITY_PICTURES = "resailer_entity"
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

HEATER_NODE_TYPES = [
    SmartboxNodeType.ACM,
    SmartboxNodeType.HTR,
    SmartboxNodeType.HTR_MOD,
]

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1)

PRESET_FROST = "frost"
PRESET_SCHEDULE = "schedule"
PRESET_SELF_LEARN = "self_learn"

SMARTBOX_DEVICES = "smartbox_devices"
SMARTBOX_NODES = "smartbox_nodes"
SMARTBOX_SESSIONS = "smartbox_sessions"

CONF_HISTORY_CONSUMPTION = "history_consumption"


class HistoryConsumptionStatus(StrEnum):
    """Config Consumption History Status."""

    START = "start"
    AUTO = "auto"
    OFF = "off"
