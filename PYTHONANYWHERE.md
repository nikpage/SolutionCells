# PythonAnywhere Deployment Guide

## Initial Setup

1. **Log into PythonAnywhere**:
   - Go to https://www.pythonanywhere.com
   - Log into your account

2. **Open Bash Console**:
   - Click on `Consoles`
   - Click on `$ Bash`

3. **Clone Repository**:
   ```bash
   cd
   git clone https://github.com/nikpage/SolutionCells.git
   cd SolutionCells
   ```

4. **Install Dependencies**:
   ```bash
   pip3 install --user pyTelegramBotAPI
   ```

## Configuration

1. **Set Environment Variables**:
   - Go to "Files" tab
   - Create a new file `.env` in your project directory:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token
     ```

2. **Create Always-On Task**:
   - Go to "Tasks" tab
   - Add a new task
   - Set the command:
     ```bash
     cd ~/SolutionCells && python3 negotiator.py
     ```
   - Set it to run daily
   - Enable "Always-On"

## Verification Steps

1. **Check Bot Status**:
   ```bash
   # In PythonAnywhere Bash console
   ps aux | grep negotiator.py
   tail -f ~/SolutionCells/bot.log
   ```

2. **Test Basic Flow**:
   - First user:
     1. Send `/start` to bot
     2. Select role (buyer/seller)
     3. Enter price
     4. Share link
   - Second user:
     1. Click shared link
     2. Enter price
     3. Verify deal result

3. **Test Languages**:
   - Send `/language`
   - Test each language:
     - 🇬🇧 English
     - 🇨🇿 Czech
     - 🇺🇦 Ukrainian
   - Verify messages update correctly

4. **Test Edge Cases**:
   - Try joining your own negotiation
   - Enter invalid prices
   - Test all commands:
     - `/status`
     - `/stop`
     - `/help`
     - `/language`

## Monitoring

1. **View Logs**:
   ```bash
   # In PythonAnywhere Bash console
   cd ~/SolutionCells
   tail -f bot.log
   ```

2. **Check Database**:
   ```bash
   # In PythonAnywhere Bash console
   cd ~/SolutionCells
   sqlite3 users.db "SELECT * FROM user_preferences;"
   ```

3. **Monitor Process**:
   ```bash
   # In PythonAnywhere Bash console
   ps aux | grep negotiator.py
   ```

## Troubleshooting

1. **Bot Not Responding**:
   ```bash
   # Check if process is running
   ps aux | grep negotiator.py

   # Check logs
   tail -f ~/SolutionCells/bot.log

   # Restart bot
   kill $(pgrep -f "python3 negotiator.py")
   cd ~/SolutionCells && python3 negotiator.py &
   ```

2. **Database Issues**:
   ```bash
   cd ~/SolutionCells
   
   # Backup database
   cp users.db users.db.bak
   
   # Check integrity
   sqlite3 users.db "PRAGMA integrity_check;"
   ```

3. **Update Code**:
   ```bash
   cd ~/SolutionCells
   git pull origin main
   
   # Restart bot
   kill $(pgrep -f "python3 negotiator.py")
   python3 negotiator.py &
   ```

## Backup

1. **Manual Backup**:
   ```bash
   cd ~/SolutionCells
   
   # Backup database
   cp users.db "users_$(date +%Y%m%d).db"
   
   # Backup logs
   cp bot.log "bot_$(date +%Y%m%d).log"
   ```

2. **Download Backups**:
   - Go to "Files" tab
   - Select backup files
   - Click "Download"

## Important Notes

1. **PythonAnywhere Limitations**:
   - Free tier has CPU and bandwidth quotas
   - Web worker hours are limited
   - Always-on tasks require paid account

2. **Best Practices**:
   - Keep logs small (delete old logs)
   - Monitor CPU usage
   - Use try-except blocks for stability
   - Set up error notifications

3. **Security**:
   - Keep `.env` file secure
   - Don't expose database file
   - Use HTTPS for API calls
   - Monitor for suspicious activity
