import asyncio
import logging
import time
import json


from homeassistant.const import (
    UnitOfTemperature,
)

from homeassistant.components.climate import (
    HVACMode,
)
from homeassistant.components.climate.const import (
    PRESET_ACTIVITY,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_HOME,
)


from homeassistant.core import HomeAssistant
from smartbox import Session, UpdateManager
from typing import Any, cast, Dict, List, Union
from unittest.mock import MagicMock

from .const import (
    GITHUB_ISSUES_URL,
    HEATER_NODE_TYPE_ACM,
    HEATER_NODE_TYPE_HTR_MOD,
    HEATER_NODE_TYPES,
    PRESET_FROST,
    PRESET_SCHEDULE,
    PRESET_SELF_LEARN,
)
from .types import FactoryOptionsDict, SetupDict, StatusDict

_LOGGER = logging.getLogger(__name__)


class SmartboxDevice(object):
    def __init__(
        self,
        dev_id: str,
        name: str,
        session: Union[Session, MagicMock],
        socket_reconnect_attempts: int,
        socket_backoff_factor: float,
    ) -> None:
        self._dev_id = dev_id
        self._name = name
        self._session = session
        self._samples: Dict[str, Any] = {}
        self._socket_reconnect_attempts = socket_reconnect_attempts
        self._socket_backoff_factor = socket_backoff_factor
        self._away = False
        self._power_limit: int = 0


    async def initialise_nodes(self, hass: HomeAssistant) -> None:
        # Would do in __init__, but needs to be a coroutine
        session_nodes = await hass.async_add_executor_job(
            self._session.get_nodes, self.dev_id
        )
        self._nodes = {}
        for node_info in session_nodes:
            status = await hass.async_add_executor_job(
                self._session.get_status, self._dev_id, node_info
            )
            setup = await hass.async_add_executor_job(
                self._session.get_setup, self._dev_id, node_info
            )
            samples: dict[str,Any] = await hass.async_add_executor_job(
                self._session.get_device_samples, self._dev_id, node_info,  (time.time() - time.time() % 3600) - 3600 , (time.time() - time.time() % 3600) + 1800
            )
                
            node = SmartboxNode(self, node_info, self._session, status, setup, samples)
            self._nodes[(node.node_type, node.addr)] = node

        _LOGGER.debug(f"Creating SocketSession for device {self._dev_id}")
        _LOGGER.debug(f"Samples: {samples}")
        self._update_manager = UpdateManager(
            self._session,
            self._dev_id,
            reconnect_attempts=self._socket_reconnect_attempts,
            backoff_factor=self._socket_backoff_factor,
        )

        self._update_manager.subscribe_to_device_away_status(self._away_status_update)
        self._update_manager.subscribe_to_device_power_limit(self._power_limit_update)
        self._update_manager.subscribe_to_node_status(self._node_status_update)
        self._update_manager.subscribe_to_node_setup(self._node_setup_update)
        self._update_manager.subscribe_to_node_samples(self._node_samples_update)

        _LOGGER.debug(f"Starting UpdateManager task for device {self._dev_id}")
        asyncio.create_task(self._update_manager.run())

    def _away_status_update(self, away_status: Dict[str, bool]) -> None:
        _LOGGER.debug(f"Away status update: {away_status}")
        self._away = away_status["away"]

    def _power_limit_update(self, power_limit: int) -> None:
        _LOGGER.debug(f"power_limit update: {power_limit}")
        self._power_limit = power_limit

    def _node_status_update(
        self, node_type: str, addr: int, node_status: StatusDict
    ) -> None:
        _LOGGER.debug(f"Node status update: {node_status}")
        node = self._nodes.get((node_type, addr), None)
        if node is not None:
            node.update_status(node_status)
        else:
            _LOGGER.error(f"Received status update for unknown node {node_type} {addr}")

    def _node_setup_update(
        self, node_type: str, addr: int, node_setup: SetupDict
    ) -> None:
        _LOGGER.debug(f"Node setup update: {node_setup}")
        node = self._nodes.get((node_type, addr), None)
        if node is not None:
            node.update_setup(node_setup)
        else:
            _LOGGER.error(f"Received setup update for unknown node {node_type} {addr}")
            
    def _node_samples_update(
        self, node_type: str, addr: int, node_samples: Dict[str, Any]
    ) -> None:
        _LOGGER.debug(f"Node samples update: {node_samples}")
        node = self._nodes.get((node_type, addr), None)
        
        _LOGGER.debug(f"Node: {node}")
        if node is not None:
             node.update_samples(self._samples)
        else:
            _LOGGER.error(f"Received setup update for unknown node {node_type} {addr}")

   
    @property
    def dev_id(self) -> str:
        return self._dev_id

    def get_nodes(self):
        return self._nodes.values()

    @property
    def name(self) -> str:
        return self._name

    @property
    def away(self) -> bool:
        return self._away

    def set_away_status(self, away: bool):
        self._session.set_device_away_status(self.dev_id, {"away": away})
        self._away = away

    @property
    def power_limit(self) -> int:
        return self._power_limit

    def set_power_limit(self, power_limit: int) -> None:
        self._session.set_device_power_limit(self.dev_id, power_limit)
        self._power_limit = power_limit

   
