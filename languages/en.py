ENGLISH = {
    'welcome': 'Welcome to Negotiation Bot',
    'choose_role': "Choose your role:",
    'buyer': "Buyer",
    'seller': "Seller",
    'enter_amount_buyer': "What would you be happy to pay?",
    'enter_amount_seller': "What would you be happy to get?",
    'invalid_number': "Please enter a valid positive number.",
    'cant_join_own': "You can't join your own negotiation.",
    'session_invalid': "This negotiation session is no longer valid.",
    'session_expired': "This negotiation session has expired.",
    'confirm_pay': "You would be happy to pay {limit}",
    'confirm_get': "You would be happy to get {limit}",
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
    'click_to_respond': "Click here to respond",
    'expires_in': "Session expires in",
    
    # Progress indicators
    'step_select_role': 'Step 1: Choose your role',
    'step_amount': 'Step 2: Amount set',
    'step_share': 'Step 3: Share and wait',
    'step_complete': 'Step 4: Negotiation complete',
    
    # Button texts
    'share_link': 'Share link',
    'change_amount': 'Change amount',
    'new_amount': 'Try new amount',
    'cancel': 'Cancel',
    'end_negotiation': 'End negotiation',
    'new_negotiation': 'Start new negotiation',
    
    # Result messages
    'final_amount': 'Agreed amount',
    'deal_complete': 'Negotiation successfully completed!',
    'price_difference': 'Current offers',
    'buyer_offers': 'Buyer offers',
    'seller_wants': 'Seller wants',
    'try_new_amount': 'Try suggesting a new amount to reach agreement',
    
    # Help and settings
    'help_text': """
📋 Available commands:
/start - Begin new negotiation
/status - Check your current bid
/cancel - End current negotiation
/help - Show this help message
/language - Change language
    """,
    'choose_language': "Please select your language:",
    'language_set': "Language set to English",
    'help': 'Help',
    
    # Additional UX keys
    'your_role': 'Your role',
    'your_amount': 'Your amount',
    'waiting_for_other': 'Waiting for other party',
    'amount_set': 'Amount successfully set',
    'check_status': 'Check status',
    'change_language': 'Change language',
    'joined_negotiation': 'You joined the negotiation session',
    
    # Error messages
    'button_expired': 'This button has expired. Sending new message...',
    'error_occurred': 'An error occurred. Please try again.'
}

CZECH = {
    'choose_role': "Vyberte si roli:",
    'buyer': "Kupující",
    'seller': "Prodejce",
    'enter_amount_buyer': "Kolik byste byli ochotni zaplatit?",
    'enter_amount_seller': "Kolik byste byli ochotni dostat?",
    'invalid_number': "Zadejte platné kladné číslo.",
    'cant_join_own': "Nemůžete se připojit k vlastnímu vyjednávání.",
    'session_invalid': "Tato vyjednávací relace již není platná.",
    'session_expired': "Tato vyjednávací relace vypršela.",
    'forward_message': "Přepošlete tuto zprávu pro pokračování:",
    'confirm_pay': "Byli byste ochotni zaplatit {limit}",
    'confirm_get': "Byli byste ochotni dostat {limit}",
    'waiting_for_buyer': "⏳ Čeká se na kupujícího. Vyprší za {expires}",
    'waiting_for_seller': "⏳ Čeká se na prodejce. Vyprší za {expires}",
    'deal_success': "Gratulujeme, jste oba ve stejném rozmezí! ✅",
    'deal_failed': "Nejste v rozmezí.\nZadejte novou částku pro pokračování v nabízení, nebo napište 'stop' pro ukončení vyjednávání.",
    'end_confirm': "Napište 'end' pro ukončení vyjednávání, nebo pokračujte s novou částkou",
    'negotiation_ended': "Vyjednávání ukončeno.",
    'other_party_ended': "Druhá strana ukončila vyjednávání.",
    'enter_new_amount': "Zadejte svou novou částku:",
    'no_active_session': "Nebylo nalezeno žádné aktivní vyjednávání.",
    'no_bid': "Žádná nabídka zatím nebyla nastavena.",
    'click_to_respond': "Klikněte zde pro odpověď",
    'expires_in': "Relace vyprší za",
    'help_text': """
Dostupné příkazy:
/start - Zahájit nové vyjednávání
/status - Zkontrolujte svou aktuální nabídku
/cancel - Ukončit aktuální vyjednávání
/help - Zobrazit tuto nápovědu
/language - Změnit jazyk
    """,
    'choose_language': "Vyberte si jazyk:",
    'language_set': "Jazyk nastaven na češtinu",
    'help': 'Nápověda'
}

UKRAINIAN = {
    'choose_role': "Виберіть свою роль:",
    'buyer': "Покупець",
    'seller': "Продавець",
    'enter_amount_buyer': "Скільки ви готові заплатити?",
    'enter_amount_seller': "Скільки ви готові отримати?",
    'invalid_number': "Будь ласка, введіть дійсне позитивне число.",
    'cant_join_own': "Ви не можете приєднатися до власних переговорів.",
    'session_invalid': "Ця сесія переговорів більше не дійсна.",
    'session_expired': "Ця сесія переговорів закінчилася.",
    'forward_message': "Перешліть це повідомлення для продовження:",
    'confirm_pay': "Ви готові заплатити {limit}",
    'confirm_get': "Ви готові отримати {limit}",
    'waiting_for_buyer': "⏳ Очікування покупця. Закінчується через {expires}",
    'waiting_for_seller': "⏳ Очікування продавця. Закінчується через {expires}",
    'deal_success': "Вітаємо, ви обидва в одному діапазоні! ✅",
    'deal_failed': "Ви не в діапазоні.\nВведіть нову суму для продовження торгів, або напишіть 'stop' для зупинки переговорів.",
    'end_confirm': "Напишіть 'end' для завершення переговорів, або продовжуйте з новою сумою",
    'negotiation_ended': "Переговори завершено.",
    'other_party_ended': "Інша сторона завершила переговори.",
    'enter_new_amount': "Будь ласка, введіть нову суму:",
    'no_active_session': "Активних переговорів не знайдено.",
    'no_bid': "Ставка ще не встановлена.",
    'click_to_respond': "Натисніть тут, щоб відповісти",
    'expires_in': "Сесія закінчується через",
    'help_text': """
Доступні команди:
/start - Почати нові переговори
/status - Перевірте свою поточну ставку
/cancel - Завершити поточні переговори
/help - Показати це повідомлення довідки
/language - Змінити мову
    """,
    'choose_language': "Будь ласка, виберіть свою мову:",
    'language_set': "Мова встановлена на українську",
    'help': 'Довідка'
}
