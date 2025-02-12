from telebot import types
from languages import TRANSLATIONS
from database import get_user_language, set_user_language

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
        bot.send_message(
            message.chat.id, 
            get_text('language_set', message.from_user.id),
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        bot.send_message(message.chat.id, "Please select a language from the keyboard.")
        return language_command(bot, message)
