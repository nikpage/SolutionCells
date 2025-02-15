from datetime import datetime, timedelta
from telebot import types
from languages import TRANSLATIONS
from database import get_user_language, save_session
from utils.money import format_money
from utils.time import format_expiry_time
from utils.translations import get_text

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
        return buyer_limit >= seller_limit

def handle_user2_session(message, bot, session_id, sessions):
    session = sessions[session_id]
    user_id = message.from_user.id
    
    if user_id == session['initiator_id']:
        bot.send_message(message.chat.id, f"⚠️ {get_text('cant_join_own', user_id)}")
        return
        
    if 'invited_id' in session:
        bot.send_message(message.chat.id, f"⚠️ {get_text('session_invalid', user_id)}")
        return
        
    if session['expires_at'] < datetime.now():
        bot.send_message(message.chat.id, f"⏰ {get_text('session_expired', user_id)}")
        return
        
    other_role = 'seller' if session['initiator_role'] == 'buyer' else 'buyer'
    prompt = get_text('enter_amount_buyer', user_id) if other_role == 'buyer' else get_text('enter_amount_seller', user_id)
    
    # Create keyboard with cancel button
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('/cancel')
    
    session['invited_id'] = user_id
    save_session(session_id, sessions)
    
    welcome_msg = f"🤝 {get_text('joined_negotiation', user_id)}\n"
    welcome_msg += f"💰 {prompt}"
    
    bot.send_message(message.chat.id, welcome_msg, reply_markup=keyboard)
    bot.register_next_step_handler(message, process_limit, bot, sessions)

def handle_role_choice(message, bot, sessions, user_sessions):
    user_id = message.from_user.id
    role = message.text.lower()

    if role not in [get_text('buyer', user_id).lower(), get_text('seller', user_id).lower()]:
        from .commands import start  # Import here to avoid circular import
        return start(message, bot, sessions, user_sessions)

    role = 'buyer' if role == get_text('buyer', user_id).lower() else 'seller'

    session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    expires_at = datetime.now() + timedelta(hours=24)

    sessions[session_id] = {
        'initiator_id': user_id,
        'initiator_role': role,
        'status': 'pending',
        'created_at': datetime.now(),
        'expires_at': expires_at
    }
    save_session(session_id, sessions)

    if user_id not in user_sessions:
        user_sessions[user_id] = []
    user_sessions[user_id].append(session_id)

    # Add progress indicator and clearer instructions
    question = f"👥 {get_text('step_select_role', user_id)}\n"
    question += f"💰 {get_text('enter_amount_buyer', user_id)}" if role == 'buyer' else f"💰 {get_text('enter_amount_seller', user_id)}"
    
    # Add cancel button to keyboard
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('/cancel')
    
    bot.send_message(message.chat.id, question, reply_markup=keyboard)
    bot.register_next_step_handler(message, process_limit_and_invite, bot, sessions, user_sessions)

def create_message_for_user2(bot, role, session_id, expires_at, sessions):
    session = sessions[session_id]
    user_id = session['initiator_id']

    if role == 'buyer':
        question = get_text('enter_amount_seller', user_id)
    else:
        question = get_text('enter_amount_buyer', user_id)

    deep_link = f"https://t.me/{bot.get_me().username}?start={session_id}"
    expiry = format_expiry_time(expires_at)

    return (f"{bot.get_me().first_name}\n"
            f"{question}\n\n"
            f"👉 {get_text('click_to_respond', user_id)}: {deep_link}\n"
            f"⏳ {get_text('expires_in', user_id)} {expiry}")

def process_limit_and_invite(message, bot, sessions, user_sessions):
    user_id = message.from_user.id
    try:
        limit = int(message.text)
        if limit <= 0:
            raise ValueError()
    except ValueError:
        # Add example with currency symbol
        example = format_money(1000, user_id)
        bot.send_message(
            message.chat.id, 
            f"{get_text('invalid_number', user_id)}\n💡 {get_text('example', user_id)}: {example}"
        )
        return bot.register_next_step_handler(message, process_limit_and_invite, bot, sessions, user_sessions)

    session_id = user_sessions[user_id][-1]
    session = sessions[session_id]
    session['initiator_limit'] = limit
    role = session['initiator_role']
    
    # First message with amount confirmation
    confirmation = f"💰 {get_text('step_amount', user_id)}\n"
    confirmation += get_text('confirm_pay' if role == 'buyer' else 'confirm_get', 
                          user_id, limit=format_money(limit, user_id))
    
    bot.send_message(
        message.chat.id,
        confirmation,
        reply_markup=types.ReplyKeyboardRemove()
    )

    # Create forward-friendly invitation message
    deep_link = f"https://t.me/{bot.get_me().username}?start={session_id}"
    invitation_msg = create_message_for_user2(bot, role, session_id, session['expires_at'], sessions)
    
    # Send the invitation message for forwarding
    bot.send_message(
        message.chat.id,
        invitation_msg
    )
    
    save_session(session_id, sessions)

