from datetime import datetime, timedelta
from telebot import types
from database import get_user_language
from utils.translations import get_text
from session_manager import Session
import uuid

def handle_user2_session(message, bot, session_id, session_manager):
    """Handle user2 joining a session."""
    # Get the session
    session = session_manager.get_session(session_id)
    if not session:
        bot.send_message(
            message.chat.id,
            get_text("session_not_found", message.from_user.id)
        )
        return

    # Check if this user is already in another session
    user_sessions = session_manager.get_user_sessions(message.from_user.id)
    if user_sessions:
        bot.send_message(
            message.chat.id,
            get_text("already_in_session", message.from_user.id)
        )
        return

    # Update session with user2
    session.participant_id = message.from_user.id
    session.status = "waiting_for_participant_limit"
    session_manager.save_session(session_id, session)

    # Ask user2 for their limit
    role = "buyer" if session.initiator_role == "seller" else "seller"
    amount_key = f"enter_amount_{role}"
    force_reply = types.ForceReply(selective=True)
    bot.send_message(
        message.chat.id,
        get_text(amount_key, message.from_user.id),
        reply_markup=force_reply
    )
    
    # Register next step handler
    bot.register_next_step_handler(
        message,
        process_limit,
        bot,
        session_manager
    )

def process_limit_and_invite(message, bot, session_manager, message_builder):
    """Process the limit and create an invite link."""
    try:
        limit = float(message.text.strip().replace(",", "."))
        if limit <= 0:
            raise ValueError
    except ValueError:
        bot.send_message(
            message.chat.id,
            get_text("invalid_amount", message.from_user.id)
        )
        return bot.register_next_step_handler(message, process_limit_and_invite, bot, session_manager, message_builder)

    # Get the users active session
    user_sessions = session_manager.get_user_sessions(message.from_user.id)
    if not user_sessions:
        bot.send_message(
            message.chat.id,
            get_text("no_active_session", message.from_user.id)
        )
        return

    session_id = user_sessions[0]
    session = session_manager.get_session(session_id)
    if not session:
        bot.send_message(
            message.chat.id,
            get_text("session_not_found", message.from_user.id)
        )
        return

    # Update session with the limit
    session.initiator_limit = limit
    session.status = "waiting_for_participant"
    session_manager.save_session(session_id, session)

    # Create the invitation message
    invite_link = f"https://t.me/{bot.get_me().username}?start={session_id}"
    other_role = "seller" if session.initiator_role == "buyer" else "buyer"
    
    # Get role name in users language
    other_role_translated = get_text(f"role_{other_role}", message.from_user.id)
    join_text = "🤝 Join my negotiation as a"
    
    forward_text = (
        f" {join_text} {other_role_translated}!\n\n"
        f"👉 Click here to join: {invite_link}"
    )
    
    # Create inline keyboard for sharing
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(
        types.InlineKeyboardButton(
            "📤 Share with...",
            switch_inline_query=forward_text
        )
    )
    
    # Send the invitation message
    msg = bot.send_message(
        message.chat.id,
        forward_text,
        reply_markup=inline_keyboard,
        disable_web_page_preview=True
    )
    
    # Pin the message
    try:
        bot.pin_chat_message(message.chat.id, msg.message_id)
    except:
        pass

def process_limit(message, bot, session_manager):
    """Process the limit for user2."""
    try:
        limit = float(message.text.strip().replace(",", "."))
        if limit <= 0:
            raise ValueError
    except ValueError:
        if message.text.lower() == 'end':
            # If user types 'end', end session with no deal
            session_id = session_manager.find_active_session(message.from_user.id)
            if session_id:
                session = session_manager.get_session(session_id)
                if session:
                    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                    start_button = types.KeyboardButton(text="🔄 Start New Negotiation", web_app=None, request_contact=None, request_location=None)
                    keyboard.row(start_button)
                    for user_id in [session.initiator_id, session.participant_id]:
                        bot.send_message(
                            user_id,
                            "❌ No deal possible",
                            reply_markup=keyboard
                        )
                    session_manager.delete_session(session_id)
            return
        
        bot.send_message(
            message.chat.id,
            get_text("invalid_amount", message.from_user.id)
        )
        return bot.register_next_step_handler(message, process_limit, bot, session_manager)

    # Get session
    session_id = session_manager.find_active_session(message.from_user.id)
    if not session_id:
        return

    session = session_manager.get_session(session_id)
    if not session:
        return

    # Store limit based on user role
    if session.initiator_id == message.from_user.id:
        session.initiator_limit = limit
    else:
        session.participant_limit = limit
    
    session_manager.save_session(session_id, session)

    # Check if both limits are set
    if session.initiator_limit is None or session.participant_limit is None:
        return

    # Determine buyer and seller limits
    if session.initiator_role == "buyer":
        buyer_limit = session.initiator_limit
        seller_limit = session.participant_limit
    else:
        buyer_limit = session.participant_limit
        seller_limit = session.initiator_limit

    if buyer_limit >= seller_limit:
        # Deal successful at seller's price
        agreed_price = seller_limit
        keyboard = types.ReplyKeyboardMarkup(is_persistent=True, resize_keyboard=True)
        start_button = types.KeyboardButton(text="🔄 Start New Negotiation", web_app=None, request_contact=None, request_location=None)
        keyboard.row(start_button)
        for user_id in [session.initiator_id, session.participant_id]:
            bot.send_message(
                user_id,
                "🎉 Deal successful!",
                reply_markup=keyboard
            )
        session_manager.delete_session(session_id)
    else:
        # No deal possible, end round and let both users start new if they want
        keyboard = types.ReplyKeyboardMarkup(is_persistent=True, resize_keyboard=True)
        start_button = types.KeyboardButton(text="🔄 Start New Negotiation", web_app=None, request_contact=None, request_location=None)
        keyboard.row(start_button)
        for user_id in [session.initiator_id, session.participant_id]:
            bot.send_message(
                user_id,
                "❌ No deal possible",
                reply_markup=keyboard
            )
        session_manager.delete_session(session_id)
        return

def handle_stop_confirmation(message, bot, session_manager):
    """Handle confirmation of stopping a negotiation."""
    if message.text.lower() != get_text("stop_confirm", message.from_user.id).lower():
        return

    # Get users active session
    user_sessions = session_manager.get_user_sessions(message.from_user.id)
    if not user_sessions:
        bot.send_message(
            message.chat.id,
            get_text("no_active_session", message.from_user.id)
        )
        return

    session_id = user_sessions[0]
    session = session_manager.get_session(session_id)
    if not session:
        bot.send_message(
            message.chat.id,
            get_text("session_not_found", message.from_user.id)
        )
        return

    # Delete the session
    session_manager.delete_session(session_id)

    # Notify both users
    for user_id in [session.initiator_id, session.participant_id]:
        if user_id:  # participant_id might be None
            bot.send_message(
                user_id,
                get_text("negotiation_stopped", user_id)
            )
