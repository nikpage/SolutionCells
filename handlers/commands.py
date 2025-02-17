from datetime import datetime, timedelta
from telebot import types
from languages import TRANSLATIONS
from database import get_user_language
from utils.translations import get_text
from .negotiation import (
    handle_user2_session,
    process_limit_and_invite
)
from .language import language_command, handle_language_choice
from session_manager import Session
import uuid

def start(message, bot, session_manager, message_builder):
    """Handle /start command."""
    args = message.text.split()
    if len(args) > 1:
        session_id = args[1]
        session = session_manager.get_session(session_id)
        if session:
            handle_user2_session(message, bot, session_id, session_manager)
            return

    # Create keyboard with role selection
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('🛒 Buyer', '💰 Seller')
    keyboard.row('🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська')
    
    # Send welcome message with role selection
    bot.send_message(
        message.chat.id,
        get_text('select_role', message.from_user.id),
        reply_markup=keyboard
    )
    
    # Register next step handler
    bot.register_next_step_handler(message, handle_role_selection, bot, session_manager, message_builder)

def handle_role_selection(message, bot, session_manager, message_builder):
    """Handle role selection."""
    if message.text in ['🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська']:
        return handle_language_choice(message, bot, session_manager)
        
    role = message.text.lower().replace('🛒 ', '').replace('💰 ', '')
    if role not in ['buyer', 'seller']:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row('🛒 Buyer', '💰 Seller')
        keyboard.row('🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська')
        bot.send_message(
            message.chat.id,
            get_text('select_role', message.from_user.id),
            reply_markup=keyboard
        )
        return bot.register_next_step_handler(message, handle_role_selection, bot, session_manager, message_builder)

    # Create new session
    session_id = str(uuid.uuid4())
    session = Session(
        initiator_id=message.from_user.id,
        initiator_role=role,
        initiator_limit=None,
        participant_id=None,
        participant_limit=None,
        status='waiting_for_limit'
    )
    session_manager.save_session(session_id, session)

    # Ask for amount
    amount_key = f'enter_amount_{role}'
    bot.send_message(
        message.chat.id,
        get_text(amount_key, message.from_user.id)
    )
    
    # Register next step handler
    bot.register_next_step_handler(
        message,
        process_limit_and_invite,
        bot,
        session_manager,
        message_builder
    )

def status_command(message, bot, session_manager):
    """Handle the /status command."""
    user_id = message.from_user.id
    session_id = session_manager.find_active_session(user_id)
    
    if not session_id:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row('🔄 Start')
        keyboard.row('🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська')
        bot.send_message(message.chat.id, get_text('no_active_session', user_id), reply_markup=keyboard)

def cancel_command(message, bot, session_manager):
    """Handle the /cancel command."""
    user_id = message.from_user.id
    session_id = session_manager.find_active_session(user_id)
    
    if not session_id:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row('🔄 Start')
        keyboard.row('🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська')
        bot.send_message(message.chat.id, get_text('no_active_session', user_id), reply_markup=keyboard)

def stop_command(message, bot, session_manager):
    """Handle the /stop command."""
    user_id = message.from_user.id
    session_id = session_manager.find_active_session(user_id)
    
    if not session_id:
        bot.send_message(message.chat.id, get_text('no_active_session', user_id))
        return
        
    session_manager.delete_session(session_id)
    bot.send_message(message.chat.id, get_text('negotiation_ended', user_id))

def help_command(message, bot) -> None:
    """Handle the /help command."""
    user_id = message.from_user.id
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('🔄 Start')
    keyboard.row('🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська')
    bot.send_message(message.chat.id, get_text('help_text', user_id), reply_markup=keyboard)
