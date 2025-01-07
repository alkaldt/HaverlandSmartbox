"""Support for Smartbox sensor entities."""

from datetime import datetime, timedelta
import logging
from typing import Any
from unittest.mock import MagicMock

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_LOCKED, PERCENTAGE, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    HEATER_NODE_TYPE_ACM,
    HEATER_NODE_TYPE_HTR,
    HEATER_NODE_TYPE_HTR_MOD,
    SMARTBOX_NODES,
)
from .model import SmartboxNode, get_temperature_unit, is_heater_node

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up platform."""
    _LOGGER.debug("Setting up Smartbox sensor platform")

    # Temperature
    async_add_entities(
        [
            TemperatureSensor(node)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if is_heater_node(node)
        ],
        True,
    )
    # Power
    async_add_entities(
        [
            PowerSensor(node)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if is_heater_node(node) and node.node_type != HEATER_NODE_TYPE_HTR_MOD
        ],
        True,
    )
    # Duty Cycle and Energy
    # Only nodes of type 'htr' seem to report the duty cycle, which is needed
    # to compute energy consumption
    async_add_entities(
        [
            DutyCycleSensor(node)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if node.node_type == HEATER_NODE_TYPE_HTR
        ],
        True,
    )
    async_add_entities(
        [
            EnergySensor(node)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if node.node_type == HEATER_NODE_TYPE_HTR
        ],
        True,
    )
    # to collect the records for temperture and electricty consumption
    # async_add_entities(
    #     [
    #         SamplesSensor(node)
    #         for node in hass.data[DOMAIN][SMARTBOX_NODES]
    #         if node.node_type == HEATER_NODE_TYPE_HTR
    #     ],
    #     True,
    # )
    # Charge Level
    async_add_entities(
        [
            ChargeLevelSensor(node)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if is_heater_node(node) and node.node_type == HEATER_NODE_TYPE_ACM
        ],
        True,
    )

    _LOGGER.debug("Finished setting up Smartbox sensor platform")


class SmartboxSensorBase(SensorEntity):
    """Base class for Smartbox sensor."""

    def __init__(self, node: SmartboxNode | MagicMock) -> None:
        """Initialize the Climate Entity."""
        self._node = node
        self._status: dict[str, Any] = {}
        self._available = False  # unavailable until we get an update
        self._samples: dict[str, Any] = {}
        self._last_update: datetime | None = None
        self._time_since_last_update: timedelta | None = None
        self._device_id = self._node.node_id
        _LOGGER.debug("Created node %s unique_id=%s", self.name, self.unique_id)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._node.name,
            model_id=self._node.device.model_id,
            sw_version=self._node.device.sw_version,
            serial_number=self._node.device.serial_number,
        )

    @property
    def extra_state_attributes(self) -> dict[str, bool]:
        """Return extra states of the sensor."""
        return {
            ATTR_LOCKED: self._status["locked"],
        }

    @property
    def available(self) -> bool:
        """Return the availability of the sensor."""
        return self._available

    async def async_update(self) -> None:
        """Get the latest data."""
        new_status = await self._node.async_update(self.hass)
        if new_status["sync_status"] == "ok":
            # update our status
            self._status = new_status
            self._available = True
            update_time = datetime.now()
            if self._last_update is not None:
                self._time_since_last_update = update_time - self._last_update
            self._last_update = update_time
        else:
            self._available = False
            self._last_update = None
            self._time_since_last_update = None

    @property
    def time_since_last_update(self) -> timedelta | None:
        """Return the time since the data have been updated."""
        return self._time_since_last_update


class TemperatureSensor(SmartboxSensorBase):
    """Smartbox heater temperature sensor."""

    device_class = SensorDeviceClass.TEMPERATURE
    state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._node.name} Temperature"

    @property
    def unique_id(self) -> str:
        """Return the unique id of the sensor."""
        return f"{self._node.node_id}_temperature"

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        return self._status["mtemp"]

    @property
    def native_unit_of_measurement(self) -> Any:
        """Return the unit of the sensor."""
        return get_temperature_unit(self._status)


class PowerSensor(SmartboxSensorBase):
    """Smartbox heater power sensor.

    Note: this represents the power the heater is drawing *when heating*; the
    heater is not always active over the entire period since the last update,
    even when 'active' is true. The duty cycle sensor indicates how much it
    was active. To measure energy consumption, use the corresponding energy
    sensor.
    """

    device_class = SensorDeviceClass.POWER
    native_unit_of_measurement = UnitOfPower.WATT
    state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._node.name} Power"

    @property
    def unique_id(self) -> str:
        """Return the unique id of the sensor."""
        return f"{self._node.node_id}_power"

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        return self._status["power"] if self._node.is_heating(self._status) else 0


class DutyCycleSensor(SmartboxSensorBase):
    """Smartbox heater duty cycle sensor: Represents the duty cycle for the heater."""

    device_class = SensorDeviceClass.POWER_FACTOR
    native_unit_of_measurement = PERCENTAGE
    state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._node.name} Duty Cycle"

    @property
    def unique_id(self) -> str:
        """Return the unique id of the sensor."""
        return f"{self._node.node_id}_duty_cycle"

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        return self._status["duty"]


class EnergySensor(SmartboxSensorBase):
    """Smartbox heater energy sensor: Represents the energy consumed by the heater."""

    device_class = SensorDeviceClass.ENERGY
    native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    state_class = SensorStateClass.TOTAL

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._node.name} Energy"

    @property
    def unique_id(self) -> str:
        """Return the unique id of the sensor."""
        return f"{self._node.node_id}_energy"

    @property
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        time_since_last_update = self.time_since_last_update
        if time_since_last_update is not None:
            return (
                float(self._status["power"])
                * float(self._status["duty"])
                / 100
                * time_since_last_update.seconds
                / 60
                / 60
            )
        return None


# class SamplesSensor(SmartboxSensorBase):
#     """Smartbox samples sensor

#     Represents the temperture and electrity consumed by the heater for each hour for the day.
#     """

#     device_class = SensorDeviceClass.ENERGY
#     native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
#     state_class = SensorStateClass.TOTAL_INCREASING

#     # TOTAL_INCREASING
#     def __init__(self, node: Union[SmartboxNode, MagicMock]) -> None:
#         super().__init__(node)

#     @property
#     def name(self) -> str:
#         return f"{self._node.name} Hour KWh"

#     @property
#     def unique_id(self) -> str:
#         return f"{self._node.node_id}_energy_hour"

#     @property
#     def native_value(self) -> float | None:
#         return self._node.get_energy_used(self._node._samples)


class ChargeLevelSensor(SmartboxSensorBase):
    """Smartbox storage heater charge level sensor."""

    device_class = SensorDeviceClass.BATTERY
    native_unit_of_measurement = PERCENTAGE
    state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._node.name} Charge Level"

    @property
    def unique_id(self) -> str:
        """Return the unique id of the sensor."""
        return f"{self._node.node_id}_charge_level"

    @property
    def native_value(self) -> int:
        """Return the native value of the sensor."""
        return self._status["charge_level"]
