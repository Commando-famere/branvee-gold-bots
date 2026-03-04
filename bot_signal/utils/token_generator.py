"""
Generate unique tokens for users
"""
import random
import string
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import TOKEN_PREFIX, TOKEN_LENGTH
except ImportError:
    # Default values if config not found
    TOKEN_PREFIX = "BRANVEE"
    TOKEN_LENGTH = 12

from database import get_user_by_token

def generate_token():
    """Generate a unique token"""
    while True:
        chars = string.ascii_uppercase + string.digits
        random_part = ''.join(random.choices(chars, k=TOKEN_LENGTH))
        
        if len(random_part) >= 8:
            token = f"{TOKEN_PREFIX}-{random_part[:4]}-{random_part[4:8]}"
        else:
            token = f"{TOKEN_PREFIX}-{random_part}"
        
        if not get_user_by_token(token):
            return token

def format_token_for_display(token):
    """Format token nicely for display"""
    return f"`{token}`"
