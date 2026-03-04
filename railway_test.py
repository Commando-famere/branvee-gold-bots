"""
Simple test bot for Railway
"""
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get('SIGNAL_BOT_TOKEN', '8741454658:AAGlyxcVQMH7tKd13OmM2Y2VGa9ex9LbPfo')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is working on Railway!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("🤖 Test bot started...")
    app.run_polling()

if __name__ == '__main__':
    main()
