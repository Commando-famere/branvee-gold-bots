"""
Signal Bot Configuration - Railway Version
"""
import os

# Telegram Bot Token (from environment or hardcoded)
BOT_TOKEN = os.environ.get('SIGNAL_BOT_TOKEN', "8741454658:AAGlyxcVQMH7tKd13OmM2Y2VGa9ex9LbPfo")

# Database path
DB_PATH = "data/branvee.db"

# Railway API URL
API_URL = os.environ.get('RAILWAY_API_URL', "https://branvee-gold-system-production.up.railway.app")

# Token settings
TOKEN_PREFIX = "BRANVEE"
TOKEN_LENGTH = 12

# Messages
WELCOME_MSG = """
🔐 **BRANVEE GOLD SIGNAL** 🔐

Please enter your registered email address to continue.
"""

INVALID_TOKEN_MSG = """
⚠️ **Invalid Token**

The token you entered is not valid or has expired.
Please check and try again.
"""

EXPIRED_TOKEN_MSG = """
⚠️ **Token Expired**

Your access token has expired.
Please contact admin for renewal.

Send /start to try again.
"""

WELCOME_BACK_MSG = """
🏆 **BRANVEE GOLD SIGNAL** 🏆

Welcome back, {email}
Token expires: {expiry}
Days left: {days_left}
"""
