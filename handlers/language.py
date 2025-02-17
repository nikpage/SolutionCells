from telebot import types
from languages import TRANSLATIONS
from database import get_user_language, set_user_language
from utils.translations import get_text

def language_command(bot, message):
    """Handle the /language command."""
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська')
    bot.send_message(message.chat.id, "Choose your language / Vyberte jazyk / Виберіть мову:", reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_language_choice, bot)

def handle_language_choice(message, bot, session_manager=None):
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
    
    # Get the last message sent to this user
    if session_manager:
        session_id = session_manager.find_active_session(user_id)
        if session_id:
            session = session_manager.get_session(session_id)
            if session:
                # Recreate the invitation message in the new language
                invite_link = f"https://t.me/{bot.get_me().username}?start={session_id}"
                other_role = 'seller' if session.initiator_role == 'buyer' else 'buyer'
                
                # Get role name in the selected language
                other_role_translated = get_text(f'role_{other_role}', user_id)
                join_text = get_text('join_negotiation', user_id)
                
                forward_text = (
                    f"🤝 {join_text} {other_role_translated}!\n\n"
                    f"{get_text('click_to_join', user_id)}: {invite_link}"
                )
                
                # Create inline keyboard for sharing
                inline_keyboard = types.InlineKeyboardMarkup()
                inline_keyboard.row(
                    types.InlineKeyboardButton(
                        "📤 " + get_text('share_with', user_id),
                        switch_inline_query=forward_text
                    )
                )
                
                # Send the updated invitation message
                msg = bot.send_message(
                    message.chat.id,
                    forward_text,
                    reply_markup=inline_keyboard,
                    disable_web_page_preview=True
                )
                
                # Pin the new message
                try:
                    bot.pin_chat_message(message.chat.id, msg.message_id)
                except:
                    pass
                return
    
    # If no active session or session_manager not provided, show the Start button
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('🔄 Start')
    keyboard.row('🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська')
    bot.send_message(message.chat.id, get_text('welcome', user_id), reply_markup=keyboard)
