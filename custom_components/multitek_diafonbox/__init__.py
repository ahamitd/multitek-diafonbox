"""The Multitek DiafonBox integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MultitekAPI
from .const import CONF_PHONE_ID, DOMAIN
from .coordinator import MultitekDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.LOCK,
    Platform.BINARY_SENSOR,
    Platform.CAMERA,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Multitek DiafonBox from a config entry."""
    email = entry.data[CONF_EMAIL]
    phone_id = entry.data[CONF_PHONE_ID]

    _LOGGER.info("Setting up Multitek DiafonBox integration for %s", email)

    session = async_get_clientsession(hass)
    api = MultitekAPI(
        email=email,
        password="",  # Not needed for invited users
        phone_id=phone_id,
        session=session,
    )


    # Test login
    if not await api.login():
        _LOGGER.error("Failed to authenticate with Multitek API")
        return False

    _LOGGER.info("Authentication successful")

    # Create coordinator
    coordinator = MultitekDataUpdateCoordinator(hass, api)

    # Fetch initial data
    _LOGGER.info("Fetching initial data...")
    await coordinator.async_config_entry_first_refresh()
    
    # Log data availability
    if coordinator.data:
        locations = coordinator.data.get("locations", [])
        _LOGGER.info(
            "Initial data loaded - Locations: %d, Coordinator data keys: %s",
            len(locations),
            list(coordinator.data.keys()),
        )
    else:
        _LOGGER.error("Coordinator data is empty!")
    
    # Setup Pushy push notifications (optional, falls back to polling)
    await coordinator.async_setup_pushy()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    _LOGGER.info("Forwarding setup to platforms...")
    
    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Platform setup complete")
    
    # Register shutdown handler
    async def async_shutdown(event):
        """Handle shutdown."""
        await coordinator.async_shutdown()
    
    entry.async_on_unload(
        hass.bus.async_listen_once("homeassistant_stop", async_shutdown)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Shutdown coordinator
    coordinator = hass.data[DOMAIN].get(entry.entry_id)
    if coordinator:
        await coordinator.async_shutdown()
    
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

