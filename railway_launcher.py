"""
Railway Launcher - Runs both Admin and Signal Bots
"""
import threading
import time
import os
import sys

def run_admin():
    os.system("python railway_admin_bot.py")

def run_signal():
    os.system("python railway_signal_bot.py")

if __name__ == '__main__':
    print("="*60)
    print("🚀 BRANVEE BOTS LAUNCHER - RAILWAY")
    print("="*60)
    
    admin_thread = threading.Thread(target=run_admin)
    signal_thread = threading.Thread(target=run_signal)
    
    admin_thread.daemon = True
    signal_thread.daemon = True
    
    admin_thread.start()
    print("✅ Admin Bot started")
    
    signal_thread.start()
    print("✅ Signal Bot started")
    
    print("\n📊 Both bots are running...")
    print("="*60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down...")
        sys.exit(0)
