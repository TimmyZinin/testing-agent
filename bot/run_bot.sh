#!/bin/bash
# Run Andry Tester Bot

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment from .env if exists
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

# Check for token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Error: TELEGRAM_BOT_TOKEN not set"
    echo ""
    echo "To set up Andry Tester bot:"
    echo "1. Message @BotFather on Telegram"
    echo "2. Send /newbot"
    echo "3. Name: Andry Tester"
    echo "4. Username: andry_tester_bot (or similar)"
    echo "5. Copy the token and set it:"
    echo "   export TELEGRAM_BOT_TOKEN=your_token_here"
    echo ""
    exit 1
fi

# Activate virtual environment if exists
if [ -d "$PROJECT_DIR/.venv12" ]; then
    source "$PROJECT_DIR/.venv12/bin/activate"
elif [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
fi

# Run bot
cd "$PROJECT_DIR"
python -m bot.telegram_bot