class SmartboxNode(object):
    def __init__(
        self,
        device: Union[SmartboxDevice, MagicMock],
        node_info: Dict[str, Any],
        session: Union[Session, MagicMock],
        status: Dict[str, Any],
        setup: Dict[str, Any],
        samples: Dict[str, Any] 
    ) -> None:
        self._device = device
        self._node_info = node_info
        self._session = session
        self._status = status
        self._setup = setup
        self._samples: Any = samples
       
    @property
    def node_id(self) -> str:
        # TODO: are addrs only unique among node types, or for the whole device?
        return f"{self._device.dev_id}-{self._node_info['addr']}"

    @property
    def name(self) -> str:
        return self._node_info["name"]

    @property
    def node_type(self) -> str:
        """Return node type, e.g. 'htr' for heaters"""
        return self._node_info["type"]

    @property
    def addr(self) -> int:
        return self._node_info["addr"]
    
    
    @property
    def status(self) -> StatusDict:
        return self._status

    def update_status(self, status: StatusDict) -> None:
        _LOGGER.debug(f"Updating node {self.name} status: {status}")
        self._status = status

  
    @property
    def setup(self) -> SetupDict:
        return self._setup

    def update_setup(self, setup: SetupDict) -> None:
        _LOGGER.debug(f"Updating node {self.name} setup: {setup}")
        self._setup = setup

    def set_status(self, **status_args) -> StatusDict:
        self._session.set_status(self._device.dev_id, self._node_info, status_args)
        # update our status locally until we get an update
        self._status |= {**status_args}
        return self._status


    @property
    def samples(self) -> Dict[str, Any]:
        return self._samples

    def update_samples(self, samples: Dict[str, Any]) -> None:
#        self._session.get_device_samples(self._device.dev_id, self._node_info,  round((time.time() - time.time() % 3600) - 3600) , round((time.time() - time.time() % 3600) + 1800))
        _LOGGER.debug(f"Updating node {self.name} samples: {samples}")
        self._samples = samples

   # def update_samples(self, **samples_args) -> SamplesDict:
    #def  update_samples(self, any, boo, boo1) -> SamplesDict:
    #    _LOGGER.debug(f"Self: {self}  any: {any} boo: {boo} boo1: {boo1}")
    #    _LOGGER.debug(f"Dev ID: {self._device.dev_id}  and Node Info: {self._node_info}")   
         
        #self._session.get_device_samples(self._device.dev_id, self._node_info,  round((time.time() - time.time() % 3600) - 3600) , round((time.time() - time.time() % 3600) + 1800))
        # update our status samples locally until we get an update
       # self._samples |= {**samples_args}
    #    _LOGGER.debug(f"Updating node {self.name} samples: {self._samples}")
       # return self._samples


    @property
    def away(self):
        return self._device.away

    def update_device_away_status(self, away: bool):
        self._device.set_away_status(away)

    async def async_update(self, hass: HomeAssistant) -> StatusDict:
        return self.status

    @property
    def window_mode(self) -> bool:
        if "window_mode_enabled" not in self._setup:
            raise KeyError(
                "window_mode_enabled not present in setup for node {self.name}"
            )
        return True #self._setup["window_mode_enabled"]

    def set_window_mode(self, window_mode: bool):
        self._session.set_setup(
            self._device.dev_id, self._node_info, {"window_mode_enabled": window_mode}
        )
        self._setup["window_mode_enabled"] = window_mode

    @property
    def true_radiant(self) -> bool:
        if "true_radiant_enabled" not in self._setup:
            raise KeyError(
                "true_radiant_enabled not present in setup for node {self.name}"
            )
        return True #self._setup["true_radiant_enabled"]

    def set_true_radiant(self, true_radiant: bool):
        self._session.set_setup(
            self._device.dev_id, self._node_info, {"true_radiant_enabled": true_radiant}
        )
        self._setup["true_radiant_enabled"] = true_radiant


