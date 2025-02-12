from languages import CURRENCY_SETTINGS
from database import get_user_language

def format_money(amount: int, user_id: int) -> str:
    """Format amount according to user's language currency settings."""
    lang = get_user_language(user_id)
    settings = CURRENCY_SETTINGS[lang]
    
    if settings['position'] == 'before':
        return f"{settings['symbol']}{amount}"
    else:
        return f"{amount} {settings['symbol']}"
