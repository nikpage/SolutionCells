from typing import Optional
from utils.translations import get_text
from utils.money import format_money
from utils.time import format_expiry_time
from utils.session import Session

class MessageBuilder:
    def __init__(self, bot_name: str, bot_username: str):
        self.bot_name = bot_name
        self.bot_username = bot_username

    def build_welcome(self, user_id: int) -> str:
        return (f"👋 {get_text('welcome', user_id)}\n\n"
                f"{get_text('choose_role', user_id)}")

    def build_amount_prompt(self, user_id: int, role: str) -> str:
        return (f"👥 {get_text('step_select_role', user_id)}\n"
                f"💰 {get_text('enter_amount_buyer' if role == 'buyer' else 'enter_amount_seller', user_id)}")

    def build_confirmation(self, user_id: int, role: str, amount: int) -> str:
        return get_text('confirm_pay' if role == 'buyer' else 'confirm_get',
                       user_id, limit=format_money(amount, user_id))

    def build_invitation(self, session: Session, role: str) -> str:
        user_id = session.initiator_id
        question = get_text('enter_amount_seller' if role == 'buyer' else 'enter_amount_buyer', user_id)
        deep_link = f"https://t.me/{self.bot_username}?start={session.session_id}"
        expiry = format_expiry_time(session.expires_at)

        return (f"{self.bot_name}\n"
                f"💰 {question}\n\n"
                f"🔗 {deep_link}\n\n"
                f"⏳ {get_text('expires_in', user_id)} {expiry}")

    def build_waiting(self, user_id: int, role: str, expires_at: datetime) -> str:
        return get_text('waiting_for_seller' if role == 'buyer' else 'waiting_for_buyer',
                       user_id, expires=format_expiry_time(expires_at))

    def build_deal_success(self, user_id: int) -> str:
        return get_text('deal_success', user_id)

    def build_deal_failed(self, user_id: int) -> str:
        return get_text('deal_failed', user_id)