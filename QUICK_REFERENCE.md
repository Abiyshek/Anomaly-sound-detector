# 📧 EMAIL QUICK REFERENCE CARD

## ✅ EVERYTHING WORKS - FULLY TESTED & VERIFIED

---

## 🎯 What Email Gets Sent?

### 🚀 START EMAIL
**Sent:** When you click `▶️ Start Monitoring`
```
FROM: aabiyshek@gmail.com
TO: raghukanish97@gmail.com
SUBJECT: 🚀 Sound Detector Monitoring Started

Contains: Config info, port, baudrate
Status: ✓ VERIFIED WORKING
```

### ⏹️ STOP EMAIL  
**Sent:** When you click `⏹️ Stop Monitoring`
```
FROM: aabiyshek@gmail.com
TO: raghukanish97@gmail.com
SUBJECT: ⏹️ Sound Detector Monitoring Stopped

Contains: Uptime, messages, detections stats
Status: ✓ VERIFIED WORKING
```

### 🚨 EMERGENCY EMAIL
**Sent:** When ESP32 detects emergencies
```
FROM: aabiyshek@gmail.com
TO: raghukanish97@gmail.com
SUBJECT: 🚨 Emergency Alert

Contains: Emergency details, sound levels
Status: ✓ WORKS (if ESP32 sends emergency messages)
```

### ⚠️ ANOMALY EMAIL
**Sent:** When ESP32 detects anomalies
```
FROM: aabiyshek@gmail.com
TO: raghukanish97@gmail.com
SUBJECT: ⚠️ Anomaly Detected

Contains: Anomaly type, severity, baseline
Status: ✓ WORKS (if ESP32 sends anomaly messages)
```

---

## 📊 QUICK FLOW

```
START BUTTON CLICKED
    ↓
✓ Email Config Check
    ↓
📧 START EMAIL SENT → raghukanish97@gmail.com
    ↓
🔗 ESP32 CONNECTED
👁️  MONITORING ACTIVE
    ↓
[OPTIONAL: 🚨 Emergency → 📧 Email Sent]
[OPTIONAL: ⚠️  Anomaly → 📧 Email Sent]
    ↓
STOP BUTTON CLICKED
    ↓
⏹️ MONITORING STOPPED
    ↓
📧 STOP EMAIL SENT → raghukanish97@gmail.com
   (includes stats)
    ↓
END
```

---

## 🔍 HOW TO CHECK IF EMAIL SENT

### In Streamlit App:
Look for these messages in the **Process Log**:

**✓ Email sent successfully:**
```
[HH:MM:SS] [SYSTEM] 📧 Sending monitoring started notification...
[HH:MM:SS] [SUCCESS] ✓ Monitoring started email sent!
```

**✗ Email failed:**
```
[HH:MM:SS] [SYSTEM] 📧 Sending monitoring started notification...
[HH:MM:SS] [WARNING] ⚠️ Could not send start email: [error details]
```

### Check Your Email:
1. Open: raghukanish97@gmail.com
2. Check inbox (and spam folder)
3. Look for emails with:
   - Subject: `🚀 Sound Detector Monitoring Started`
   - Subject: `⏹️ Sound Detector Monitoring Stopped`

---

## 🧪 TEST EMAILS

### Before using the app, test emails:

```bash
python test_email_config.py
```
Should show: `✓ All tests PASSED`

```bash
python test_start_stop_emails.py
```
Should show: `✓ Start Email: PASS` and `✓ Stop Email: PASS`

---

## ⚙️ EMAIL CONFIGURATION

**Current Setting:** `python_whatsapp/config.py`

```python
EMAIL_USERNAME = 'aabiyshek@gmail.com'
EMAIL_PASSWORD = 'yifr ulzv pecs mejr'
EMERGENCY_EMAIL = 'raghukanish97@gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

EMAIL_COOLDOWN = 20        # Seconds between emergency emails
ANOMALY_COOLDOWN = 180     # Seconds between anomaly emails
```

### To Change Recipient:
Edit `python_whatsapp/config.py`:
```python
EMERGENCY_EMAIL = 'your_email@example.com'
```

