# ✅ Start/Stop Email Notifications - ENABLED

## What's New

The Streamlit app now sends **automatic email notifications** when:

### 1. **Monitoring STARTS** 🚀
When you click the **▶️ Start Monitoring** button:
- Email is sent to: `{EMERGENCY_EMAIL}`
- Subject: `🚀 Sound Detector Monitoring Started`
- Contains: Device status, location, configuration details

### 2. **Monitoring STOPS** ⏹️
When you click the **⏹️ Stop Monitoring** button:
- Email is sent to: `{EMERGENCY_EMAIL}`
- Subject: `⏹️ Sound Detector Monitoring Stopped`
- Contains: Session statistics (uptime, messages, detections)

### 3. **Emergency/Anomaly Alerts** 🚨⚠️
As before:
- Emergency emails sent when emergencies detected
- Anomaly emails sent when anomalies detected
- Both respect cooldown periods to prevent spam

## Email Flow

```
┌─────────────────────────────────────────┐
│  Click "Start Monitoring" Button         │
└─────────────────────────────────────────┘
                    ↓
        ✓ Email "Monitoring Started"
           → Sent to {EMERGENCY_EMAIL}
                    ↓
    ESP32 Connects & Monitoring Begins
                    ↓
     ┌──────────────────────────────┐
     │  Monitoring is Running       │
     │ Looking for emergencies...   │
     └──────────────────────────────┘
                    ↓
        (Optional) Emergency/Anomaly Detected
               ✓ Email Sent
                    ↓
        Click "Stop Monitoring" Button
                    ↓
        ✓ Email "Monitoring Stopped"
           → Sent to {EMERGENCY_EMAIL}
           → Includes session stats
```

## Email Recipients

Both start and stop emails are sent to:
- **Primary**: `EMERGENCY_EMAIL` in config.py
- **CC**: None (configurable in config.py)

Current setting:
```python
EMERGENCY_EMAIL = 'raghukanish97@gmail.com'
CC_EMAILS = []
```

To add CC recipients, edit `python_whatsapp/config.py`:
```python
CC_EMAILS = ['someone@example.com', 'another@example.com']
```

## What's In Each Email

### 🚀 Monitoring Started Email
```
═══════════════════════════════════════════════════════════
🚀 MONITORING STARTED
═══════════════════════════════════════════════════════════

Timestamp: 2025-12-15 10:30:45
Device: ESP32 Sound Detector
Location: Unknown
Status: ✓ Active

The Arduino Sound Detector monitoring system has been started.
Emergency and anomaly alerts will be sent to this email address.

Configuration:
- Port: COM5
- Baudrate: 115200
- Emergency Cooldown: 20s
- Anomaly Cooldown: 180s

═══════════════════════════════════════════════════════════
```

### ⏹️ Monitoring Stopped Email
```
═══════════════════════════════════════════════════════════
⏹️ MONITORING STOPPED
═══════════════════════════════════════════════════════════

Timestamp: 2025-12-15 10:45:30
Device: ESP32 Sound Detector
Status: ✓ Stopped

The Arduino Sound Detector monitoring system has been stopped.

Session Statistics:
- Uptime: 0h 14m 45s
- Messages Processed: 125
- Emergencies Detected: 2
- Anomalies Detected: 5

Restart the monitoring to resume detection.

═══════════════════════════════════════════════════════════
```

## Process Log Output

When you start monitoring, you'll see in the Process Log:

```
[10:30:45] [SYSTEM] Initializing system...
[10:30:45] [SYSTEM] Testing email configuration...
[10:30:46] [SUCCESS] ✓ Email configuration OK
[10:30:46] [SYSTEM] 📧 Sending monitoring started notification...
[10:30:47] [SUCCESS] ✓ Monitoring started email sent!
[10:30:47] [SYSTEM] Connecting to ESP32 on COM5...
[10:30:48] [SUCCESS] ✓ Connected to ESP32 on COM5
```

When you stop monitoring:

```
[10:45:30] [SYSTEM] Stopping monitoring...
[10:45:30] [SUCCESS] ✓ Monitoring stopped
[10:45:30] [SYSTEM] 📧 Sending monitoring stopped notification...
[10:45:31] [SUCCESS] ✓ Monitoring stopped email sent!
```

## Troubleshooting

### Email Not Sent on Start/Stop

**Check these:**

1. **Is email configuration working?**
   ```bash
   python test_email_config.py
   ```
   All tests should show ✓

2. **Check the Process Log** in Streamlit:
   - Look for: `📧 Sending monitoring started notification...`
   - Should be followed by: `✓ Email sent!`
   - If you see `⚠️ Could not send start email:`, check the error message

3. **Check internet connection**
   - Emails need internet to be sent

4. **Check recipient email address**
   - Is `EMERGENCY_EMAIL` in config.py correct?
   - Check your email inbox (including spam folder)

### Emails Being Sent Multiple Times

This shouldn't happen, but if it does:
- Each click on Start button = one email sent
- Each click on Stop button = one email sent
- No automatic resends

### Want to Disable Start/Stop Emails

Edit `streamlit_app.py` and comment out these sections:

**For Start emails:** Lines ~70-99
**For Stop emails:** Lines ~200-230

Or edit `config.py` to change the recipient email address.

## Summary

✅ **Monitoring Started** - Email automatically sent when you click Start  
✅ **Monitoring Stopped** - Email automatically sent when you click Stop  
✅ **Emergency Alerts** - Emails sent when emergencies detected  
✅ **Anomaly Alerts** - Emails sent when anomalies detected  
✅ **Session Stats** - Stop email includes usage statistics  

All emails go to: `raghukanish97@gmail.com` (configurable in config.py)
