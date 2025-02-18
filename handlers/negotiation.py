from datetime import datetime
from telebot import types
from languages import TRANSLATIONS
from database import get_user_language, set_user_language
from utils.translations import get_text
from .language import handle_language_choice

class NegotiationSession:
    def __init__(self, session_data: dict):
        self.session = session_data

    def calculate_limits(self):
        if self.session['initiator_role'] == 'buyer':
            buyer_limit = self.session['initiator_limit']
            seller_limit = self.session['invited_limit']
        else:  # initiator is seller
            buyer_limit = self.session['invited_limit']
            seller_limit = self.session['initiator_limit']
        return buyer_limit, seller_limit

    def compare_limits(self):
        buyer_limit, seller_limit = self.calculate_limits()
        if buyer_limit >= seller_limit:
            return (buyer_limit + seller_limit) // 2
        else:
            return None

def handle_user2_session(message, bot, session_id, session_manager):
    # Check if it's a language selection first
    if message.text in ['🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська']:
        return handle_language_choice(message, bot, session_manager)

    session = session_manager.get_session(session_id)
    if not session:
        bot.send_message(message.chat.id, get_text('no_active_session', message.from_user.id))
        return

    # Check if user is trying to join their own session
    if message.from_user.id == session.initiator_id:
        bot.send_message(message.chat.id, get_text('cant_join_own', message.from_user.id))
        return

    # Set participant ID and role (opposite of initiator)
    session.invited_id = message.from_user.id
    session_manager.update_session(session_id, invited_id=message.from_user.id)
    
    # Add session to second user's active sessions
    if message.from_user.id not in session_manager.user_sessions:
        session_manager.user_sessions[message.from_user.id] = []
    session_manager.user_sessions[message.from_user.id].append(session_id)

    # Ask for amount based on predetermined role
    participant_role = 'buyer' if session.initiator_role == 'seller' else 'seller'
    bot.send_message(
        message.chat.id,
        get_text(f'enter_amount_{participant_role}', message.from_user.id)
    )
    bot.register_next_step_handler(message, process_limit, bot, session_manager)

def handle_role_choice(message, bot, session_manager, message_builder):
    user_id = message.from_user.id
    
    # Check if it's a language selection
    if message.text in ['🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська']:
        return handle_language_choice(message, bot, session_manager)
    
    role = message.text.lower().replace('🛒 ', '').replace('💰 ', '')

    if role not in [get_text('buyer', user_id).lower(), get_text('seller', user_id).lower()]:
        from .commands import start
        return start(message, bot, session_manager, message_builder)

    role = 'buyer' if role == get_text('buyer', user_id).lower() else 'seller'
    
    session_id = session_manager.create_session(user_id, role)
    session = session_manager.get_session(session_id)
    
    question = message_builder.build_amount_prompt(user_id, role)
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська')
    
    bot.send_message(message.chat.id, question, reply_markup=keyboard)
    bot.register_next_step_handler(message, process_limit_and_invite, bot, session_manager, message_builder)

def process_limit_and_invite(message, bot, session_manager, message_builder):
    if message.text in ['🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська']:
        return handle_language_choice(message, bot, session_manager)
        
    try:
        limit = int(message.text.strip())
        if limit <= 0:
            bot.send_message(message.chat.id, get_text('invalid_amount', message.from_user.id))
            return bot.register_next_step_handler(message, process_limit_and_invite, bot, session_manager, message_builder)
    except ValueError:
        bot.send_message(message.chat.id, get_text('invalid_amount', message.from_user.id))
        return bot.register_next_step_handler(message, process_limit_and_invite, bot, session_manager, message_builder)

    user_id = message.from_user.id
    session_id = session_manager.find_active_session(user_id)
    if not session_id:
        return
        
    session = session_manager.get_session(session_id)
    session.session['initiator_limit'] = limit
    session_manager.save_session(session_id, session)
    
    # Create the invitation message with role
    invite_link = f"https://t.me/{bot.get_me().username}?start={session_id}"
    
    # Create inline keyboard for sharing
    inline_keyboard = types.InlineKeyboardMarkup()
    other_role = 'seller' if session.session['initiator_role'] == 'buyer' else 'buyer'
    forward_text = (
        f"🤝 {get_text('join_negotiation', user_id)} {get_text(f'role_{other_role}', user_id)}!\n\n"
        f"{get_text('click_to_join', user_id)}: {invite_link}"
    )
    
    # Use Telegram's native share button
    inline_keyboard.row(
        types.InlineKeyboardButton(
            "📤 " + get_text('share_with', user_id),
            switch_inline_query=forward_text
        )
    )
    
    # Send the invitation message with share button
    msg = bot.send_message(
        message.chat.id,
        forward_text,
        reply_markup=inline_keyboard,
        disable_web_page_preview=True
    )
    
    # Pin the forward message for easy access
    try:
        bot.pin_chat_message(message.chat.id, msg.message_id)
    except:
        pass

