"""
Start command handler
"""
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID, WELCOME_MSG
from keyboards.main_menu import get_main_menu

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    
    # Check if user is admin
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized. This bot is for admin use only.")
        return
    
    await update.message.reply_text(
        WELCOME_MSG,
        reply_markup=get_main_menu(),
        parse_mode='Markdown'
    )
