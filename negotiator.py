# 1
import os
import logging
import telebot
from datetime import datetime

# Import handlers
from handlers.language import language_command, handle_language_choice
from handlers.negotiation import (
    process_limit, process_limit_and_invite, 
    handle_stop_confirmation, compare_limits
)
from handlers.commands import (
    start, status_command, cancel_command, help_command
)

# Import utils
from database import get_db
from utils.session import SessionManager
from utils.message import MessageBuilder

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
TOKEN = "7707543229:AAEfyqpFhSXkwpYhPju_il4_SzS6cy1Izlk"
bot = telebot.TeleBot(TOKEN)

try:
    BOT_INFO = bot.get_me()
    BOT_NAME = BOT_INFO.first_name
    BOT_USERNAME = BOT_INFO.username
    logger.info(f"Successfully connected to bot {BOT_NAME}")
except Exception as e:
    logger.error(f"Failed to initialize bot: {str(e)}")
    raise e

# Initialize global managers
session_manager = SessionManager(timeout_hours=24)
message_builder = MessageBuilder(BOT_NAME, BOT_USERNAME)

# Command handlers
@bot.message_handler(commands=['start'])
def start_command(message):
    start(message, bot, session_manager, message_builder)

@bot.message_handler(commands=['language'])
def handle_language(message):
    language_command(bot, message)

@bot.message_handler(commands=['status'])
def handle_status(message):
    status_command(message, bot, session_manager)

@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    cancel_command(message, bot, session_manager)

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_command(message, bot)

if __name__ == '__main__':
    try:
        get_db()  # Initialize database
        logger.info("Starting infinity polling...")
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Error during bot execution: {str(e)}")
        raise e
