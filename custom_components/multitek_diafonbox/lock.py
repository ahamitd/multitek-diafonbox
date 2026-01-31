"""Lock platform for Multitek DiafonBox."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_DEVICE_MAC,
    ATTR_DEVICE_SIP,
    ATTR_LOCATION_ID,
    ATTR_LOCATION_NAME,
    DOMAIN,
    EVENT_DOOR_OPENED,
)
from .coordinator import MultitekDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Multitek lock entities."""
    coordinator: MultitekDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    
    locations = coordinator.data.get("locations", [])
    _LOGGER.info("Setting up lock entities for %d locations", len(locations))
    
    # Create a lock entity for each location
    for location in locations:
        location_id = location.get("location_id")
        location_name = location.get("location_name")
        devices = location.get("location_devices", [])
        
        _LOGGER.debug(
            "Location: %s (%s) - Devices: %d",
            location_name,
            location_id,
            len(devices),
        )
        
        if devices:
            device = devices[0]  # Use first device
            _LOGGER.info(
                "Creating lock entity: %s (SIP: %s)",
                location_name,
                device.get("sip"),
            )
            entities.append(
                MultitekLock(
                    coordinator,
                    location_id,
                    location_name,
                    device,
                )
            )

    _LOGGER.info("Adding %d lock entities", len(entities))
    async_add_entities(entities)


class MultitekLock(CoordinatorEntity, LockEntity):
    """Representation of a Multitek door lock."""

    def __init__(
        self,
        coordinator: MultitekDataUpdateCoordinator,
        location_id: str,
        location_name: str,
        device: dict[str, Any],
    ) -> None:
        """Initialize the lock."""
        super().__init__(coordinator)
        
        self._location_id = location_id
        self._location_name = location_name
        self._device = device
        self._attr_name = f"{location_name} Kapı"
        self._attr_unique_id = f"{DOMAIN}_{location_id}_lock"
        
        # Device info for grouping
        self._attr_device_info = {
            "identifiers": {(DOMAIN, location_id)},
            "name": location_name,
            "manufacturer": "Multitek",
            "model": "DiafonBox",
            "sw_version": device.get("version", "1.0"),
        }

    @property
    def is_locked(self) -> bool:
        """Return true if lock is locked."""
        # Door is always locked (can only be unlocked momentarily)
        return True

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_LOCATION_ID: self._location_id,
            ATTR_LOCATION_NAME: self._location_name,
            ATTR_DEVICE_MAC: self._device.get("mac"),
            ATTR_DEVICE_SIP: self._device.get("sip"),
        }

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the door."""
        device_sip = self._device.get("sip")
        
        try:
            success = await self.coordinator.api.open_door(
                device_sip=device_sip,
                location_id=self._location_id,
            )
            
            if success:
                _LOGGER.info("Door opened: %s", self._location_name)
                
                # Fire event
                self.hass.bus.fire(
                    EVENT_DOOR_OPENED,
                    {
                        ATTR_LOCATION_ID: self._location_id,
                        ATTR_LOCATION_NAME: self._location_name,
                        ATTR_DEVICE_SIP: device_sip,
                    },
                )
            else:
                _LOGGER.error("Failed to open door: %s", self._location_name)
                
        except Exception as err:
            _LOGGER.error("Error opening door: %s", err)

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the door (not supported)."""
        # Door locks automatically, no action needed
        _LOGGER.debug("Lock action not supported (door auto-locks)")
