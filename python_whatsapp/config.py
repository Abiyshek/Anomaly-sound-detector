"""
Configuration file for ESP32 Sound Detector Email Integration
Optimized for ESP32 with 12-bit ADC and 115200 baudrate
"""

# ESP32 Serial Settings
ARDUINO_PORT = 'COM5'      # CHANGE THIS: Windows: COM3-COM10 | Linux: /dev/ttyUSB0 | Mac: /dev/cu.usbserial*
BAUDRATE = 115200          # ESP32 standard baudrate (much faster than Arduino)
SERIAL_TIMEOUT = 3         # Longer timeout for ESP32 initialization (ESP32 needs time to boot)

# Email Settings
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USERNAME = 'xxxxxxxxxxxxxxxx'     # CHANGE THIS: Your email
EMAIL_PASSWORD = 'xxxxxxxxxxxxx'     # CHANGE THIS: Your app password
EMERGENCY_EMAIL = 'xxxxxxxxxxxxxxxxxx'    # CHANGE THIS: Emergency recipient
CC_EMAILS = []                              # Optional: Additional recipients

# Alternative Email Providers:
# Outlook: smtp.office365.com, port 587
# Yahoo: smtp.mail.yahoo.com, port 587

# ESP32 Detection Settings (Optimized for 12-bit ADC: 0-4095 range)
EMERGENCY_COOLDOWN = 20        # seconds between emergency emails (ESP32 processes faster)
ANOMALY_COOLDOWN = 180         # seconds between anomaly emails (3 minutes)
HIGH_SEVERITY_ONLY = True      # Only send email for HIGH/CRITICAL anomalies

# ESP32 Specific Settings
ESP32_MODE = True                           # Enable ESP32 optimizations
ESP32_ADC_RESOLUTION = 12                   # ESP32 12-bit ADC
ESP32_ADC_RANGE = 4095                      # 0-4095 range
ESP32_BASELINE_TYPICAL = 200                # Typical ESP32 baseline noise level
ESP32_THRESHOLD_MULTIPLIER = 1.5            # ESP32 threshold adjustment
ESP32_INIT_DELAY = 3                        # ESP32 initialization delay (seconds)

# Detection Patterns (ESP32 optimized)
HELP_KEYWORDS = [
    'HELP_DETECTED',
    'VOICE_HELP',
    'EMERGENCY:HELP',
    'HELP COMMAND',
    'PERSON NEEDS HELP'
]

ANOMALY_KEYWORDS = [
    'ALERT:',
    'ANOMALY',
    'SOUND SPIKE',
    'UNUSUAL SOUND'
]

# Notification Settings
DESKTOP_NOTIFICATIONS = True
SOUND_ALERTS = True
LOG_MESSAGES = True
LOG_FILE = 'logs/esp32_detection_log.txt'

# Email Templates
EMERGENCY_SUBJECT = "🚨 EMERGENCY ALERT - HELP DETECTED - {location}"
EMERGENCY_TEMPLATE = """🚨 EMERGENCY ALERT - HELP COMMAND DETECTED 🚨

⚠️ IMMEDIATE ACTION REQUIRED ⚠️

Location: {location}
Device: {device_id} (ESP32)
Time: {timestamp}
Sound Level: {sound_level} (ESP32 12-bit ADC: 0-4095)
Emergency Type: HELP Voice Command

SOMEONE IS CALLING FOR HELP!
Please check the location immediately and respond to this emergency.

System Details:
- Detection Time: {timestamp}
- Sound Level: {sound_level}/4095
- Location: {location}
- Device ID: {device_id}
- System Uptime: {uptime}
- Contact: {contact}

This is an automated emergency alert from your ESP32 Sound Detector.
The system detected a person saying "HELP" at the monitored location.

⚠️ PLEASE RESPOND IMMEDIATELY ⚠️

If this is a false alarm, please check the device sensitivity settings.
"""

