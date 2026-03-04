"""
BRANVEE ADMIN BOT - STANDALONE RAILWAY VERSION
All code in one file for easy deployment
"""

import logging
import sqlite3
import os
import sys
from datetime import datetime, timedelta
import random
import string
import re
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

BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '8659878049:AAFosBtLo5ElKjH3w3pcfxvM19SOT-DwQ7I')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 6980711942))
DB_PATH = 'data/branvee.db'

os.makedirs('data', exist_ok=True)

# ============================================
# DATABASE FUNCTIONS
# ============================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        token TEXT UNIQUE NOT NULL,
        telegram_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        is_suspended BOOLEAN DEFAULT 0,
        created_by INTEGER
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS renewal_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        old_expiry TIMESTAMP,
        new_expiry TIMESTAMP,
        renewed_by INTEGER,
        renewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()
    print("✅ Admin DB initialized")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def add_user(email, token, expires_at, created_by):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (email, token, expires_at, created_by) VALUES (?, ?, ?, ?)',
                 (email, token, expires_at, created_by))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except Exception as e:
        conn.close()
        return None

def get_user_by_email(email):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE LOWER(email) = LOWER(?)', (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = c.fetchall()
    conn.close()
    return users

def get_active_users():
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('SELECT * FROM users WHERE expires_at > ? AND is_suspended = 0', (now,))
    users = c.fetchall()
    conn.close()
    return users

def get_expired_users():
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('SELECT * FROM users WHERE expires_at <= ?', (now,))
    users = c.fetchall()
    conn.close()
    return users

def renew_user(user_id, new_expiry, renewed_by):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT expires_at FROM users WHERE id = ?', (user_id,))
    old = c.fetchone()
    if not old:
        conn.close()
        return False
    
    old_expiry = old['expires_at']
    c.execute('UPDATE users SET expires_at = ? WHERE id = ?', (new_expiry, user_id))
    c.execute('INSERT INTO renewal_history (user_id, old_expiry, new_expiry, renewed_by) VALUES (?, ?, ?, ?)',
             (user_id, old_expiry, new_expiry, renewed_by))
    conn.commit()
    conn.close()
    return True

def suspend_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET is_suspended = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def activate_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET is_suspended = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def get_stats():
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()
    
    total = c.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    active = c.execute('SELECT COUNT(*) FROM users WHERE expires_at > ? AND is_suspended = 0', (now,)).fetchone()[0]
    expired = c.execute('SELECT COUNT(*) FROM users WHERE expires_at <= ?', (now,)).fetchone()[0]
    suspended = c.execute('SELECT COUNT(*) FROM users WHERE is_suspended = 1').fetchone()[0]
    
    conn.close()
    return {'total': total, 'active': active, 'expired': expired, 'suspended': suspended}

# ============================================
# UTILITY FUNCTIONS
# ============================================

def generate_token():
    chars = string.ascii_uppercase + string.digits
    part1 = ''.join(random.choices(chars, k=4))
    part2 = ''.join(random.choices(chars, k=4))
    return f"BRANVEE-{part1}-{part2}"

def format_token(token):
    return f"`{token}`"

def calculate_expiry(days):
    return datetime.now() + timedelta(days=days)

def days_until(expiry_date):
    if isinstance(expiry_date, str):
        expiry_date = datetime.fromisoformat(expiry_date)
    delta = expiry_date - datetime.now()
    return delta.days

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ============================================
# CONVERSATION STATES
# ============================================

EMAIL, DURATION = range(2)

