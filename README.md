# Arduino Sound Detector with Email Integration

Complete system for detecting sound anomalies and HELP voice commands with email notifications.

## Project Structure

```
arduino_sound_detector/
│
├── arduino_code/
│   └── sound_detector/
│       ├── sound_detector.ino      # Main Arduino file
│       ├── config.h                # Arduino configuration
│       └── sound_analysis.h        # Sound analysis functions
│
├── python_whatsapp/                # Renamed but contains email code
│   ├── main.py                     # Main email integration script
│   ├── arduino_reader.py           # Serial communication (unchanged)
│   ├── email_sender.py             # Email functionality
│   ├── message_parser.py           # Parse Arduino messages (unchanged)
│   ├── config.py                   # Python email configuration
│   └── requirements.txt            # Python dependencies
│
├── logs/
│   └── detection_log.txt           # Auto-created log file
│
├── README.md                       # This setup guide
└── run_system.py                   # Simple startup script
```

## Quick Setup Steps

### 1. Arduino Setup (Keep Existing Code)
Your Arduino code is perfect as-is. Just update these two lines in `config.h`:
```cpp
#define DEVICE_LOCATION "Your Room Name"    // Change this
#define EMERGENCY_CONTACT "+1234567890"     // Change this (not used for email)
```

### 2. Python Setup

Install dependencies:
```bash
cd python_whatsapp
pip install -r requirements.txt
```

### 3. Email Configuration

Edit `python_whatsapp/config.py`:

```python
# Email Settings (CHANGE THESE)
SMTP_SERVER = 'smtp.gmail.com'              # Gmail SMTP
SMTP_PORT = 587                             # TLS port
EMAIL_USERNAME = 'your_email@gmail.com'     # Your email
EMAIL_PASSWORD = 'your_app_password'        # App password (NOT regular password)
EMERGENCY_EMAIL = 'emergency@example.com'   # Who receives alerts
CC_EMAILS = ['backup@example.com']          # Optional additional recipients

# Arduino Settings (CHANGE PORT)
ARDUINO_PORT = 'COM5'  # Windows: COM3,COM4,COM5 | Linux: /dev/ttyUSB0 | Mac: /dev/cu.usbmodem*
```

## Email Provider Setup

### Gmail (Recommended)
1. **Enable 2-Factor Authentication**:
   - Go to Google Account settings
   - Security → 2-Step Verification → Turn On

2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
   - Use THIS password in `config.py`, not your regular password

3. **Update config.py**:
   ```python
   EMAIL_USERNAME = 'youremail@gmail.com'
   EMAIL_PASSWORD = 'abcd efgh ijkl mnop'  # 16-char app password
   EMERGENCY_EMAIL = 'recipient@gmail.com'
   ```

### Outlook/Hotmail
```python
SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
EMAIL_USERNAME = 'youremail@outlook.com'
EMAIL_PASSWORD = 'your_password'
```

### Yahoo Mail
```python
SMTP_SERVER = 'smtp.mail.yahoo.com'
SMTP_PORT = 587
EMAIL_USERNAME = 'youremail@yahoo.com'
EMAIL_PASSWORD = 'your_app_password'  # Generate app password in Yahoo settings
```

### Custom SMTP Server
```python
SMTP_SERVER = 'mail.yourdomain.com'
SMTP_PORT = 587  # or 465 for SSL
EMAIL_USERNAME = 'alert@yourdomain.com'
EMAIL_PASSWORD = 'your_password'
```

## Running the System

### Test Email First
```bash
python run_system.py test
```
This sends a test email to verify configuration.

### Check Configuration
```bash
python run_system.py config
```
Shows your current settings without revealing passwords.

### Start Full System
```bash
python run_system.py
```
Begins monitoring Arduino and sending email alerts.

## System Features

### Emergency Detection
- **Trigger**: Say "HELP" near the sensor
- **Response**: Immediate high-priority email alert
- **Cooldown**: 30 seconds between emergency emails
- **Subject**: "🚨 EMERGENCY ALERT - [Location]"

