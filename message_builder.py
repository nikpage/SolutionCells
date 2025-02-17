from utils.translations import get_text

class MessageBuilder:
    def __init__(self):
        pass
        
    def build_welcome(self, user_id):
        return get_text('welcome', user_id)
        
    def build_amount_prompt(self, user_id, role):
        return get_text(f'enter_amount_{role}', user_id)
