"""
Main Railway entry point - Runs Signal Bot
"""
import os
import sys
import logging

# Add signal bot to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bot_signal'))

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    try:
        from bot import main
        print("🚀 Starting Signal Bot on Railway...")
        main()
    except Exception as e:
        logging.error(f"Failed to start: {e}")
        sys.exit(1)
