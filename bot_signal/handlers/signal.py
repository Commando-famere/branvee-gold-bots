"""
Signal handler - Returns ONLY sticker and returns to menu
"""
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import API_URL

async def signal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle get signal button - returns sticker and returns to menu"""
    query = update.callback_query
    await query.answer()
    
    if 'user_id' not in context.user_data:
        await query.edit_message_text("Session expired. Please /start again.")
        return
    
    try:
        response = requests.get(f"{API_URL}/api/signal", timeout=5)
        data = response.json()
        signal = data.get('signal', 'HOLD')
        
        # Send sticker based on signal
        if signal == 'BUY':
            emoji = "🟢🟢🟢🟢🟢🟢🟢🟢\n🟢🟢🟢🟢🟢🟢🟢🟢\n🟢🟢🟢🟢🟢🟢🟢🟢"
        elif signal == 'SELL':
            emoji = "🔴🔴🔴🔴🔴🔴🔴🔴\n🔴🔴🔴🔴🔴🔴🔴🔴\n🔴🔴🔴🔴🔴🔴🔴🔴"
        else:
            emoji = "⚪⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪⚪"
        
        await query.message.reply_text(emoji)
        
        # Return to menu - button only, no typing
        await return_to_menu(query, context)
        
    except Exception as e:
        await query.message.reply_text(f"❌ Error")
        await return_to_menu(query, context)

async def return_to_menu(query, context):
    """Return to main menu - buttons only"""
    message = "\n\n\n\n\n\n\n\n\n\n⚡⚡⚡ **READY** ⚡⚡⚡\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 CHANGE STRATEGY", callback_data='menu_strategy')],
        [InlineKeyboardButton("ℹ️ ACCOUNT INFO", callback_data='menu_account')],
        [InlineKeyboardButton("⚡⚡⚡ GET SIGNAL ⚡⚡⚡", callback_data='get_signal')]
    ]
    
    await query.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
