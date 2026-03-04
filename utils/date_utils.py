"""
Date utilities for expiry calculations
"""
from datetime import datetime, timedelta

def calculate_expiry(days):
    """Calculate expiry date from now plus days"""
    return datetime.now() + timedelta(days=days)

def format_date(date):
    """Format date for display"""
    return date.strftime("%Y-%m-%d %H:%M")

def days_until(expiry_date):
    """Calculate days until expiry"""
    if isinstance(expiry_date, str):
        expiry_date = datetime.fromisoformat(expiry_date)
    delta = expiry_date - datetime.now()
    return delta.days

def get_duration_options():
    """Get duration options for menu"""
    return {
        "1 Day": 1,
        "7 Days": 7,
        "15 Days": 15,
        "30 Days": 30,
        "60 Days": 60,
        "90 Days": 90,
        "1 Year": 365
    }
