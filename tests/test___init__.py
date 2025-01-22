import pytest
import requests
from unittest.mock import AsyncMock, patch
from homeassistant.exceptions import ConfigEntryAuthFailed
from custom_components.smartbox import async_setup_entry, update_listener
from custom_components.smartbox import (
    create_smartbox_session_from_entry,
    InvalidAuth,
)


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


@pytest.mark.asyncio
async def test_update_listener(hass, config_entry):
    with patch.object(hass.config_entries, "async_reload", AsyncMock()) as mock_reload:
        await update_listener(hass, config_entry)
        mock_reload.assert_called_once_with(config_entry.entry_id)
