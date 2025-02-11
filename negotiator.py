import os
import logging
import sqlite3
from datetime import datetime, timedelta
import telebot
from telebot import types
import threading
from typing import Dict, Optional

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

# Language dictionaries
SUPPORTED_LANGUAGES = ['en', 'cs', 'uk']  # English, Czech, Ukrainian

TRANSLATIONS = {
    'en': {
        'choose_role': "Choose your role:",
        'buyer': "Buyer",
        'seller': "Seller",
        'enter_amount_buyer': "What would you be happy to pay?",
        'enter_amount_seller': "What would you be happy to get?",
        'invalid_number': "Please enter a valid positive number.",
        'cant_join_own': "You can't join your own negotiation.",
        'session_invalid': "This negotiation session is no longer valid.",
        'session_expired': "This negotiation session has expired.",
        'forward_message': "Forward this message to continue:",
        'confirm_pay': "You would be happy to pay ${limit}",
        'confirm_get': "You would be happy to get ${limit}",
        'waiting_for_buyer': "⏳ Waiting for buyer. Expires in {expires}",
        'waiting_for_seller': "⏳ Waiting for seller. Expires in {expires}",
        'deal_success': "Congratulations, you are both in the same range! ✅",
        'deal_failed': "You are not within range.\nEnter new amount to continue bidding, or type 'stop' to stop negotiation.",
        'end_confirm': "Type 'end' to end negotiation, or continue with a new amount",
        'negotiation_ended': "Negotiation ended.",
        'other_party_ended': "The other party has ended the negotiation.",
        'enter_new_amount': "Please enter your new amount:",
        'no_active_session': "No active negotiation found.",
        'no_bid': "No bid set yet.",
        'click_to_respond': "Click here to respond",  # English
        'expires_in': "Session expires in",
        'help_text': """
Available commands:
/start - Begin new negotiation
/status - Check your current bid
/cancel - End current negotiation
/help - Show this help message
/language - Change language
        """,
        'choose_language': "Please select your language:",
        'language_set': "Language set to English"
    },
    'cs': {
        'choose_role': "Vyberte svoji roli:",
        'buyer': "Kupující",
        'seller': "Prodávající",
        'enter_amount_buyer': "Kolik byste byli ochotni zaplatit?",
        'enter_amount_seller': "Kolik byste chtěli dostat?",
        'invalid_number': "Prosím zadejte platné kladné číslo.",
        'cant_join_own': "Nemůžete se připojit k vlastnímu vyjednávání.",
        'session_invalid': "Toto vyjednávací sezení již není platné.",
        'session_expired': "Toto vyjednávací sezení vypršelo.",
        'forward_message': "Pro pokračování přepošlete tuto zprávu:",
        'confirm_pay': "Byli byste ochotni zaplatit ${limit}",
        'confirm_get': "Byli byste ochotni přijmout ${limit}",
        'waiting_for_buyer': "⏳ Čekání na kupujícího. Vyprší za {expires}",
        'waiting_for_seller': "⏳ Čekání na prodávajícího. Vyprší za {expires}",
        'deal_success': "Gratulujeme, jste ve stejném cenovém rozmezí! ✅",
        'deal_failed': "Nejste v cenovém rozmezí.\nZadejte novou částku pro pokračování, nebo napište 'stop' pro ukončení.",
        'end_confirm': "Napište 'end' pro ukončení vyjednávání, nebo pokračujte novou částkou",
        'negotiation_ended': "Vyjednávání ukončeno.",
        'other_party_ended': "Druhá strana ukončila vyjednávání.",
        'enter_new_amount': "Prosím zadejte novou částku:",
        'no_active_session': "Nenalezeno žádné aktivní vyjednávání.",
        'no_bid': "Zatím nebyla zadána žádná nabídka.",
        'click_to_respond': "Klikněte zde pro odpověď",  # Czech
        'expires_in': "Relace vyprší za",
        'help_text': """
Dostupné příkazy:
/start - Začít nové vyjednávání
/status - Zkontrolovat aktuální nabídku
/cancel - Ukončit vyjednávání
/help - Zobrazit tuto nápovědu
/language - Změnit jazyk
        """,
        'choose_language': "Prosím vyberte jazyk:",
        'language_set': "Jazyk nastaven na češtinu"
    },
    'uk': {
        'choose_role': "Оберіть свою роль:",
        'buyer': "Покупець",
        'seller': "Продавець",
        'enter_amount_buyer': "Скільки ви готові заплатити?",
        'enter_amount_seller': "Скільки ви хочете отримати?",
        'invalid_number': "Будь ласка, введіть дійсне додатне число.",
        'cant_join_own': "Ви не можете приєднатися до власних переговорів.",
        'session_invalid': "Ця сесія переговорів більше недійсна.",
        'session_expired': "Термін дії цієї сесії переговорів закінчився.",
        'forward_message': "Перешліть це повідомлення для продовження:",
        'confirm_pay': "Ви готові заплатити ${limit}",
        'confirm_get': "Ви готові прийняти ${limit}",
        'waiting_for_buyer': "⏳ Очікування покупця. Закінчується через {expires}",
        'waiting_for_seller': "⏳ Очікування продавця. Закінчується через {expires}",
        'deal_success': "Вітаємо, ви в однаковому ціновому діапазоні! ✅",
        'deal_failed': "Ви не в ціновому діапазоні.\nВведіть нову суму для продовження, або напишіть 'stop' для зупинки.",
        'end_confirm': "Напишіть 'end' для завершення переговорів, або продовжіть з новою сумою",
        'negotiation_ended': "Переговори завершено.",
        'other_party_ended': "Інша сторона завершила переговори.",
        'enter_new_amount': "Будь ласка, введіть нову суму:",
        'no_active_session': "Активних переговорів не знайдено.",
        'no_bid': "Ще не встановлено ставку.",
        'click_to_respond': "Натисніть тут, щоб відповісти",  # Ukrainian
        'expires_in': "Сесія закінчується через",
        'help_text': """
Доступні команди:
/start - Почати нові переговори
/status - Перевірити поточну ставку
/cancel - Завершити переговори
/help - Показати цю довідку
/language - Змінити мову
        """,
        'choose_language': "Будь ласка, оберіть мову:",
        'language_set': "Мову встановлено на українську"
    }
}

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

