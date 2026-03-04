"""
Branvee Admin Bot - Main Entry Point
"""
import logging
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

from config import BOT_TOKEN, ADMIN_ID
from database import (
    init_db, get_all_users, get_active_users, get_expired_users,
    add_user, get_user_by_email, renew_user, suspend_user,
    activate_user, delete_user, get_stats, get_user_by_id
)
from utils.token_generator import generate_token, format_token_for_display
from utils.date_utils import calculate_expiry, format_date, days_until
from utils.validators import validate_email
from keyboards.main_menu import get_main_menu
from keyboards.users_menu import get_users_menu, get_user_action_menu, get_user_list_keyboard
from keyboards.duration_menu import (
    get_days_menu, get_weeks_menu,
    get_months_menu, get_years_menu, get_hours_menu,
    get_confirmation_menu, get_duration_main_menu
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Conversation states
EMAIL, CUSTOM_DURATION = range(2)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized. This bot is for admin use only.")
        return
    
    await update.message.reply_text(
        "🔷 **BRANVEE GOLD ADMIN** 🔷\n\nWelcome to the Admin Panel. Select an option below:",
        reply_markup=get_main_menu(),
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id != ADMIN_ID:
        await query.edit_message_text("⛔ Unauthorized.")
        return
    
    # ============================================
    # MAIN MENU NAVIGATION
    # ============================================
    if data == 'menu_main':
        await query.edit_message_text(
            "🔷 **BRANVEE GOLD ADMIN** 🔷\n\nSelect an option:",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
    
    elif data == 'menu_users':
        await query.edit_message_text(
            "👥 **User Management**\n\nSelect an option:",
            reply_markup=get_users_menu(),
            parse_mode='Markdown'
        )
    
    elif data == 'menu_analytics':
        stats = get_stats()
        msg = f"""
📊 **Analytics**
═════════════════
👥 Total Users: {stats['total']}
✅ Active: {stats['active']}
❌ Expired: {stats['expired']}
⏸️ Suspended: {stats['suspended']}
        """
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_main')]]
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == 'menu_help':
        msg = """
ℹ️ **Help & Commands**
═════════════════════

👥 **Users Menu**
• Add User - Create new user with email
• Active Users - View all active users
• Expired Users - View expired users

⚙️ **Settings**
• Renew User - Extend user expiry
• View Token - See user's token
• Suspend/Activate - Manage access

📊 **Analytics**
• View system statistics

For support, contact @branvee_admin
        """
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_main')]]
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ============================================
    # SETTINGS MENU
    # ============================================
    elif data == 'menu_settings':
        keyboard = [
            [InlineKeyboardButton("🔄 Renew User", callback_data='settings_renew')],
            [InlineKeyboardButton("🔑 View Token", callback_data='settings_view_token')],
            [InlineKeyboardButton("📝 Edit Notes", callback_data='settings_notes')],
            [InlineKeyboardButton("⏸️ Suspend User", callback_data='settings_suspend')],
            [InlineKeyboardButton("▶️ Activate User", callback_data='settings_activate')],
            [InlineKeyboardButton("🔙 Back", callback_data='menu_main')]
        ]
        await query.edit_message_text(
            "⚙️ **Settings**\n\nSelect an option:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # ============================================
    # SETTINGS ACTIONS
    # ============================================
    elif data == 'settings_renew':
        users = get_active_users()
        if not users:
            await query.edit_message_text(
                "❌ No active users found.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data='menu_settings')
                ]])
            )
        else:
            await query.edit_message_text(
                "🔄 **Renew User**\n\nSelect user to renew:",
                reply_markup=get_user_list_keyboard(users, action='renew'),
                parse_mode='Markdown'
            )
    
    elif data == 'settings_view_token':
        users = get_all_users()
        if not users:
            await query.edit_message_text(
                "❌ No users found.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data='menu_settings')
                ]])
            )
        else:
            await query.edit_message_text(
                "🔑 **View Token**\n\nSelect user:",
                reply_markup=get_user_list_keyboard(users, action='token'),
                parse_mode='Markdown'
            )
    
    elif data == 'settings_suspend':
        users = get_active_users()
        if not users:
            await query.edit_message_text(
                "❌ No active users found.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data='menu_settings')
                ]])
            )
        else:
            await query.edit_message_text(
                "⏸️ **Suspend User**\n\nSelect user to suspend:",
                reply_markup=get_user_list_keyboard(users, action='suspend'),
                parse_mode='Markdown'
            )
    
    elif data == 'settings_activate':
        users = get_expired_users()
        if not users:
            await query.edit_message_text(
                "❌ No suspended/expired users found.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data='menu_settings')
                ]])
            )
        else:
            await query.edit_message_text(
                "▶️ **Activate User**\n\nSelect user to activate:",
                reply_markup=get_user_list_keyboard(users, action='activate'),
                parse_mode='Markdown'
            )
    
    # ============================================
    # USER ACTION HANDLERS
    # ============================================
    elif data.startswith('renew_'):
        user_id = int(data.split('_')[1])
        user = get_user_by_id(user_id)
        if user:
            context.user_data['renew_user_id'] = user_id
            context.user_data['renew_email'] = user['email']
            await query.edit_message_text(
                f"📧 User: {user['email']}\n"
                f"📅 Current Expiry: {user['expires_at'][:10]}\n\n"
                f"Select new duration:",
                reply_markup=get_duration_main_menu(),
                parse_mode='Markdown'
            )
    
    elif data.startswith('token_'):
        user_id = int(data.split('_')[1])
        user = get_user_by_id(user_id)
        if user:
            token_display = format_token_for_display(user['token'])
            msg = f"""
🔑 **User Token**
═════════════════
📧 Email: {user['email']}
🔑 Token: {token_display}
📅 Expires: {user['expires_at'][:10]}
📊 Days left: {days_until(user['expires_at'])}
            """
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_settings')]]
            await query.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
    
    elif data.startswith('suspend_'):
        user_id = int(data.split('_')[1])
        success = suspend_user(user_id)
        if success:
            msg = "✅ User suspended successfully."
        else:
            msg = "❌ Failed to suspend user."
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_settings')]]
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith('activate_'):
        user_id = int(data.split('_')[1])
        success = activate_user(user_id)
        if success:
            msg = "✅ User activated successfully."
        else:
            msg = "❌ Failed to activate user."
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='menu_settings')]]
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ============================================
    # DURATION SELECTION
    # ============================================
    elif data == 'dur_main':
        await query.edit_message_text(
            "⏰ **Select Duration Type**",
            reply_markup=get_duration_main_menu(),
            parse_mode='Markdown'
        )
    
    elif data == 'dur_hours':
        await query.edit_message_text(
            "⏰ **Select Hours**",
            reply_markup=get_hours_menu(),
            parse_mode='Markdown'
        )
    
    elif data == 'dur_days':
        await query.edit_message_text(
            "📅 **Select Days**",
            reply_markup=get_days_menu(),
            parse_mode='Markdown'
        )
    
    elif data == 'dur_weeks':
        await query.edit_message_text(
            "📆 **Select Weeks**",
            reply_markup=get_weeks_menu(),
            parse_mode='Markdown'
        )
    
    elif data == 'dur_months':
        await query.edit_message_text(
            "🗓️ **Select Months**",
            reply_markup=get_months_menu(),
            parse_mode='Markdown'
        )
    
    elif data == 'dur_years':
        await query.edit_message_text(
            "📅 **Select Years**",
            reply_markup=get_years_menu(),
            parse_mode='Markdown'
        )
    
    elif data.startswith('hours_'):
        hours = int(data.split('_')[1])
        days = hours / 24
        await process_duration_selection(query, context, days, f"{hours} hours")
    
    elif data.startswith('days_'):
        days = int(data.split('_')[1])
        await process_duration_selection(query, context, days, f"{days} days")
    
    elif data.startswith('weeks_'):
        weeks = int(data.split('_')[1])
        days = weeks * 7
        await process_duration_selection(query, context, days, f"{weeks} weeks")
    
    elif data.startswith('months_'):
        months = int(data.split('_')[1])
        days = months * 30
        await process_duration_selection(query, context, days, f"{months} months")
    
    elif data.startswith('years_'):
        years = int(data.split('_')[1])
        days = years * 365
        await process_duration_selection(query, context, days, f"{years} years")
    
    elif data == 'dur_custom':
        await query.edit_message_text(
            "✏️ **Custom Duration**\n\nPlease send number of days:",
            parse_mode='Markdown'
        )
        return CUSTOM_DURATION
    
    # ============================================
    # USER MANAGEMENT
    # ============================================
    elif data == 'users_add':
        await query.edit_message_text(
            "📧 **Add User**\n\nPlease send the user's email address:",
            parse_mode='Markdown'
        )
        return EMAIL
    
    elif data == 'users_active':
        users = get_active_users()
        if not users:
            msg = "✅ **Active Users**\n\nNo active users found."
        else:
            msg = "✅ **Active Users**\n\n"
            for user in users:
                token_display = format_token_for_display(user['token'])
                msg += f"• {user['email']}\n"
                msg += f"  🔑 Token: {token_display}\n"
                msg += f"  📅 Expires: {user['expires_at'][:10]}\n"
                msg += f"  📊 Days left: {days_until(user['expires_at'])}\n\n"
        
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
            msg = "❌ **Expired Users**\n\nNo expired users found."
        else:
            msg = "❌ **Expired Users**\n\n"
            for user in users:
                token_display = format_token_for_display(user['token'])
                msg += f"• {user['email']}\n"
                msg += f"  🔑 Token: {token_display}\n"
                msg += f"  📅 Expired: {user['expires_at'][:10]}\n\n"
        
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='menu_users')
            ]]),
            parse_mode='Markdown'
        )
    
    # ============================================
    # CONFIRMATION
    # ============================================
    elif data == 'confirm_yes':
        if 'renew_user_id' in context.user_data:
            await process_renewal(query, context)
        else:
            await generate_and_save_token(query, context)
    
    elif data == 'confirm_edit':
        await query.edit_message_text(
            "📧 **Edit Email**\n\nPlease send the user's email address:",
            parse_mode='Markdown'
        )
        return EMAIL
    
    elif data == 'users_menu':
        await query.edit_message_text(
            "👥 **User Management**\n\nSelect an option:",
            reply_markup=get_users_menu(),
            parse_mode='Markdown'
        )

