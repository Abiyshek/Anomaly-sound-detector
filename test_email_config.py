#!/usr/bin/env python3
"""
Email Configuration Diagnostic Tool
Tests all email settings and identifies issues
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_whatsapp'))

from config import *
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_credentials():
    print_section("1. CREDENTIAL CHECK")
    
    print(f"Email Address: {EMAIL_USERNAME}")
    print(f"Password Length: {len(EMAIL_PASSWORD)} characters")
    print(f"Password (masked): {'*' * len(EMAIL_PASSWORD)}")
    
    if ' ' in EMAIL_PASSWORD:
        print("⚠️  WARNING: Password contains spaces (may cause issues with Gmail)")
        print("   Solution: Remove spaces from the password or use app-specific password")
    
    print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"Emergency Email: {EMERGENCY_EMAIL}")
    print(f"CC Emails: {CC_EMAILS if CC_EMAILS else 'None'}")

def test_smtp_connection():
    print_section("2. SMTP CONNECTION TEST")
    
    try:
        print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5)
        print("✓ TCP Connection successful")
        
        print("Attempting STARTTLS...")
        server.starttls()
        print("✓ STARTTLS successful")
        
        print(f"Attempting login with username: {EMAIL_USERNAME}")
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        print("✓ Authentication successful!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"✗ AUTHENTICATION FAILED: {e}")
        print("\nPossible solutions:")
        print("1. For Gmail: Use App Password, NOT regular password")
        print("   - Enable 2-Factor Authentication")
        print("   - Generate App Password: https://myaccount.google.com/apppasswords")
        print("2. Check if email address is correct")
        print("3. Check if password has extra spaces (copy carefully)")
        print("4. Ensure Less Secure App Access is enabled (if using older Gmail)")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"✗ SERVER DISCONNECTED: {e}")
        print("Possible solutions:")
        print("1. Check internet connection")
        print("2. Verify SMTP server address is correct")
        print("3. Check firewall/proxy settings")
        print("4. Try alternative SMTP server")
        return False
        
    except smtplib.SMTPException as e:
        print(f"✗ SMTP ERROR: {e}")
        return False
        
    except Exception as e:
        print(f"✗ CONNECTION ERROR: {e}")
        return False

def test_email_sending():
    print_section("3. EMAIL SENDING TEST")
    
    try:
        # Create test email manually
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = EMERGENCY_EMAIL
        msg['Subject'] = "🧪 Test Email - Arduino Sound Detector"
        msg['X-Priority'] = '1'
        
        test_message = f"""Test Email from Arduino Sound Detector

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you received this email, the email configuration is working correctly!

Test Configuration:
- From: {EMAIL_USERNAME}
- To: {EMERGENCY_EMAIL}
- Server: {SMTP_SERVER}:{SMTP_PORT}
"""
        
        msg.attach(MIMEText(test_message, 'plain'))
        
        print(f"Attempting to send test email to: {EMERGENCY_EMAIL}")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, [EMERGENCY_EMAIL], text)
        server.quit()
        
        print("✓ Test email sent successfully!")
        return True
            
    except Exception as e:
        print(f"✗ Email sending error: {e}")
        return False

def check_email_settings():
    print_section("4. EMAIL CONFIGURATION")
    
    print(f"Cooldown Settings:")
    print(f"  Emergency Cooldown: {EMERGENCY_COOLDOWN} seconds")
    print(f"  Anomaly Cooldown: {ANOMALY_COOLDOWN} seconds")
    print(f"  High Severity Only: {HIGH_SEVERITY_ONLY}")
    
    if EMERGENCY_COOLDOWN < 10:
        print("⚠️  WARNING: Emergency cooldown is very short (may spam emails)")
    
    if ANOMALY_COOLDOWN < 60:
        print("⚠️  WARNING: Anomaly cooldown is very short (may spam emails)")

def main():
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*15 + "EMAIL CONFIGURATION DIAGNOSTIC TOOL" + " "*9 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        'Credentials': True,
        'SMTP Connection': False,
        'Email Sending': False,
        'Configuration': True
    }
    
    check_credentials()
    results['SMTP Connection'] = test_smtp_connection()
    
    if results['SMTP Connection']:
        results['Email Sending'] = test_email_sending()
    
    check_email_settings()
    
    # Summary
    print_section("SUMMARY")
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ All tests PASSED! Email is ready to use.")
    else:
        print("✗ Some tests FAILED. Check the above for solutions.")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