# ============================================
# KEYBOARDS
# ============================================

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("👥 Users", callback_data='menu_users')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='menu_settings')],
        [InlineKeyboardButton("📊 Analytics", callback_data='menu_analytics')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_users_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Add User", callback_data='users_add')],
        [InlineKeyboardButton("✅ Active Users", callback_data='users_active')],
        [InlineKeyboardButton("❌ Expired Users", callback_data='users_expired')],
        [InlineKeyboardButton("🔙 Back", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_duration_menu():
    keyboard = [
        [InlineKeyboardButton("1 Day", callback_data='days_1'),
         InlineKeyboardButton("7 Days", callback_data='days_7')],
        [InlineKeyboardButton("15 Days", callback_data='days_15'),
         InlineKeyboardButton("30 Days", callback_data='days_30')],
        [InlineKeyboardButton("60 Days", callback_data='days_60'),
         InlineKeyboardButton("90 Days", callback_data='days_90')],
        [InlineKeyboardButton("✏️ Custom", callback_data='dur_custom')],
        [InlineKeyboardButton("🔙 Back", callback_data='users_add')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_menu():
    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data='confirm_yes')],
        [InlineKeyboardButton("✏️ Edit", callback_data='confirm_edit')],
        [InlineKeyboardButton("🔙 Cancel", callback_data='menu_users')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================
# HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized")
        return
    
    await update.message.reply_text(
        "🔷 **BRANVEE GOLD ADMIN** 🔷\n\nSelect an option:",
        reply_markup=get_main_menu(),
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await query.edit_message_text("⛔ Unauthorized")
        return
    
    data = query.data
    
    if data == 'menu_main':
        await query.edit_message_text(
            "🔷 **BRANVEE GOLD ADMIN** 🔷\n\nSelect an option:",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
    
    elif data == 'menu_users':
        await query.edit_message_text(
            "👥 **User Management**",
            reply_markup=get_users_menu(),
            parse_mode='Markdown'
        )
    
    elif data == 'users_add':
        await query.edit_message_text(
            "📧 Send user's email:",
            parse_mode='Markdown'
        )
        return EMAIL
    
    elif data == 'users_active':
        users = get_active_users()
        if not users:
            msg = "✅ No active users"
        else:
            msg = "✅ **Active Users**\n\n"
            for u in users:
                days = days_until(u['expires_at'])
                msg += f"• {u['email']} - {days} days left\n"
        
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='menu_users')
            ]]),
            parse_mode='Markdown'
        )
    
    elif data == 'users_expired':
        users = get_expired_users()
        if not users:
            msg = "❌ No expired users"
        else:
            msg = "❌ **Expired Users**\n\n"
            for u in users:
                msg += f"• {u['email']}\n"
        
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='menu_users')
            ]]),
            parse_mode='Markdown'
        )
    
    elif data == 'menu_analytics':
        stats = get_stats()
        msg = f"📊 **Analytics**\n\nTotal: {stats['total']}\nActive: {stats['active']}\nExpired: {stats['expired']}\nSuspended: {stats['suspended']}"
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='menu_main')
            ]]),
            parse_mode='Markdown'
        )
    
    elif data.startswith('days_'):
        days = int(data.split('_')[1])
        context.user_data['duration'] = days
        await show_confirmation(query, context)
    
    elif data == 'confirm_yes':
        await generate_and_save_token(query, context)
    
    elif data == 'menu_users':
        await query.edit_message_text(
            "👥 **User Management**",
            reply_markup=get_users_menu(),
            parse_mode='Markdown'
        )

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    
    if not validate_email(email):
        await update.message.reply_text("❌ Invalid email. Try again:")
        return EMAIL
    
    if get_user_by_email(email):
        await update.message.reply_text("❌ Email exists. Try another:")
        return EMAIL
    
    context.user_data['email'] = email
    
    await update.message.reply_text(
        "📅 Select duration:",
        reply_markup=get_duration_menu()
    )
    return ConversationHandler.END

async def show_confirmation(query, context):
    email = context.user_data.get('email')
    days = context.user_data.get('duration')
    expiry = calculate_expiry(days)
    
    msg = f"📧 Email: {email}\n📅 Days: {days}\n📆 Expires: {expiry.strftime('%Y-%m-%d')}\n\nConfirm?"
    await query.edit_message_text(
        msg,
        reply_markup=get_confirmation_menu()
    )

async def generate_and_save_token(query, context):
    email = context.user_data.get('email')
    days = context.user_data.get('duration', 30)
    expiry = calculate_expiry(days)
    token = generate_token()
    
    user_id = add_user(email, token, expiry.isoformat(), ADMIN_ID)
    
    if user_id:
        msg = f"✅ **User Added**\n\n📧 {email}\n🔑 {format_token(token)}\n📆 Expires: {expiry.strftime('%Y-%m-%d')}"
    else:
        msg = "❌ Error adding user"
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("👥 Back", callback_data='menu_users')
        ]]),
        parse_mode='Markdown'
    )
    
    context.user_data.clear()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled")
    return ConversationHandler.END

# ============================================
# MAIN
# ============================================

def main():
    init_db()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='^users_add$')],
        states={EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)]},
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    app.add_handler(conv_handler)
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("\n" + "="*50)
    print("🤖 BRANVEE ADMIN BOT - RAILWAY")
    print("="*50)
    print("✅ Bot is running...")
    print("="*50 + "\n")
    
    app.run_polling()

if __name__ == '__main__':
    main()
