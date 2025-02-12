"""Support for Smartbox sensor entities."""

import logging
import time
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

from dateutil import tz
from homeassistant.components.energy.data import (
    DeviceConsumption,
    EnergyPreferences,
    async_get_manager,
)
from homeassistant.components.recorder import DOMAIN as RECORDER_DOMAIN
from homeassistant.components.recorder.models.statistics import (
    StatisticData,
    StatisticMetaData,
)
from homeassistant.components.recorder.statistics import async_import_statistics
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_LOCKED,
    PERCENTAGE,
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    CONF_HISTORY_CONSUMPTION,
    CONF_AUTO_ADD_ENERGY_DEVICES,
    DOMAIN,
    SMARTBOX_NODES,
    HistoryConsumptionStatus,
    SmartboxNodeType,
)
from .entity import SmartBoxNodeEntity
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
            TemperatureSensor(node, entry)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if is_heater_node(node)
        ],
        True,
    )
    # Power
    async_add_entities(
        [
            PowerSensor(node, entry)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if is_heater_node(node) and node.node_type != SmartboxNodeType.HTR_MOD
        ],
        True,
    )
    # Duty Cycle and Energy
    # Only nodes of type 'htr' seem to report the duty cycle, which is needed
    # to compute energy consumption
    async_add_entities(
        [
            DutyCycleSensor(node, entry)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if node.node_type == SmartboxNodeType.HTR
        ],
        True,
    )
    async_add_entities(
        [
            EnergySensor(node, entry)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if node.node_type == SmartboxNodeType.HTR
        ],
        True,
    )
    async_add_entities(
        [
            TotalConsumptionSensor(node, entry)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if node.node_type == SmartboxNodeType.HTR
        ],
        True,
    )

    # Charge Level
    async_add_entities(
        [
            ChargeLevelSensor(node, entry)
            for node in hass.data[DOMAIN][SMARTBOX_NODES]
            if is_heater_node(node) and node.node_type == SmartboxNodeType.ACM
        ],
        True,
    )

    _LOGGER.debug("Finished setting up Smartbox sensor platform")


class SmartboxSensorBase(SmartBoxNodeEntity, SensorEntity):
    """Base class for Smartbox sensor."""

    def __init__(
        self, node: SmartboxNode | MagicMock, entry: ConfigEntry, **kwargs: Any
    ) -> None:
        """Initialize the Climate Entity."""
        super().__init__(node=node, entry=entry, **kwargs)
        self.config_entry = entry
        self._status: dict[str, Any] = {}
        self._available = False  # unavailable until we get an update
        self._last_update: datetime | None = None
        self._time_since_last_update: timedelta | None = None
        self._attr_websocket_event = "status"
        _LOGGER.debug("Created node unique_id=%s", self.unique_id)

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

    _attr_key = "temperature"
    device_class = SensorDeviceClass.TEMPERATURE
    state_class = SensorStateClass.MEASUREMENT

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

    _attr_key = "power"
    device_class = SensorDeviceClass.POWER
    native_unit_of_measurement = UnitOfPower.WATT
    state_class = SensorStateClass.MEASUREMENT
    entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        return self._status["power"] if self._node.is_heating(self._status) else 0


class DutyCycleSensor(SmartboxSensorBase):
    """Smartbox heater duty cycle sensor: Represents the duty cycle for the heater."""

    _attr_key = "duty_cycle"
    device_class = SensorDeviceClass.POWER_FACTOR
    native_unit_of_measurement = PERCENTAGE
    state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        return self._status["duty"]


class EnergySensor(SmartboxSensorBase):
    """Smartbox heater energy sensor: Represents the energy consumed by the heater."""

    _attr_key = "energy"
    device_class = SensorDeviceClass.ENERGY
    native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    state_class = SensorStateClass.TOTAL

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


class TotalConsumptionSensor(SmartboxSensorBase):
    """Smartbox heater energy sensor: Represents the energy consumed by the heater in total."""

    _attr_key = "total_consumption"
    device_class = SensorDeviceClass.ENERGY
    native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_value = None

    @property
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        return self._node.total_energy

    async def async_update(self) -> None:
        """Get the latest data."""
        await super().async_update()
        await self._node.update_samples()

    async def async_added_to_hass(self) -> None:
        """When added to hass."""
        # perform initial statistics import when sensor is added, otherwise it would take
        # 1 day when _handle_coordinator_update is triggered for the first time.
        await self.update_statistics()
        await super().async_added_to_hass()
        if self.config_entry.options.get(CONF_AUTO_ADD_ENERGY_DEVICES, False) is True:
            energy_manager = await async_get_manager(self.hass)
            if (
                next(
                    (
                        d
                        for d in energy_manager.data["device_consumption"]
                        if d["stat_consumption"] == self.entity_id
                    ),
                    None,
                )
                is None
            ):
                _LOGGER.debug(
                    "Adding the device %s to energy dashboard", self.entity_id
                )
                await energy_manager.async_update(
                    EnergyPreferences(
                        device_consumption=[
                            DeviceConsumption(stat_consumption=self.entity_id)
                        ]
                    )
                )

        async_track_time_interval(
            self.hass,
            self.update_statistics,
            timedelta(hours=24),
            name=f"Update statistics - {self.name}",
            cancel_on_shutdown=True,
        )

    async def update_statistics(self, *args, **kwargs) -> None:
        """Update statistics from samples."""
        history_status = HistoryConsumptionStatus(
            self.config_entry.options.get(
                CONF_HISTORY_CONSUMPTION, HistoryConsumptionStatus.START
            )
        )
        statistic_id = f"{self.entity_id}"
        hourly_data = []
        if history_status == HistoryConsumptionStatus.START:
            # last 3 years
            for year in (3, 2, 1):
                year_sample = await self._node.get_samples(
                    time.time() - (year * 365 * 24 * 60 * 60),
                    time.time() - ((year - 1) * 365 * 24 * 60 * 60 - 3600),
                )
                hourly_data.extend(year_sample["samples"])
            self.hass.config_entries.async_update_entry(
                entry=self.config_entry,
                options={
                    **self.config_entry.options,
                    CONF_HISTORY_CONSUMPTION: HistoryConsumptionStatus.AUTO,
                },
            )
        elif history_status == HistoryConsumptionStatus.AUTO:
            # last day
            hourly_data = (
                await self._node.get_samples(
                    time.time() - (24 * 60 * 50),
                    time.time() + 3600,
                )
            )["samples"]

        hourly_data = sorted(hourly_data, key=lambda x: x["t"])
        statistics: list[StatisticData] = [
            StatisticData(
                start=datetime.fromtimestamp(entry["t"], tz.tzlocal())
                - timedelta(hours=1),
                sum=entry["counter"],
                state=entry["counter"],
            )
            for entry in hourly_data
        ]
        metadata: StatisticMetaData = StatisticMetaData(
            has_mean=False,
            has_sum=True,
            source=RECORDER_DOMAIN,
            name=statistic_id,
            statistic_id=statistic_id,
            unit_of_measurement=self.native_unit_of_measurement,
        )
        if statistics and history_status != HistoryConsumptionStatus.OFF:
            _LOGGER.debug("Insert statistics: %s %s", metadata, statistics)
            async_import_statistics(self.hass, metadata, statistics)


class ChargeLevelSensor(SmartboxSensorBase):
    """Smartbox storage heater charge level sensor."""

    _attr_key = "charge_level"
    device_class = SensorDeviceClass.BATTERY
    native_unit_of_measurement = PERCENTAGE
    state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return the native value of the sensor."""
        return self._status["charge_level"]
