"""
Authentication handlers - Typing ONLY for email and token
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH
from utils.validators import validate_email

EMAIL, TOKEN = range(2)

def get_user_by_email_case_insensitive(email):
    """Find user with case-insensitive email search"""
    try:
        email_lower = email.lower()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email_lower,))
        user = c.fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def link_telegram_id(user_id, telegram_id):
    """Link Telegram ID to user account"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE users SET telegram_id = ? WHERE id = ?', (telegram_id, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Link Error: {e}")
        return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start - typing allowed for email"""
    context.user_data.clear()
    await update.message.reply_text(
        "📧 **BRANVEE GOLD SIGNAL** 📧\n\nPlease enter your registered email address:",
        parse_mode='Markdown'
    )
    return EMAIL

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle email input - typing allowed"""
    email_input = update.message.text.strip()
    telegram_id = update.effective_user.id
    
    if not validate_email(email_input):
        await update.message.reply_text("❌ Invalid email format. Try again:")
        return EMAIL
    
    user = get_user_by_email_case_insensitive(email_input)
    
    if not user:
        await update.message.reply_text(
            f"❌ Email not registered.\n\nPlease contact admin."
        )
        return EMAIL
    
    # Check if suspended
    if user['is_suspended']:
        await update.message.reply_text("❌ Account suspended. Contact admin.")
        return EMAIL
    
    # Check if token expired
    now = datetime.now().isoformat()
    if user['expires_at'] < now:
        await update.message.reply_text("⚠️ Token expired. Contact admin.")
        return EMAIL
    
    # Check Telegram ID locking
    if user['telegram_id'] and user['telegram_id'] != telegram_id:
        await update.message.reply_text(
            "❌ This account is already linked to another Telegram user.\n\n"
            "Contact admin if this is a mistake."
        )
        return EMAIL
    
    context.user_data['auth_user'] = {
        'id': user['id'],
        'email': user['email'],
        'token': user['token'],
        'expires_at': user['expires_at'],
        'telegram_id': user['telegram_id']
    }
    context.user_data['telegram_id'] = telegram_id
    
    await update.message.reply_text(
        f"✅ Email found: {user['email']}\n\nNow enter your access token:"
    )
    return TOKEN

async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle token input - typing allowed (LAST TIME)"""
    token = update.message.text.strip().upper()
    user = context.user_data.get('auth_user')
    telegram_id = context.user_data.get('telegram_id')
    
    if not user:
        await update.message.reply_text("❌ Session expired. Please /start again.")
        return ConversationHandler.END
    
    if user['token'] != token:
        await update.message.reply_text("❌ Invalid token. Try again:")
        return TOKEN
    
    # If this is first login (telegram_id is NULL), link it
    if not user['telegram_id']:
        link_telegram_id(user['id'], telegram_id)
        user['telegram_id'] = telegram_id
    
    context.user_data['user_id'] = user['id']
    context.user_data['email'] = user['email']
    context.user_data['expires_at'] = user['expires_at']
    context.user_data['strategy'] = 'SCALPING'
    
    expiry = datetime.fromisoformat(user['expires_at'])
    days_left = (expiry - datetime.now()).days
    
    await update.message.reply_text(
        f"✅ **Login Successful!**\n\n"
        f"📧 Email: {user['email']}\n"
        f"📅 Expires: {user['expires_at'][:10]} ({days_left} days)\n"
        f"🔒 Account locked to this Telegram account.",
        parse_mode='Markdown'
    )
    
    # NO MORE TYPING AFTER THIS - ONLY BUTTONS
    await show_main_menu(update, context)
    return ConversationHandler.END

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show menu with GET SIGNAL at BOTTOM - NO TYPING ALLOWED"""
    
    # Create message that pushes button to bottom
    message = (
        "\n\n\n\n\n\n\n\n\n\n\n\n\n\n"  # 14 empty lines
        "⚡⚡⚡ **TAP BELOW FOR SIGNAL** ⚡⚡⚡\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔄 CHANGE STRATEGY", callback_data='menu_strategy')],
        [InlineKeyboardButton("ℹ️ ACCOUNT INFO", callback_data='menu_account')],
        [InlineKeyboardButton("⚡⚡⚡ GET SIGNAL ⚡⚡⚡", callback_data='get_signal')]
    ]
    
    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel authentication"""
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END
