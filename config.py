"""
Admin Bot Configuration - Railway Version
"""
import os

# Telegram Bot Token (from environment or hardcoded)
BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', "YOUR_ADMIN_BOT_TOKEN")

# Admin Telegram ID (from environment or hardcoded)
ADMIN_ID = int(os.environ.get('ADMIN_ID', 6980711942))

# Database path
DB_PATH = "data/branvee.db"

# Token settings
TOKEN_PREFIX = "BRANVEE"
TOKEN_LENGTH = 12

# Duration options
DURATION_OPTIONS = {
    "1 Day": 1,
    "7 Days": 7,
    "15 Days": 15,
    "30 Days": 30,
    "60 Days": 60,
    "90 Days": 90,
    "1 Year": 365
}

# Messages
WELCOME_MSG = """
🔷 **BRANVEE GOLD ADMIN** 🔷

Welcome to the Admin Panel. Select an option below:
"""