def get_user_language(user_id: int) -> str:
    """Get user's preferred language from database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'en'
        )
    ''')
    conn.commit()
    
    cursor.execute('SELECT language FROM user_preferences WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 'en'

def set_user_language(user_id: int, language: str) -> None:
    """Set user's preferred language in database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_preferences (user_id, language)
        VALUES (?, ?)
    ''', (user_id, language))
    conn.commit()

def get_text(key: str, user_id: int, **kwargs) -> str:
    """Get translated text for given key and user."""
    lang = get_user_language(user_id)
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['en'][key])
    return text.format(**kwargs) if kwargs else text

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
    # Using the initiator's ID for translations since this message will be forwarded
    session = sessions[session_id]
    user_id = session['initiator_id']

    if role == 'buyer':
        question = get_text('enter_amount_seller', user_id)
    else:
        question = get_text('enter_amount_buyer', user_id)

    deep_link = f"https://t.me/{BOT_USERNAME}?start={session_id}"
    expiry = format_expiry_time(expires_at)

    return (f"{BOT_NAME}\n"
            f"{question}\n\n"
            f"👉 {get_text('click_to_respond', user_id)}: {deep_link}\n"
            f"⏳ {get_text('expires_in', user_id)} {expiry}")

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

@bot.message_handler(commands=['language'])
def language_command(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('English 🇬🇧', 'Čeština 🇨🇿', 'Українська 🇺🇦')
    bot.send_message(message.chat.id, get_text('choose_language', message.from_user.id), 
                    reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_language_choice)

def handle_language_choice(message):
    lang_map = {
        'English 🇬🇧': 'en',
        'Čeština 🇨🇿': 'cs',
        'Українська 🇺🇦': 'uk'
    }
    chosen_lang = lang_map.get(message.text)
    if chosen_lang:
        set_user_language(message.from_user.id, chosen_lang)
        bot.send_message(message.chat.id, get_text('language_set', message.from_user.id),
                        reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "Please select a language from the keyboard.")
        return language_command(message)

@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    if len(args) > 1:
        session_id = args[1]
        if session_id in sessions:
            handle_user2_session(message, session_id)
            return

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(get_text('buyer', message.from_user.id), 
                get_text('seller', message.from_user.id))
    bot.send_message(message.chat.id, get_text('choose_role', message.from_user.id), 
                    reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_role_choice)

def handle_user2_session(message, session_id):
    session = sessions[session_id]
    user_id = message.from_user.id

    if user_id == session['initiator_id']:
        bot.send_message(message.chat.id, get_text('cant_join_own', user_id))
        return

    if 'invited_id' in session:
        bot.send_message(message.chat.id, get_text('session_invalid', user_id))
        return

    if session['expires_at'] < datetime.now():
        bot.send_message(message.chat.id, get_text('session_expired', user_id))
        return

    other_role = 'seller' if session['initiator_role'] == 'buyer' else 'buyer'
    prompt = get_text('enter_amount_buyer', user_id) if other_role == 'buyer' else get_text('enter_amount_seller', user_id)

    session['invited_id'] = user_id
    save_session(session_id)

    bot.send_message(message.chat.id, prompt)
    bot.register_next_step_handler(message, process_limit)

def handle_role_choice(message):
    user_id = message.from_user.id
    role = message.text.lower()

    if role not in [get_text('buyer', user_id).lower(), get_text('seller', user_id).lower()]:
        return start(message)

    role = 'buyer' if role == get_text('buyer', user_id).lower() else 'seller'
    
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

    question = get_text('enter_amount_buyer', user_id) if role == 'buyer' else get_text('enter_amount_seller', user_id)
    bot.send_message(message.chat.id, question, reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_limit_and_invite)

def process_limit_and_invite(message):
    user_id = message.from_user.id
    try:
        limit = int(message.text)
        if limit <= 0:
            raise ValueError()
    except ValueError:
        bot.send_message(message.chat.id, get_text('invalid_number', user_id))
        return bot.register_next_step_handler(message, process_limit_and_invite)

    session_id = user_sessions[user_id][-1]
    session = sessions[session_id]
    session['initiator_limit'] = limit
    save_session(session_id)

    role = session['initiator_role']
    confirmation = get_text('confirm_pay' if role == 'buyer' else 'confirm_get', user_id, limit=limit)
    bot.send_message(message.chat.id, f"✅ {confirmation}")

    msg_for_user2 = create_message_for_user2(role, session_id, session['expires_at'])
    bot.send_message(message.chat.id, get_text('forward_message', user_id))
    bot.send_message(message.chat.id, msg_for_user2)

def process_limit(message):
    if message.text.lower() == 'stop':
        bot.send_message(message.chat.id, get_text('end_confirm', message.from_user.id))
        return bot.register_next_step_handler(message, handle_stop_confirmation)

    try:
        limit = int(message.text)
        if limit <= 0:
            raise ValueError()
    except ValueError:
        bot.send_message(message.chat.id, get_text('invalid_number', message.from_user.id))
        return bot.register_next_step_handler(message, process_limit)

    user_id = message.chat.id
    session_id = find_active_session(user_id)
    if not session_id:
        bot.send_message(message.chat.id, get_text('no_active_session', user_id))
        return

    session = sessions[session_id]
    if session['expires_at'] < datetime.now():
        bot.send_message(message.chat.id, get_text('session_expired', user_id))
        return

    role = 'buyer' if ((session['initiator_id'] == user_id and session['initiator_role'] == 'buyer') or
                      (session['invited_id'] == user_id and session['initiator_role'] != 'buyer')) else 'seller'

    confirmation = get_text('confirm_pay' if role == 'buyer' else 'confirm_get', user_id, limit=limit)
    waiting_msg = get_text('waiting_for_seller' if role == 'buyer' else 'waiting_for_buyer', 
                          user_id, expires=format_expiry_time(session['expires_at']))

    if user_id == session.get('initiator_id'):
        session['initiator_limit'] = limit
    else:
        session['invited_limit'] = limit
        session['invited_id'] = user_id

    bot.send_message(message.chat.id, f"✅ {confirmation}\n{waiting_msg}")
    save_session(session_id)

    if 'initiator_limit' in session and 'invited_limit' in session:
        compare_limits(session_id)

def handle_stop_confirmation(message):
    if message.text.lower() == 'end':
        bot.send_message(message.chat.id, get_text('negotiation_ended', message.from_user.id))
        session_id = find_active_session(message.chat.id)
        if session_id:
            session = sessions[session_id]
            other_id = session['invited_id'] if message.chat.id == session['initiator_id'] else session['initiator_id']
            bot.send_message(other_id, get_text('other_party_ended', other_id))
            session['status'] = 'ended'
            save_session(session_id, 'ended')
    else:
        bot.send_message(message.chat.id, get_text('enter_new_amount', message.from_user.id))
        bot.register_next_step_handler(message, process_limit)

def compare_limits(session_id):
    session = sessions[session_id]
    
    negotiation = NegotiationSession(session)
    is_deal = negotiation.compare_limits()

    if is_deal:
        result = get_text('deal_success', session['initiator_id'])
        session['status'] = 'completed'
    else:
        result = get_text('deal_failed', session['initiator_id'])
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
        bot.send_message(message.chat.id, get_text('no_active_session', message.from_user.id))
        return

    session = sessions[session_id]
    user_id = message.chat.id
    role = 'buyer' if ((session['initiator_id'] == user_id and session['initiator_role'] == 'buyer') or
                      (session['invited_id'] == user_id and session['initiator_role'] != 'buyer')) else 'seller'

    limit = (session['initiator_limit'] if user_id == session['initiator_id']
            else session.get('invited_limit'))

    if limit:
        status = get_text('confirm_pay' if role == 'buyer' else 'confirm_get', user_id, limit=limit)
        expiry = get_text('waiting_for_seller' if role == 'buyer' else 'waiting_for_buyer', 
                         user_id, expires=format_expiry_time(session['expires_at']))
        bot.send_message(message.chat.id, f"{status}\n{expiry}")
    else:
        bot.send_message(message.chat.id, get_text('no_bid', user_id))

@bot.message_handler(commands=['cancel'])
def cancel_command(message):
    bot.send_message(message.chat.id, get_text('end_confirm', message.from_user.id))
    bot.register_next_step_handler(message, handle_stop_confirmation)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = get_text('help_text', message.from_user.id)
    bot.reply_to(message, help_text)

if __name__ == '__main__':
    try:
        get_db()
        logger.info(f"Bot started as {BOT_NAME}")
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Error: {e}")