ANOMALY_SUBJECT = "⚠️ Sound Anomaly Detected - {severity} - {location}"
ANOMALY_TEMPLATE = """⚠️ UNUSUAL SOUND ACTIVITY DETECTED

Location: {location}
Device: {device_id} (ESP32)
Severity: {severity}
Current Sound Level: {level}/4095 (ESP32 12-bit ADC)
Baseline Level: {baseline}/4095
Difference: +{difference}
Detection Time: {timestamp}
System Uptime: {uptime}

Analysis:
- Current Reading: {level} (out of 4095 max)
- Normal Baseline: {baseline}
- Deviation: {difference} units above normal
- Severity Classification: {severity}

ESP32 System Info:
- ADC Resolution: 12-bit (0-4095 range)
- CPU Frequency: 240 MHz
- Baseline: {baseline}
- Detection Threshold: {baseline} + 150

This automated alert indicates unusual sound activity at the monitored location.
The ESP32 detected sound levels significantly above the normal baseline.

Note: Only {severity} severity alerts trigger email notifications.
Lower severity events are logged locally for review.

---
Powered by ESP32 Sound Detector System
"""

# Startup notification template
STARTUP_SUBJECT = "✅ ESP32 Sound Detector Started - {location}"
STARTUP_TEMPLATE = """✅ ESP32 SOUND DETECTOR SYSTEM STARTED

System Status: Online and Monitoring
Device Type: ESP32 (Dual-core, 240MHz)
Start Time: {timestamp}
Location: {location}
Device ID: {device_id}

ESP32 Configuration:
- ADC Resolution: 12-bit (0-4095 range)
- Baudrate: 115200 (high-speed)
- CPU Frequency: 240 MHz
- Sample Rate: 8000 Hz
- Baseline Calibration: Complete

Monitoring Features:
✓ Emergency HELP voice command detection
✓ Sound anomaly pattern analysis
✓ Adaptive baseline noise filtering
✓ Real-time email alerts

Alert Configuration:
- Emergency Contact: {emergency_email}
- Emergency Cooldown: {emergency_cooldown}s
- Anomaly Cooldown: {anomaly_cooldown}s
- High Severity Only: {high_severity_only}

The ESP32 system is now actively monitoring for:
1. Emergency HELP voice commands (immediate alert)
2. High severity sound anomalies
3. Unusual sound patterns

System Status: READY ✓
Monitoring: ACTIVE ✓

Say "HELP" near the sensor to trigger an emergency alert.

---
Powered by ESP32 Sound Detector System
"""

# Shutdown notification template
SHUTDOWN_SUBJECT = "🛑 ESP32 Sound Detector Stopped - {location}"
SHUTDOWN_TEMPLATE = """🛑 ESP32 SOUND DETECTOR STOPPED

Stop Time: {timestamp}
Location: {location}
Device ID: {device_id}
Total Uptime: {uptime}

Session Statistics:
- Messages Processed: {messages_processed}
- Emergencies Detected: {emergencies_detected}
- Anomalies Detected: {anomalies_detected}
- Total Emails Sent: {total_emails}

The ESP32 monitoring system has been stopped.
Sound detection and email alerts are no longer active.

To resume monitoring:
1. Ensure ESP32 is connected via USB
2. Run: python main_esp32.py

---
Powered by ESP32 Sound Detector System
"""

# Status report template
STATUS_SUBJECT = "📊 ESP32 Sound Detector Status Report - {date}"
STATUS_TEMPLATE = """📊 ESP32 SOUND DETECTOR DAILY STATUS REPORT

Report Date: {timestamp}
Location: {location}
Device: {device_id}
System Status: {status}

Performance Statistics:
- System Uptime: {uptime_hours:.1f} hours
- Messages Processed: {messages_processed}
- Emergencies Detected: {emergencies_detected}
- Anomalies Detected: {anomalies_detected}
- Email Alerts Sent: {total_emails}

Email Breakdown:
- Emergency Emails: {emergency_emails}
- Anomaly Emails: {anomaly_emails}

ESP32 System Health:
- ADC Resolution: 12-bit (0-4095)
- Current Baseline: ~{baseline}
- CPU Frequency: 240 MHz
- Memory Status: OK
- Connection: Stable

Detection Settings:
- Emergency Cooldown: {emergency_cooldown}s
- Anomaly Cooldown: {anomaly_cooldown}s
- High Severity Only: {high_severity_only}
- HELP Detection: Enabled

Device Information:
- Location: {location}
- Device ID: {device_id}
- Device Type: ESP32
- Firmware: Latest

System Health: ✓ All systems operational
Monitoring: ✓ Active and responsive

This automated status report confirms your ESP32 sound detector
is operating normally and monitoring for emergencies.

---
Powered by ESP32 Sound Detector System
"""