#!/usr/bin/env python3
"""
Test Start/Stop Email Notifications
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_whatsapp'))

from config import *
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Get cooldown values with defaults
EMAIL_COOLDOWN = globals().get('EMAIL_COOLDOWN', 20)
ANOMALY_COOLDOWN = globals().get('ANOMALY_COOLDOWN', 180)

def send_test_start_email():
    """Send test 'Monitoring Started' email"""
    print("\n" + "="*60)
    print("📧 TESTING: Monitoring Started Email")
    print("="*60)
    
    try:
        start_message = f"""
═══════════════════════════════════════════════════════════
🚀 MONITORING STARTED (TEST)
═══════════════════════════════════════════════════════════

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Device: ESP32 Sound Detector
Location: Test Location
Status: ✓ Active

The Arduino Sound Detector monitoring system has been started.
Emergency and anomaly alerts will be sent to this email address.

Configuration:
- Port: {ARDUINO_PORT}
- Baudrate: {BAUDRATE}
- Emergency Cooldown: {EMAIL_COOLDOWN}s
- Anomaly Cooldown: {ANOMALY_COOLDOWN}s

═══════════════════════════════════════════════════════════
"""
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = EMERGENCY_EMAIL
        msg['Subject'] = "🚀 Sound Detector Monitoring Started (TEST)"
        msg['X-Priority'] = '2'
        msg.attach(MIMEText(start_message, 'plain'))
        
        print(f"\nSending to: {EMERGENCY_EMAIL}")
        print(f"From: {EMAIL_USERNAME}")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, [EMERGENCY_EMAIL], msg.as_string())
        server.quit()
        
        print("✓ Start email sent successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Failed to send start email: {str(e)}")
        return False

def send_test_stop_email():
    """Send test 'Monitoring Stopped' email"""
    print("\n" + "="*60)
    print("📧 TESTING: Monitoring Stopped Email")
    print("="*60)
    
    try:
        stop_message = f"""
═══════════════════════════════════════════════════════════
⏹️ MONITORING STOPPED (TEST)
═══════════════════════════════════════════════════════════

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Device: ESP32 Sound Detector
Status: ✓ Stopped

The Arduino Sound Detector monitoring system has been stopped.

Session Statistics:
- Uptime: 0h 5m 30s
- Messages Processed: 42
- Emergencies Detected: 1
- Anomalies Detected: 3

Restart the monitoring to resume detection.

═══════════════════════════════════════════════════════════
"""
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = EMERGENCY_EMAIL
        msg['Subject'] = "⏹️ Sound Detector Monitoring Stopped (TEST)"
        msg['X-Priority'] = '2'
        msg.attach(MIMEText(stop_message, 'plain'))
        
        print(f"\nSending to: {EMERGENCY_EMAIL}")
        print(f"From: {EMAIL_USERNAME}")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, [EMERGENCY_EMAIL], msg.as_string())
        server.quit()
        
        print("✓ Stop email sent successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Failed to send stop email: {str(e)}")
        return False

def main():
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*12 + "START/STOP EMAIL NOTIFICATION TEST" + " "*12 + "║")
    print("╚" + "="*58 + "╝")
    
    print(f"\nEmail Configuration:")
    print(f"  From: {EMAIL_USERNAME}")
    print(f"  To: {EMERGENCY_EMAIL}")
    print(f"  SMTP: {SMTP_SERVER}:{SMTP_PORT}")
    
    results = {
        'Start Email': False,
        'Stop Email': False
    }
    
    # Test start email
    results['Start Email'] = send_test_start_email()
    
    # Test stop email
    results['Stop Email'] = send_test_stop_email()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ All start/stop emails work correctly!")
        print("\nWhen you click Start/Stop in the Streamlit app,")
        print("these emails will be automatically sent.")
    else:
        print("✗ Some emails failed. Check your configuration.")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