def is_heater_node(node: Union[SmartboxNode, MagicMock]) -> bool:
    return node.node_type in HEATER_NODE_TYPES


def is_supported_node(node: Union[SmartboxNode, MagicMock]) -> bool:
    return is_heater_node(node)


def get_temperature_unit(status) -> None | Any:
    if "units" not in status:
        return None
    unit = status["units"]
    if unit == "C":
        return UnitOfTemperature.CELSIUS
    elif unit == "F":
        return UnitOfTemperature.FAHRENHEIT
    else:
        raise ValueError(f"Unknown temp unit {unit}")
    



async def get_devices(
    hass: HomeAssistant,
    api_name: str,
    basic_auth_creds: str,
    x_referer: str,
    x_serialid: str,
    username: str,
    password: str,
    session_retry_attempts: int,
    session_backoff_factor: float,
) -> List[SmartboxDevice]:
    _LOGGER.info(
        f"Creating Smartbox session for {api_name}"
        f"(session_retry_attempts={session_retry_attempts}"
        f", session_backoff_factor={session_backoff_factor}"
    )
    session = await hass.async_add_executor_job(
        Session,
        api_name,
        basic_auth_creds,
        x_referer,
        x_serialid,
        username,
        password,
        session_retry_attempts,
        session_backoff_factor,
    )
    session_devices = await hass.async_add_executor_job(session.get_devices)
    
    # TODO: gather?
    devices = [
        await create_smartbox_device(
            hass,
            session_device["dev_id"],
            session_device["name"],
            session,
            session_retry_attempts,
            session_backoff_factor,
        )
        for session_device in session_devices
    ]
    return devices


async def create_smartbox_device(
    hass: HomeAssistant,
    dev_id: str,
    name: str,
    session: Union[Session, MagicMock],
    socket_reconnect_attempts: int,
    socket_backoff_factor: float,
) -> Union[SmartboxDevice, MagicMock]:
    """Factory function for SmartboxDevices"""
    device = SmartboxDevice(
        dev_id, name, session, socket_reconnect_attempts, socket_backoff_factor
    )
    await device.initialise_nodes(hass)
    return device


def _check_status_key(key: str, node_type: str, status: Dict[str, Any]):
    if key not in status:
        raise KeyError(
            f"'{key}' not found in {node_type} - please report to {GITHUB_ISSUES_URL}. "
            f"status: {status}"
        )


def get_target_temperature(node_type: str, status: Dict[str, Any]) -> float:
    if node_type == HEATER_NODE_TYPE_HTR_MOD:
        _check_status_key("selected_temp", node_type, status)
        if status["selected_temp"] == "comfort":
            _check_status_key("comfort_temp", node_type, status)
            return float(status["comfort_temp"])
        elif status["selected_temp"] == "eco":
            _check_status_key("comfort_temp", node_type, status)
            _check_status_key("eco_offset", node_type, status)
            return float(status["comfort_temp"]) - float(status["eco_offset"])
        elif status["selected_temp"] == "ice":
            _check_status_key("ice_temp", node_type, status)
            return float(status["ice_temp"])
        else:
            raise KeyError(
                f"'Unexpected 'selected_temp' value {status['selected_temp']}"
                f" found for {node_type} - please report to"
                f" {GITHUB_ISSUES_URL}. status: {status}"
            )
    else:
        _check_status_key("stemp", node_type, status)
        return float(status["stemp"])


