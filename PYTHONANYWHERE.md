# PythonAnywhere Deployment Guide

## Directory Structure

```
/home/p23/
    ├── CHANGELOG.md
    ├── PRODUCTION.md
    ├── PYTHONANYWHERE.md
    ├── README.md
    ├── SolutionCells/        # Git repository
    ├── VERSION
    ├── database/
    ├── flask_app.py
    ├── handlers/
    ├── languages/
    ├── message_builder.py
    ├── myenv/               # Virtual environment
    ├── mysite/
    ├── negotiations.db
    ├── negotiator.py
    ├── requirements.txt
    ├── session_manager.py
    ├── utils/
    └── webhook.log
```

## Initial Setup

1. **Open Bash Console**:
   - Click on `Consoles`
   - Click on `$ Bash`

2. **Setup Project Directory**:
   ```bash
   cd /home/p23
   git clone https://github.com/nikpage/SolutionCells.git SolutionCells
   ```
   Note: The dot (.) at the end clones directly into the current directory

3. **Install Dependencies**:
   ```bash
   cd /home/p23
   source myenv/bin/activate
   pip install pyTelegramBotAPI
   ```

## Configuration

1. **Set Environment Variables**:
   - Go to "Files" tab
   - Navigate to `/home/p23`
   - Create `.env`:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token
     ```

2. **Create Always-On Task**:
   - Go to "Tasks" tab
   - Add new task
   - Command:
     ```bash
     cd /home/p23 && source myenv/bin/activate && python3 negotiator.py
     ```
   - Set to run daily
   - Enable "Always-On"

## Verification Steps

1. **Check Bot Status**:
   ```bash
   # In PythonAnywhere Bash console
   cd /home/p23
   ps aux | grep negotiator.py
   tail -f webhook.log
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
   cd /home/p23
   tail -f webhook.log
   ```

2. **Check Database**:
   ```bash
   # In PythonAnywhere Bash console
   cd /home/p23
   sqlite3 negotiations.db "SELECT * FROM user_preferences;"
   ```

3. **Monitor Process**:
   ```bash
   # In PythonAnywhere Bash console
   ps aux | grep negotiator.py
   ```

## Troubleshooting

1. **Bot Not Responding**:
   ```bash
   cd /home/p23
   source myenv/bin/activate
   
   # Check if process is running
   ps aux | grep negotiator.py

   # Check logs
   tail -f webhook.log

   # Restart bot
   kill $(pgrep -f "python3 negotiator.py")
   python3 negotiator.py &
   ```

2. **Database Issues**:
   ```bash
   cd /home/p23
   
   # Backup database
   cp negotiations.db negotiations.db.bak
   
   # Check integrity
   sqlite3 negotiations.db "PRAGMA integrity_check;"
   ```

3. **Update Code**:
   ```bash
   cd /home/p23/SolutionCells
   git pull origin main
   
   # Copy updated files
   cp -r handlers/ ../
   cp -r database/ ../
   cp -r utils/ ../
   cp -r languages/ ../
   cp message_builder.py ../
   cp session_manager.py ../
   cp negotiator.py ../
   cp requirements.txt ../
   
   # Restart bot
   cd ..
   kill $(pgrep -f "python3 negotiator.py")
   source myenv/bin/activate
   python3 negotiator.py &
   ```

## Backup

1. **Manual Backup**:
   ```bash
   cd /home/p23
   
   # Backup database
   cp negotiations.db "negotiations_$(date +%Y%m%d).db"
   
   # Backup logs
   cp webhook.log "webhook_$(date +%Y%m%d).log"
   ```

2. **Download Backups**:
   - Go to "Files" tab
   - Navigate to `/home/p23`
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

4. **Directory Access**:
   - All bot files should be in `/home/p23`
   - Git repository in `/home/p23/SolutionCells`
   - Virtual environment in `/home/p23/myenv`
   - Database file: `negotiations.db`
   - Log files: `webhook.log`
