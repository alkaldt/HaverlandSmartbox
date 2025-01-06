from typing import Any, Dict, List

from custom_components.smartbox.const import (
    DOMAIN,
    CONF_API_NAME,
    CONF_BASIC_AUTH_CREDS,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SESSION_RETRY_ATTEMPTS,
    CONF_SESSION_BACKOFF_FACTOR,
    CONF_SOCKET_RECONNECT_ATTEMPTS,
    CONF_SOCKET_BACKOFF_FACTOR,
    HEATER_NODE_TYPE_ACM,
    HEATER_NODE_TYPE_HTR,
    HEATER_NODE_TYPE_HTR_MOD,
)

TEST_CONFIG_1 = {
    DOMAIN: {
        CONF_API_NAME: "test_api_name_1",
        CONF_USERNAME: "test_username_1",
        CONF_PASSWORD: "test_password_1",
        CONF_SESSION_RETRY_ATTEMPTS: 4,
        CONF_SESSION_BACKOFF_FACTOR: 0.1,
        CONF_SOCKET_RECONNECT_ATTEMPTS: 3,
        CONF_SOCKET_BACKOFF_FACTOR: 0.2,
        CONF_BASIC_AUTH_CREDS: "test_basic_auth_creds",
    }
}

# TEST_CONFIG_2 = {
#     DOMAIN: {
#         CONF_ACCOUNTS: [
#             {
#                 CONF_API_NAME: "test_api_name_1",
#                 CONF_USERNAME: "test_username_1",
#                 CONF_PASSWORD: "test_password_1",
#                 CONF_DEVICE_IDS: ["test_device_id_1"],
#                 CONF_SESSION_RETRY_ATTEMPTS: 5,
#                 CONF_SESSION_BACKOFF_FACTOR: 0.2,
#                 CONF_SOCKET_RECONNECT_ATTEMPTS: 4,
#                 CONF_SOCKET_BACKOFF_FACTOR: 0.3,
#             },
#             {
#                 CONF_API_NAME: "test_api_name_2",
#                 CONF_USERNAME: "test_username_2",
#                 CONF_PASSWORD: "test_password_2",
#                 CONF_DEVICE_IDS: ["test_device_id_2_1", "test_device_id_2_2"],
#                 CONF_SESSION_RETRY_ATTEMPTS: 6,
#                 CONF_SESSION_BACKOFF_FACTOR: 0.3,
#                 CONF_SOCKET_RECONNECT_ATTEMPTS: 5,
#                 CONF_SOCKET_BACKOFF_FACTOR: 0.4,
#             },
#         ],
#         CONF_BASIC_AUTH_CREDS: "test_basic_auth_creds",
#     }
# }

TEST_CONFIG_3 = {
    DOMAIN: {
        CONF_API_NAME: "test_api_name_1",
        CONF_USERNAME: "test_username_1",
        CONF_PASSWORD: "test_password_1",
        CONF_SESSION_RETRY_ATTEMPTS: 7,
        CONF_SESSION_BACKOFF_FACTOR: 0.4,
        CONF_SOCKET_RECONNECT_ATTEMPTS: 6,
        CONF_SOCKET_BACKOFF_FACTOR: 0.5,
        CONF_BASIC_AUTH_CREDS: "test_basic_auth_creds",
    }
}

MOCK_SMARTBOX_CONFIG = {
    DOMAIN: {
        CONF_API_NAME: "test_api_name_1",
        CONF_USERNAME: "test_username_1",
        CONF_PASSWORD: "test_password_1",
        CONF_SESSION_RETRY_ATTEMPTS: 7,
        CONF_SESSION_BACKOFF_FACTOR: 0.4,
        CONF_SOCKET_RECONNECT_ATTEMPTS: 6,
        CONF_SOCKET_BACKOFF_FACTOR: 0.5,
        CONF_BASIC_AUTH_CREDS: "test_basic_auth_creds",
    }
}

MOCK_SMARTBOX_DEVICE_INFO = {
    "test_device_id_1": {
        "dev_id": "test_device_id_1",
        "name": "Device 1",
    },
    "test_device_id_2": {
        "dev_id": "test_device_id_2",
        "name": "Device 2",
    },
}

