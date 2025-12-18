#!/usr/bin/env python3
"""
ESP32 Sound Detector Email Integration
Optimized for ESP32 with 12-bit ADC and high-speed serial communication
Monitors ESP32 serial output and sends email alerts for emergencies and anomalies
"""

import sys
import time
import signal
from datetime import datetime
from arduino_reader import ArduinoReader
from message_parser import ArduinoMessageParser
from email_sender import EmailSender
from config import *

class ESP32EmailIntegration:
    def __init__(self):
        self.esp32 = ArduinoReader(ARDUINO_PORT, BAUDRATE, SERIAL_TIMEOUT)
        self.parser = ArduinoMessageParser()
        self.email_sender = EmailSender()
        self.running = False
        self.stats = {
            'messages_processed': 0,
            'emergencies_detected': 0,
            'anomalies_detected': 0,
            'start_time': time.time(),
            'location': 'Unknown',
            'device_id': 'ESP32_SOUND_001',
            'baseline': 200,
            'esp32_ready': False
        }
        
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def setup(self):
        """Setup ESP32 connection and email"""
        print("=" * 70)
        print("ESP32 SOUND DETECTOR - EMAIL INTEGRATION SYSTEM")
        print("=" * 70)
        print(f"Device: ESP32 (12-bit ADC, 240MHz, 115200 baud)")
        print(f"Target Port: {ARDUINO_PORT}")
        print(f"Baudrate: {BAUDRATE} (high-speed)")
        print(f"Emergency Email: {EMERGENCY_EMAIL}")
        print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
        if CC_EMAILS:
            print(f"CC Recipients: {', '.join(CC_EMAILS)}")
        print()
        
        # Test email first
        print("Testing email configuration...")
        if not self.email_sender.test_connection():
            print("\n" + "="*60)
            print("⚠️  EMAIL SETUP REQUIRED")
            print("="*60)
            print("For Gmail:")
            print("1. Enable 2-Factor Authentication")
            print("2. Generate App Password: https://myaccount.google.com/apppasswords")
            print("3. Update config.py with your App Password")
            print()
            print("Update config.py:")
            print("  EMAIL_USERNAME = 'your_email@gmail.com'")
            print("  EMAIL_PASSWORD = 'your_app_password'")
            print("  EMERGENCY_EMAIL = 'recipient@example.com'")
            print("="*60)
            return False
        
        # Connect to ESP32
        print(f"\nConnecting to ESP32 on {ARDUINO_PORT}...")
        if not self.esp32.connect():
            print("Trying alternative ports...")
            
            alternative_ports = [
                'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',  # Windows
                '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0',  # Linux
                '/dev/cu.usbserial-0001', '/dev/cu.usbmodem14101'  # Mac
            ]
            
            connected = False
            for port in alternative_ports:
                if port != ARDUINO_PORT:
                    print(f"  Trying {port}...")
                    self.esp32.port = port
                    if self.esp32.connect():
                        print(f"✓ Connected to ESP32 on {port}")
                        connected = True
                        break
                    time.sleep(0.5)
            
            if not connected:
                print("✗ Failed to connect to ESP32!")
                print("\nTroubleshooting:")
                print("1. Check USB connection")
                print("2. Verify ESP32 code is uploaded")
                print("3. Check port in config.py")
                print("4. Try unplugging and reconnecting ESP32")
                return False
        
        # Start reading from ESP32
        print("\nStarting ESP32 communication...")
        if not self.esp32.start_reading():
            print("✗ Failed to start reading from ESP32")
            return False
        
        # Wait for ESP32 to calibrate (ESP32 needs time to initialize)
        print(f"Waiting {ESP32_INIT_DELAY}s for ESP32 initialization and calibration...")
        time.sleep(ESP32_INIT_DELAY)
        
        # Check for ESP32 ready messages
        print("Checking ESP32 status...")
        ready_check_start = time.time()
        esp32_responding = False
        
        while time.time() - ready_check_start < 10:
            msg = self.esp32.get_message(timeout=0.5)
            if msg:
                print(f"  ESP32: {msg}")
                if 'READY' in msg or 'MONITORING' in msg or 'ESP32' in msg:
                    esp32_responding = True
                    self.stats['esp32_ready'] = True
                if 'BASELINE:' in msg:
                    try:
                        self.stats['baseline'] = int(msg.split(':')[1].strip())
                    except:
                        pass
                if 'LOCATION' in msg:
                    try:
                        self.stats['location'] = msg.split(':')[-1].strip()
                    except:
                        pass
        
        if esp32_responding:
            print("✓ ESP32 is responding and ready!")
        else:
            print("⚠️  ESP32 not responding to status checks")
            print("   Continuing anyway - ESP32 may be working")
        
        print("✓ ESP32 setup complete!")
        print("✓ Email setup complete!")
        print()
        return True
    
    def run(self):
        """Main integration loop"""
        if not self.setup():
            print("Setup failed. Exiting.")
            return False
        
        self.running = True
        
        print("=" * 70)
        print("🚀 ESP32 EMAIL INTEGRATION STARTED!")
        print("=" * 70)
        print("✓ Monitoring ESP32 for sound anomalies and emergencies")
        print("✓ HELP voice command detection enabled")
        print("✓ Email alerts configured")
        print()
        print("💡 Say 'HELP' near the sensor to test emergency detection")
        print("💡 Press Ctrl+C to stop")
        print()
        print("📝 Manual test commands (type + Enter):")
        print("   'test_emergency' - Simulate HELP detection")
        print("   'test_anomaly'   - Simulate sound anomaly")
        print("   'status'         - Show current stats")
        print("   'esp32_status'   - Request ESP32 status")
        print("   'esp32_testhelp' - Trigger ESP32 HELP test")
        print("   'esp32_baseline' - Recalibrate ESP32 baseline")
        print("=" * 70)
        print()
        
        # Send startup email
        self._send_startup_email()
        
        # Start input handler thread
        import threading
        input_thread = threading.Thread(target=self._input_handler, daemon=True)
        input_thread.start()
        
        try:
            last_status_time = time.time()
            last_report_time = time.time()
            
            while self.running:
                # Get message from ESP32
                message = self.esp32.get_message(timeout=1.0)
                
                if message:
                    self.stats['messages_processed'] += 1
                    
                    # Parse the message
                    parsed_data = self.parser.parse_message(message)
                    
                    # Also try ESP32-specific detection
                    if not parsed_data:
                        parsed_data = self._detect_esp32_patterns(message)
                    
                    if parsed_data:
                        self._handle_parsed_data(parsed_data)
                    
                    # Show periodic stats
                    if self.stats['messages_processed'] % 100 == 0:
                        self._show_stats()
                
                # Show status every 60 seconds
                if time.time() - last_status_time > 60:
                    self._show_current_status()
                    last_status_time = time.time()
                
                # Send daily report
                if time.time() - last_report_time > 86400:  # 24 hours
                    self._send_daily_report()
                    last_report_time = time.time()
                
                time.sleep(0.05)  # Fast polling for ESP32
        
        except Exception as e:
            print(f"✗ Error in main loop: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self._cleanup()
        
        return True
    
    def _detect_esp32_patterns(self, message):
        """Detect ESP32-specific patterns"""
        msg_upper = message.upper()
        
        # ESP32 HELP detection patterns
        help_triggers = [
            'HELP_DETECTED',
            'EMERGENCY:HELP',
            'VOICE_HELP',
            'PERSON NEEDS HELP',
            'HELP COMMAND'
        ]
        
        for trigger in help_triggers:
            if trigger in msg_upper:
                return {
                    'type': 'emergency',
                    'emergency_type': 'HELP',
                    'level': 999,
                    'immediate': True,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'esp32_help_detection',
                    'trigger_message': message
                }
        
        # ESP32 baseline updates
        if 'BASELINE:' in message or 'ESP32_BASELINE:' in message:
            try:
                baseline = int(message.split(':')[-1].strip())
                self.stats['baseline'] = baseline
                print(f"📊 ESP32 Baseline updated: {baseline}/4095")
            except:
                pass
        
        # ESP32 sound level detection (12-bit ADC)
        if 'LEVEL:' in msg_upper or 'CURRENT:' in msg_upper:
            try:
                parts = message.split(':')
                level = int(parts[-1].strip())
                
                if level > 1500:  # High threshold for ESP32
                    severity = 'CRITICAL' if level > 3000 else 'HIGH' if level > 2000 else 'MEDIUM'
                    return {
                        'type': 'anomaly',
                        'severity': severity,
                        'level': level,
                        'baseline': self.stats.get('baseline', 200),
                        'difference': level - self.stats.get('baseline', 200),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'esp32_adc_reading'
                    }
            except:
                pass
        
        return None
    
    def _handle_parsed_data(self, data):
        """Handle parsed message data"""
        data_type = data.get('type')
        
        if 'location' in data:
            self.stats['location'] = data['location']
        
        if data_type == 'emergency':
            self._handle_emergency(data)
        elif data_type == 'anomaly':
            self._handle_anomaly(data)
        elif data_type == 'status':
            self._handle_status(data)
    
    def _handle_emergency(self, data):
        """Handle emergency detection"""
        self.stats['emergencies_detected'] += 1
        
        print("\n" + "🚨" * 30)
        print("🚨 EMERGENCY DETECTED - HELP COMMAND!")
        print("🚨" * 30)
        print(f"Type: {data.get('emergency_type', 'HELP')}")
        print(f"Location: {data.get('location', self.stats['location'])}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Sound Level: {data.get('level', 'Unknown')}/4095")
        print(f"Source: {data.get('source', 'ESP32')}")
        print("🚨" * 30)
        print()
        
        # Send emergency email
        emergency_data = {
            'emergency_type': data.get('emergency_type', 'HELP'),
            'location': data.get('location', self.stats['location']),
            'sound_level': data.get('level', 999),
            'device_id': self.stats['device_id'],
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'uptime': self._get_uptime(),
            'contact': EMERGENCY_CONTACT if 'EMERGENCY_CONTACT' in dir() else 'N/A'
        }
        
        success = self.email_sender.send_emergency_email(emergency_data)
        
        if success:
            print("✓ Emergency email sent successfully!")
        else:
            print("✗ Failed to send emergency email")
        print()
    
    def _handle_anomaly(self, data):
        """Handle anomaly detection"""
        severity = data.get('severity', 'MEDIUM').upper()
        
        if HIGH_SEVERITY_ONLY and severity not in ['HIGH', 'CRITICAL']:
            return
        
        self.stats['anomalies_detected'] += 1
        
        print(f"\n⚠️  SOUND ANOMALY DETECTED - {severity}")
        print(f"Level: {data.get('level', 'Unknown')}/4095")
        print(f"Baseline: {data.get('baseline', 'Unknown')}/4095")
        print(f"Difference: +{data.get('difference', 'Unknown')}")
        print(f"Location: {data.get('location', self.stats['location'])}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        anomaly_data = {
            'severity': severity,
            'level': data.get('level', 0),
            'baseline': data.get('baseline', self.stats['baseline']),
            'difference': data.get('difference', 0),
            'location': data.get('location', self.stats['location']),
            'device_id': self.stats['device_id'],
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'uptime': self._get_uptime()
        }
        
        if severity in ['HIGH', 'CRITICAL']:
            success = self.email_sender.send_anomaly_email(anomaly_data)
            if success:
                print("✓ Anomaly email sent!")
            else:
                print("✗ Failed to send anomaly email")
        else:
            print(f"Severity '{severity}' - logged only, no email")
        print()
    
    def _handle_status(self, data):
        """Handle status messages"""
        field = data.get('field', '')
        value = data.get('value', '')
        
        if field == 'ready':
            print("✓ ESP32 ready and monitoring")
            self.stats['esp32_ready'] = True
        elif field == 'baseline':
            try:
                self.stats['baseline'] = int(value)
                print(f"📊 ESP32 Baseline: {value}/4095")
            except:
                pass
    
    def _send_startup_email(self):
        """Send startup notification email"""
        subject = STARTUP_SUBJECT.format(location=self.stats['location'])
        message = STARTUP_TEMPLATE.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            location=self.stats['location'],
            device_id=self.stats['device_id'],
            emergency_email=EMERGENCY_EMAIL,
            emergency_cooldown=EMERGENCY_COOLDOWN,
            anomaly_cooldown=ANOMALY_COOLDOWN,
            high_severity_only=HIGH_SEVERITY_ONLY
        )
        
        if self.email_sender._send_email(subject, message):
            print("✓ Startup notification email sent\n")
    
    def _send_daily_report(self):
        """Send daily status report"""
        uptime_hours = (time.time() - self.stats['start_time']) / 3600
        
        subject = STATUS_SUBJECT.format(
            date=datetime.now().strftime('%Y-%m-%d')
        )
        message = STATUS_TEMPLATE.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            location=self.stats['location'],
            device_id=self.stats['device_id'],
            status='Online and Monitoring',
            uptime_hours=uptime_hours,
            messages_processed=self.stats['messages_processed'],
            emergencies_detected=self.stats['emergencies_detected'],
            anomalies_detected=self.stats['anomalies_detected'],
            total_emails=self.email_sender.emergency_count + self.email_sender.anomaly_count,
            emergency_emails=self.email_sender.emergency_count,
            anomaly_emails=self.email_sender.anomaly_count,
            baseline=self.stats['baseline'],
            emergency_cooldown=EMERGENCY_COOLDOWN,
            anomaly_cooldown=ANOMALY_COOLDOWN,
            high_severity_only=HIGH_SEVERITY_ONLY
        )
        
        if self.email_sender._send_email(subject, message):
            print("✓ Daily status report sent")
    
    def _show_stats(self):
        """Show statistics"""
        uptime = self._get_uptime()
        print(f"📊 Stats: {self.stats['messages_processed']} msgs, "
              f"{self.stats['emergencies_detected']} emergencies, "
              f"{self.stats['anomalies_detected']} anomalies | "
              f"Emails: {self.email_sender.emergency_count} emergency, "
              f"{self.email_sender.anomaly_count} anomaly | "
              f"Uptime: {uptime}")
    
    def _show_current_status(self):
        """Show current status"""
        uptime = self._get_uptime()
        print(f"\n📈 System Status:")
        print(f"   ESP32: {'✓ Connected' if self.esp32.is_connected else '✗ Disconnected'}")
        print(f"   Baseline: {self.stats['baseline']}/4095")
        print(f"   Uptime: {uptime}")
        print(f"   Messages: {self.stats['messages_processed']}")
        print(f"   Emergencies: {self.stats['emergencies_detected']}")
        print(f"   Anomalies: {self.stats['anomalies_detected']}\n")
    
    def _get_uptime(self):
        """Get formatted uptime"""
        uptime_seconds = int(time.time() - self.stats['start_time'])
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _input_handler(self):
        """Handle user input commands"""
        while self.running:
            try:
                cmd = input().strip().lower()
                
                if cmd == 'test_emergency':
                    print("🧪 Simulating HELP detection...")
                    self._handle_emergency({
                        'type': 'emergency',
                        'emergency_type': 'HELP',
                        'level': 999,
                        'timestamp': datetime.now().isoformat()
                    })
                
                elif cmd == 'test_anomaly':
                    print("🧪 Simulating HIGH anomaly...")
                    self._handle_anomaly({
                        'type': 'anomaly',
                        'severity': 'HIGH',
                        'level': 2500,
                        'baseline': self.stats['baseline'],
                        'difference': 2500 - self.stats['baseline'],
                        'timestamp': datetime.now().isoformat()
                    })
                
                elif cmd == 'status':
                    self._show_current_status()
                
                elif cmd.startswith('esp32_'):
                    esp32_cmd = cmd.replace('esp32_', '').upper()
                    if self.esp32.is_connected:
                        print(f"📤 Sending to ESP32: {esp32_cmd}")
                        self.esp32.send_command(esp32_cmd)
                    else:
                        print("✗ ESP32 not connected")
            
            except:
                pass
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\n🛑 Shutdown requested...")
        self.running = False
    
    def _cleanup(self):
        """Cleanup and shutdown"""
        print("\n🔄 Shutting down...")
        self.running = False
        
        # Send shutdown email
        subject = SHUTDOWN_SUBJECT.format(location=self.stats['location'])
        message = SHUTDOWN_TEMPLATE.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            location=self.stats['location'],
            device_id=self.stats['device_id'],
            uptime=self._get_uptime(),
            messages_processed=self.stats['messages_processed'],
            emergencies_detected=self.stats['emergencies_detected'],
            anomalies_detected=self.stats['anomalies_detected'],
            total_emails=self.email_sender.emergency_count + self.email_sender.anomaly_count
        )
        
        try:
            self.email_sender._send_email(subject, message)
            print("✓ Shutdown notification sent")
        except:
            pass
        
        self.esp32.disconnect()
        self._show_stats()
        print("\n✓ ESP32 integration stopped\n")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            print("Testing email functionality...")
            sender = EmailSender()
            if sender.test_connection() and sender.send_test_email():
                print("✓ Email test successful!")
            return
        
        elif sys.argv[1] == 'help':
            print("""
ESP32 Sound Detector Email Integration

Usage:
  python main_esp32.py        - Run integration
  python main_esp32.py test   - Test email
  python main_esp32.py help   - Show help

ESP32 Features:
  - 12-bit ADC (0-4095 range)
  - 115200 baudrate
  - HELP voice command detection
  - Real-time email alerts
            """)
            return
    
    integration = ESP32EmailIntegration()
    integration.run()

if __name__ == "__main__":
    main()