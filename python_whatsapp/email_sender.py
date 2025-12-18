import smtplib
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import *

# Try to import desktop notifications
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("Warning: plyer not available - desktop notifications disabled")

class EmailSender:
    def __init__(self):
        self.last_emergency_time = 0
        self.last_anomaly_time = 0
        self.emergency_count = 0
        self.anomaly_count = 0
        self.smtp_connection = None
    
    def test_connection(self):
        """Test email server connection"""
        try:
            print("Testing email server connection...")
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.quit()
            print("✓ Email server connection successful!")
            return True
        except smtplib.SMTPAuthenticationError:
            print("✗ Email authentication failed!")
            print("Please check your email username and password.")
            print("For Gmail, make sure you're using an App Password, not your regular password.")
            return False
        except smtplib.SMTPServerDisconnected:
            print("✗ Could not connect to email server!")
            print(f"Please check SMTP server settings: {SMTP_SERVER}:{SMTP_PORT}")
            return False
        except Exception as e:
            print(f"✗ Email connection error: {e}")
            return False
    
    def send_emergency_email(self, emergency_data):
        """Send emergency email alert"""
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_emergency_time < EMERGENCY_COOLDOWN:
            print(f"Emergency cooldown active ({EMERGENCY_COOLDOWN - (current_time - self.last_emergency_time):.0f}s remaining)")
            return False
        
        # Format the emergency email
        subject = EMERGENCY_SUBJECT.format(
            location=emergency_data.get('location', 'Unknown Location')
        )
        message = self._format_emergency_message(emergency_data)
        
        # Send email
        success = self._send_email(subject, message, is_emergency=True)
        
        if success:
            self.last_emergency_time = current_time
            self.emergency_count += 1
            print(f"🚨 Emergency Email #{self.emergency_count} sent successfully!")
            
            # Send desktop notification
            self._send_desktop_notification(
                "🚨 EMERGENCY EMAIL SENT",
                f"Email sent to {EMERGENCY_EMAIL}"
            )
            
            # Log the emergency
            self._log_message("EMERGENCY", emergency_data, message)
        
        return success
    
    def send_anomaly_email(self, anomaly_data):
        """Send anomaly email alert (only for high severity)"""
        severity = anomaly_data.get('severity', '').upper()
        
        # Only send email for high severity anomalies
        if HIGH_SEVERITY_ONLY and severity not in ['HIGH', 'CRITICAL']:
            print(f"Anomaly severity '{severity}' below threshold for email")
            return False
        
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_anomaly_time < ANOMALY_COOLDOWN:
            print(f"Anomaly cooldown active ({ANOMALY_COOLDOWN - (current_time - self.last_anomaly_time):.0f}s remaining)")
            return False
        
        # Format the anomaly email
        subject = ANOMALY_SUBJECT.format(
            severity=severity,
            location=anomaly_data.get('location', 'Unknown Location')
        )
        message = self._format_anomaly_message(anomaly_data)
        
        # Send email
        success = self._send_email(subject, message, is_emergency=False)
        
        if success:
            self.last_anomaly_time = current_time
            self.anomaly_count += 1
            print(f"⚠️ Anomaly Email #{self.anomaly_count} sent successfully!")
            
            # Send desktop notification
            self._send_desktop_notification(
                f"⚠️ {severity} ANOMALY EMAIL SENT",
                f"Email sent to {EMERGENCY_EMAIL}"
            )
            
            # Log the anomaly
            self._log_message("ANOMALY", anomaly_data, message)
        
        return success
    
    def _format_emergency_message(self, data):
        """Format emergency message using template"""
        return EMERGENCY_TEMPLATE.format(
            location=data.get('location', 'Unknown Location'),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            sound_level=data.get('sound_level', 'Unknown'),
            device_id=data.get('emergency_id', 'SOUND_001'),
            uptime=data.get('uptime', 'Unknown')
        )
    
    def _format_anomaly_message(self, data):
        """Format anomaly message using template"""
        return ANOMALY_TEMPLATE.format(
            location=data.get('location', 'Unknown Location'),
            severity=data.get('severity', 'Unknown'),
            level=data.get('level', 'Unknown'),
            baseline=data.get('baseline', 'Unknown'),
            difference=data.get('difference', 'Unknown'),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            device_id=data.get('alert_id', 'SOUND_001'),
            uptime=data.get('uptime', 'Unknown')
        )
    
    def _send_email(self, subject, message, is_emergency=False):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USERNAME
            msg['To'] = EMERGENCY_EMAIL
            
            # Add CC recipients if specified
            if CC_EMAILS:
                msg['Cc'] = ', '.join(CC_EMAILS)
                recipients = [EMERGENCY_EMAIL] + CC_EMAILS
            else:
                recipients = [EMERGENCY_EMAIL]
            
            msg['Subject'] = subject
            
            # Add priority for emergencies
            if is_emergency:
                msg['X-Priority'] = '1'  # High priority
                msg['X-MSMail-Priority'] = 'High'
            
            # Attach message
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            print(f"Sending email to {recipients}...")
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            
            text = msg.as_string()
            server.sendmail(EMAIL_USERNAME, recipients, text)
            server.quit()
            
            print(f"✓ Email sent successfully to {len(recipients)} recipient(s)")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"✗ Email authentication error: {e}")
            print("Check your email credentials and app password")
            return False
        except smtplib.SMTPException as e:
            print(f"✗ SMTP error: {e}")
            return False
        except Exception as e:
            print(f"✗ Email send error: {e}")
            return False
    
    def _send_desktop_notification(self, title, message):
        """Send desktop notification"""
        if not DESKTOP_NOTIFICATIONS or not NOTIFICATIONS_AVAILABLE:
            return
        
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=10
            )
        except Exception as e:
            print(f"Desktop notification error: {e}")
    
    def _log_message(self, msg_type, data, sent_message):
        """Log sent messages to file"""
        if not LOG_MESSAGES:
            return
        
        try:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(LOG_FILE)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            timestamp = datetime.now().isoformat()
            
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"{timestamp} - {msg_type} EMAIL SENT\n")
                f.write(f"Recipients: {EMERGENCY_EMAIL}")
                if CC_EMAILS:
                    f.write(f", {', '.join(CC_EMAILS)}")
                f.write(f"\nData: {data}\n")
                f.write(f"Message: {sent_message}\n")
                f.write(f"{'='*50}\n")
        
        except Exception as e:
            print(f"Logging error: {e}")
    
    def send_test_email(self):
        """Send test email"""
        test_subject = "🧪 Arduino Sound Detector Test Email"
        test_message = f"""🧪 TEST EMAIL

Arduino Sound Detector Email Integration Test
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a test email to verify that the email integration is working correctly.

If you received this email, the system is properly configured and ready to send:
- Emergency alerts when HELP commands are detected
- Anomaly alerts for unusual sound patterns

System Configuration:
- SMTP Server: {SMTP_SERVER}:{SMTP_PORT}
- Sender: {EMAIL_USERNAME}
- Emergency Contact: {EMERGENCY_EMAIL}
- CC Recipients: {', '.join(CC_EMAILS) if CC_EMAILS else 'None'}

The system is now monitoring for sound anomalies.

This is an automated test message from your Arduino Sound Detector.
"""
        
        print("Sending test email...")
        success = self._send_email(test_subject, test_message, is_emergency=False)
        
        if success:
            print("✓ Test email sent successfully!")
            print(f"Check your inbox at {EMERGENCY_EMAIL}")
        else:
            print("✗ Test email failed!")
        
        return success
    
    def get_stats(self):
        """Get sending statistics"""
        return {
            'emergency_count': self.emergency_count,
            'anomaly_count': self.anomaly_count,
            'last_emergency': self.last_emergency_time,
            'last_anomaly': self.last_anomaly_time
        }
    
    def send_status_report(self, system_stats):
        """Send periodic status report"""
        subject = f"📊 Arduino Sound Detector Status Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        uptime_seconds = system_stats.get('uptime', 0)
        uptime_hours = uptime_seconds / 3600
        
        message = f"""📊 ARDUINO SOUND DETECTOR STATUS REPORT

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
System Status: Online and Monitoring

Statistics:
- System Uptime: {uptime_hours:.1f} hours
- Messages Processed: {system_stats.get('messages_processed', 0)}
- Emergencies Detected: {system_stats.get('emergencies_detected', 0)}
- Anomalies Detected: {system_stats.get('anomalies_detected', 0)}
- Emails Sent: {self.emergency_count + self.anomaly_count}

Email Breakdown:
- Emergency Emails: {self.emergency_count}
- Anomaly Emails: {self.anomaly_count}

Current Settings:
- Emergency Cooldown: {EMERGENCY_COOLDOWN}s
- Anomaly Cooldown: {ANOMALY_COOLDOWN}s
- High Severity Only: {HIGH_SEVERITY_ONLY}

Device Information:
- Location: {system_stats.get('location', 'Unknown')}
- Device ID: {system_stats.get('device_id', 'SOUND_001')}

This automated status report confirms your sound detector is operating normally.
"""
        
        return self._send_email(subject, message, is_emergency=False)