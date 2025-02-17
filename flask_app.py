import os
import logging
import telebot
from flask import Flask, request, abort
from negotiator import setup_bot_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize bot
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
setup_bot_handlers(bot)  # Set up all the handlers

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook requests from Telegram."""
    if request.headers.get('content-type') != 'application/json':
        abort(403)

    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    
    try:
        bot.process_new_updates([update])
        return 'OK', 200
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)
        return 'Error', 500

# Health check route
@app.route('/health')
def health():
    """Simple health check endpoint."""
    return 'OK', 200
