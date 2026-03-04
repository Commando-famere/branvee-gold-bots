"""
Users submenu keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_users_menu():
    """Get users management menu"""
    keyboard = [
        [InlineKeyboardButton("➕ Add User", callback_data='users_add')],
        [InlineKeyboardButton("✅ Active Users", callback_data='users_active')],
        [InlineKeyboardButton("❌ Expired Users", callback_data='users_expired')],
        [InlineKeyboardButton("🔙 Back", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_action_menu(user_id, email):
    """Get actions for a specific user"""
    keyboard = [
        [InlineKeyboardButton("🔄 Renew", callback_data=f'renew_{user_id}')],
        [InlineKeyboardButton("⏸️ Suspend", callback_data=f'suspend_{user_id}')],
        [InlineKeyboardButton("▶️ Activate", callback_data=f'activate_{user_id}')],
        [InlineKeyboardButton("🔑 View Token", callback_data=f'token_{user_id}')],
        [InlineKeyboardButton("📝 Edit Notes", callback_data=f'notes_{user_id}')],
        [InlineKeyboardButton("❌ Delete", callback_data=f'delete_{user_id}')],
        [InlineKeyboardButton("🔙 Back", callback_data='users_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_list_keyboard(users, action='select'):
    """Get keyboard with list of users"""
    keyboard = []
    for user in users[:10]:  # Limit to 10 users per page
        btn_text = f"{user['email'][:20]}..." if len(user['email']) > 20 else user['email']
        keyboard.append([InlineKeyboardButton(
            btn_text,
            callback_data=f"{action}_{user['id']}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='menu_users')])
    return InlineKeyboardMarkup(keyboard)