def process_limit(message, bot, sessions):
    user_id = message.from_user.id
    try:
        limit = int(message.text)
        if limit <= 0:
            raise ValueError()
    except ValueError:
        # Add currency example
        example = format_money(1000, user_id)
        error_msg = f"❌ {get_text('invalid_number', user_id)}\n"
        error_msg += f"💡 {get_text('example', user_id)}: {example}"
        bot.send_message(message.chat.id, error_msg)
        return bot.register_next_step_handler(message, process_limit, bot, sessions)
        
    session_id = find_active_session(user_id, sessions)
    if not session_id:
        bot.send_message(message.chat.id, f"❌ {get_text('no_active_session', user_id)}")
        return
        
    session = sessions[session_id]
    if session['expires_at'] < datetime.now():
        bot.send_message(message.chat.id, f"⏰ {get_text('session_expired', user_id)}")
        return
        
    role = 'buyer' if ((session['initiator_id'] == user_id and session['initiator_role'] == 'buyer') or
                      (session['invited_id'] == user_id and session['initiator_role'] != 'buyer')) else 'seller'
                      
    confirmation = get_text('confirm_pay' if role == 'buyer' else 'confirm_get',
                          user_id, limit=format_money(limit, user_id))
    waiting_msg = get_text('waiting_for_seller' if role == 'buyer' else 'waiting_for_buyer',
                          user_id, expires=format_expiry_time(session['expires_at']))
    
    if user_id == session.get('initiator_id'):
        session['initiator_limit'] = limit
    else:
        session['invited_limit'] = limit
        
    status_msg = f"✅ {get_text('amount_set', user_id)}\n"
    status_msg += f"💰 {confirmation}\n"
    status_msg += f"⏳ {waiting_msg}"
    
    # Send message without inline keyboard since we don't have handlers
    bot.send_message(message.chat.id, status_msg)
    save_session(session_id, sessions)
    
    if 'initiator_limit' in session and 'invited_limit' in session:
        compare_limits(session_id, bot, sessions)

def handle_stop_confirmation(message, bot, sessions):
    user_id = message.from_user.id
    if message.text.lower() == 'end':
        bot.send_message(message.chat.id, get_text('negotiation_ended', user_id))
        session_id = find_active_session(user_id, sessions)
        if session_id:
            session = sessions[session_id]
            other_id = session['invited_id'] if message.chat.id == session['initiator_id'] else session['initiator_id']
            bot.send_message(other_id, get_text('other_party_ended', other_id))
            session['status'] = 'ended'
            save_session(session_id, sessions, 'ended')
    else:
        bot.send_message(message.chat.id, get_text('enter_new_amount', user_id))
        bot.register_next_step_handler(message, process_limit, bot, sessions)

def compare_limits(session_id, bot, sessions):
    session = sessions[session_id]
    negotiation = NegotiationSession(session)
    is_deal = negotiation.compare_limits()

    initiator_id = session['initiator_id']
    invited_id = session['invited_id']

    # Calculate amounts for display
    buyer_limit, seller_limit = negotiation.calculate_limits()
    buyer_amount = format_money(buyer_limit, initiator_id)
    seller_amount = format_money(seller_limit, initiator_id)

    if is_deal:
        # Success message with visual comparison
        success_msg = f"✅ {get_text('deal_success', initiator_id)}\n\n"
        success_msg += f"💰 {get_text('final_amount', initiator_id)}: {seller_amount}\n"
        success_msg += f"🤝 {get_text('deal_complete', initiator_id)}"
        
        session['status'] = 'completed'
        # Send success messages
        bot.send_message(initiator_id, success_msg)
        bot.send_message(invited_id, success_msg)
    else:
        # Create visual comparison message
        comparison_msg = f"❌ {get_text('deal_failed', initiator_id)}\n\n"
        comparison_msg += f"📊 {get_text('price_difference', initiator_id)}:\n"
        comparison_msg += f"💰 {get_text('buyer_offers', initiator_id)}: {buyer_amount}\n"
        comparison_msg += f"💰 {get_text('seller_wants', initiator_id)}: {seller_amount}\n\n"
        comparison_msg += f"💡 {get_text('try_new_amount', initiator_id)}"

        session['status'] = 'awaiting_updates'
        session['buyer_updated'] = False
        session['seller_updated'] = False

        # Send comparison messages 
        bot.send_message(initiator_id, comparison_msg)
        bot.send_message(invited_id, comparison_msg)

    save_session(session_id, sessions, session['status'])

    if session['status'] == 'awaiting_updates':
        bot.register_next_step_handler_by_chat_id(initiator_id, process_limit, bot, sessions)
        bot.register_next_step_handler_by_chat_id(invited_id, process_limit, bot, sessions)

def find_active_session(user_id, sessions):
    for session_id, session in sessions.items():
        if ((session.get('initiator_id') == user_id or session.get('invited_id') == user_id) and
            session.get('status') in ['pending', 'awaiting_updates']):
            if session['expires_at'] > datetime.now():
                return session_id
            else:
                session['status'] = 'expired'
                save_session(session_id, sessions, 'expired')
    return None