def process_limit(message, bot, session_manager):
    # Check if it's a language selection
    if message.text in ['🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська']:
        return handle_language_choice(message, bot, session_manager)
    
    user_id = message.from_user.id
    try:
        limit = int(message.text.strip())
        if limit <= 0:
            bot.send_message(message.chat.id, get_text('invalid_amount', user_id))
            return bot.register_next_step_handler(message, process_limit, bot, session_manager)
    except ValueError:
        bot.send_message(message.chat.id, get_text('invalid_amount', user_id))
        return bot.register_next_step_handler(message, process_limit, bot, session_manager)

    # Find session where user is participant or initiator
    session_id = None
    for sid, session in session_manager._sessions.items():
        if ((session.initiator_id == user_id or session.invited_id == user_id) and
            session.status in ['pending', 'awaiting_updates']):
            if session.expires_at > datetime.now():
                session_id = sid
                break

    if not session_id:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('🇬🇧 English'))
        markup.add(types.KeyboardButton('🇨🇿 Čeština'))
        markup.add(types.KeyboardButton('🇺🇦 Українська'))
        bot.send_message(message.chat.id, get_text('no_active_session', user_id), reply_markup=markup)
        return

    session = session_manager.get_session(session_id)
    if not session:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('🇬🇧 English'))
        markup.add(types.KeyboardButton('🇨🇿 Čeština'))
        markup.add(types.KeyboardButton('🇺🇦 Українська'))
        bot.send_message(message.chat.id, get_text('no_active_session', user_id), reply_markup=markup)
        return

    # Update the limit for the appropriate user
    if user_id == session.initiator_id:
        session.initiator_limit = limit
        session_manager.update_session(session_id, initiator_limit=limit)
    else:
        session.invited_limit = limit
        session_manager.update_session(session_id, invited_limit=limit)

    # Check if both limits are set
    if session.initiator_limit is not None and session.invited_limit is not None:
        # Determine if there's a deal based on buyer/seller roles
        if session.initiator_role == 'buyer':
            buyer_limit = session.initiator_limit
            seller_limit = session.invited_limit
        else:
            buyer_limit = session.invited_limit
            seller_limit = session.initiator_limit

        if buyer_limit >= seller_limit:
            # Deal successful at seller's price
            agreed_price = seller_limit
            bot.send_message(
                message.chat.id,
                get_text('deal_success', user_id).format(price=agreed_price)
            )
            if session.initiator_id != user_id:
                bot.send_message(
                    session.initiator_id,
                    get_text('deal_success', session.initiator_id).format(price=agreed_price)
                )
            # Clean up the session
            session_manager.delete_session(session_id)
        else:
            # No deal possible, but allow new bids
            bot.send_message(message.chat.id, get_text('deal_failed', user_id))
            if session.initiator_id != user_id:
                bot.send_message(
                    session.initiator_id,
                    get_text('deal_failed', session.initiator_id)
                )

def handle_stop_confirmation(message, bot, session_manager):
    # Check if it's a language selection
    if message.text in ['🇬🇧 English', '🇨🇿 Čeština', '🇺🇦 Українська']:
        return handle_language_choice(message, bot, session_manager)
    
    user_id = message.from_user.id
    if message.text.lower() == 'end':
        session_id = session_manager.find_active_session(user_id)
        if session_id:
            session_manager.delete_session(session_id)
            bot.send_message(message.chat.id, get_text('negotiation_ended', user_id))
        else:
            bot.send_message(message.chat.id, get_text('no_active_session', user_id))
    else:
        bot.send_message(message.chat.id, get_text('negotiation_cancelled', user_id))

def register_forward_handler(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith('forward:'))
    def forward_callback(call):
        session_id = call.data.split(':')[1]
        session = session_manager.get_session(session_id)
        if not session:
            bot.answer_callback_query(call.id, "Session not found or expired")
            return
            
        invite_link = f"https://t.me/{bot.get_me().username}?start={session_id}"
        other_role = 'seller' if session.session['initiator_role'] == 'buyer' else 'buyer'
        forward_text = (
            f"🤝 Join my negotiation as a {other_role}!\n\n"
            f"Click here to join: {invite_link}"
        )
        
        bot.send_message(
            call.message.chat.id,
            forward_text,
            disable_web_page_preview=True
        )
        bot.answer_callback_query(call.id, "Message ready to forward!")

def find_active_session(user_id, sessions):
    for session_id, session in sessions.items():
        if ((session.initiator_id == user_id or session.invited_id == user_id) and
            session.status in ['pending', 'awaiting_updates']):
            if session.expires_at > datetime.now():
                return session_id
            else:
                session.status = 'expired'
                session_manager.save_session(session_id, session)
    return None
