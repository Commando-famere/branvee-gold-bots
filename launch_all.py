#!/usr/bin/env python
"""
BRANVEE BOTS LAUNCHER
Starts both Admin Bot and Signal Bot simultaneously
"""

import subprocess
import os
import signal
import sys
import time

# Colors for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

print(f"\n{BLUE}{'='*60}{RESET}")
print(f"{GREEN}🚀 BRANVEE BOTS LAUNCHER{RESET}")
print(f"{BLUE}{'='*60}{RESET}")

# Store process objects
processes = []

def print_status(name, status, color=GREEN):
    """Print colored status"""
    timestamp = time.strftime('%H:%M:%S')
    print(f"{color}[{timestamp}] {name}: {status}{RESET}")

def signal_handler(sig, frame):
    """Handle Ctrl+C to kill all processes"""
    print(f"\n{YELLOW}⏹️  Stopping all bots...{RESET}")
    for proc in processes:
        proc.terminate()
    for proc in processes:
        proc.wait()
    print(f"{GREEN}✅ All bots stopped{RESET}")
    sys.exit(0)

# Register signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Start Admin Bot
try:
    print_status("Admin Bot", "Starting...", YELLOW)
    admin_process = subprocess.Popen(
        ['python', 'bot.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append(admin_process)
    print_status("Admin Bot", f"Started (PID: {admin_process.pid})", GREEN)
except Exception as e:
    print_status("Admin Bot", f"Failed: {e}", RED)

# Start Signal Bot
try:
    print_status("Signal Bot", "Starting...", YELLOW)
    signal_process = subprocess.Popen(
        ['python', 'bot_signal/bot.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    processes.append(signal_process)
    print_status("Signal Bot", f"Started (PID: {signal_process.pid})", GREEN)
except Exception as e:
    print_status("Signal Bot", f"Failed: {e}", RED)

print(f"\n{BLUE}{'='*60}{RESET}")
print(f"{GREEN}✅ Both bots are running!{RESET}")
print(f"{YELLOW}📊 Admin Bot: Adding users{RESET}")
print(f"{YELLOW}📈 Signal Bot: Sending signals{RESET}")
print(f"{BLUE}{'='*60}{RESET}")
print(f"{RED}Press Ctrl+C to stop both bots{RESET}")
print(f"{BLUE}{'='*60}{RESET}\n")

# Monitor and display logs from both bots
while processes:
    for proc in processes[:]:
        if proc.poll() is not None:
            # Process died, remove from list
            processes.remove(proc)
            print_status("Bot", f"Process {proc.pid} terminated", RED)
            continue
        
        # Read output if available
        try:
            line = proc.stdout.readline()
            if line:
                # Determine which bot
                if proc == admin_process:
                    prefix = f"{GREEN}[ADMIN]{RESET}"
                else:
                    prefix = f"{BLUE}[SIGNAL]{RESET}"
                print(f"{prefix} {line.strip()}")
        except:
            pass
    
    time.sleep(0.1)

print(f"\n{RED}All bots have stopped{RESET}")
