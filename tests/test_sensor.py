import logging
import time
from unittest.mock import AsyncMock, patch

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import ATTR_FRIENDLY_NAME, ATTR_LOCKED, STATE_UNAVAILABLE
from mocks import (
    active_or_charging_update,
    get_entity_id_from_unique_id,
    get_node_unique_id,
    get_object_id,
    get_sensor_entity_id,
    get_sensor_entity_name,
    is_heater_node,
)
from pytest import approx
from pytest_homeassistant_custom_component.common import MockConfigEntry
from test_utils import convert_temp, round_temp

from custom_components.smartbox.const import (
    CONF_HISTORY_CONSUMPTION,
    DOMAIN,
    HistoryConsumptionStatus,
    SmartboxNodeType,
)
from custom_components.smartbox.sensor import TotalConsumptionSensor

_LOGGER = logging.getLogger(__name__)


def _check_temp_state(hass, mock_node_status, state):
    assert round_temp(hass, float(state.state)) == round_temp(
        hass,
        convert_temp(hass, mock_node_status["units"], float(mock_node_status["mtemp"])),
    )


async def test_basic_temp(hass, mock_smartbox, config_entry):
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 25
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    for mock_device in await mock_smartbox.session.get_devices():
        for mock_node in await mock_smartbox.session.get_nodes(mock_device["dev_id"]):
            if not is_heater_node(mock_node):
                continue
            entity_id = get_sensor_entity_id(mock_node, "temperature")
            state = hass.states.get(entity_id)

            # check basic properties
            assert state.object_id.startswith(
                get_object_id(get_sensor_entity_name(mock_node, "temperature"))
            )
            assert state.entity_id.startswith(
                get_sensor_entity_id(mock_node, "temperature")
            )
            assert state.name == f"{mock_node['name']} Temperature"
            assert (
                state.attributes[ATTR_FRIENDLY_NAME]
                == f"{mock_node['name']} Temperature"
            )
            unique_id = get_node_unique_id(mock_device, mock_node, "temperature")
            assert entity_id == get_entity_id_from_unique_id(
                hass, SENSOR_DOMAIN, unique_id
            )

            mock_node_status = await mock_smartbox.session.get_status(
                mock_device["dev_id"], mock_node
            )
            assert state.attributes[ATTR_LOCKED] == mock_node_status["locked"]
            _check_temp_state(hass, mock_node_status, state)

            mock_node_status = mock_smartbox.generate_socket_status_update(
                mock_device,
                mock_node,
                {"mtemp": str(float(mock_node_status["mtemp"]) + 1)},
            )

            await hass.helpers.entity_component.async_update_entity(entity_id)
            new_state = hass.states.get(entity_id)
            assert new_state.state != state.state
            _check_temp_state(hass, mock_node_status, new_state)

            # test unavailable
            mock_node_status = mock_smartbox.generate_socket_node_unavailable(
                mock_device, mock_node
            )
            await hass.helpers.entity_component.async_update_entity(entity_id)
            state = hass.states.get(entity_id)
            assert state.state == STATE_UNAVAILABLE

            mock_node_status = mock_smartbox.generate_new_socket_status(
                mock_device, mock_node
            )
            await hass.helpers.entity_component.async_update_entity(entity_id)
            state = hass.states.get(entity_id)
            assert state.state != STATE_UNAVAILABLE


