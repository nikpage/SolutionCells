# 1
import os
import logging
from datetime import datetime
from telebot import TeleBot
from message_builder import MessageBuilder
from session_manager import SessionManager
from handlers import (
    language_command,
    start,
    status_command,
    cancel_command,
    help_command,
    stop_command
)

BOT_TOKEN = "7707543229:AAEfyqpFhSXkwpYhPju_il4_SzS6cy1Izlk"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("Starting bot...")

def main():
    # Initialize bot and message builder
    bot = TeleBot(BOT_TOKEN)
    message_builder = MessageBuilder()
    session_manager = SessionManager()

    try:
        BOT_INFO = bot.get_me()
        BOT_NAME = BOT_INFO.first_name
        BOT_USERNAME = BOT_INFO.username
        logger.info(f"Successfully connected to bot {BOT_NAME}")
    except Exception as e:
        logger.error(f"Failed to initialize bot: {str(e)}")
        raise e

    # Register command handlers
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        """Handle /start command."""
        logger.info(f"Start command from user {message.from_user.id}")
        start(message, bot, session_manager, message_builder)

    @bot.message_handler(func=lambda message: message.text == '🔄 Start')
    def handle_start_button(message):
        start(message, bot, session_manager, message_builder)

    @bot.message_handler(func=lambda message: message.text == 'Start')
    def handle_start_text(message):
        start(message, bot, session_manager, message_builder)

    @bot.message_handler(commands=['language'])
    def handle_language(message):
        """Handle /language command."""
        logger.info(f"Language command from user {message.from_user.id}")
        language_command(bot, message)

    @bot.message_handler(commands=['status'])
    def handle_status(message):
        """Handle /status command."""
        logger.info(f"Status command from user {message.from_user.id}")
        status_command(message, bot, session_manager)

    @bot.message_handler(commands=['cancel'])
    def handle_cancel(message):
        """Handle /cancel command."""
        logger.info(f"Cancel command from user {message.from_user.id}")
        cancel_command(message, bot, session_manager)

    @bot.message_handler(commands=['help'])
    def handle_help(message):
        """Handle /help command."""
        logger.info(f"Help command from user {message.from_user.id}")
        help_command(message, bot)

    @bot.message_handler(commands=['stop'])
    def handle_stop(message):
        """Handle /stop command."""
        logger.info(f"Stop command from user {message.from_user.id}")
        stop_command(message, bot, session_manager)

    # Start bot
    try:
        logger.info("Starting infinity polling...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}")
    finally:
        logger.info("Bot stopped")

if __name__ == '__main__':
    main()
