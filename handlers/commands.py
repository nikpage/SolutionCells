from datetime import datetime, timedelta
from telebot import types
from languages import TRANSLATIONS
from database import get_user_language
from utils.money import format_money
from .negotiation import (
    handle_user2_session, handle_role_choice, 
    find_active_session, format_expiry_time
)

def start(message, bot, sessions, user_sessions):
    args = message.text.split()
    if len(args) > 1:
        session_id = args[1]
        if session_id in sessions:
            handle_user2_session(message, bot, session_id, sessions)
            return

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(
        get_text('buyer', message.from_user.id), 
        get_text('seller', message.from_user.id)
    )
    bot.send_message(
        message.chat.id, 
        get_text('choose_role', message.from_user.id), 
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, handle_role_choice, bot, sessions, user_sessions)

def status_command(message, bot, sessions):
    user_id = message.from_user.id
    session_id = find_active_session(user_id, sessions)
    if not session_id:
        bot.send_message(message.chat.id, get_text('no_active_session', user_id))
        return

    session = sessions[session_id]
    role = 'buyer' if ((session['initiator_id'] == user_id and session['initiator_role'] == 'buyer') or
                      (session['invited_id'] == user_id and session['initiator_role'] != 'buyer')) else 'seller'

    limit = (session['initiator_limit'] if user_id == session['initiator_id']
            else session.get('invited_limit'))

    if limit:
        status = get_text('confirm_pay' if role == 'buyer' else 'confirm_get', 
                         user_id, limit=format_money(limit, user_id))
        expiry = get_text('waiting_for_seller' if role == 'buyer' else 'waiting_for_buyer', 
                         user_id, expires=format_expiry_time(session['expires_at']))
        bot.send_message(message.chat.id, f"{status}\n{expiry}")
    else:
        bot.send_message(message.chat.id, get_text('no_bid', user_id))

def cancel_command(message, bot, sessions):
    bot.send_message(message.chat.id, get_text('end_confirm', message.from_user.id))
    from .negotiation import handle_stop_confirmation  # Import here to avoid circular import
    bot.register_next_step_handler(message, handle_stop_confirmation, bot, sessions)

def help_command(message, bot):
    help_text = get_text('help_text', message.from_user.id)
    bot.reply_to(message, help_text)