### Anomaly Detection  
- **Trigger**: Unusual sound patterns detected
- **Response**: Email for HIGH/CRITICAL severity only
- **Cooldown**: 5 minutes between anomaly emails
- **Subject**: "⚠️ Sound Anomaly Detected - [Severity] - [Location]"

### Status Monitoring
- **Startup**: Email notification when system starts
- **Daily Reports**: Automatic daily status emails
- **Shutdown**: Email notification when system stops

## Configuration Options

### Detection Sensitivity
```python
# In config.py
HIGH_SEVERITY_ONLY = True   # Only email for high severity anomalies
EMERGENCY_COOLDOWN = 30     # Seconds between emergency emails  
ANOMALY_COOLDOWN = 300      # Seconds between anomaly emails
```

### Email Recipients
```python
EMERGENCY_EMAIL = 'primary@example.com'    # Main recipient
CC_EMAILS = [                              # Additional recipients (optional)
    'backup@example.com',
    'security@example.com'
]
```

### Notifications
```python
DESKTOP_NOTIFICATIONS = True  # Show desktop alerts
LOG_MESSAGES = True          # Log all emails to file
LOG_FILE = '../logs/detection_log.txt'
```

## Troubleshooting

### Common Issues

**"Email authentication failed"**
- For Gmail: Use App Password, not regular password
- Ensure 2-Factor Authentication is enabled
- Check username/password spelling

**"Could not connect to email server"**
- Verify SMTP server and port
- Check internet connection
- Try port 465 with SSL instead of 587 with TLS

**"Arduino not found"**
- Check USB connection
- Verify correct port in config.py
- Try alternative ports listed in startup messages

**"No emails received"**
- Check spam/junk folder
- Verify recipient email address
- Test with `python run_system.py test`

### Arduino Port Detection
If Arduino port is unknown:
```bash
# Windows - Check Device Manager under "Ports (COM & LPT)"
# Linux - Try: ls /dev/tty*
# Mac - Try: ls /dev/cu.*
```

### Email Debugging
Enable detailed email logs by adding to config.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Command Reference

### Arduino Serial Commands
Send these through Serial Monitor:
- `STATUS` - Show system status
- `RESET` - Reset counters and recalibrate
- `BASELINE` - Recalibrate baseline noise
- `TEST` - Send test anomaly alert
- `TESTHELP` - Send test emergency alert

### Python Commands
```bash
python main.py           # Run full system
python main.py test      # Test email functionality  
python main.py config    # Show configuration
python main.py help      # Show help

python run_system.py         # Same as above but from root directory
python run_system.py test    # Test from root directory
```

## Email Template Customization

Edit templates in `config.py`:

```python
EMERGENCY_TEMPLATE = """🚨 EMERGENCY ALERT 🚨
Custom emergency message here...
Location: {location}
Time: {timestamp}
etc...
"""

ANOMALY_TEMPLATE = """⚠️ SOUND ANOMALY
Custom anomaly message here...
Severity: {severity}
etc...
"""
```

Available variables:
- `{location}` - Device location
- `{timestamp}` - Current date/time
- `{sound_level}` - Current sound level
- `{baseline}` - Baseline noise level
- `{severity}` - Anomaly severity
- `{device_id}` - Device identifier

## Security Considerations

1. **Email Passwords**: Use app passwords, not account passwords
2. **Log Files**: May contain sensitive information
3. **Network**: Ensure secure WiFi if using wireless
4. **Recipients**: Verify email addresses are correct

## System Requirements

- **Arduino**: Uno/Nano with sound sensor
- **Python**: 3.6 or higher
- **Internet**: Required for sending emails
- **Email Account**: Gmail, Outlook, Yahoo, or custom SMTP

## Support

If you encounter issues:
1. Test email configuration first: `python run_system.py test`
2. Check Arduino connection: Look for port detection messages
3. Review configuration: `python run_system.py config`  
4. Check logs: `logs/detection_log.txt`

The system will automatically attempt common Arduino ports and provide helpful error messages for debugging.