def set_temperature_args(
    node_type: str, status: Dict[str, Any], temp: float
) -> Dict[str, Any]:
    _check_status_key("units", node_type, status)
    if node_type == HEATER_NODE_TYPE_HTR_MOD:
        if status["selected_temp"] == "comfort":
            target_temp = temp
        elif status["selected_temp"] == "eco":
            _check_status_key("eco_offset", node_type, status)
            target_temp = temp + float(status["eco_offset"])
        elif status["selected_temp"] == "ice":
            raise ValueError(
                "Can't set temperature for htr_mod devices when ice mode is selected"
            )
        else:
            raise KeyError(
                f"'Unexpected 'selected_temp' value {status['selected_temp']}"
                f" found for {node_type} - please report to "
                f"{GITHUB_ISSUES_URL}. status: {status}"
            )
        return {
            "on": True,
            "mode": status["mode"],
            "selected_temp": status["selected_temp"],
            "comfort_temp": str(target_temp),
            "eco_offset": status["eco_offset"],
            "units": status["units"],
        }
    else:
        return {
            "stemp": str(temp),
            "units": status["units"],
        }


def get_hvac_mode(node_type: str, status: Dict[str, Any]) -> str:
    _check_status_key("mode", node_type, status)
    if status["mode"] == "off":
        return HVACMode.OFF
    elif node_type == HEATER_NODE_TYPE_HTR_MOD and not status["on"]:
        return HVACMode.OFF
    elif status["mode"] == "manual":
        return HVACMode.HEAT
    elif status["mode"] == "auto":
        return HVACMode.AUTO
    elif status["mode"] == "modified_auto":
        # This occurs when the temperature is modified while in auto mode.
        # Mapping it to auto seems to make this most sense
        return HVACMode.AUTO
    elif status["mode"] == "self_learn":
        return HVACMode.AUTO
    elif status["mode"] == "presence":
        return HVACMode.AUTO
    else:
        _LOGGER.error(f"Unknown smartbox node mode {status['mode']}")
        raise ValueError(f"Unknown smartbox node mode {status['mode']}")


def set_hvac_mode_args(
    node_type: str, status: Dict[str, Any], hvac_mode: str
) -> Dict[str, Any]:
    if node_type == HEATER_NODE_TYPE_HTR_MOD:
        if hvac_mode == HVACMode.OFF:
            return {"on": False}
        elif hvac_mode == HVACMode.HEAT:
            # We need to pass these status keys on when setting the mode
            required_status_keys = ["selected_temp"]
            for key in required_status_keys:
                _check_status_key(key, node_type, status)
            hvac_mode_args = {k: status[k] for k in required_status_keys}
            hvac_mode_args["on"] = True
            hvac_mode_args["mode"] = "manual"
            return hvac_mode_args
        elif hvac_mode == HVACMode.AUTO:
            return {"on": True, "mode": "auto"}
        else:
            raise ValueError(f"Unsupported hvac mode {hvac_mode}")
    else:
        if hvac_mode == HVACMode.OFF:
            return {"mode": "off"}
        elif hvac_mode == HVACMode.HEAT:
            return {"mode": "manual"}
        elif hvac_mode == HVACMode.AUTO:
            return {"mode": "auto"}
        else:
            raise ValueError(f"Unsupported hvac mode {hvac_mode}")


def _get_htr_mod_preset_mode(node_type: str, mode: str, selected_temp: str) -> str:
    if mode == "manual":
        if selected_temp == "comfort":
            return PRESET_COMFORT
        elif selected_temp == "eco":
            return PRESET_ECO
        elif selected_temp == "ice":
            return PRESET_FROST
        else:
            raise ValueError(
                f"'Unexpected 'selected_temp' value {'selected_temp'} found for "
                f"{node_type} - please report to {GITHUB_ISSUES_URL}."
            )
    elif mode == "auto":
        return PRESET_SCHEDULE
    elif mode == "presence":
        return PRESET_ACTIVITY
    elif mode == "self_learn":
        return PRESET_SELF_LEARN
    else:
        raise ValueError(f"Unknown smartbox node mode {mode}")


