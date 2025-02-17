# SolutionCells Negotiation Bot v1.0.0

A Telegram bot that facilitates price negotiations between buyers and sellers.

## Features

- **Role Selection**: Users can choose to be either a buyer or seller
- **Price Negotiation**: 
  - Buyers set maximum price
  - Sellers set minimum price
  - Automatic deal calculation if prices overlap
- **Multi-language Support**:
  - 🇬🇧 English
  - 🇨🇿 Czech
  - 🇺🇦 Ukrainian
  - Language can be changed at any time during negotiation
- **Session Management**:
  - One active negotiation per user
  - Unique session IDs for each negotiation
  - Automatic session cleanup after completion
- **Share & Forward**:
  - Shareable invitation links
  - Built-in Telegram share button
  - Message pinning for easy access

## Technical Details

### Components

1. **Session Manager**:
   - In-memory session storage
   - Session tracking by unique ID
   - Participant management
   - Session state tracking

2. **Message Builder**:
   - Handles message construction
   - Supports multiple languages
   - Dynamic message updates

3. **Language Handler**:
   - Real-time language switching
   - Message updates in new language
   - Persistent user language preferences

4. **Command Handlers**:
   - `/start`: Begin negotiation
   - `/language`: Change language
   - `/status`: Check negotiation status
   - `/stop`: End negotiation
   - `/help`: Show help message

### Data Structures

1. **Session**:
   ```python
   @dataclass
   class Session:
       initiator_id: int
       initiator_role: str
       initiator_limit: Optional[int]
       participant_id: Optional[int]
       participant_limit: Optional[int]
       status: str
   ```

2. **Message Flow**:
   - Role Selection → Price Input → Share Link → Participant Price Input → Result

### Dependencies

- Python 3.12+
- `pyTelegramBotAPI` for Telegram integration
- SQLite for user preferences storage

## Important Notes

1. **Session Handling**:
   - Sessions are not persistent (in-memory only)
   - One active session per user
   - Sessions expire after completion or cancellation

2. **Price Calculation**:
   - Deal successful if buyer_limit ≥ seller_limit
   - Agreed price = (buyer_limit + seller_limit) / 2
   - All prices must be positive integers

3. **Language Support**:
   - Language changes affect all future messages
   - Last message is automatically updated in new language
   - Default language is English

4. **Security**:
   - Users cannot join their own negotiations
   - Each session has a unique ID
   - Invalid session IDs are rejected

## Future Improvements

1. **Persistence**:
   - Add persistent session storage
   - Add negotiation history
   - Add user statistics

2. **Features**:
   - Add more languages
   - Add price suggestions
   - Add negotiation timeouts
   - Add message templates

3. **UI/UX**:
   - Add inline keyboards for all actions
   - Add progress indicators
   - Add confirmation dialogs
   - Add help messages for each step
