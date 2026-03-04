"""
Input validators
"""
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    """Sanitize user input"""
    # Remove any potentially harmful characters
    return text.strip()

def validate_token(token):
    """Validate token format"""
    pattern = r'^BRANVEE-[A-Z0-9]{4}-[A-Z0-9]{4}$'
    return re.match(pattern, token) is not None
