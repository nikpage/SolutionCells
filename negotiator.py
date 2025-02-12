import os
import logging
import telebot
from datetime import datetime, timedelta

# Import handlers
from handlers.language import language_command, handle_language_choice
from handlers.negotiation import (
    process_limit, process_limit_and_invite, 
    handle_stop_confirmation, compare_limits
)
from handlers.commands import (
    start, status_command, cancel_command, help_command
)

# Import database
from database import get_db

# Setup logging
logging.basicConfig(
    format='%(asctime)s | %(message)s',
    level=logging.INFO,
    filename='bot_debug.log',
    force=True
)
logger = logging.getLogger(__name__)
logger.info("Starting bot...")

# Bot initialization
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
BOT_INFO = bot.get_me()
BOT_NAME = BOT_INFO.first_name
BOT_USERNAME = BOT_INFO.username

# Global state
sessions = {}
user_sessions = {}
SESSION_TIMEOUT = 24

# Command handlers
@bot.message_handler(commands=['start'])
def start_command(message):
    start(message, bot, sessions, user_sessions)

@bot.message_handler(commands=['language'])
def handle_language(message):
    language_command(bot, message)

@bot.message_handler(commands=['status'])
def handle_status(message):
    status_command(message, bot, sessions)

@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    cancel_command(message, bot, sessions)

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_command(message, bot)

if __name__ == '__main__':
    try:
        get_db()  # Initialize database
        logger.info(f"Bot started as {BOT_NAME}")
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Error: {e}")
