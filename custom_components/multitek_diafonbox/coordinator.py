"""Data update coordinator for Multitek DiafonBox."""
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MultitekAPI, MultitekAPIError
from .const import (
    CALL_STATE_MISSED,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EVENT_DOORBELL_PRESSED,
)

_LOGGER = logging.getLogger(__name__)


class MultitekDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Multitek data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: MultitekAPI,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api
        self._last_call_ids: set[str] = set()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            # Get locations and devices
            locations = await self.api.get_locations()
            
            # Get call records
            call_records = await self.api.get_call_records()
            
            # Detect new doorbell rings
            self._detect_doorbell_events(call_records)
            
            # Get account info
            account = await self.api.get_account()

            return {
                "locations": locations,
                "call_records": call_records,
                "account": account,
            }

        except MultitekAPIError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def _detect_doorbell_events(self, call_records: list[dict[str, Any]]) -> None:
        """Detect new doorbell rings and fire events."""
        for call in call_records:
            call_id = call.get("call_id")
            call_state = call.get("call_state")
            
            # Only process missed calls (doorbell rings)
            if call_state != CALL_STATE_MISSED:
                continue
            
            # Skip if we've already processed this call
            if call_id in self._last_call_ids:
                continue
            
            # Add to processed calls
            self._last_call_ids.add(call_id)
            
            # Fire doorbell event
            event_data = {
                "call_id": call_id,
                "call_from": call.get("call_from"),
                "call_to": call.get("call_to"),
                "location_id": call.get("location_id"),
                "timestamp": call.get("date"),
                "snapshot_path": call.get("path"),
            }
            
            self.hass.bus.fire(EVENT_DOORBELL_PRESSED, event_data)
            
            _LOGGER.info(
                "Doorbell pressed: from=%s to=%s",
                call.get("call_from"),
                call.get("call_to"),
            )

    def get_device_by_location(self, location_id: str) -> dict[str, Any] | None:
        """Get device for a location."""
        if not self.data:
            return None
        
        for location in self.data.get("locations", []):
            if location.get("location_id") == location_id:
                devices = location.get("location_devices", [])
                if devices:
                    return devices[0]  # Return first device
        
        return None

    def get_recent_calls(
        self,
        call_to: str | None = None,
        minutes: int = 1,
    ) -> list[dict[str, Any]]:
        """Get recent calls within specified minutes."""
        if not self.data:
            return []
        
        import time
        current_time = int(time.time() * 1000)
        cutoff_time = current_time - (minutes * 60 * 1000)
        
        recent_calls = []
        for call in self.data.get("call_records", []):
            call_date = int(call.get("date", 0))
            
            if call_date < cutoff_time:
                continue
            
            if call_to and call.get("call_to") != call_to:
                continue
            
            recent_calls.append(call)
        
        return recent_calls

    def get_today_call_count(self) -> int:
        """Get number of calls today."""
        if not self.data:
            return 0
        
        import time
        from datetime import datetime
        
        today_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ).timestamp() * 1000
        
        count = 0
        for call in self.data.get("call_records", []):
            call_date = int(call.get("date", 0))
            if call_date >= today_start:
                count += 1
        
        return count
