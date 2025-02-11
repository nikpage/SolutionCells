import os
import logging
import sqlite3
from datetime import datetime, timedelta
import telebot
from telebot import types
import threading

print(f"Current directory: {os.getcwd()}")
try:
    logging.basicConfig(
        format='%(asctime)s | %(message)s',
        level=logging.INFO,
        filename='bot_debug.log',
        force=True
    )
    print("Logging setup complete")
except Exception as e:
    print(f"Logging setup failed: {e}")

logger = logging.getLogger(__name__)
try:
    logger.info("Starting bot...")
    print("First log message sent")
except Exception as e:
    print(f"Failed to write to log: {e}")

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
BOT_INFO = bot.get_me()
BOT_NAME = BOT_INFO.first_name
BOT_USERNAME = BOT_INFO.username

sessions = {}
user_sessions = {}
thread_local = threading.local()
SESSION_TIMEOUT = 24

class NegotiationSession:
    """Handles price comparison and deal validation for negotiation sessions."""

    def __init__(self, session_data: dict):
        self.session = session_data
        self.logger = logging.getLogger(__name__)

    def calculate_limits(self):
        """Calculate buyer and seller limits based on session data."""
        self.logger.debug(f"Debug - initiator role: {self.session['initiator_role']}, "
                         f"limit: {self.session['initiator_limit']}")
        self.logger.debug(f"Debug - invited user's limit: {self.session['invited_limit']}")

        # Fixed logic: Correctly assign limits based on initiator role
        if self.session['initiator_role'] == 'buyer':
            buyer_limit = self.session['initiator_limit']
            seller_limit = self.session['invited_limit']
        else:  # initiator is seller
            buyer_limit = self.session['invited_limit']
            seller_limit = self.session['initiator_limit']

        return buyer_limit, seller_limit

    def compare_limits(self):
        """Compare buyer and seller limits to determine if a deal is possible."""
        self.logger.debug("=== COMPARE LIMITS START ===")
        self.logger.debug(f"Full session data: {self.session}")

        buyer_limit, seller_limit = self.calculate_limits()

        self.logger.debug(f"Calculated buyer_limit: {buyer_limit}")
        self.logger.debug(f"Calculated seller_limit: {seller_limit}")

        is_deal = buyer_limit >= seller_limit
        self.logger.debug(f"Is deal? {is_deal}")
        self.logger.debug("=== COMPARE LIMITS END ===")

        return is_deal

