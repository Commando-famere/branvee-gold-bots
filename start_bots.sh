#!/bin/bash
echo "========================================"
echo "🚀 BRANVEE BOTS LAUNCHER"
echo "========================================"

# Function to kill all background processes
cleanup() {
    echo ""
    echo "⏹️  Stopping all bots..."
    kill $ADMIN_PID $SIGNAL_PID 2>/dev/null
    wait $ADMIN_PID $SIGNAL_PID 2>/dev/null
    echo "✅ All bots stopped"
    exit 0
}

# Set up trap for Ctrl+C
trap cleanup SIGINT SIGTERM

# Start Admin Bot
echo "📊 Starting Admin Bot..."
cd ~/branvee-admin-bot
python bot.py > admin.log 2>&1 &
ADMIN_PID=$!
echo "  ✅ Admin Bot started (PID: $ADMIN_PID)"

# Start Signal Bot
echo "📈 Starting Signal Bot..."
cd ~/branvee-admin-bot/bot_signal
python bot.py > signal.log 2>&1 &
SIGNAL_PID=$!
echo "  ✅ Signal Bot started (PID: $SIGNAL_PID)"

echo "========================================"
echo "✅ Both bots are running!"
echo "📊 Admin Bot logs: tail -f ~/branvee-admin-bot/admin.log"
echo "📈 Signal Bot logs: tail -f ~/branvee-admin-bot/bot_signal/signal.log"
echo "========================================"
echo "Press Ctrl+C to stop both bots"
echo "========================================"

# Wait indefinitely
while true; do
    sleep 1
done
