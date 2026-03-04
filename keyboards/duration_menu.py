"""
Duration selection keyboard
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_duration_main_menu():
    """Get main duration type menu"""
    keyboard = [
        [InlineKeyboardButton("⏰ Hours", callback_data='dur_hours')],
        [InlineKeyboardButton("📅 Days", callback_data='dur_days')],
        [InlineKeyboardButton("📆 Weeks", callback_data='dur_weeks')],
        [InlineKeyboardButton("🗓️ Months", callback_data='dur_months')],
        [InlineKeyboardButton("📅 Years", callback_data='dur_years')],
        [InlineKeyboardButton("🔙 Back", callback_data='menu_users')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_days_menu():
    """Get days selection menu"""
    keyboard = [
        [InlineKeyboardButton("1 Day", callback_data='days_1'),
         InlineKeyboardButton("7 Days", callback_data='days_7')],
        [InlineKeyboardButton("15 Days", callback_data='days_15'),
         InlineKeyboardButton("30 Days", callback_data='days_30')],
        [InlineKeyboardButton("60 Days", callback_data='days_60'),
         InlineKeyboardButton("90 Days", callback_data='days_90')],
        [InlineKeyboardButton("✏️ Custom", callback_data='dur_custom')],
        [InlineKeyboardButton("🔙 Back", callback_data='dur_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_weeks_menu():
    """Get weeks selection menu"""
    keyboard = [
        [InlineKeyboardButton("1 Week", callback_data='weeks_1'),
         InlineKeyboardButton("2 Weeks", callback_data='weeks_2')],
        [InlineKeyboardButton("3 Weeks", callback_data='weeks_3'),
         InlineKeyboardButton("4 Weeks", callback_data='weeks_4')],
        [InlineKeyboardButton("✏️ Custom", callback_data='dur_custom')],
        [InlineKeyboardButton("🔙 Back", callback_data='dur_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_months_menu():
    """Get months selection menu"""
    keyboard = [
        [InlineKeyboardButton("1 Month", callback_data='months_1'),
         InlineKeyboardButton("3 Months", callback_data='months_3')],
        [InlineKeyboardButton("6 Months", callback_data='months_6'),
         InlineKeyboardButton("9 Months", callback_data='months_9')],
        [InlineKeyboardButton("12 Months", callback_data='months_12')],
        [InlineKeyboardButton("✏️ Custom", callback_data='dur_custom')],
        [InlineKeyboardButton("🔙 Back", callback_data='dur_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_years_menu():
    """Get years selection menu"""
    keyboard = [
        [InlineKeyboardButton("1 Year", callback_data='years_1'),
         InlineKeyboardButton("2 Years", callback_data='years_2')],
        [InlineKeyboardButton("3 Years", callback_data='years_3'),
         InlineKeyboardButton("5 Years", callback_data='years_5')],
        [InlineKeyboardButton("✏️ Custom", callback_data='dur_custom')],
        [InlineKeyboardButton("🔙 Back", callback_data='dur_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_hours_menu():
    """Get hours selection menu"""
    keyboard = [
        [InlineKeyboardButton("1 Hour", callback_data='hours_1'),
         InlineKeyboardButton("6 Hours", callback_data='hours_6')],
        [InlineKeyboardButton("12 Hours", callback_data='hours_12'),
         InlineKeyboardButton("24 Hours", callback_data='hours_24')],
        [InlineKeyboardButton("✏️ Custom", callback_data='dur_custom')],
        [InlineKeyboardButton("🔙 Back", callback_data='dur_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_menu():
    """Get confirmation menu"""
    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data='confirm_yes')],
        [InlineKeyboardButton("✏️ Edit", callback_data='confirm_edit')],
        [InlineKeyboardButton("🔙 Cancel", callback_data='users_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)
