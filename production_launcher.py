#!/usr/bin/env python
"""
BRANVEE PRODUCTION LAUNCHER
Auto-restarts bots if they crash
"""

import subprocess
import time
import signal
import sys

BOTS = [
    {'name': 'Admin Bot', 'path': 'bot.py', 'cwd': '.'},
    {'name': 'Signal Bot', 'path': 'bot_signal/bot.py', 'cwd': '.'}
]

processes = {}

def start_bot(name, path, cwd):
    """Start a bot and return process"""
    print(f"🚀 Starting {name}...")
    return subprocess.Popen(
        ['python', path],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

def monitor_bots():
    """Monitor and restart crashed bots"""
    for bot in BOTS:
        name = bot['name']
        if name not in processes or processes[name].poll() is not None:
            if name in processes:
                print(f"⚠️ {name} crashed! Restarting...")
            processes[name] = start_bot(name, bot['path'], bot['cwd'])

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    print("\n⏹️  Stopping all bots...")
    for proc in processes.values():
        proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print("="*60)
print("🏭 BRANVEE PRODUCTION LAUNCHER")
print("="*60)
print("✅ Auto-restart enabled")
print("="*60)

try:
    while True:
        monitor_bots()
        time.sleep(5)
except KeyboardInterrupt:
    signal_handler(None, None)
