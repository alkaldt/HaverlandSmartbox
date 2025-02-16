# """Test NextDNS system health."""

# import asyncio

# from aiohttp import ClientError

# from custom_components.smartbox.const import DOMAIN
# from homeassistant.core import HomeAssistant
# from homeassistant.setup import async_setup_component
# from homeassistant.components import system_health
# from pytest_homeassistant_custom_component.common import get_system_health_info
# from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
# from unittest.mock import AsyncMock, Mock, patch
# from pytest_homeassistant_custom_component.common import mock_platform


# async def test_system_health(
#     hass: HomeAssistant,
#     aioclient_mock: AiohttpClientMocker,
# ) -> None:
#     """Test registering via platform."""
#     aioclient_mock.get("http://api.example.com/status", text="aa")
#     aioclient_mock.get("http://web.example.com/", exc=ClientError)
#     hass.config.components.add(DOMAIN)
#     mock_platform(
#         hass,
#         f"{DOMAIN}.system_health",
#         Mock(
#             async_register=lambda hass, register: register.async_register_info(
#                 AsyncMock(
#                     return_value={
#                         "api_health_check": system_health.async_check_can_reach_url(
#                             hass, "http://api.example.com/"
#                         ),
#                         "can_reach_web_resailer": system_health.async_check_can_reach_url(
#                             hass,
#                             "http://web.example.com/",
#                         ),
#                     }
#                 ),
#                 "/config/fake_integration",
#             )
#         ),
#     )

#     assert await async_setup_component(hass, "system_health", {})
#     info = await get_system_health_info(hass, DOMAIN)
#     a = await info["api_health_check"]
#     for key, val in info.items():
#         if asyncio.iscoroutine(val):
#             info[key] = await val


# async def test_nextdns_system_health(
#     hass: HomeAssistant,
#     aioclient_mock: AiohttpClientMocker,
#     config_entry,
#     mock_smartbox,
# ) -> None:
#     """Test NextDNS system health."""
#     aioclient_mock.get("https://api.example.com/", text="")
#     hass.config.components.add(DOMAIN)
#     assert await async_setup_component(hass, "system_health", {})
#     assert await hass.config_entries.async_setup(config_entry.entry_id)
#     await hass.async_block_till_done()

#     info = await get_system_health_info(hass, DOMAIN)

#     for key, val in info.items():
#         if asyncio.iscoroutine(val):
#             info[key] = await val

#     assert info == {"can_reach_server": "ok"}


# async def test_nextdns_system_health_fail(
#     hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, resailer
# ) -> None:
#     """Test NextDNS system health."""
#     aioclient_mock.get("https://api.example.com/", exc=ClientError)
#     hass.config.components.add(DOMAIN)
#     assert await async_setup_component(hass, "system_health", {})
#     await hass.async_block_till_done()

#     info = await get_system_health_info(hass, DOMAIN)

#     for key, val in info.items():
#         if asyncio.iscoroutine(val):
#             info[key] = await val

#     assert info == {"can_reach_server": {"type": "failed", "error": "unreachable"}}