async def test_basic_power(hass, mock_smartbox, config_entry):
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 25
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    for mock_device in await mock_smartbox.session.get_devices():
        for mock_node in await mock_smartbox.session.get_nodes(mock_device["dev_id"]):
            if (
                not is_heater_node(mock_node)
                or mock_node["type"] == SmartboxNodeType.HTR_MOD
            ):
                continue
            entity_id = get_sensor_entity_id(mock_node, "power")
            state = hass.states.get(entity_id)

            # check basic properties
            assert state.object_id.startswith(
                get_object_id(get_sensor_entity_name(mock_node, "power"))
            )
            assert state.entity_id.startswith(get_sensor_entity_id(mock_node, "power"))
            assert state.name == f"{mock_node['name']} Power"
            assert state.attributes[ATTR_FRIENDLY_NAME] == f"{mock_node['name']} Power"
            unique_id = get_node_unique_id(mock_device, mock_node, "power")
            assert entity_id == get_entity_id_from_unique_id(
                hass, SENSOR_DOMAIN, unique_id
            )

            # make sure it's active/charging
            mock_smartbox.generate_socket_status_update(
                mock_device,
                mock_node,
                active_or_charging_update(mock_node["type"], True),
            )
            await hass.helpers.entity_component.async_update_entity(entity_id)
            state = hass.states.get(entity_id)
            mock_node_status = await mock_smartbox.session.get_status(
                mock_device["dev_id"], mock_node
            )
            assert state.attributes[ATTR_LOCKED] == mock_node_status["locked"]
            assert float(state.state) == approx(float(mock_node_status["power"]))

            # make sure it's inactive/not charging
            mock_smartbox.generate_socket_status_update(
                mock_device,
                mock_node,
                active_or_charging_update(mock_node["type"], False),
            )
            await hass.helpers.entity_component.async_update_entity(entity_id)
            state = hass.states.get(entity_id)
            mock_node_status = await mock_smartbox.session.get_status(
                mock_device["dev_id"], mock_node
            )
            assert float(state.state) == 0

            # test unavailable
            mock_node_status = mock_smartbox.generate_socket_node_unavailable(
                mock_device, mock_node
            )
            await hass.helpers.entity_component.async_update_entity(entity_id)
            state = hass.states.get(entity_id)
            assert state.state == STATE_UNAVAILABLE

            mock_node_status = mock_smartbox.generate_new_socket_status(
                mock_device, mock_node
            )
            await hass.helpers.entity_component.async_update_entity(entity_id)
            state = hass.states.get(entity_id)
            assert state.state != STATE_UNAVAILABLE


async def test_unavailable(hass, mock_smartbox_unavailable):
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="test_username_1",
        data=mock_smartbox_unavailable.config[DOMAIN],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 25
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    for mock_device in await mock_smartbox_unavailable.session.get_devices():
        for mock_node in await mock_smartbox_unavailable.session.get_nodes(
            mock_device["dev_id"]
        ):
            if not is_heater_node(mock_node):
                continue
            sensor_types = (
                ["temperature"]
                if mock_node["type"] == SmartboxNodeType.HTR_MOD
                else ["temperature", "power"]
            )
            for sensor_type in sensor_types:
                entity_id = get_sensor_entity_id(mock_node, "temperature")

                state = hass.states.get(entity_id)
                assert state.state == STATE_UNAVAILABLE


