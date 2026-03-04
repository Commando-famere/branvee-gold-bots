"""
BRANVEE GOLD SIGNAL BOT - Railway Version
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
import sys
import os

# Add paths for Railway
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BOT_TOKEN
from database import init_db

from handlers.auth import (
    EMAIL, TOKEN,
    start_command,
    handle_email,
    handle_token,
    cancel
)
from handlers.menu import menu_callback
from handlers.signal import signal_callback
from handlers.strategy import strategy_callback

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Start bot"""
    # Initialize database
    try:
        init_db()
        print("✅ Database connected")
    except Exception as e:
        print(f"⚠️ Database warning: {e}")
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Email + Token authentication
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
    
    # Menu navigation
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
