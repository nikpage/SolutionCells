from datetime import datetime
from telebot import types
from languages import TRANSLATIONS
from database import get_user_language, save_session
from utils.money import format_money
from utils.time import format_expiry_time
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
        return buyer_limit >= seller_limit

def handle_user2_session(message, bot, session_id, session_manager):
    # Check if it's a language selection first
    if message.text in ['English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦']:
        return handle_language_choice(message, bot)

    session = session_manager.get_session(session_id)
    if not session:
        return
        
    user_id = message.from_user.id
    
    if user_id == session.initiator_id:
        bot.send_message(message.chat.id, f"⚠️ {get_text('cant_join_own', user_id)}")
        return
        
    if session.invited_id:
        bot.send_message(message.chat.id, f"⚠️ {get_text('session_invalid', user_id)}")
        return
        
    if session.expires_at < datetime.now():
        bot.send_message(message.chat.id, f"⏰ {get_text('session_expired', user_id)}")
        return
        
    other_role = 'seller' if session.initiator_role == 'buyer' else 'buyer'
    prompt = get_text('enter_amount_buyer', user_id) if other_role == 'buyer' else get_text('enter_amount_seller', user_id)
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('/cancel')
    
    session.invited_id = user_id
    save_session(session_id, session)
    
    welcome_msg = f"🤝 {get_text('joined_negotiation', user_id)}\n"
    welcome_msg += f"💰 {prompt}"
    
    bot.send_message(message.chat.id, welcome_msg, reply_markup=keyboard)
    bot.register_next_step_handler(message, process_limit, bot, session_manager)

def handle_role_choice(message, bot, session_manager, message_builder):
    user_id = message.from_user.id
    
    # Check if it's a language selection
    if message.text in ['English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦']:
        return handle_language_choice(message, bot)
    
    role = message.text.lower().replace('🛒 ', '').replace('💰 ', '')

    if role not in [get_text('buyer', user_id).lower(), get_text('seller', user_id).lower()]:
        from .commands import start
        return start(message, bot, session_manager, message_builder)

    role = 'buyer' if role == get_text('buyer', user_id).lower() else 'seller'
    
    session_id = session_manager.create_session(user_id, role)
    session = session_manager.get_session(session_id)
    
    question = message_builder.build_amount_prompt(user_id, role)
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('/cancel')
    keyboard.row('English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦')
    
    bot.send_message(message.chat.id, question, reply_markup=keyboard)
    bot.register_next_step_handler(message, process_limit_and_invite, bot, session_manager, message_builder)

def process_limit_and_invite(message, bot, session_manager, message_builder):
    # Check if it's a language selection first
    if message.text in ['English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦']:
        return handle_language_choice(message, bot)
    
    user_id = message.from_user.id
    try:
        limit = int(message.text)
        if limit <= 0:
            raise ValueError()
    except ValueError:
        bot.send_message(
            message.chat.id, 
            get_text('invalid_number', user_id)
        )
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add('/cancel')
        keyboard.row('English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦')
        bot.send_message(message.chat.id, get_text('enter_new_amount', user_id), reply_markup=keyboard)
        return bot.register_next_step_handler(message, process_limit_and_invite, bot, session_manager, message_builder)

    session_id = session_manager.find_active_session(user_id)
    if not session_id:
        return
        
    session = session_manager.get_session(session_id)
    session.initiator_limit = limit
    save_session(session_id, session)
    
    confirmation = message_builder.build_confirmation(user_id, session.initiator_role, limit)
    bot.send_message(message.chat.id, confirmation)

    invite_msg = message_builder.build_invitation(session, session.initiator_role)
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row('English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦')
    bot.send_message(message.chat.id, invite_msg, reply_markup=keyboard)

    # Register the next step handler to continue the negotiation process
    bot.register_next_step_handler(message, process_limit, bot, session_manager)