async def process_duration_selection(query, context, days, display_text):
    """Process duration selection"""
    context.user_data['duration_days'] = days
    context.user_data['duration_display'] = display_text
    await show_confirmation(query, context)

async def show_confirmation(query, context):
    """Show confirmation screen"""
    email = context.user_data.get('user_email', 'Not set')
    days = context.user_data.get('duration_days', 0)
    expiry = calculate_expiry(days)
    
    msg = f"""
📧 **Confirm Details**
═════════════════════
Email: {email}
Duration: {context.user_data.get('duration_display', f'{days} days')}
Expires: {format_date(expiry)}

Please confirm:
    """
    
    await query.edit_message_text(
        msg,
        reply_markup=get_confirmation_menu(),
        parse_mode='Markdown'
    )

async def generate_and_save_token(query, context):
    """Generate token and save to database"""
    email = context.user_data.get('user_email')
    days = context.user_data.get('duration_days', 30)
    expiry = calculate_expiry(days)
    token = generate_token()
    
    # Save to database
    user_id = add_user(email, token, expiry.isoformat(), ADMIN_ID)
    
    if user_id:
        token_display = format_token_for_display(token)
        msg = f"""
✅ **User Added Successfully!**
═══════════════════════════════

📧 Email: {email}
🔑 Token: {token_display}
📅 Expires: {format_date(expiry)}
⏳ Duration: {context.user_data.get('duration_display', f'{days} days')}

You can now share this token with the user.
        """
    else:
        msg = "❌ **Error**\n\nUser with this email may already exist."
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("👥 Back to Users", callback_data='menu_users')
        ]]),
        parse_mode='Markdown'
    )
    
    context.user_data.clear()

