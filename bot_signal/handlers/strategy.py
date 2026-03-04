"""
Strategy handler
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

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
        keyboard = [
            [InlineKeyboardButton("📊 GET SIGNAL", callback_data='get_signal')],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='menu_main')]
        ]
        await query.edit_message_text(
            f"✅ Strategy changed to **{strategies[data]}**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
