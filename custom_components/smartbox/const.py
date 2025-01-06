"""Constants for the Smartbox integration."""

from datetime import timedelta

DOMAIN = "smartbox"

CONF_API_NAME = "api_name"
CONF_BASIC_AUTH_CREDS = "basic_auth_creds"
CONF_X_REFERER = "x_referer"
CONF_X_SERIALID = "x_serialid"
CONF_PASSWORD = "password"
CONF_USERNAME = "username"
CONF_SESSION_RETRY_ATTEMPTS = "session_retry_attempts"
CONF_SESSION_BACKOFF_FACTOR = "session_backoff_factor"
CONF_SOCKET_RECONNECT_ATTEMPTS = "socket_reconnect_attempts"
CONF_SOCKET_BACKOFF_FACTOR = "socket_backoff_factor"

DEFAULT_SESSION_RETRY_ATTEMPTS = 8
DEFAULT_SESSION_BACKOFF_FACTOR = 0.1
DEFAULT_SOCKET_RECONNECT_ATTEMPTS = 3
DEFAULT_SOCKET_BACKOFF_FACTOR = 0.1

GITHUB_ISSUES_URL = "https://github.com/ajtudela/hass-smartbox/issues"
DEVICE_MANUFACTURER = "HJM"

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
