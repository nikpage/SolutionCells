# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-02-17

### Added
- Initial release of the Negotiation Bot
- Role selection (buyer/seller)
- Price negotiation with automatic deal calculation
- Multi-language support (English, Czech, Ukrainian)
- Real-time language switching
- Session management with unique IDs
- Share and forward functionality
- Command handlers (/start, /language, /status, /stop, /help)
- In-memory session storage
- Message builder with language support
- User language preferences in SQLite
- Automatic session cleanup
- Security checks for session access

### Technical Details
- Python 3.12+ compatibility
- pyTelegramBotAPI integration
- SQLite database for user preferences
- In-memory session management
- Message builder pattern
- Command handler pattern
- Real-time language switching without confirmation messages
- Automatic message updates in new language
