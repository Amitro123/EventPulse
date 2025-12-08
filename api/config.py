"""API configuration module."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Settings
API_VERSION = "1.0.0"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Ticketmaster API
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY", "")
TICKETMASTER_BASE_URL = "https://app.ticketmaster.com/discovery/v2"

# Booking.com Affiliate
BOOKING_AFFILIATE_ID = os.getenv("BOOKING_AFFILIATE_ID", "TEST_AID")
BOOKING_BASE_URL = "https://www.booking.com/searchresults.html"

# Default search parameters
DEFAULT_COUNTRY_CODE = "IL"
DEFAULT_CATEGORY = "music"

