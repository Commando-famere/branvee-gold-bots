"""
Railway entry point - Runs both Admin and Signal bots
"""
import subprocess
import threading
import time
import os
import signal
import sys

def run_admin_bot():
    """Run admin bot"""
    from bot import main as admin_main
    admin_main()

def run_signal_bot():
    """Run signal bot"""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bot_signal'))
    from bot_signal.bot import main as signal_main
    signal_main()

if __name__ == '__main__':
    print("="*60)
    print("🚀 BRANVEE GOLD SYSTEM - RAILWAY DEPLOYMENT")
    print("="*60)
    
    # Create threads for both bots
    admin_thread = threading.Thread(target=run_admin_bot, name="AdminBot")
    signal_thread = threading.Thread(target=run_signal_bot, name="SignalBot")
    
    admin_thread.daemon = True
    signal_thread.daemon = True
    
    admin_thread.start()
    print("✅ Admin Bot started")
    
    signal_thread.start()
    print("✅ Signal Bot started")
    
    print("\n📊 Both bots are running...")
    print("="*60)
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down bots...")
        sys.exit(0)