def get_preset_mode(node_type: str, status: Dict[str, Any], away: bool) -> str:
    if away:
        return PRESET_AWAY
    if node_type == HEATER_NODE_TYPE_HTR_MOD:
        _check_status_key("mode", node_type, status)
        _check_status_key("selected_temp", node_type, status)
        return _get_htr_mod_preset_mode(
            node_type, status["mode"], status["selected_temp"]
        )
    else:
        return PRESET_HOME


def get_preset_modes(node_type: str) -> List[str]:
    if node_type == HEATER_NODE_TYPE_HTR_MOD:
        return [
            PRESET_ACTIVITY,
            PRESET_AWAY,
            PRESET_COMFORT,
            PRESET_ECO,
            PRESET_FROST,
            PRESET_SCHEDULE,
            PRESET_SELF_LEARN,
        ]
    else:
        return [PRESET_AWAY, PRESET_HOME]


def set_preset_mode_status_update(
    node_type: str, status: Dict[str, Any], preset_mode: str
) -> Dict[str, Any]:
    if node_type != HEATER_NODE_TYPE_HTR_MOD:
        raise ValueError(f"{node_type} nodes do not support preset {preset_mode}")
    # PRESET_HOME and PRESET_AWAY are not handled via status updates
    assert preset_mode != PRESET_HOME and preset_mode != PRESET_AWAY

    if preset_mode == PRESET_SCHEDULE:
        return set_hvac_mode_args(node_type, status, HVACMode.AUTO)
    elif preset_mode == PRESET_SELF_LEARN:
        return {"on": True, "mode": "self_learn"}
    elif preset_mode == PRESET_ACTIVITY:
        return {"on": True, "mode": "presence"}
    elif preset_mode == PRESET_COMFORT:
        return {"on": True, "mode": "manual", "selected_temp": "comfort"}
    elif preset_mode == PRESET_ECO:
        return {"on": True, "mode": "manual", "selected_temp": "eco"}
    elif preset_mode == PRESET_FROST:
        return {"on": True, "mode": "manual", "selected_temp": "ice"}
    else:
        raise ValueError(f"Unsupported preset {preset_mode} for node type {node_type}")


def is_heating(node_type: str, status: Dict[str, Any]) -> str:
    return status["charging"] if node_type == HEATER_NODE_TYPE_ACM else status["active"]


def get_factory_options(node: Union[SmartboxNode, MagicMock]) -> FactoryOptionsDict:
    return cast(FactoryOptionsDict, node.setup.get("factory_options", {}))


def window_mode_available(node: Union[SmartboxNode, MagicMock]) -> bool:
    return get_factory_options(node).get("window_mode_available", False)


def true_radiant_available(node: Union[SmartboxNode, MagicMock]) -> bool:
    return get_factory_options(node).get("true_radiant_available", False)


    
def get_energy_used(samples) -> None | Any:
        _LOGGER.debug(f"Model: Samples: {samples}" )
        startKWh: int=0
        endKWh: int=0
        kwh: int=0
        count: int=0
        sample : Dict[str, int]  = samples['samples']
        
        
        _LOGGER.debug(f"Model: Temp2 {sample}" )
        
        if len(sample) == 1:
            return kwh
        else:
        
            for counter in sample:
                temp2 = str(counter).split(',')
                _LOGGER.debug(f"{temp2[2]}")            
           
                if count == 0:
                    lenCount: int = len(temp2[2])
                    _LOGGER.debug(f"LenCount:{lenCount}")

                    startKWh =  int(temp2[2][12:lenCount-1])
                    _LOGGER.debug(f"StartKwh:{startKWh}")
                    count = count + 1
                else:
                    lenCount: int = len(temp2[2])
                    endKWh =  int(temp2[2][12:lenCount-1])
        
        kwh = endKWh-startKWh               
        
        _LOGGER.debug(f"Model: KWH: {kwh}" )
        return kwh   
