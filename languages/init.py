from .en import ENGLISH
from .cs import CZECH
from .uk import UKRAINIAN

TRANSLATIONS = {
    'en': ENGLISH,
    'cs': CZECH,
    'uk': UKRAINIAN
}

CURRENCY_SETTINGS = {
    'en': {'symbol': '$', 'position': 'before'},  # $100
    'cs': {'symbol': 'Kč', 'position': 'after'},  # 100 Kč
    'uk': {'symbol': '₴', 'position': 'before'}   # ₴100
}
