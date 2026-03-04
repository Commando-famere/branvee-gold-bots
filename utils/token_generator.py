"""
Generate unique tokens for users
"""
import random
import string
from config import TOKEN_PREFIX, TOKEN_LENGTH
from database import get_user_by_token

def generate_token():
    """Generate a unique token"""
    while True:
        # Generate random string
        chars = string.ascii_uppercase + string.digits
        random_part = ''.join(random.choices(chars, k=TOKEN_LENGTH))
        
        # Format: BRANVEE-XXXX-XXXX
        if len(random_part) >= 8:
            token = f"{TOKEN_PREFIX}-{random_part[:4]}-{random_part[4:8]}"
        else:
            token = f"{TOKEN_PREFIX}-{random_part}"
        
        # Check if unique
        if not get_user_by_token(token):
            return token

def format_token_for_display(token):
    """Format token nicely for display"""
    return f"`{token}`"  # Monospace for easy copying
