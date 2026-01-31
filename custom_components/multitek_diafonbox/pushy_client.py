"""Pushy.me Push Notification Client for Multitek DiafonBox."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

import aiohttp

_LOGGER = logging.getLogger(__name__)

PUSHY_API_BASE = "https://api.pushy.me"


class PushyClient:
    """Client for Pushy.me push notifications."""

    def __init__(
        self,
        token: str,
        auth: str,
        session: aiohttp.ClientSession,
        callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        """Initialize Pushy client.
        
        Args:
            token: Device token from getAccount response
            auth: Pushy auth key
            session: aiohttp session
            callback: Callback function for incoming notifications
        """
        self.token = token
        self.auth = auth
        self.session = session
        self.callback = callback
        self._connected = False
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._listen_task: asyncio.Task | None = None

    async def authenticate(self) -> bool:
        """Authenticate device with Pushy."""
        try:
            url = f"{PUSHY_API_BASE}/devices/auth"
            data = {
                "auth": self.auth,
                "token": self.token,
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        _LOGGER.info("Pushy authentication successful")
                        return True
                    
                _LOGGER.error("Pushy authentication failed: %s", await response.text())
                return False
                
        except Exception as err:
            _LOGGER.error("Pushy authentication error: %s", err)
            return False

    async def subscribe(self, topics: list[str]) -> bool:
        """Subscribe to topics.
        
        Args:
            topics: List of topic names to subscribe to
        """
        try:
            url = f"{PUSHY_API_BASE}/devices/subscribe"
            data = {
                "token": self.token,
                "auth": self.auth,
                "topics": topics,
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        _LOGGER.info("Subscribed to topics: %s", topics)
                        return True
                    
                _LOGGER.error("Topic subscription failed: %s", await response.text())
                return False
                
        except Exception as err:
            _LOGGER.error("Topic subscription error: %s", err)
            return False

    async def unsubscribe(self, topics: list[str]) -> bool:
        """Unsubscribe from topics.
        
        Args:
            topics: List of topic names to unsubscribe from
        """
        try:
            url = f"{PUSHY_API_BASE}/devices/unsubscribe"
            data = {
                "token": self.token,
                "auth": self.auth,
                "topics": topics,
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        _LOGGER.info("Unsubscribed from topics: %s", topics)
                        return True
                    
                _LOGGER.error("Topic unsubscription failed: %s", await response.text())
                return False
                
        except Exception as err:
            _LOGGER.error("Topic unsubscription error: %s", err)
            return False

    async def connect(self, topics: list[str]) -> bool:
        """Connect to Pushy and subscribe to topics.
        
        Args:
            topics: List of topics to subscribe to
        """
        # First authenticate
        if not await self.authenticate():
            return False
        
        # Then subscribe to topics
        if not await self.subscribe(topics):
            return False
        
        self._connected = True
        
        # Start listening task
        # Note: Pushy.me uses HTTP long-polling or WebSocket
        # For now, we'll use polling as fallback
        # TODO: Implement WebSocket or long-polling listener
        
        return True

    async def disconnect(self) -> None:
        """Disconnect from Pushy."""
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        
        if self._ws:
            await self._ws.close()
        
        self._connected = False
        _LOGGER.info("Pushy client disconnected")

    @property
    def is_connected(self) -> bool:
        """Return if client is connected."""
        return self._connected
