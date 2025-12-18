#!/usr/bin/env python3
"""
Arduino Sound Detector Email Integration - NO ARDUINO TEST VERSION
Monitors Arduino serial output and sends email alerts for emergencies and anomalies
This version skips the Arduino communication test to allow the system to run
"""

import sys
import time
import signal
from datetime import datetime
from arduino_reader import ArduinoReader
from message_parser import ArduinoMessageParser
from email_sender import EmailSender
from config import *

class ArduinoEmailIntegration:
    def __init__(self):
        self.arduino = ArduinoReader(ARDUINO_PORT, BAUDRATE, SERIAL_TIMEOUT)
        self.parser = ArduinoMessageParser()
        self.email_sender = EmailSender()
        self.running = False
        self.stats = {
            'messages_processed': 0,
            'emergencies_detected': 0,
            'anomalies_detected': 0,
            'start_time': time.time(),
            'location': 'Unknown',
            'device_id': 'SOUND_001'
        }
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def setup(self):
        """Setup Arduino connection and email (SKIP ARDUINO TEST)"""
        print("=" * 60)
        print("ARDUINO SOUND DETECTOR - EMAIL INTEGRATION")
        print("=" * 60)
        print(f"Target Arduino Port: {ARDUINO_PORT}")
        print(f"Emergency Email: {EMERGENCY_EMAIL}")
        print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
        if CC_EMAILS:
            print(f"CC Recipients: {', '.join(CC_EMAILS)}")
        print()
        
        # Test email connection first
        print("Testing email configuration...")
        if not self.email_sender.test_connection():
            print("\n" + "="*50)
            print("EMAIL SETUP INSTRUCTIONS:")
            print("="*50)
            print("1. For Gmail users:")
            print("   - Enable 2-Factor Authentication")
            print("   - Generate an App Password:")
            print("     https://myaccount.google.com/apppasswords")
            print("   - Use the App Password in config.py, not your regular password")
            print()
            print("2. Update config.py with your settings:")
            print("   - EMAIL_USERNAME = 'your_email@gmail.com'")
            print("   - EMAIL_PASSWORD = 'your_app_password'")
            print("   - EMERGENCY_EMAIL = 'recipient@example.com'")
            print()
            print("3. For other email providers:")
            print("   - Update SMTP_SERVER and SMTP_PORT in config.py")
            print("   - Ensure 'Less secure app access' is enabled if required")
            print("="*50)
            print("Setup failed. Exiting.")
            return False
        
        # Try multiple ports for Arduino
        if not self.arduino.connect():
            # Try other common ports
            other_ports = ['COM3', 'COM4', 'COM6', 'COM7']
            connected = False
            for port in other_ports:
                print(f"Trying alternative port: {port}")
                self.arduino.port = port
                if self.arduino.connect():
                    connected = True
                    break
            
            if not connected:
                print("✗ Failed to connect to Arduino on any port!")
                print("Please check:")
                print("1. Arduino is connected via USB")
                print("2. Arduino code is uploaded and running")
                print("3. Correct port is specified in config.py")
                print("\nContinuing without Arduino for now...")
                print("You can upload the Arduino code and restart later")
        
        # SKIP Arduino communication test - just start reading
        print("⚠️  Skipping Arduino communication test...")
        print("📝 Starting Arduino reader (will show any messages received)")
        
        if self.arduino.is_connected:
            if not self.arduino.start_reading():
                print("✗ Failed to start reading from Arduino")
                print("Continuing anyway - will retry connection during operation")
        
        print("✓ Email setup complete!")
        print("✓ System setup complete!")
        print()
        return True
    
    def run(self):
        """Main integration loop"""
        if not self.setup():
            return
        
        print("=" * 60)
        print("ARDUINO SOUND DETECTOR - RUNNING")
        print("=" * 60)
        print("✓ System ready and monitoring...")
        print("✓ Emergency alerts will be sent to:", EMERGENCY_EMAIL)
        if CC_EMAILS:
            print("✓ CC recipients:", ', '.join(CC_EMAILS))
        print()
        print("Say 'HELP' near the sensor to test emergency detection")
        print("Press Ctrl+C to stop the system")
        print()
        print("🧪 MANUAL TEST COMMANDS:")
        print("   Type 'test_emergency' + Enter to simulate HELP detection")
        print("   Type 'test_anomaly' + Enter to simulate sound anomaly")
        print("   Type 'status' + Enter to show current stats")
        print("   Type 'trigger_help' + Enter to make ESP32 send HELP signal")
        print("   Type 'send_arduino_test' + Enter to send test to ESP32")
        print("   Type 'arduino_testhelp' + Enter to trigger ESP32 HELP test")
        print("   Type 'arduino_status' + Enter to request ESP32 status")
        print("=" * 60)
        print()
        
        self.running = True
        
        # Start input thread for manual test commands
        import threading
        input_thread = threading.Thread(target=self._input_handler, daemon=True)
        input_thread.start()
        
        try:
            while self.running:
                # Try to reconnect Arduino if disconnected
                if not self.arduino.is_connected:
                    print("⚠️  Arduino disconnected, attempting to reconnect...")
                    if self.arduino.connect():
                        self.arduino.start_reading()
                        print("✓ Arduino reconnected")
                    else:
                        print("✗ Arduino still disconnected, will retry in 10 seconds")
                        time.sleep(10)
                        continue
                
                # Get message from Arduino
                message = self.arduino.get_message(timeout=1.0)
                
                if message:
                    print(f"📨 Arduino: {message}")
                    self.stats['messages_processed'] += 1
                    
                    # Parse the message
                    parsed = self.parser.parse_message(message)
                    
                    # Also check for simple volume-based detection
                    if not parsed:
                        parsed = self._simple_detection(message)
                    
                    # DEBUG: Show what was parsed
                    if parsed:
                        print(f"🔍 PARSED: {parsed}")
                    
                    if parsed:
                        # Handle emergency detection
                        if parsed['type'] == 'emergency':
                            self._handle_emergency(parsed)
                        
                        # Handle anomaly detection
                        elif parsed['type'] == 'anomaly':
                            self._handle_anomaly(parsed)
                        
                        # Handle status updates
                        elif parsed['type'] == 'status':
                            self._handle_status(parsed)
                    
                # Show periodic status
                self._show_periodic_status()
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
        except Exception as e:
            print(f"✗ Error in main loop: {e}")
        finally:
            self.shutdown()
    
    def _input_handler(self):
        """Handle manual test commands from user input"""
        try:
            while self.running:
                try:
                    user_input = input().strip().lower()
                    
                    if user_input == 'test_emergency':
                        print("🧪 SIMULATING EMERGENCY...")
                        test_emergency = {
                            'type': 'emergency',
                            'emergency_type': 'HELP',
                            'level': 999,
                            'immediate': True,
                            'timestamp': datetime.now().isoformat()
                        }
                        self._handle_emergency(test_emergency)
                        
                    elif user_input == 'test_anomaly':
                        print("🧪 SIMULATING ANOMALY...")
                        test_anomaly = {
                            'type': 'anomaly',
                            'severity': 'HIGH',
                            'level': 200,
                            'baseline': 45,
                            'difference': 155,
                            'timestamp': datetime.now().isoformat()
                        }
                        self._handle_anomaly(test_anomaly)
                        
                    elif user_input == 'status':
                        self._show_current_status()
                        
                    elif user_input == 'send_arduino_test':
                        if self.arduino.is_connected:
                            print("🧪 Sending test command to Arduino...")
                            self.arduino.send_command("TEST_EMERGENCY")
                        else:
                            print("❌ Arduino not connected")
                    
                    elif user_input == 'trigger_help':
                        if self.arduino.is_connected:
                            print("🧪 Triggering HELP detection on Arduino...")
                            # Send command to Arduino to simulate HELP detection
                            self.arduino.send_command("SIMULATE_HELP")
                        else:
                            print("❌ Arduino not connected")
                            
                    elif user_input.startswith('arduino_'):
                        command = user_input.replace('arduino_', '').upper()
                        if self.arduino.is_connected:
                            print(f"🧪 Sending command to Arduino: {command}")
                            self.arduino.send_command(command)
                        else:
                            print("❌ Arduino not connected")
                        
                except EOFError:
                    break
                except Exception as e:
                    pass  # Ignore input errors
        except:
            pass

    def _simple_detection(self, message):
        """Simple detection for volume-based emergencies (ESP32 optimized)"""
        message = message.strip()
        
        # Look for HELP command detection - more patterns including ESP32 specific
        help_keywords = ["HELP", "EMERGENCY", "ALERT", "ESP32"]
        detected_keywords = ["DETECTED", "COMMAND", "ALERT", "TRIGGERED", "CALIBRATED"]
        
        message_upper = message.upper()
        
        # Check for ESP32 specific messages
        if "ESP32" in message_upper and any(keyword in message_upper for keyword in help_keywords):
            if any(keyword in message_upper for keyword in detected_keywords):
                return {
                    'type': 'emergency',
                    'emergency_type': 'HELP',
                    'level': 999,
                    'immediate': True,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'esp32_detection',
                    'trigger_message': message
                }
        
        # Check for any HELP-related detection
        has_help = any(keyword in message_upper for keyword in help_keywords)
        has_detection = any(keyword in message_upper for keyword in detected_keywords)
        
        if has_help and has_detection:
            return {
                'type': 'emergency',
                'emergency_type': 'HELP',
                'level': 999,
                'immediate': True,
                'timestamp': datetime.now().isoformat(),
                'source': 'keyword_detection',
                'trigger_message': message
            }
        
        # Look for direct EMERGENCY messages
        if message_upper.startswith("EMERGENCY:") and "HELP" in message_upper:
            return {
                'type': 'emergency',
                'emergency_type': 'HELP',
                'level': 999,
                'immediate': True,
                'timestamp': datetime.now().isoformat(),
                'source': 'emergency_message',
                'trigger_message': message
            }
        
        # ESP32 specific sound level detection (12-bit ADC: 0-4095)
        if ("CURRENT:" in message or "LEVEL:" in message) and ":" in message:
            try:
                # Extract number from message
                parts = message.split(":")
                level = None
                
                for part in parts:
                    try:
                        potential_level = int(part.strip())
                        # ESP32 ADC range check
                        if 0 <= potential_level <= 4095:
                            level = potential_level
                            break
                    except:
                        continue
                
                if level is not None:
                    # ESP32 thresholds (higher due to 12-bit ADC)
                    if level > 1000:  # High threshold for ESP32
                        severity = 'HIGH' if level > 2000 else 'MEDIUM'
                        return {
                            'type': 'anomaly',
                            'severity': severity,
                            'level': level,
                            'baseline': 200,  # Assumed ESP32 baseline
                            'difference': level - 200,
                            'timestamp': datetime.now().isoformat(),
                            'source': 'esp32_volume_detection',
                            'trigger_message': message
                        }
            except:
                pass
        
        # Look for ESP32 baseline values for context
        if "ESP32_BASELINE:" in message_upper or "ESP32_THRESHOLD:" in message_upper:
            return {
                'type': 'status',
                'field': 'esp32_calibration',
                'value': message,
                'timestamp': datetime.now().isoformat()
            }
        
        return None

    def _show_current_status(self):
        """Show current system status"""
        uptime = self._get_uptime()
        print(f"\n📊 CURRENT STATUS:")
        print(f"   Uptime: {uptime}")
        print(f"   Messages: {self.stats['messages_processed']}")
        print(f"   Emergencies: {self.stats['emergencies_detected']}")
        print(f"   Anomalies: {self.stats['anomalies_detected']}")
        print(f"   Arduino: {'✅ Connected' if self.arduino.is_connected else '❌ Disconnected'}")
        print(f"   Email: {'✅ Ready' if self.email_sender else '❌ Not configured'}")
        print()

    def _handle_emergency(self, parsed_data):
        """Handle emergency alerts"""
        print("🚨 EMERGENCY DETECTED!")
        print(f"   Type: {parsed_data.get('emergency_type', 'HELP')}")
        print(f"   Level: {parsed_data.get('level', 'Unknown')}")
        print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.stats['emergencies_detected'] += 1
        
        # Send emergency email
        try:
            emergency_data = {
                'emergency_type': parsed_data.get('emergency_type', 'HELP'),
                'location': self.stats['location'],
                'sound_level': parsed_data.get('level', 0),
                'device_id': self.stats['device_id'],
                'timestamp': parsed_data.get('timestamp', datetime.now().isoformat()),
                'uptime': self._get_uptime()
            }
            
            success = self.email_sender.send_emergency_email(emergency_data)
            
            if success:
                print("   ✅ Emergency email sent successfully!")
            else:
                print("   ❌ Failed to send emergency email")
                
        except Exception as e:
            print(f"   ❌ Error sending emergency email: {e}")
    
    def _handle_anomaly(self, parsed_data):
        """Handle anomaly detection"""
        severity = parsed_data.get('severity', 'MEDIUM')
        
        # Only process high/critical anomalies if configured
        if HIGH_SEVERITY_ONLY and severity not in ['HIGH', 'CRITICAL']:
            return
        
        print(f"⚠️  ANOMALY DETECTED!")
        print(f"   Severity: {severity}")
        print(f"   Level: {parsed_data.get('level', 'Unknown')}")
        print(f"   Baseline: {parsed_data.get('baseline', 'Unknown')}")
        print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.stats['anomalies_detected'] += 1
        
        # Send anomaly email
        try:
            anomaly_data = {
                'severity': severity,
                'sound_level': parsed_data.get('level', 0),
                'baseline': parsed_data.get('baseline', 0),
                'difference': parsed_data.get('difference', 0),
                'location': self.stats['location'],
                'device_id': self.stats['device_id'],
                'timestamp': parsed_data.get('timestamp', datetime.now().isoformat()),
                'uptime': self._get_uptime()
            }
            
            success = self.email_sender.send_anomaly_email(anomaly_data)
            
            if success:
                print("   ✅ Anomaly email sent successfully!")
            else:
                print("   ❌ Failed to send anomaly email")
                
        except Exception as e:
            print(f"   ❌ Error sending anomaly email: {e}")
    
    def _handle_status(self, parsed_data):
        """Handle status updates from Arduino"""
        # Update stats
        if 'baseline' in parsed_data:
            print(f"📊 Status Update - Baseline: {parsed_data['baseline']}")
        if 'uptime' in parsed_data:
            print(f"📊 Arduino Uptime: {parsed_data['uptime']}s")
    
    def _show_periodic_status(self):
        """Show periodic status updates"""
        current_time = time.time()
        if not hasattr(self, '_last_status_time'):
            self._last_status_time = current_time
        
        # Show status every 30 seconds
        if current_time - self._last_status_time > 30:
            uptime = self._get_uptime()
            print(f"\n📈 System Status:")
            print(f"   Uptime: {uptime}")
            print(f"   Messages: {self.stats['messages_processed']}")
            print(f"   Emergencies: {self.stats['emergencies_detected']}")
            print(f"   Anomalies: {self.stats['anomalies_detected']}")
            print(f"   Arduino: {'✅ Connected' if self.arduino.is_connected else '❌ Disconnected'}")
            print()
            self._last_status_time = current_time
    
    def _get_uptime(self):
        """Get system uptime as formatted string"""
        uptime_seconds = int(time.time() - self.stats['start_time'])
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutdown signal received")
        self.running = False
    
    def shutdown(self):
        """Clean shutdown"""
        print("\n🔄 Shutting down...")
        self.running = False
        
        if self.arduino:
            self.arduino.disconnect()
        
        # Final stats
        uptime = self._get_uptime()
        print(f"\n📊 Final Statistics:")
        print(f"   Total Runtime: {uptime}")
        print(f"   Messages Processed: {self.stats['messages_processed']}")
        print(f"   Emergencies Detected: {self.stats['emergencies_detected']}")
        print(f"   Anomalies Detected: {self.stats['anomalies_detected']}")
        print()
        print("✅ System shutdown complete")

def main():
    """Main function"""
    print("🚀 Starting ESP32 Sound Detector (No Arduino Test Version)")
    print("This version will start even if ESP32 doesn't respond to test commands")
    print("Optimized for ESP32 with 115200 baudrate and 12-bit ADC")
    print()
    
    # Run main integration
    integration = ArduinoEmailIntegration()
    integration.run()

if __name__ == "__main__":
    main()