async def test_basic_charge_level(hass, mock_smartbox, config_entry):
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(SENSOR_DOMAIN)) == 25
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    for mock_device in await mock_smartbox.session.get_devices():
        for mock_node in await mock_smartbox.session.get_nodes(mock_device["dev_id"]):
            # Only supported on acm nodes
            if mock_node["type"] != SmartboxNodeType.ACM:
                continue

            entity_id = get_sensor_entity_id(mock_node, "charge_level")
            state = hass.states.get(entity_id)

            # check basic properties
            assert state.object_id.startswith(
                get_object_id(get_sensor_entity_name(mock_node, "charge_level"))
            )
            assert state.entity_id.startswith(
                get_sensor_entity_id(mock_node, "charge_level")
            )
            assert state.name == f"{mock_node['name']} Charge Level"
            assert (
                state.attributes[ATTR_FRIENDLY_NAME]
                == f"{mock_node['name']} Charge Level"
            )
            unique_id = get_node_unique_id(mock_device, mock_node, "charge_level")
            assert entity_id == get_entity_id_from_unique_id(
                hass, SENSOR_DOMAIN, unique_id
            )

            # Check charge level is correct
            mock_smartbox.generate_socket_status_update(
                mock_device,
                mock_node,
                active_or_charging_update(mock_node["type"], True),
            )
            await hass.helpers.entity_component.async_update_entity(entity_id)
            state = hass.states.get(entity_id)
            mock_node_status = await mock_smartbox.session.get_status(
                mock_device["dev_id"], mock_node
            )
            assert state.attributes[ATTR_LOCKED] == mock_node_status["locked"]
            assert int(state.state) == approx(int(mock_node_status["charge_level"]))

            # Update charge level via socket
            mock_smartbox.generate_socket_status_update(
                mock_device, mock_node, {"charge_level": 5}
            )
            await hass.helpers.entity_component.async_update_entity(entity_id)
            state = hass.states.get(entity_id)
            mock_node_status = await mock_smartbox.session.get_status(
                mock_device["dev_id"], mock_node
            )
            assert int(state.state) == 5

            # test unavailable
            mock_node_status = mock_smartbox.generate_socket_node_unavailable(
                mock_device, mock_node
            )
            await hass.helpers.entity_component.async_update_entity(entity_id)
            state = hass.states.get(entity_id)
            assert state.state == STATE_UNAVAILABLE

            mock_node_status = mock_smartbox.generate_new_socket_status(
                mock_device, mock_node
            )
            await hass.helpers.entity_component.async_update_entity(entity_id)
            state = hass.states.get(entity_id)
            assert state.state != STATE_UNAVAILABLE


async def test_update_statistics_start(hass, mock_smartbox, config_entry):
    mock_node = AsyncMock()
    mock_node.get_samples = AsyncMock(
        return_value={"samples": [{"t": 1739966400, "counter": 100}]}
    )
    sensor = TotalConsumptionSensor(mock_node, config_entry)
    sensor.hass = hass
    hass.config_entries.async_update_entry(
        entry=config_entry,
        options={
            **config_entry.options,
            CONF_HISTORY_CONSUMPTION: HistoryConsumptionStatus.START,
        },
    )

    with (
        patch.object(hass.config_entries, "async_update_entry") as mock_update_entry,
        patch(
            "custom_components.smartbox.sensor.async_import_statistics"
        ) as mock_import_statistics,
    ):
        await sensor.update_statistics()

        assert mock_node.get_samples.call_count == 3
        mock_update_entry.assert_called_once_with(
            entry=config_entry,
            options={
                **config_entry.options,
                CONF_HISTORY_CONSUMPTION: HistoryConsumptionStatus.AUTO,
            },
        )
        assert mock_import_statistics.called


async def test_update_statistics_auto(hass, mock_smartbox, config_entry):
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    mock_node = AsyncMock()
    mock_node.get_samples = AsyncMock(
        return_value={"samples": [{"t": 1739966400, "counter": 100}]}
    )
    sensor = TotalConsumptionSensor(mock_node, config_entry)
    sensor.hass = hass
    hass.config_entries.async_update_entry(
        entry=config_entry,
        options={
            **config_entry.options,
            CONF_HISTORY_CONSUMPTION: HistoryConsumptionStatus.AUTO,
        },
    )

    with patch(
        "custom_components.smartbox.sensor.async_import_statistics"
    ) as mock_import_statistics:
        await sensor.update_statistics()

        mock_node.get_samples.assert_called_once()
        assert mock_import_statistics.called


async def test_update_statistics_off(hass, mock_smartbox, config_entry):
    mock_node = AsyncMock()
    mock_node.get_samples = AsyncMock(
        return_value={"samples": [{"t": time.time(), "counter": 100}]}
    )
    sensor = TotalConsumptionSensor(mock_node, config_entry)
    sensor.hass = hass
    hass.config_entries.async_update_entry(
        entry=config_entry,
        options={
            **config_entry.options,
            CONF_HISTORY_CONSUMPTION: HistoryConsumptionStatus.OFF,
        },
    )

    with patch(
        "custom_components.smartbox.sensor.async_import_statistics"
    ) as mock_import_statistics:
        await sensor.update_statistics()

        mock_import_statistics.assert_not_called()
