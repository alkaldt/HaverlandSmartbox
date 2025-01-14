from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN
from homeassistant.components.number import ATTR_VALUE, SERVICE_SET_VALUE
from homeassistant.const import ATTR_ENTITY_ID, ATTR_FRIENDLY_NAME
from custom_components.smartbox.const import DOMAIN

from mocks import (
    get_entity_id_from_unique_id,
    get_object_id,
    get_power_limit_number_entity_id,
    get_power_limit_number_entity_name,
    get_device_unique_id,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_power_limit(hass, mock_smartbox):
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="test_username_1",
        data=mock_smartbox.config[DOMAIN],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert len(hass.states.async_entity_ids(NUMBER_DOMAIN)) == 2
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1

    assert DOMAIN in hass.config.components

    for mock_device in mock_smartbox.session.get_devices():
        entity_id = get_power_limit_number_entity_id(mock_device)
        state = hass.states.get(entity_id)

        # check basic properties
        assert state.object_id.startswith(
            get_object_id(get_power_limit_number_entity_name(mock_device))
        )
        assert state.entity_id.startswith(get_power_limit_number_entity_id(mock_device))
        assert state.name == f"{mock_device['name']} Power Limit"
        assert (
            state.attributes[ATTR_FRIENDLY_NAME] == f"{mock_device['name']} Power Limit"
        )
        unique_id = get_device_unique_id(mock_device, "power_limit")
        assert entity_id == get_entity_id_from_unique_id(hass, NUMBER_DOMAIN, unique_id)

        # Starts not away
        assert state.state == "0"

    # Set device 1 power limit
    mock_device_1 = mock_smartbox.session.get_devices()[0]
    mock_smartbox.dev_data_update(
        mock_device_1, {"htr_system": {"setup": {"power_limit": "1000"}}}
    )

    entity_id = get_power_limit_number_entity_id(mock_device_1)
    await hass.helpers.entity_component.async_update_entity(entity_id)
    state = hass.states.get(entity_id)
    assert state.state == "1000"

    mock_device_2 = mock_smartbox.session.get_devices()[1]
    entity_id = get_power_limit_number_entity_id(mock_device_2)
    await hass.helpers.entity_component.async_update_entity(entity_id)
    state = hass.states.get(entity_id)
    assert state.state == "0"

    # Set back to 0 via HA
    entity_id = get_power_limit_number_entity_id(mock_device_1)
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: entity_id, ATTR_VALUE: 0},
        blocking=True,
    )
    await hass.helpers.entity_component.async_update_entity(entity_id)
    state = hass.states.get(entity_id)
    assert state.state == "0"

    # Set device 2 to 500 via HA
    entity_id = get_power_limit_number_entity_id(mock_device_2)
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: entity_id, ATTR_VALUE: 500},
        blocking=True,
    )
    await hass.helpers.entity_component.async_update_entity(entity_id)
    state = hass.states.get(entity_id)
    assert state.state == "500"
