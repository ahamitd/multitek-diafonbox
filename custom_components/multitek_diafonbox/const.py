"""Constants for the Multitek DiafonBox integration."""
from typing import Final

DOMAIN: Final = "multitek_diafonbox"

# API Configuration
API_BASE_URL: Final = "https://cloud.multitek.com.tr:8096/multitek_service/root"
API_USERNAME: Final = "multitek"
API_PASSWORD: Final = "Mlt.3838!"

# API Endpoints
ENDPOINT_LOGIN: Final = "userAccountControl"
ENDPOINT_GET_LOCATIONS: Final = "getUserLocations"
ENDPOINT_GET_CALLS: Final = "getCallAllRecords"
ENDPOINT_ADD_CALL: Final = "addCall"
ENDPOINT_GET_ACCOUNT: Final = "getAccount"
ENDPOINT_RESUME_APP: Final = "resumeApp"
ENDPOINT_ASK_CURRENT_CALL: Final = "askCurrentCall"
ENDPOINT_SET_CALL_DURATION: Final = "setCallDuration"

# Configuration
CONF_EMAIL: Final = "email"
CONF_PASSWORD: Final = "password"
CONF_PHONE_ID: Final = "phone_id"

# Defaults
DEFAULT_SCAN_INTERVAL: Final = 30  # seconds
DEFAULT_PHONE_ID: Final = "home-assistant-integration"

# Device Types
DEVICE_TYPE_GATEWAY_DOOR: Final = "DEVICE_TYPE_GATEWAY_DOOR"

# Call States
CALL_STATE_MISSED: Final = "Missed"
CALL_STATE_OUTGOING: Final = "Outgoing"

# Platforms
PLATFORMS: Final = ["lock", "binary_sensor", "camera", "sensor"]

# Events
EVENT_DOORBELL_PRESSED: Final = f"{DOMAIN}_doorbell_pressed"
EVENT_DOOR_OPENED: Final = f"{DOMAIN}_door_opened"

# Attributes
ATTR_LOCATION_ID: Final = "location_id"
ATTR_LOCATION_NAME: Final = "location_name"
ATTR_DEVICE_MAC: Final = "device_mac"
ATTR_DEVICE_SIP: Final = "device_sip"
ATTR_LAST_RING_TIME: Final = "last_ring_time"
ATTR_SNAPSHOT_URL: Final = "snapshot_url"
ATTR_CALL_FROM: Final = "call_from"
ATTR_CALL_TO: Final = "call_to"
ATTR_CALL_DURATION: Final = "call_duration"
ATTR_TODAY_COUNT: Final = "today_count"
