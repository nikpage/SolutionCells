from languages import TRANSLATIONS
from database import get_user_language

def get_text(key: str, user_id: int, **kwargs) -> str:
    """Get translated text for given key and user."""
    lang = get_user_language(user_id)
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['en'][key])
    return text.format(**kwargs) if kwargs else text
