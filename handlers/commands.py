from datetime import datetime, timedelta
from telebot import types
from languages import TRANSLATIONS
from database import get_user_language
from utils.money import format_money
from utils.translations import get_text as translate_text  # Rename to avoid conflicts
from .negotiation import (
    handle_user2_session, handle_role_choice,
    find_active_session, format_expiry_time
)

def get_text(key: str, user_id: int, **kwargs) -> str:
    """Wrapper for translate_text to ensure it's always available"""
    return translate_text(key, user_id, **kwargs)

def start(message, bot, sessions: dict, user_sessions: dict) -> None:
    """Handle the /start command."""
    args = message.text.split()
    if len(args) > 1:
        session_id = args[1]
        if session_id in sessions:
            handle_user2_session(message, bot, session_id, sessions)
            return

    # Create role selection keyboard with emojis
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    user_id = message.from_user.id
    keyboard.row(
        f"🛒 {get_text('buyer', user_id)}", 
        f"💰 {get_text('seller', user_id)}"
    )
    keyboard.row(f"❓ {get_text('help', user_id)}")
    
    welcome_msg = f"👋 {get_text('welcome', user_id)}\n\n"
    welcome_msg += get_text('choose_role', user_id)
    
    bot.send_message(
        message.chat.id,
        welcome_msg,
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, handle_role_choice, bot, sessions, user_sessions)

def status_command(message, bot, sessions: dict) -> None:
    """Handle the /status command."""
    user_id = message.from_user.id
    session_id = find_active_session(user_id, sessions)
    
    if not session_id:
        bot.send_message(message.chat.id, f"📭 {get_text('no_active_session', user_id)}")
        return

    session = sessions[session_id]
    role = 'buyer' if ((session['initiator_id'] == user_id and session['initiator_role'] == 'buyer') or
                      (session['invited_id'] == user_id and session['initiator_role'] != 'buyer')) else 'seller'
    
    # Get own limit and role
    limit = (session['initiator_limit'] if user_id == session['initiator_id']
            else session.get('invited_limit'))

    # Create a status message with visual indicators
    status_msg = "📊 Negotiation Status:\n\n"
    
    # Add role indicator
    role_icon = "🛒" if role == 'buyer' else "💰"
    status_msg += f"{role_icon} {get_text('your_role', user_id)}: {get_text(role, user_id)}\n\n"
    
    # Add amount if set
    if limit:
        status_msg += f"💵 {get_text('your_amount', user_id)}: {format_money(limit, user_id)}\n"
        
        # Add status indicators
        if session['status'] == 'pending':
            status_msg += f"⏳ {get_text('waiting_for_other', user_id)}\n"
        elif session['status'] == 'completed':
            status_msg += f"✅ {get_text('deal_success', user_id)}\n"
        elif session['status'] == 'ended':
            status_msg += f"🚫 {get_text('negotiation_ended', user_id)}\n"
        
        # Add expiry time
        expires = format_expiry_time(session['expires_at'])
        if session['status'] not in ['completed', 'ended']:
            status_msg += f"\n⏰ {get_text('expires_in', user_id)} {expires}"
    else:
        status_msg += f"❓ {get_text('no_bid', user_id)}"

    # Create inline keyboard for actions if negotiation is active
    keyboard = None
    if session['status'] not in ['completed', 'ended']:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        new_amount_btn = types.InlineKeyboardButton(
            text=f"💱 {get_text('change_amount', user_id)}", 
            callback_data='new_amount'
        )
        end_btn = types.InlineKeyboardButton(
            text=f"🚫 {get_text('end_negotiation', user_id)}", 
            callback_data='end'
        )
        keyboard.row(new_amount_btn, end_btn)

    bot.send_message(
        message.chat.id,
        status_msg,
        reply_markup=keyboard
    )

def cancel_command(message, bot, sessions: dict) -> None:
    """Handle the /cancel command."""
    bot.send_message(message.chat.id, get_text('end_confirm', message.from_user.id))
    from .negotiation import handle_stop_confirmation  # Import here to avoid circular import
    bot.register_next_step_handler(message, handle_stop_confirmation, bot, sessions)

def help_command(message, bot) -> None:
    """Handle the /help command."""
    user_id = message.from_user.id
    help_text = get_text('help_text', user_id)
    
    # Create quick access keyboard
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    new_nego_btn = types.InlineKeyboardButton(
        text=f"🆕 {get_text('new_negotiation', user_id)}", 
        callback_data='new_negotiation'
    )
    status_btn = types.InlineKeyboardButton(
        text=f"📊 {get_text('check_status', user_id)}", 
        callback_data='check_status'
    )
    lang_btn = types.InlineKeyboardButton(
        text=f"🌐 {get_text('change_language', user_id)}", 
        callback_data='change_language'
    )
    
    keyboard.add(new_nego_btn)
    keyboard.row(status_btn, lang_btn)
    
    bot.reply_to(message, help_text, reply_markup=keyboard)
