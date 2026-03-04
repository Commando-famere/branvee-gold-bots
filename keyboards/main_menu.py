"""
Main menu keyboard
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    """Get main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("👥 Users", callback_data='menu_users')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='menu_settings')],
        [InlineKeyboardButton("📊 Analytics", callback_data='menu_analytics')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='menu_help')]
    ]
    return InlineKeyboardMarkup(keyboard)