MOCK_SMARTBOX_NODE_INFO = {
    "test_device_id_1": [
        {
            "addr": 0,
            "name": "Test device 1 node 0",
            "type": HEATER_NODE_TYPE_HTR,
        },
        {
            "addr": 1,
            "name": "Test device 1 node 1",
            "type": HEATER_NODE_TYPE_ACM,
        },
    ],
    "test_device_id_2": [
        {
            "addr": 0,
            "name": "Test device 2 node 0",
            "type": HEATER_NODE_TYPE_HTR_MOD,
        },
        {
            "addr": 1,
            "name": "Test device 2 node 1",
            "type": HEATER_NODE_TYPE_HTR_MOD,
        },
        {
            "addr": 2,
            "name": "Test device 2 node 2",
            "type": HEATER_NODE_TYPE_HTR_MOD,
        },
        {
            "addr": 3,
            "name": "Test device 2 node 3",
            "type": HEATER_NODE_TYPE_HTR_MOD,
        },
        {
            "addr": 4,
            "name": "Test device 2 node 4",
            "type": HEATER_NODE_TYPE_HTR_MOD,
        },
        {
            "addr": 5,
            "name": "Test device 2 node 5",
            "type": HEATER_NODE_TYPE_HTR_MOD,
        },
    ],
}

MOCK_SMARTBOX_NODE_SETUP: Dict[str, List[Dict[str, Any]]] = {
    "test_device_id_1": [
        {
            "factory_options": {
                "true_radiant_available": True,
                "window_mode_available": True,
            },
            "true_radiant_enabled": False,
            "window_mode_enabled": False,
        },
        {
            "factory_options": {
                "true_radiant_available": False,
                "window_mode_available": False,
            },
        },
    ],
    "test_device_id_2": [
        {
            "factory_options": {
                "true_radiant_available": True,
                "window_mode_available": True,
            },
            "true_radiant_enabled": True,
            "window_mode_enabled": True,
        },
        {
            "factory_options": {
                "true_radiant_available": True,
                "window_mode_available": True,
            },
            "true_radiant_enabled": False,
            "window_mode_enabled": False,
        },
        {
            "factory_options": {
                "true_radiant_available": True,
                "window_mode_available": True,
            },
            "true_radiant_enabled": True,
            "window_mode_enabled": True,
        },
        {
            "factory_options": {
                "true_radiant_available": True,
                "window_mode_available": True,
            },
            "true_radiant_enabled": False,
            "window_mode_enabled": False,
        },
        {
            "factory_options": {
                "true_radiant_available": False,
                "window_mode_available": False,
            },
            "true_radiant_enabled": True,
            "window_mode_enabled": True,
        },
        {
            # Test factory_options missing
        },
    ],
}

MOCK_SMARTBOX_NODE_STATUS: Dict[str, List[Dict[str, Any]]] = {
    "test_device_id_1": [
        {
            "mtemp": "25.7",
            "stemp": "20.3",
            "units": "C",
            "sync_status": "ok",
            "locked": False,
            "active": True,
            "power": "510",
            "duty": "50",
            "mode": "auto",
        },
        {
            "mtemp": "19.2",
            "stemp": "21",
            "units": "C",
            "sync_status": "ok",
            "locked": False,
            # acm nodes have a 'charging' state rather than 'active'
            "charging": True,
            "charge_level": 2,
            "power": "620",
            "mode": "manual",
        },
    ],
    "test_device_id_2": [
        {
            "on": True,
            "mtemp": "25.7",
            "selected_temp": "comfort",
            "comfort_temp": "20.3",
            "eco_offset": "4",
            "ice_temp": "7",
            "units": "C",
            "sync_status": "ok",
            "locked": False,
            "active": True,
            "mode": "auto",
        },
        {
            "on": True,
            "mtemp": "18.2",
            "selected_temp": "comfort",
            "comfort_temp": "22.3",
            "eco_offset": "4",
            "ice_temp": "7",
            "units": "C",
            "sync_status": "ok",
            "locked": False,
            "active": True,
            "mode": "manual",
        },
        {
            "on": True,
            "mtemp": "19.2",
            "selected_temp": "eco",
            "comfort_temp": "24.3",
            "eco_offset": "4",
            "ice_temp": "7",
            "units": "C",
            "sync_status": "ok",
            "locked": False,
            "active": True,
            "mode": "manual",
        },
        {
            "on": True,
            "mtemp": "17.2",
            "selected_temp": "ice",
            "comfort_temp": "23.3",
            "eco_offset": "4",
            "ice_temp": "7",
            "units": "C",
            "sync_status": "ok",
            "locked": False,
            "active": True,
            "mode": "manual",
        },
        {
            "on": True,
            "mtemp": "16.2",
            "selected_temp": "ice",
            "comfort_temp": "23.3",
            "eco_offset": "4",
            "ice_temp": "7",
            "units": "C",
            "sync_status": "ok",
            "locked": False,
            "active": True,
            "mode": "self_learn",
        },
        {
            "on": True,
            "mtemp": "15.2",
            "selected_temp": "ice",
            "comfort_temp": "23.3",
            "eco_offset": "4",
            "ice_temp": "7",
            "units": "C",
            "sync_status": "ok",
            "locked": False,
            "active": True,
            "mode": "presence",
        },
    ],
}
