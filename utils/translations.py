from languages import TRANSLATIONS
from database import get_user_language

TRANSLATIONS = {
    'en': {
        'role_buyer': 'buyer',
        'role_seller': 'seller',
        'join_negotiation': 'Join my negotiation as a',
        'click_to_join': 'Click here to join',
        'share_with': 'Share with...',
        'select_role': 'Please select your role:',
        'enter_amount_buyer': 'Enter your maximum price:',
        'enter_amount_seller': 'Enter your minimum price:',
        'invalid_amount': 'Please enter a valid number.',
        'deal_success': 'Deal successful! The agreed price is {price}',
        'deal_failed': 'No deal possible. Your limits are too far apart.',
        'welcome': 'Welcome to the negotiation bot! Please select your role.',
        'negotiation_cancelled': 'Negotiation cancelled.',
        'no_active_session': 'No active negotiation session.',
        'invalid_number': 'Please enter a valid number.',
        'enter_new_amount': 'Please enter a new amount:',
        'negotiation_ended': 'Negotiation ended.',
        'cant_join_own': 'You cannot join your own negotiation.'
    },
    'cs': {
        'role_buyer': 'kupující',
        'role_seller': 'prodávající',
        'join_negotiation': 'Připojte se k mému vyjednávání jako',
        'click_to_join': 'Klikněte zde pro připojení',
        'share_with': 'Sdílet s...',
        'select_role': 'Vyberte svoji roli:',
        'enter_amount_buyer': 'Zadejte svoji maximální cenu:',
        'enter_amount_seller': 'Zadejte svoji minimální cenu:',
        'invalid_amount': 'Zadejte prosím platné číslo.',
        'deal_success': 'Dohoda uzavřena! Dohodnutá cena je {price}',
        'deal_failed': 'Dohoda není možná. Vaše limity jsou příliš vzdálené.',
        'welcome': 'Vítejte v negotiation botu! Vyberte svoji roli.',
        'negotiation_cancelled': 'Vyjednávání zrušeno.',
        'no_active_session': 'Žádné aktivní vyjednávání.',
        'invalid_number': 'Zadejte prosím platné číslo.',
        'enter_new_amount': 'Zadejte novou částku:',
        'negotiation_ended': 'Vyjednávání ukončeno.',
        'cant_join_own': 'Nemůžete se připojit k vlastnímu vyjednávání.'
    },
    'uk': {
        'role_buyer': 'покупець',
        'role_seller': 'продавець',
        'join_negotiation': 'Приєднайтесь до моїх переговорів як',
        'click_to_join': 'Натисніть тут, щоб приєднатися',
        'share_with': 'Поділитися з...',
        'select_role': 'Будь ласка, виберіть свою роль:',
        'enter_amount_buyer': 'Введіть максимальну ціну:',
        'enter_amount_seller': 'Введіть мінімальну ціну:',
        'invalid_amount': 'Будь ласка, введіть дійсне число.',
        'deal_success': 'Угода успішна! Узгоджена ціна {price}',
        'deal_failed': 'Угода неможлива. Ваші ліміти занадто далекі.',
        'welcome': 'Ласкаво просимо до бота переговорів! Виберіть свою роль.',
        'negotiation_cancelled': 'Переговори скасовано.',
        'no_active_session': 'Немає активної сесії переговорів.',
        'invalid_number': 'Будь ласка, введіть дійсне число.',
        'enter_new_amount': 'Будь ласка, введіть нову суму:',
        'negotiation_ended': 'Переговори завершено.',
        'cant_join_own': 'Ви не можете приєднатися до власних переговорів.'
    }
}

def get_text(key, user_id):
    """Get translated text for the given key and user's language."""
    lang = get_user_language(user_id)
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    return translations.get(key, TRANSLATIONS['en'].get(key, key))
