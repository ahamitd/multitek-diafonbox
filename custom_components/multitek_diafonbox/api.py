"""API Client for Multitek DiafonBox."""
import asyncio
import hashlib
import logging
from typing import Any

import aiohttp
from aiohttp import BasicAuth

from .const import (
    API_BASE_URL,
    API_PASSWORD,
    API_USERNAME,
    ENDPOINT_ADD_CALL,
    ENDPOINT_GET_ACCOUNT,
    ENDPOINT_GET_CALLS,
    ENDPOINT_GET_LOCATIONS,
    ENDPOINT_LOGIN,
    ENDPOINT_RESUME_APP,
)

_LOGGER = logging.getLogger(__name__)


class MultitekAPIError(Exception):
    """Exception for Multitek API errors."""


class MultitekAuthError(MultitekAPIError):
    """Exception for authentication errors."""


class MultitekAPI:
    """API client for Multitek DiafonBox."""

    def __init__(
        self,
        email: str,
        password: str,
        phone_id: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client."""
        self.email = email
        self.password_hash = hashlib.md5(password.encode()).hexdigest().upper()
        self.phone_id = phone_id
        self.session = session
        self.auth = BasicAuth(API_USERNAME, API_PASSWORD)
        self._user_sip: str | None = None

    async def _request(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Make API request."""
        url = f"{API_BASE_URL}/{endpoint}"
        
        if data is None:
            data = {}
        
        # Add common fields
        data.setdefault("email", self.email)
        data.setdefault("phone_id", self.phone_id)
        data.setdefault("language", "tr-TR")

        try:
            async with self.session.post(
                url,
                json=data,
                auth=self.auth,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 401:
                    raise MultitekAuthError("Authentication failed")
                
                if response.status != 200:
                    raise MultitekAPIError(
                        f"API request failed with status {response.status}"
                    )

                content_type = response.headers.get("Content-Type", "")
                
                if "application/json" in content_type:
                    return await response.json()
                else:
                    # Some endpoints return plain text (e.g., "1")
                    text = await response.text()
                    return text

        except aiohttp.ClientError as err:
            raise MultitekAPIError(f"API request failed: {err}") from err

    async def login(self) -> bool:
        """Test login credentials."""
        try:
            data = {
                "email": self.email,
                "password": self.password_hash,
                "phone_id": self.phone_id,
                "phone_info": "Home Assistant",
                "pushy_token": "",
                "push_kit_token": "",
                "language": "tr-TR",
            }
            
            result = await self._request(ENDPOINT_LOGIN, data)
            
            # Response is "1" for success
            if result == "1" or result == 1:
                # Get user account info to retrieve SIP number
                account = await self.get_account()
                self._user_sip = account.get("sip")
                return True
            
            return False

        except MultitekAuthError:
            return False

    async def get_account(self) -> dict[str, Any]:
        """Get user account information."""
        return await self._request(ENDPOINT_GET_ACCOUNT)

    async def get_locations(self) -> list[dict[str, Any]]:
        """Get user locations and devices."""
        result = await self._request(ENDPOINT_GET_LOCATIONS)
        return result if isinstance(result, list) else []

    async def get_call_records(self) -> list[dict[str, Any]]:
        """Get call history records."""
        result = await self._request(ENDPOINT_GET_CALLS)
        return result if isinstance(result, list) else []

    async def open_door(self, device_sip: str, location_id: str) -> bool:
        """Open door by initiating a call."""
        if not self._user_sip:
            account = await self.get_account()
            self._user_sip = account.get("sip")

        if not self._user_sip:
            raise MultitekAPIError("User SIP number not available")

        import time
        import uuid

        call_id = uuid.uuid4().hex[:30]
        
        data = {
            "call_model": {
                "call_id": call_id,
                "call_from": self._user_sip,
                "call_to": device_sip,
                "date": str(int(time.time() * 1000)),
                "call_state": "Outgoing",
                "data": "New call",
                "path": "",
                "location_id": location_id,
                "duration": "0",
                "notification_id": 0,
                "extra_data": "",
                "call_type": "DEVICE_TYPE_GATEWAY_DOOR",
                "selected": False,
                "isRead": False,
            }
        }

        result = await self._request(ENDPOINT_ADD_CALL, data)
        
        # Response is "1" for success
        return result == "1" or result == 1

    async def resume_app(self) -> dict[str, Any]:
        """Resume app session."""
        data = {
            "phoneInfo": "Home Assistant",
            "phoneOS": "Linux",
            "appVersion": "Home Assistant Integration v1.0.0",
            "locationLat": -1,
            "locationLong": -1,
            "locationCountry": "",
            "locationCity": "",
            "locationDistrict": "",
            "locationFindType": "",
            "locationLastUpdateTime": str(int(asyncio.get_event_loop().time() * 1000)),
            "pushyToken": "",
            "pushKitToken": "",
        }
        
        return await self._request(ENDPOINT_RESUME_APP, data)
