import pytest
import requests
from unittest.mock import AsyncMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed
from custom_components.smartbox import async_setup_entry
from custom_components.smartbox.const import DOMAIN, SMARTBOX_DEVICES, SMARTBOX_NODES
from custom_components.smartbox import (
    async_setup_entry,
    create_smartbox_session_from_entry,
    InvalidAuth,
)
from custom_components.smartbox.const import (
    DOMAIN,
    SMARTBOX_DEVICES,
    SMARTBOX_NODES,
    CONF_API_NAME,
    CONF_BASIC_AUTH_CREDS,
    CONF_USERNAME,
    CONF_PASSWORD,
)


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.check_refresh_auth = AsyncMock()
    return session


@pytest.fixture
def mock_devices():
    device = AsyncMock()
    device.dev_id = "device_1"
    device.get_nodes = AsyncMock(return_value=[])
    return [device]


@pytest.fixture
def mock_get_devices(mock_devices):
    with patch("custom_components.smartbox.get_devices", return_value=mock_devices):
        yield


@pytest.mark.asyncio
async def test_async_setup_entry_auth_failed(hass, config_entry):
    with patch(
        "custom_components.smartbox.create_smartbox_session_from_entry",
        side_effect=Exception,
    ):
        with pytest.raises(ConfigEntryAuthFailed):
            await async_setup_entry(hass, config_entry)


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.check_refresh_auth = AsyncMock()
    return session


@pytest.fixture
def mock_devices():
    device = AsyncMock()
    device.dev_id = "device_1"
    device.get_nodes = AsyncMock(return_value=[])
    return [device]


@pytest.fixture
def mock_get_devices(mock_devices):
    with patch("custom_components.smartbox.get_devices", return_value=mock_devices):
        yield


@pytest.mark.asyncio
async def test_async_setup_entry_auth_failed(hass, config_entry):
    with patch(
        "custom_components.smartbox.create_smartbox_session_from_entry",
        side_effect=Exception,
    ):
        with pytest.raises(ConfigEntryAuthFailed):
            await async_setup_entry(hass, config_entry)


@pytest.mark.asyncio
async def test_create_smartbox_session_from_entry_success(
    hass, config_entry, mock_session
):
    with patch(
        "custom_components.smartbox.async_get_clientsession", return_value=AsyncMock()
    ), patch(
        "custom_components.smartbox.AsyncSmartboxSession", return_value=mock_session
    ):
        session = await create_smartbox_session_from_entry(hass, config_entry)
        assert session is not None
        assert session.check_refresh_auth.called


@pytest.mark.asyncio
async def test_create_smartbox_session_from_entry_connection_error(hass, config_entry):
    with patch(
        "custom_components.smartbox.async_get_clientsession", return_value=AsyncMock()
    ), patch(
        "custom_components.smartbox.AsyncSmartboxSession",
        side_effect=requests.exceptions.ConnectionError,
    ):
        with pytest.raises(requests.exceptions.ConnectionError):
            await create_smartbox_session_from_entry(hass, config_entry)


@pytest.mark.asyncio
async def test_create_smartbox_session_from_entry_invalid_auth(hass, config_entry):

    with patch(
        "custom_components.smartbox.async_get_clientsession", return_value=AsyncMock()
    ), patch(
        "custom_components.smartbox.AsyncSmartboxSession", side_effect=InvalidAuth
    ):
        with pytest.raises(InvalidAuth):
            await create_smartbox_session_from_entry(hass, config_entry)
