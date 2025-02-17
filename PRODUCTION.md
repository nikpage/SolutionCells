# Production Deployment Guide

## Prerequisites

1. **Server Requirements**:
   - Python 3.12+
   - SQLite3
   - Systemd (for service management)

2. **Environment Variables**:
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token
   ```

## Deployment Steps

1. **Clone Repository**:
   ```bash
   git clone https://github.com/nikpage/SolutionCells.git
   cd SolutionCells
   ```

2. **Setup Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create Systemd Service**:
   ```bash
   sudo nano /etc/systemd/system/negotiator.service
   ```
   
   Add the following content:
   ```ini
   [Unit]
   Description=Telegram Negotiation Bot
   After=network.target

   [Service]
   Type=simple
   User=your_user
   WorkingDirectory=/path/to/SolutionCells
   Environment=TELEGRAM_BOT_TOKEN=your_bot_token
   ExecStart=/path/to/SolutionCells/venv/bin/python negotiator.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable negotiator
   sudo systemctl start negotiator
   ```

5. **Monitor Logs**:
   ```bash
   # View service logs
   sudo journalctl -u negotiator -f

   # View application logs
   tail -f bot.log
   ```

## Verification Steps

1. **Basic Flow Test**:
   ```
   First User:
   1. /start
   2. Select role
   3. Enter price
   4. Share link

   Second User:
   1. Click link
   2. Enter price
   3. Verify result
   ```

2. **Language Test**:
   ```
   1. /language
   2. Test each language:
      - 🇬🇧 English
      - 🇨🇿 Czech
      - 🇺🇦 Ukrainian
   3. Verify messages update
   ```

3. **Edge Cases**:
   ```
   1. Self-join test
   2. Invalid price test
   3. Concurrent sessions test
   4. Command test:
      - /status
      - /stop
      - /help
      - /language
   ```

## Monitoring

1. **Log Analysis**:
   ```bash
   # Error count by type
   grep ERROR bot.log | cut -d' ' -f6- | sort | uniq -c | sort -nr

   # User activity
   grep "command from user" bot.log | cut -d' ' -f8 | sort | uniq -c

   # Session statistics
   grep "Deal" bot.log | wc -l
   ```

2. **Health Check**:
   ```bash
   # Service status
   systemctl status negotiator

   # Process check
   ps aux | grep negotiator.py

   # Memory usage
   smem -t -k -c pss -P negotiator.py
   ```

3. **Database Check**:
   ```bash
   # Check user preferences
   sqlite3 users.db "SELECT * FROM user_preferences;"
   ```

## Backup

1. **Database Backup**:
   ```bash
   # Daily backup
   0 0 * * * sqlite3 /path/to/users.db ".backup '/path/to/backups/users_$(date +\%Y\%m\%d).db'"
   ```

2. **Log Rotation**:
   ```bash
   # /etc/logrotate.d/negotiator
   /path/to/SolutionCells/bot.log {
       daily
       rotate 7
       compress
       delaycompress
       missingok
       notifempty
       create 644 root root
   }
   ```

## Troubleshooting

1. **Bot Not Responding**:
   ```bash
   # Check service status
   systemctl status negotiator

   # Check logs
   tail -f bot.log

   # Restart service
   systemctl restart negotiator
   ```

2. **Database Issues**:
   ```bash
   # Check database integrity
   sqlite3 users.db "PRAGMA integrity_check;"

   # Backup and recreate if needed
   cp users.db users.db.bak
   rm users.db
   sqlite3 users.db < schema.sql
   ```

3. **Memory Issues**:
   ```bash
   # Check memory usage
   smem -t -k -c pss -P negotiator.py

   # Restart if too high
   systemctl restart negotiator
   ```