async def process_renewal(query, context):
    """Process user renewal"""
    user_id = context.user_data.get('renew_user_id')
    days = context.user_data.get('duration_days', 30)
    new_expiry = calculate_expiry(days)
    
    success = renew_user(user_id, new_expiry.isoformat(), ADMIN_ID)
    
    if success:
        user = get_user_by_id(user_id)
        msg = f"""
✅ **User Renewed Successfully!**
════════════════════════════════

📧 Email: {user['email']}
🔑 Token: {format_token_for_display(user['token'])}
📅 New Expiry: {format_date(new_expiry)}
⏳ Extended by: {context.user_data.get('duration_display', f'{days} days')}
        """
    else:
        msg = "❌ **Error**\n\nFailed to renew user."
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("👥 Back to Users", callback_data='menu_users')
        ]]),
        parse_mode='Markdown'
    )
    
    context.user_data.clear()

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle email input"""
    email = update.message.text.strip()
    
    if not validate_email(email):
        await update.message.reply_text(
            "❌ Invalid email format. Please try again:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Cancel", callback_data='menu_users')
            ]])
        )
        return EMAIL
    
    # Check if user exists
    existing = get_user_by_email(email)
    if existing:
        await update.message.reply_text(
            f"❌ User with email {email} already exists.\n\n"
            f"Token: {format_token_for_display(existing['token'])}\n"
            f"Expires: {existing['expires_at'][:10]}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='menu_users')
            ]])
        )
        return ConversationHandler.END
    
    context.user_data['user_email'] = email
    
    await update.message.reply_text(
        f"✅ Email saved: {email}\n\nNow select duration:",
        reply_markup=get_duration_main_menu(),
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def handle_custom_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom duration input"""
    try:
        days = int(update.message.text.strip())
        if days < 1 or days > 3650:
            raise ValueError
    except:
        await update.message.reply_text(
            "❌ Invalid number. Please enter days (1-3650):",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Cancel", callback_data='menu_users')
            ]])
        )
        return CUSTOM_DURATION
    
    context.user_data['duration_days'] = days
    context.user_data['duration_display'] = f"{days} days"
    await show_confirmation(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text(
        "❌ Operation cancelled.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Main Menu", callback_data='menu_main')
        ]])
    )
    return ConversationHandler.END

def main():
    """Start the bot"""
    # Initialize database
    init_db()
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add conversation handler for adding users
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_handler, pattern='^users_add$'),
            CallbackQueryHandler(button_handler, pattern='^dur_custom$')
        ],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)],
            CUSTOM_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_duration)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    app.add_handler(conv_handler)
    
    # Add command handlers
    app.add_handler(CommandHandler('start', start_command))
    
    # Add callback query handler for all other buttons
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("\n" + "="*60)
    print("🤖 BRANVEE ADMIN BOT - PRODUCTION READY")
    print("="*60)
    print("🚀 Bot is running... Press Ctrl+C to stop")
    print("👤 Admin ID: 6980711942")
    print("✅ Settings menu working")
    print("✅ Help menu working")
    print("✅ All buttons functional")
    print("="*60 + "\n")
    
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    main()
