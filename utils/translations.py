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
        'deal_failed': 'Your offers are not within range.\n If you want to change your bid enter the number now.\n If you want to end the negotiation type end.',
        'welcome': 'Welcome to the negotiation bot! Please select your role.',
        'negotiation_cancelled': 'Negotiation cancelled.',
        'no_active_session': 'No active negotiation session.',
        'invalid_number': 'Please enter a valid number.',
        'enter_new_amount': 'Please enter a new amount:',
        'negotiation_ended': 'Negotiation ended.',
        'cant_join_own': 'You cannot join your own negotiation.'
    }
}

def get_text(key, user_id):
    """Get translated text for the given key and user's language."""
    lang = get_user_language(user_id)
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    return translations.get(key, TRANSLATIONS['en'].get(key, key))
