"""
Menu handlers - NO TYPING ALLOWED, ONLY BUTTONS
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_user_by_id

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'menu_main':
        await show_main_menu(query, context)
    elif data == 'menu_strategy':
        await show_strategy_menu(query)
    elif data == 'menu_account':
        await show_account_info(query, context)

async def show_main_menu(query, context):
    """Show menu with GET SIGNAL at BOTTOM where typing area would be"""
    
    # Create a message that pushes the button to the bottom
    # The empty lines force the button to appear at the bottom
    message = (
        "\n\n\n\n\n\n\n\n\n\n\n\n"  # 12 empty lines
        "⚡⚡⚡ **READY FOR SIGNAL** ⚡⚡⚡\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("📊 CHANGE STRATEGY", callback_data='menu_strategy')],
        [InlineKeyboardButton("ℹ️ ACCOUNT INFO", callback_data='menu_account')],
        [InlineKeyboardButton("⚡⚡⚡ GET SIGNAL ⚡⚡⚡", callback_data='get_signal')]  # Large button at bottom
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_strategy_menu(query):
    """Strategy selection menu - all buttons, no typing"""
    keyboard = [
        [InlineKeyboardButton("📊 SCALPING", callback_data='strategy_scalping')],
        [InlineKeyboardButton("📈 TREND", callback_data='strategy_trend')],
        [InlineKeyboardButton("📉 PRESSURE", callback_data='strategy_pressure')],
        [InlineKeyboardButton("📊 FRACTALS", callback_data='strategy_fractals')],
        [InlineKeyboardButton("🔙 BACK TO MENU", callback_data='menu_main')]
    ]
    
    await query.edit_message_text(
        "📊 **SELECT STRATEGY**\n\nChoose your trading style:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_account_info(query, context):
    """Account info with back button only"""
    user_id = context.user_data.get('user_id')
    user = get_user_by_id(user_id)
    
    if not user:
        await query.edit_message_text("Error retrieving account.")
        return
    
    expiry = datetime.fromisoformat(user['expires_at'])
    days_left = (expiry - datetime.now()).days
    status = "🟢 ACTIVE" if not user['is_suspended'] else "🔴 SUSPENDED"
    
    message = (
        f"👤 **ACCOUNT INFO**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📧 **Email:** `{user['email']}`\n"
        f"📅 **Expires:** {user['expires_at'][:10]} ({days_left} days)\n"
        f"🔒 **Status:** {status}\n"
        f"🆔 **Telegram ID:** `{user['telegram_id'] or 'Not linked'}`\n"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 BACK TO MENU", callback_data='menu_main')]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def logout_user(query, context):
    """Logout and clear session"""
    context.user_data.clear()
    await query.edit_message_text(
        "👋 **Logged out**\n\nSend /start to login again.",
        parse_mode='Markdown'
    )
