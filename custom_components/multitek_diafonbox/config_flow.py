"""Config flow for Multitek DiafonBox integration."""
from __future__ import annotations

import logging
import uuid
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MultitekAPI, MultitekAuthError, MultitekAPIError
from .const import CONF_PHONE_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PHONE_ID): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    
    phone_id = data[CONF_PHONE_ID].strip()
    
    api = MultitekAPI(
        email=data[CONF_EMAIL],
        password="",  # Not needed for invited users
        phone_id=phone_id,
        session=session,
    )

    # Test login
    if not await api.login():
        raise MultitekAuthError("Invalid email or phone_id")

    # Get account info for title
    account = await api.get_account()
    user_name = account.get("user_name", "")
    user_surname = account.get("user_surname", "")
    
    title = f"{user_name} {user_surname}".strip()
    if not title:
        title = data[CONF_EMAIL]

    return {"title": title, "phone_id": phone_id}


class MultitekConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Multitek DiafonBox."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except MultitekAuthError:
                errors["base"] = "invalid_auth"
            except MultitekAPIError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create entry
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_PHONE_ID: info["phone_id"],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
