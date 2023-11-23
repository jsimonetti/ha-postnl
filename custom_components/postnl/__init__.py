import logging
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.config_entry_oauth2_flow import async_get_config_entry_implementation, OAuth2Session

from .login_api import PostNLLoginAPI
from .const import DOMAIN, PLATFORMS
from .graphql import PostNLGraphql

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> True:
    """Set up PostNL from config entry."""
    _LOGGER.debug("Setup Entry PostNL")

    implementation = await async_get_config_entry_implementation(hass, entry)
    session = OAuth2Session(hass, entry, implementation)
    await session.async_ensure_token_valid()

    _LOGGER.debug('Using access token: %s', entry.data['token']['access_token'])
    _LOGGER.debug('Using refresh token: %s', entry.data['token']['refresh_token'])

    postnl_login_api = PostNLLoginAPI(entry.data['token']['access_token'])
    userinfo = await hass.async_add_executor_job(postnl_login_api.userinfo)

    if "error" in userinfo:
        raise ConfigEntryNotReady

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
