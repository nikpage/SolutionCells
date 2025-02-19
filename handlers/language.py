from telebot import types
from database import set_user_language
from utils.translations import get_text

def language_command(bot, message):
    """Handle the /language command."""
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row("🇬🇧 English")
    bot.send_message(
        message.chat.id,
        get_text("select_language", message.from_user.id),
        reply_markup=keyboard
    )

def handle_language_choice(message, bot):
    """Handle language selection."""
    language_codes = {
        "🇬🇧 English": "en",
    }
    
    if message.text not in language_codes:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row("🇬🇧 English")
        bot.send_message(
            message.chat.id,
            get_text("select_language", message.from_user.id),
            reply_markup=keyboard
        )
        return

    lang_code = language_codes[message.text]
    set_user_language(message.from_user.id, lang_code)
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row("🇬🇧 English")
    bot.send_message(
        message.chat.id,
        get_text("language_set", message.from_user.id),
        reply_markup=keyboard
    )
