from telebot import types
from languages import TRANSLATIONS
from database import get_user_language, set_user_language
from utils.translations import get_text

def language_command(bot, message):
    """Handle the /language command."""
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська')
    bot.send_message(message.chat.id, "Choose your language / Vyberte jazyk / Виберіть мову:", reply_markup=keyboard)

def handle_language_choice(message, bot):
    """Handle language selection."""
    lang_map = {
        '🇬🇧 English': 'en',
        '🇨🇿 Čeština': 'cs',
        '🇺🇦 Українська': 'uk'
    }
    
    if message.text not in lang_map:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row('🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська')
        bot.send_message(message.chat.id, "Please select a language / Prosím vyberte jazyk / Будь ласка, виберіть мову:", reply_markup=keyboard)
        return
    
    lang_code = lang_map[message.text]
    user_id = message.from_user.id
    set_user_language(user_id, lang_code)
    
    # Show role selection after language is set
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('🛒 Buyer', '💰 Seller')
    bot.send_message(
        message.chat.id,
        get_text('select_role', message.from_user.id),
        reply_markup=keyboard
    )