---

## 🚀 GETTING STARTED

### 1 Command to Start:
```bash
streamlit run streamlit_app.py
```

### 3 Steps to Test:
1. Click `▶️ Start Monitoring`
2. Watch Process Log (should show ✓ email sent)
3. Click `⏹️ Stop Monitoring` (another email sent)

### Check Results:
- Open: raghukanish97@gmail.com
- Should have 2 new emails

---

## 📱 PROCESS LOG REFERENCE

### Email Sending Messages:
| Message | Meaning |
|---------|---------|
| `📧 Sending monitoring...` | Email being sent |
| `✓ Monitoring...email sent!` | ✓ Email sent successfully |
| `⚠️ Could not send email:` | ✗ Email failed (see reason) |
| `⏱️ Cooldown: X seconds` | Still waiting before next alert |

### Other Process Log Messages:
| Prefix | Meaning |
|--------|---------|
| `[SYSTEM]` | System operation |
| `[SUCCESS]` | ✓ Operation succeeded |
| `[ERROR]` | ✗ Error occurred |
| `[WARNING]` | ⚠️ Warning |
| `[INFO]` | ℹ️ General info |
| `[RAW]` | Raw ESP32 message |

---

## 🎯 MONITORING SESSION STATS

### Included in STOP Email:

```
Session Statistics:
- Uptime: 0h 15m 30s
- Messages Processed: 125
- Emergencies Detected: 2
- Anomalies Detected: 5
```

These numbers help you understand system activity.

---

## 🔧 TROUBLESHOOTING

### Email Not Sent?
**Solution:**
1. Run: `python test_email_config.py`
2. Check internet connection
3. Look for error in Process Log
4. Check email address in config.py

### Wrong Email Recipient?
**Solution:**
1. Edit: `python_whatsapp/config.py`
2. Change: `EMERGENCY_EMAIL = 'correct_email@example.com'`
3. Restart app

### Email in Spam Folder?
**Solution:**
1. Check spam/junk folder
2. Mark as "Not Spam"
3. Emails may be correct but marked as spam by email provider

### Too Many Emails?
**Solution:**
1. Increase cooldown in config.py
2. Change: `EMAIL_COOLDOWN = 60` (was 20)
3. Or: `ANOMALY_COOLDOWN = 600` (was 180)

---

## 📋 FILES REFERENCE

### Main App:
- **streamlit_app.py** - The Streamlit GUI with email functionality

### Testing Tools:
- **test_email_config.py** - Test all email functions
- **test_start_stop_emails.py** - Test start/stop notifications

### Documentation:
- **QUICK_START.md** - Fast reference (this is helpful!)
- **COMPLETE_EMAIL_GUIDE.md** - Full documentation
- **IMPLEMENTATION_SUMMARY.md** - Technical details

---

## ✨ SUMMARY

✅ **Start Email** - Works perfectly  
✅ **Stop Email** - Works perfectly  
✅ **Process Logging** - Shows all activity  
✅ **Error Handling** - Graceful failures  
✅ **Configuration** - Easy to customize  
✅ **Testing** - Diagnostic tools included  
✅ **Documentation** - Complete guides provided  

**Status: READY TO USE!** 🎉

Just run: `streamlit run streamlit_app.py`

---

## 📞 QUICK HELP

| Need | Command |
|------|---------|
| Start app | `streamlit run streamlit_app.py` |
| Test emails | `python test_email_config.py` |
| Test start/stop | `python test_start_stop_emails.py` |
| Change recipient | Edit `python_whatsapp/config.py` |
| View logs | Check Process Log in Streamlit |

---

## 🎓 REMEMBER

- ✅ Email to: `raghukanish97@gmail.com`
- ✅ Sent when Start button clicked
- ✅ Sent when Stop button clicked  
- ✅ Check Process Log to confirm
- ✅ Check email inbox for messages
- ✅ Fully tested and verified

**Everything is working!** ✨

---

**Last Updated:** December 15, 2025  
**Status:** ✅ COMPLETE & VERIFIED  
**All Tests:** ✅ PASSED
