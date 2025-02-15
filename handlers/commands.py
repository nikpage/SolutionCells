from datetime import datetime, timedelta
from telebot import types
from languages import TRANSLATIONS
from database import get_user_language
from utils.money import format_money
from utils.translations import get_text
from .negotiation import (
    handle_user2_session, handle_role_choice,
    find_active_session, format_expiry_time
)

def get_text(key: str, user_id: int, **kwargs) -> str:
    """Get translated text for given key and user."""
    from languages import TRANSLATIONS
    from database import get_user_language

    lang = get_user_language(user_id)
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['en'][key])
    return text.format(**kwargs) if kwargs else text

def language_command(bot, message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦')
    bot.send_message(
        message.chat.id,
        get_text('choose_language', message.from_user.id),
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, handle_language_choice, bot)

def start(message, bot, session_manager, message_builder) -> None:
    """Handle the /start command."""
    args = message.text.split()
    if len(args) > 1:
        session_id = args[1]
        session = session_manager.get_session(session_id)
        if session:
            handle_user2_session(message, bot, session_id, session_manager)
            return

    # Create role selection keyboard with emojis
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    user_id = message.from_user.id
    keyboard.row(
        f"🛒 {get_text('buyer', user_id)}", 
        f"💰 {get_text('seller', user_id)}"
    )
    keyboard.row('English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦')
    
    welcome_msg = message_builder.build_welcome(user_id)
    
    bot.send_message(
        message.chat.id,
        welcome_msg,
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, handle_role_choice, bot, session_manager, message_builder)

def status_command(message, bot, session_manager) -> None:
    """Handle the /status command."""
    user_id = message.from_user.id
    session_id = session_manager.find_active_session(user_id)
    
    if not session_id:
        bot.send_message(message.chat.id, f"📭 {get_text('no_active_session', user_id)}")
        return

    session = session_manager.get_session(session_id)
    if not session:
        return

    # Create a status message with visual indicators
    status_msg = "📊 Negotiation Status:\n\n"
    
    # Add role indicator
    role = 'buyer' if ((session.initiator_id == user_id and session.initiator_role == 'buyer') or
                      (session.invited_id == user_id and session.initiator_role != 'buyer')) else 'seller'
    role_icon = "🛒" if role == 'buyer' else "💰"
    status_msg += f"{role_icon} {get_text('your_role', user_id)}: {get_text(role, user_id)}\n\n"
    
    # Add amount if set
    limit = (session.initiator_limit if user_id == session.initiator_id else session.invited_limit)
    if limit:
        status_msg += f"💵 {get_text('your_amount', user_id)}: {limit}\n"
        
        # Add status indicators
        if session.status == 'pending':
            status_msg += f"⏳ {get_text('waiting_for_other', user_id)}\n"
        elif session.status == 'completed':
            status_msg += f"✅ {get_text('deal_success', user_id)}\n"
        elif session.status == 'ended':
            status_msg += f"🚫 {get_text('negotiation_ended', user_id)}\n"
        
        # Add expiry time
        if session.status not in ['completed', 'ended']:
            status_msg += f"\n⏰ {get_text('expires_in', user_id)}"
    else:
        status_msg += f"❓ {get_text('no_bid', user_id)}"

    bot.send_message(message.chat.id, status_msg)

def cancel_command(message, bot, session_manager) -> None:
    """Handle the /cancel command."""
    bot.send_message(message.chat.id, get_text('end_confirm', message.from_user.id))
    from .negotiation import handle_stop_confirmation  # Import here to avoid circular import
    bot.register_next_step_handler(message, handle_stop_confirmation, bot, session_manager)

def help_command(message, bot) -> None:
    """Handle the /help command."""
    user_id = message.from_user.id
    help_text = get_text('help_text', user_id)
    bot.reply_to(message, help_text)
