import os
from typing import Dict, Optional
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    ConversationHandler, 
    filters,
    ContextTypes
)
import sqlite3
from datetime import datetime

class NegotiationPriceBot:
    # Conversation states
    (CHOOSE_ROLE, 
     BUYER_LIMIT, 
     SELLER_LIMIT, 
     NEGOTIATION_RESULT) = range(4)

    def __init__(self, token: str):
        self.token = token
        self.negotiations: Dict[int, Dict[str, Optional[int]]] = {}
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database for storing negotiation data"""
        self.conn = sqlite3.connect('negotiations.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS negotiations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                initial_limit INTEGER,
                final_limit INTEGER,
                rounds INTEGER,
                result TEXT,
                timestamp DATETIME
            )
        ''')
        self.conn.commit()

    def save_negotiation_data(self, user_id: int, role: str, initial_limit: int, 
                               final_limit: Optional[int], rounds: int, result: str):
        """Save negotiation data to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO negotiations 
            (user_id, role, initial_limit, final_limit, rounds, result, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 
            role, 
            initial_limit, 
            final_limit, 
            rounds, 
            result, 
            datetime.now()
        ))
        self.conn.commit()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the negotiation process"""
        keyboard = [['Buyer', 'Seller']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        
        await update.message.reply_text(
            "Welcome to Price Negotiation Bot! Choose your role:", 
            reply_markup=reply_markup
        )
        return self.CHOOSE_ROLE

    async def choose_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process role selection"""
        user_id = update.effective_user.id
        role = update.message.text.lower()
        
        if role not in ['buyer', 'seller']:
            await update.message.reply_text("Please choose either 'Buyer' or 'Seller'")
            return self.CHOOSE_ROLE
        
        # Initialize negotiation context
        if user_id not in self.negotiations:
            self.negotiations[user_id] = {}
        
        self.negotiations[user_id]['role'] = role

        await update.message.reply_text(
            f"You are a {role}. Enter your price limit:", 
            reply_markup=ReplyKeyboardRemove()
        )
        return self.BUYER_LIMIT if role == 'buyer' else self.SELLER_LIMIT

    async def process_buyer_limit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process buyer's price limit"""
        user_id = update.effective_user.id
        try:
            buyer_limit = int(update.message.text)
            self.negotiations[user_id]['buyer_limit'] = buyer_limit
            
            # If seller's limit already exists, compare
            if 'seller_limit' in self.negotiations[user_id]:
                return await self.compare_limits(update, context)
            
            await update.message.reply_text("Waiting for seller's limit...")
            return self.SELLER_LIMIT
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")
            return self.BUYER_LIMIT

    async def process_seller_limit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process seller's price limit"""
        user_id = update.effective_user.id
        try:
            seller_limit = int(update.message.text)
            self.negotiations[user_id]['seller_limit'] = seller_limit
            
            # If buyer's limit already exists, compare
            if 'buyer_limit' in self.negotiations[user_id]:
                return await self.compare_limits(update, context)
            
            await update.message.reply_text("Waiting for buyer's limit...")
            return self.BUYER_LIMIT
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")
            return self.SELLER_LIMIT

    async def compare_limits(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Compare buyer and seller limits"""
        user_id = update.effective_user.id
        negotiation = self.negotiations[user_id]
        
        buyer_limit = negotiation['buyer_limit']
        seller_limit = negotiation['seller_limit']
        
        if buyer_limit >= seller_limit:
            result = "Agreement Possible"
            message = "Great news! You are within the same price range."
        else:
            result = "No Agreement"
            message = "Unfortunately, your price ranges do not overlap."
        
        # Save negotiation data
        self.save_negotiation_data(
            user_id=user_id,
            role=negotiation['role'],
            initial_limit=buyer_limit if negotiation['role'] == 'buyer' else seller_limit,
            final_limit=None,
            rounds=1,
            result=result
        )
        
        await update.message.reply_text(message)
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the negotiation"""
        await update.message.reply_text("Negotiation cancelled.")
        return ConversationHandler.END

    def build_application(self) -> Application:
        """Build the Telegram bot application"""
        application = Application.builder().token(self.token).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                self.CHOOSE_ROLE: [
                    MessageHandler(filters.Regex('^(Buyer|Seller)$'), self.choose_role)
                ],
                self.BUYER_LIMIT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_buyer_limit)
                ],
                self.SELLER_LIMIT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_seller_limit)
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        application.add_handler(conv_handler)
        return application

def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        raise ValueError("No Telegram Bot Token found. Set TELEGRAM_BOT_TOKEN environment variable.")
    
    bot = NegotiationPriceBot(TOKEN)
    application = bot.build_application()
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()