def process_limit(message, bot, session_manager):
    # Check if it's a language selection
    if message.text in ['English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦']:
        return handle_language_choice(message, bot)
    
    user_id = message.from_user.id
    try:
        limit = int(message.text)
        if limit <= 0:
            raise ValueError()
    except ValueError:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add('/cancel')
        keyboard.row('English 🇬🇧', 'Čeština 🇨‚', 'Українська 🇺🇦')
        bot.send_message(message.chat.id, get_text('invalid_number', user_id), reply_markup=keyboard)
        return bot.register_next_step_handler(message, process_limit, bot, session_manager)
        
    session_id = session_manager.find_active_session(user_id)
    if not session_id:
        bot.send_message(message.chat.id, get_text('no_active_session', user_id))
        return
        
    session = session_manager.get_session(session_id)
    if session.expires_at < datetime.now():
        bot.send_message(message.chat.id, get_text('session_expired', user_id))
        return
        
    role = 'buyer' if ((session.initiator_id == user_id and session.initiator_role == 'buyer') or
                      (session.invited_id == user_id and session.initiator_role != 'buyer')) else 'seller'
                      
    confirmation = get_text('confirm_pay' if role == 'buyer' else 'confirm_get',
                          user_id, limit=format_money(limit, user_id))
    
    if user_id == session.initiator_id:
        session.initiator_limit = limit
        waiting_msg = get_text('waiting_for_seller' if role == 'buyer' else 'waiting_for_buyer',
                             user_id, expires=format_expiry_time(session.expires_at))
        bot.send_message(message.chat.id, confirmation)
        bot.send_message(message.chat.id, waiting_msg)
    else:
        session.invited_limit = limit
        bot.send_message(message.chat.id, confirmation)
        
    save_session(session_id, session)
    
    if session.initiator_limit and session.invited_limit:
        compare_limits(session_id, bot, session_manager)

def handle_stop_confirmation(message, bot, session_manager):
    # Check if it's a language selection
    if message.text in ['English 🇬🇧', 'Čeština 🇨‚', 'Українська 🇺🇦']:
        return handle_language_choice(message, bot)
    
    user_id = message.from_user.id
    if message.text.lower() == 'end':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.row('English 🇬🇧', 'Čeština 🇨‚', 'Українська 🇺🇦')
        bot.send_message(message.chat.id, get_text('negotiation_ended', user_id), reply_markup=keyboard)
        session_id = session_manager.find_active_session(user_id)
        if session_id:
            session = session_manager.get_session(session_id)
            other_id = session.invited_id if message.chat.id == session.initiator_id else session.initiator_id
            bot.send_message(other_id, get_text('other_party_ended', other_id))
            session_manager.end_session(session_id)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('/cancel')
        keyboard.row('English 🇬‚', 'Čeština 🇨‚', 'Українська 🇺🇦')
        bot.send_message(message.chat.id, get_text('enter_new_amount', user_id), reply_markup=keyboard)
        bot.register_next_step_handler(message, process_limit, bot, session_manager)

def compare_limits(session_id, bot, session_manager):
    session = session_manager.get_session(session_id)
    if not session:
        return

    is_deal = session_manager.is_deal_successful(session_id)
    if is_deal:
        success_msg = get_text('deal_success', session.initiator_id)
        session.status = 'completed'
        bot.send_message(session.initiator_id, success_msg)
        bot.send_message(session.invited_id, success_msg)
        save_session(session_id, session, 'completed')
    else:
        session.status = 'awaiting_updates'
        bot.send_message(session.initiator_id, get_text('deal_failed', session.initiator_id))
        bot.send_message(session.invited_id, get_text('deal_failed', session.invited_id))
        save_session(session_id, session, 'awaiting_updates')
        bot.register_next_step_handler_by_chat_id(session.initiator_id, process_limit, bot, session_manager)
        bot.register_next_step_handler_by_chat_id(session.invited_id, process_limit, bot, session_manager)

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
