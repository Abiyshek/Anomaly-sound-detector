# ✅ Email Configuration - WORKING

## Great News!
Your email configuration is **100% working** ✓

The diagnostic test confirmed:
- ✓ SMTP connection successful
- ✓ Authentication successful  
- ✓ Test email sent successfully

## Why Emails May Not Be Sending in the Streamlit App

The email system itself is working perfectly. If emails aren't being sent when monitoring, check these things:

### 1. **ESP32 Not Sending Emergency/Anomaly Alerts**
The email system only sends when your ESP32/Arduino sends emergency or anomaly messages. Make sure your firmware is:
- Detecting emergencies (EMERGENCY: prefix messages)
- Detecting anomalies (ANOMALY: prefix messages)

**Check in the Process Log:**
- Look for `🚨 EMERGENCY DETECTED!` or `⚠️ ANOMALY DETECTED!` messages
- If you don't see these, your ESP32 is not detecting anything

### 2. **Email Cooldown Period**
Emails have a cooldown to prevent spam:
- **Emergency emails**: 20 seconds between emails (configurable in `config.py`)
- **Anomaly emails**: 180 seconds (3 minutes) between emails

After the first email, you must wait for the cooldown to expire before another email can be sent.

**Check in the Process Log:**
- Look for `⏱️ Emergency cooldown: X seconds remaining`
- This means an email was sent, but cooldown is active

### 3. **Monitor the Process Log**
The Streamlit app shows EXACTLY what's happening:

```
[HH:MM:SS] [RAW] Received message from ESP32
[HH:MM:SS] [EMERGENCY] 🚨 EMERGENCY DETECTED!
[HH:MM:SS] [SYSTEM] 📧 Sending emergency email...
[HH:MM:SS] [SUCCESS] ✓ Emergency email sent successfully!
```

If you don't see the SUCCESS message, there's an issue that will be logged.

## Quick Diagnostic Steps

1. **Start Monitoring** with the Streamlit app
2. **Watch the Process Log** for:
   - Messages being received: `[RAW] Received message`
   - Emergencies/Anomalies being detected: `🚨 EMERGENCY` or `⚠️ ANOMALY`
   - Email sending attempts: `📧 Sending email`
   - Success/Failure status: `✓` or `✗`

3. **If emails aren't sending:**
   - Is your ESP32 detecting emergencies? (Check for 🚨)
   - Is cooldown still active? (Check for ⏱️)
   - Any error messages? (Check for ✗)

## Test Email Configuration

Run the diagnostic tool anytime to verify email:

```bash
python test_email_config.py
```

This will test:
- Email credentials
- SMTP connection
- Email sending capability
- Configuration settings

## Email Configuration in `config.py`

Your current settings:
```python
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USERNAME = 'aabiyshek@gmail.com'     
EMAIL_PASSWORD = 'yifr ulzv pecs mejr'     # Gmail App Password
EMERGENCY_EMAIL = 'raghukanish97@gmail.com'

EMERGENCY_COOLDOWN = 20      # seconds between emergency emails
ANOMALY_COOLDOWN = 180       # seconds between anomaly emails
HIGH_SEVERITY_ONLY = True    # Only HIGH/CRITICAL anomalies trigger email
```

## Common Issues & Solutions

### Issue: "Email authentication failed"
**Solution:** 
- Make sure you're using an **App Password**, not your regular Gmail password
- Get App Password: https://myaccount.google.com/apppasswords
- Ensure 2-Factor Authentication is enabled

### Issue: "No emails being sent"
**Solution:**
- Check if ESP32 is sending EMERGENCY/ANOMALY messages
- Check the cooldown period hasn't elapsed
- Look at Process Log for error messages

### Issue: "Too many emails"
**Solution:**
- Increase `EMERGENCY_COOLDOWN` (currently 20 seconds)
- Increase `ANOMALY_COOLDOWN` (currently 180 seconds)
- Set `HIGH_SEVERITY_ONLY = True` to only send for critical alerts

### Issue: "Can't connect to ESP32"
**Solution:**
- Check USB cable connection
- Verify port number in `config.py` (currently COM5)
- The app will auto-try alternative ports
- Check the Process Log for connection attempts

## Understanding the Process Log

The Process Log shows exactly what's happening:

| Prefix | Meaning |
|--------|---------|
| `[RAW]` | Raw message from ESP32 |
| `[SYSTEM]` | System operations (init, connection) |
| `[INFO]` | General information |
| `[SUCCESS]` | ✓ Operation succeeded |
| `[WARNING]` | ⚠️ Warning or anomaly detected |
| `[EMERGENCY]` | 🚨 Emergency detected |
| `[ERROR]` | ✗ Error occurred |
| `[DEBUG]` | Technical details |

## Next Steps

1. **Verify ESP32 is connected** and sending messages
2. **Trigger an emergency/anomaly** to test email sending
3. **Watch the Process Log** for real-time feedback
4. **Wait for cooldown** if trying multiple tests
5. **Check recipient inbox** for emails

## Support

If you still have issues:
1. Run `python test_email_config.py` to verify email setup
2. Check the Process Log in the Streamlit app
3. Look for error messages (marked with ✗)
4. Verify ESP32 is sending EMERGENCY/ANOMALY messages
