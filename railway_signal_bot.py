"""
BRANVEE GOLD SIGNAL BOT - STANDALONE RAILWAY VERSION
All code in one file for easy deployment
"""

import logging
import sqlite3
import os
import sys
from datetime import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)

# ============================================
# CONFIGURATION
# ============================================

# Get tokens from environment variables
BOT_TOKEN = os.environ.get('SIGNAL_BOT_TOKEN', '8741454658:AAGlyxcVQMH7tKd13OmM2Y2VGa9ex9LbPfo')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 6980711942))
API_URL = os.environ.get('RAILWAY_API_URL', 'https://branvee-gold-system-production.up.railway.app')

# Database path
DB_PATH = 'data/branvee.db'

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# ============================================
# DATABASE FUNCTIONS
# ============================================

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        token TEXT UNIQUE NOT NULL,
        telegram_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        is_suspended BOOLEAN DEFAULT 0
    )''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def get_user_by_email(email):
    """Get user by email (case insensitive)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE LOWER(email) = LOWER(?)', (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def link_telegram_id(user_id, telegram_id):
    """Link Telegram ID to user"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET telegram_id = ? WHERE id = ?', (telegram_id, user_id))
    conn.commit()
    conn.close()
    return True

# ============================================
# VALIDATION FUNCTIONS
# ============================================

def validate_email(email):
    """Simple email validation"""
    return '@' in email and '.' in email

# ============================================
# CONVERSATION STATES
# ============================================

EMAIL, TOKEN = range(2)

# ============================================
# AUTH HANDLERS
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - ask for email"""
    context.user_data.clear()
    await update.message.reply_text(
        "📧 **BRANVEE GOLD SIGNAL** 📧\n\nPlease enter your registered email address:",
        parse_mode='Markdown'
    )
    return EMAIL

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle email input"""
    email = update.message.text.strip()
    telegram_id = update.effective_user.id
    
    if not validate_email(email):
        await update.message.reply_text("❌ Invalid email format. Try again:")
        return EMAIL
    
    user = get_user_by_email(email)
    
    if not user:
        await update.message.reply_text("❌ Email not registered. Contact admin.")
        return EMAIL
    
    if user['is_suspended']:
        await update.message.reply_text("❌ Account suspended. Contact admin.")
        return EMAIL
    
    now = datetime.now().isoformat()
    if user['expires_at'] < now:
        await update.message.reply_text("⚠️ Token expired. Contact admin.")
        return EMAIL
    
    if user['telegram_id'] and user['telegram_id'] != telegram_id:
        await update.message.reply_text(
            "❌ This account is linked to another Telegram user."
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
    """Handle token input"""
    token = update.message.text.strip().upper()
    user = context.user_data.get('auth_user')
    telegram_id = context.user_data.get('telegram_id')
    
    if not user:
        await update.message.reply_text("❌ Session expired. Please /start again.")
        return ConversationHandler.END
    
    if user['token'] != token:
        await update.message.reply_text("❌ Invalid token. Try again:")
        return TOKEN
    
    if not user['telegram_id']:
        link_telegram_id(user['id'], telegram_id)
    
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
        f"🔒 Account locked.",
        parse_mode='Markdown'
    )
    
    await show_main_menu(update, context)
    return ConversationHandler.END

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu with GET SIGNAL at bottom"""
    message = "\n\n\n\n\n\n\n\n⚡⚡⚡ **GET SIGNAL** ⚡⚡⚡\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Change Strategy", callback_data='menu_strategy')],
        [InlineKeyboardButton("ℹ️ Account Info", callback_data='menu_account')],
        [InlineKeyboardButton("⚡⚡⚡ GET SIGNAL ⚡⚡⚡", callback_data='get_signal')]
    ]
    
    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel"""
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

# ============================================
# MENU HANDLERS
# ============================================

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'menu_main':
        await show_main_menu_callback(query, context)
    elif data == 'menu_strategy':
        await show_strategy_menu(query)
    elif data == 'menu_account':
        await show_account_info(query, context)