def get_db():
    if not hasattr(thread_local, "conn"):
        thread_local.conn = sqlite3.connect('negotiations.db')
        cursor = thread_local.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                initiator_id INTEGER,
                invited_id INTEGER,
                initiator_role TEXT,
                initiator_limit INTEGER,
                invited_limit INTEGER,
                status TEXT,
                created_at DATETIME,
                expires_at DATETIME
            )
        ''')
        thread_local.conn.commit()
    return thread_local.conn

def save_session(session_id, status='pending', result=None):
    conn = get_db()
    cursor = conn.cursor()
    session = sessions[session_id]
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO sessions
            (session_id, initiator_id, invited_id, initiator_role,
             initiator_limit, invited_limit, status, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            session['initiator_id'],
            session.get('invited_id'),
            session['initiator_role'],
            session.get('initiator_limit'),
            session.get('invited_limit'),
            status,
            session.get('created_at'),
            session.get('expires_at')
        ))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"DB Error: {e}")

def format_expiry_time(expires_at):
    now = datetime.now()
    diff = expires_at - now
    hours = int(diff.total_seconds() / 3600)
    return f"{hours}h" if hours > 1 else "soon"

def create_message_for_user2(role, session_id, expires_at):
    if role == 'buyer':
        question = "What would you be happy to get?"
    else:
        question = "What would you be happy to pay?"

    deep_link = f"https://t.me/{BOT_USERNAME}?start={session_id}"
    expiry = format_expiry_time(expires_at)

    return (f"{BOT_NAME}\n"
            f"{question}\n\n"
            f"👉 Click here to respond: {deep_link}\n"
            f"⏳ Session expires in {expiry}")

def find_active_session(user_id):
    for session_id, session in sessions.items():
        if ((session.get('initiator_id') == user_id or session.get('invited_id') == user_id) and
            session.get('status') in ['pending', 'awaiting_updates']):
            if session['expires_at'] > datetime.now():
                return session_id
            else:
                session['status'] = 'expired'
                save_session(session_id, 'expired')
    return None

@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    if len(args) > 1:
        session_id = args[1]
        if session_id in sessions:
            handle_user2_session(message, session_id)
            return

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('Buyer', 'Seller')
    bot.send_message(message.chat.id, "Choose your role:", reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_role_choice)

def handle_user2_session(message, session_id):
    session = sessions[session_id]
    user_id = message.from_user.id

    if user_id == session['initiator_id']:
        bot.send_message(message.chat.id, "You can't join your own negotiation.")
        return

    if 'invited_id' in session:
        bot.send_message(message.chat.id, "This negotiation session is no longer valid.")
        return

    if session['expires_at'] < datetime.now():
        bot.send_message(message.chat.id, "This negotiation session has expired.")
        return

    other_role = 'seller' if session['initiator_role'] == 'buyer' else 'buyer'
    prompt = "What would you be happy to pay?" if other_role == 'buyer' else "What would you be happy to get?"

    session['invited_id'] = user_id
    save_session(session_id)

    bot.send_message(message.chat.id, prompt)
    bot.register_next_step_handler(message, process_limit)

def handle_role_choice(message):
    user_id = message.from_user.id
    role = message.text.lower()

    if role not in ['buyer', 'seller']:
        return start(message)

    session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    expires_at = datetime.now() + timedelta(hours=SESSION_TIMEOUT)

    sessions[session_id] = {
        'initiator_id': user_id,
        'initiator_role': role,
        'status': 'pending',
        'created_at': datetime.now(),
        'expires_at': expires_at
    }
    save_session(session_id)

    if user_id not in user_sessions:
        user_sessions[user_id] = []
    user_sessions[user_id].append(session_id)

    question = "What would you be happy to pay?" if role == 'buyer' else "What would you be happy to get?"
    bot.send_message(message.chat.id, question, reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_limit_and_invite)

def process_limit_and_invite(message):
    user_id = message.from_user.id
    try:
        limit = int(message.text)
        if limit <= 0:
            raise ValueError()
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid positive number.")
        return bot.register_next_step_handler(message, process_limit_and_invite)

    session_id = user_sessions[user_id][-1]
    session = sessions[session_id]
    session['initiator_limit'] = limit
    save_session(session_id)

    role = session['initiator_role']
    confirmation = f"You would be happy to {'pay' if role == 'buyer' else 'get'} ${limit}"
    bot.send_message(message.chat.id, f"✅ {confirmation}")

    msg_for_user2 = create_message_for_user2(role, session_id, session['expires_at'])
    bot.send_message(message.chat.id, "Forward this message to continue:")
    bot.send_message(message.chat.id, msg_for_user2)

def process_limit(message):
    if message.text.lower() == 'stop':
        bot.send_message(message.chat.id, "Type 'end' to end negotiation, or continue with a new amount")
        return bot.register_next_step_handler(message, handle_stop_confirmation)

    try:
        limit = int(message.text)
        if limit <= 0:
            raise ValueError()
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid positive number.")
        return bot.register_next_step_handler(message, process_limit)

    user_id = message.chat.id
    session_id = find_active_session(user_id)
    if not session_id:
        bot.send_message(message.chat.id, "Session not found or expired.")
        return

    session = sessions[session_id]
    if session['expires_at'] < datetime.now():
        bot.send_message(message.chat.id, "This session has expired.")
        return

    role = 'buyer' if ((session['initiator_id'] == user_id and session['initiator_role'] == 'buyer') or
                      (session['invited_id'] == user_id and session['initiator_role'] != 'buyer')) else 'seller'

    confirmation = f"You would be happy to {'pay' if role == 'buyer' else 'get'} ${limit}"
    waiting_msg = f"⏳ Waiting for {'seller' if role == 'buyer' else 'buyer'}. Expires in {format_expiry_time(session['expires_at'])}"

    if user_id == session.get('initiator_id'):
        session['initiator_limit'] = limit
    else:
        session['invited_limit'] = limit
        session['invited_id'] = user_id

    bot.send_message(message.chat.id, f"✅ {confirmation}\n{waiting_msg}")
    save_session(session_id)

    if 'initiator_limit' in session and 'invited_limit' in session:
        print(f"Debug - initiator role: {session['initiator_role']}, limit: {session['initiator_limit']}")
        print(f"Debug - invited user's limit: {session['invited_limit']}")
        compare_limits(session_id)

def handle_stop_confirmation(message):
    if message.text.lower() == 'end':
        bot.send_message(message.chat.id, "Negotiation ended.")
        session_id = find_active_session(message.chat.id)
        if session_id:
            session = sessions[session_id]
            other_id = session['invited_id'] if message.chat.id == session['initiator_id'] else session['initiator_id']
            bot.send_message(other_id, "The other party has ended the negotiation.")
            session['status'] = 'ended'
            save_session(session_id, 'ended')
    else:
        bot.send_message(message.chat.id, "Please enter your new amount:")
        bot.register_next_step_handler(message, process_limit)

def compare_limits(session_id):
    """Compare price limits using the fixed NegotiationSession class."""
    session = sessions[session_id]

    # Use the fixed NegotiationSession class for comparison
    negotiation = NegotiationSession(session)
    is_deal = negotiation.compare_limits()

    if is_deal:
        result = "Congratulations, you are both in the same range! ✅"
        session['status'] = 'completed'
    else:
        result = ("You are not within range.\n"
                 "Enter new amount to continue bidding, or type 'end' to end negotiation.\n"
                 "Note: Both parties must update their amounts to continue.")
        session['status'] = 'awaiting_updates'
        session['buyer_updated'] = False
        session['seller_updated'] = False

    save_session(session_id, session['status'])

    try:
        bot.send_message(session['initiator_id'], result)
        bot.send_message(session['invited_id'], result)

        if session['status'] == 'awaiting_updates':
            bot.register_next_step_handler_by_chat_id(session['initiator_id'], process_limit)
            bot.register_next_step_handler_by_chat_id(session['invited_id'], process_limit)
    except Exception as e:
        logger.error(f"Error: {e}")

@bot.message_handler(commands=['status'])
def status_command(message):
    session_id = find_active_session(message.chat.id)
    if not session_id:
        bot.send_message(message.chat.id, "No active negotiation found.")
        return

    session = sessions[session_id]
    user_id = message.chat.id
    role = 'buyer' if ((session['initiator_id'] == user_id and session['initiator_role'] == 'buyer') or
                      (session['invited_id'] == user_id and session['initiator_role'] != 'buyer')) else 'seller'

    limit = (session['initiator_limit'] if user_id == session['initiator_id']
            else session.get('invited_limit'))

    if limit:
        status = f"You would {'pay' if role == 'buyer' else 'accept'} ${limit}"
        expiry = f"\n⏳ Expires in {format_expiry_time(session['expires_at'])}"
        bot.send_message(message.chat.id, f"{status}{expiry}")
    else:
        bot.send_message(message.chat.id, "No bid set yet.")

@bot.message_handler(commands=['cancel'])
def cancel_command(message):
    bot.send_message(message.chat.id, "Type 'end' to end negotiation, or continue with a new amount")
    bot.register_next_step_handler(message, handle_stop_confirmation)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = f"""
Available commands:
/start - Begin new negotiation
/status - Check your current bid
/cancel - End current negotiation
/help - Show this help message
    """
    bot.reply_to(message, help_text)

if __name__ == '__main__':
    try:
        get_db()
        logger.info(f"Bot started as {BOT_NAME}")
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Error: {e}")
