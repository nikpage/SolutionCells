from datetime import datetime
from telebot import types
from languages import TRANSLATIONS
from database import get_user_language, set_user_language
from utils.translations import get_text

def language_command(bot, message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦')
    bot.send_message(
        message.chat.id,
        get_text('choose_language', message.from_user.id),
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, handle_language_choice, bot)

def handle_language_choice(message, bot):
    lang_map = {
        'English 🇬🇧': 'en',
        'Čeština 🇨🇿': 'cs',
        'Українська 🇺🇦': 'uk'
    }
    chosen_lang = lang_map.get(message.text)
    if chosen_lang:
        set_user_language(message.from_user.id, chosen_lang)
        # Restate the last step in the selected language
        last_step = message.reply_to_message.text
        translated_step = get_text(last_step, message.from_user.id)
        bot.send_message(
            message.chat.id,
            translated_step,
            reply_markup=types.ReplyKeyboardRemove()
        )
        # Display role buttons
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row(
            f"🛒 {get_text('buyer', message.from_user.id)}", 
            f"💰 {get_text('seller', message.from_user.id)}"
        )
        keyboard.row('English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦')
        bot.send_message(
            message.chat.id,
            get_text('choose_role', message.from_user.id),
            reply_markup=keyboard
        )
    else:
        bot.send_message(message.chat.id, "Please select a language from the keyboard.")
        return language_command(bot, message)