async def show_main_menu_callback(query, context):
    """Show main menu from callback"""
    message = "\n\n\n\n\n\n\n\n⚡⚡⚡ **GET SIGNAL** ⚡⚡⚡\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 Change Strategy", callback_data='menu_strategy')],
        [InlineKeyboardButton("ℹ️ Account Info", callback_data='menu_account')],
        [InlineKeyboardButton("⚡⚡⚡ GET SIGNAL ⚡⚡⚡", callback_data='get_signal')]
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_strategy_menu(query):
    """Show strategy menu"""
    keyboard = [
        [InlineKeyboardButton("📊 Scalping", callback_data='strategy_scalping')],
        [InlineKeyboardButton("📈 Trend", callback_data='strategy_trend')],
        [InlineKeyboardButton("📉 Pressure", callback_data='strategy_pressure')],
        [InlineKeyboardButton("📊 Fractals", callback_data='strategy_fractals')],
        [InlineKeyboardButton("🔙 Back", callback_data='menu_main')]
    ]
    
    await query.edit_message_text(
        "📊 **Select Strategy**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_account_info(query, context):
    """Show account info"""
    user_id = context.user_data.get('user_id')
    user = get_user_by_id(user_id)
    
    if not user:
        await query.edit_message_text("Error retrieving account.")
        return
    
    expiry = datetime.fromisoformat(user['expires_at'])
    days_left = (expiry - datetime.now()).days
    
    message = (
        f"📧 **Email:** {user['email']}\n"
        f"📅 **Expires:** {user['expires_at'][:10]} ({days_left} days)\n"
        f"🔒 **Linked:** {'Yes' if user['telegram_id'] else 'No'}"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_main')]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ============================================
# SIGNAL HANDLERS
# ============================================

async def signal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle get signal button"""
    query = update.callback_query
    await query.answer()
    
    if 'user_id' not in context.user_data:
        await query.edit_message_text("Session expired. Please /start again.")
        return
    
    try:
        response = requests.get(f"{API_URL}/api/signal", timeout=5)
        data = response.json()
        signal = data.get('signal', 'HOLD')
        
        if signal == 'BUY':
            emoji = "🟢" * 16 + "\n" + "🟢" * 16 + "\n" + "🟢" * 16
        elif signal == 'SELL':
            emoji = "🔴" * 16 + "\n" + "🔴" * 16 + "\n" + "🔴" * 16
        else:
            emoji = "⚪" * 16 + "\n" + "⚪" * 16 + "\n" + "⚪" * 16
        
        await query.message.reply_text(emoji)
        await show_main_menu_callback(query, context)
        
    except Exception as e:
        await query.message.reply_text(f"❌ Error")
        await show_main_menu_callback(query, context)

# ============================================
# STRATEGY HANDLERS
# ============================================

async def strategy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle strategy selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    strategies = {
        'strategy_scalping': 'SCALPING',
        'strategy_trend': 'TREND',
        'strategy_pressure': 'PRESSURE',
        'strategy_fractals': 'FRACTALS'
    }
    
    if data in strategies:
        context.user_data['strategy'] = strategies[data]
        await query.edit_message_text(
            f"✅ Strategy: {strategies[data]}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📊 GET SIGNAL", callback_data='get_signal')
            ]])
        )

# ============================================
# MAIN
# ============================================

def main():
    """Start the bot"""
    init_db()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)],
            TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_token)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    app.add_handler(conv_handler)
    
    app.add_handler(CallbackQueryHandler(menu_callback, pattern='^menu_'))
    app.add_handler(CallbackQueryHandler(signal_callback, pattern='^get_signal$'))
    app.add_handler(CallbackQueryHandler(strategy_callback, pattern='^strategy_'))
    
    print("\n" + "="*50)
    print("🤖 BRANVEE SIGNAL BOT - RAILWAY")
    print("="*50)
    print("✅ Bot is running...")
    print("="*50 + "\n")
    
    app.run_polling()

if __name__ == '__main__':
    main()
