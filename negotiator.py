import os
import logging
from datetime import datetime
from telebot import TeleBot
from message_builder import MessageBuilder
from session_manager import SessionManager
from handlers.negotiation import process_limit_and_invite, handle_stop_confirmation
from handlers.commands import start, status_command, cancel_command, help_command, stop_command
from utils.translations import get_text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get bot token from environment
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', "7707543229:AAEfyqpFhSXkwpYhPju_il4_SzS6cy1Izlk")

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
        raise

    # Register message handlers
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        start(message, bot, session_manager, message_builder)

    @bot.message_handler(commands=['status'])
    def handle_status(message):
        status_command(message, bot, session_manager)

    @bot.message_handler(commands=['cancel'])
    def handle_cancel(message):
        cancel_command(message, bot, session_manager)

    @bot.message_handler(commands=['help'])
    def handle_help(message):
        help_command(message, bot)

    @bot.message_handler(commands=['stop'])
    def handle_stop(message):
        stop_command(message, bot, session_manager)

    @bot.message_handler(func=lambda message: message.text and message.text.lower() == 'end')
    def handle_end(message):
        user_sessions = session_manager.get_user_sessions(message.from_user.id)
        if user_sessions:
            session_id = user_sessions[0]  # Get first active session
            session = session_manager.get_session(session_id)
            if session:
                session_manager.delete_session(session_id)
                bot.send_message(message.chat.id, get_text('negotiation_ended', message.from_user.id))
                if session.initiator_id != message.from_user.id:
                    bot.send_message(session.initiator_id, get_text('negotiation_ended', session.initiator_id))
        else:
            bot.send_message(message.chat.id, get_text('no_active_session', message.from_user.id))

    @bot.message_handler(func=lambda message: message.text and message.text == "🔄 Start New Negotiation")
    def handle_start_button(message):
        start(message, bot, session_manager, message_builder)

    logger.info("Starting infinity polling...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        raise

if __name__ == '__main__':
    main()
