#!/usr/bin/env python3
"""
Streamlit GUI for Arduino Sound Detector with Email Integration
"""

import streamlit as st
import threading
import time
from datetime import datetime
import sys
import os
from collections import deque
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add python_whatsapp to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_whatsapp'))

from arduino_reader import ArduinoReader
from message_parser import ArduinoMessageParser
from email_sender import EmailSender
from config import *

class SoundDetectorApp:
    def __init__(self):
        self.running = False
        self.thread = None
        self.logs = deque(maxlen=100)  # Keep last 100 log messages
        self.stats = {
            'messages_processed': 0,
            'emergencies_detected': 0,
            'anomalies_detected': 0,
            'start_time': None,
            'status': 'Stopped',
            'esp32_ready': False,
            'baseline': 0,
            'location': 'Unknown'
        }
        
    def add_log(self, message, log_type="INFO"):
        """Add a log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] [{log_type}] {message}")
        print(f"[{timestamp}] [{log_type}] {message}")  # Also print to console
        
    def monitoring_loop(self):
        """Main monitoring loop running in background thread"""
        try:
            self.add_log("Initializing system...", "SYSTEM")
            
            # Initialize components
            esp32 = ArduinoReader(ARDUINO_PORT, BAUDRATE, SERIAL_TIMEOUT)
            parser = ArduinoMessageParser()
            email_sender = EmailSender()
            
            # Test email connection
            self.add_log("Testing email configuration...", "SYSTEM")
            if not email_sender.test_connection():
                self.add_log("Email configuration failed! Check config.py", "ERROR")
                self.stats['status'] = 'Error: Email Setup Failed'
                self.running = False
                return
            
            self.add_log("✓ Email configuration OK", "SUCCESS")
            
            # Send "Monitoring Started" email
            self.add_log("📧 Sending monitoring started notification...", "SYSTEM")
            try:
                start_message = f"""
═══════════════════════════════════════════════════════════
🚀 MONITORING STARTED
═══════════════════════════════════════════════════════════

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Device: ESP32 Sound Detector
Location: {self.stats['location']}
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
                msg['Subject'] = "🚀 Sound Detector Monitoring Started"
                msg['X-Priority'] = '2'
                msg.attach(MIMEText(start_message, 'plain'))
                
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5)
                server.starttls()
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, [EMERGENCY_EMAIL], msg.as_string())
                server.quit()
                
                self.add_log("✓ Monitoring started email sent!", "SUCCESS")
            except Exception as e:
                self.add_log(f"⚠️ Could not send start email: {str(e)}", "WARNING")
            
            # Connect to ESP32
            self.add_log(f"Connecting to ESP32 on {ARDUINO_PORT}...", "SYSTEM")
            if not esp32.connect():
                self.add_log(f"Failed to connect on {ARDUINO_PORT}, trying alternatives...", "WARNING")
                
                alternative_ports = ['COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']
                connected = False
                
                for port in alternative_ports:
                    if port != ARDUINO_PORT:
                        self.add_log(f"  Trying {port}...", "INFO")
                        esp32.port = port
                        if esp32.connect():
                            self.add_log(f"✓ Connected to ESP32 on {port}", "SUCCESS")
                            connected = True
                            break
                        time.sleep(0.5)
                
                if not connected:
                    self.add_log("Failed to connect to ESP32!", "ERROR")
                    self.stats['status'] = 'Error: ESP32 Connection Failed'
                    self.running = False
                    return
            else:
                self.add_log(f"✓ Connected to ESP32 on {ARDUINO_PORT}", "SUCCESS")
            
            # Start reading
            if not esp32.start_reading():
                self.add_log("Failed to start reading from ESP32", "ERROR")
                self.stats['status'] = 'Error: Reading Failed'
                self.running = False
                return
            
            self.add_log("✓ ESP32 communication started", "SUCCESS")
            self.add_log(f"Waiting {ESP32_INIT_DELAY}s for ESP32 initialization...", "INFO")
            time.sleep(ESP32_INIT_DELAY)
            
            # Main monitoring loop
            self.add_log("✓ Monitoring started!", "SUCCESS")
            self.stats['status'] = 'Monitoring'
            self.stats['esp32_ready'] = True
            
            last_email_time = {}
            message_count = 0
            
            while self.running:
                msg = esp32.get_message(timeout=0.5)
                
                if msg:
                    message_count += 1
                    self.stats['messages_processed'] += 1
                    self.add_log(f"[MSG #{message_count}] {msg[:70]}", "RAW")
                    
                    # Parse message
                    parsed = parser.parse_message(msg)
                    
                    if parsed is None:
                        continue
                    
                    msg_type = parsed.get('type', 'unknown')
                    
                    if msg_type == 'error':
                        self.add_log(f"Error: {msg}", "ERROR")
                        
                    elif msg_type == 'status':
                        # Extract status info
                        if 'BASELINE' in msg:
                            try:
                                self.stats['baseline'] = int(msg.split(':')[1].strip())
                                self.add_log(f"Baseline: {self.stats['baseline']}", "INFO")
                            except:
                                pass
                        elif 'LOCATION' in msg:
                            try:
                                self.stats['location'] = msg.split(':')[-1].strip()
                                self.add_log(f"Location: {self.stats['location']}", "INFO")
                            except:
                                pass
                        else:
                            self.add_log(f"Status: {msg}", "INFO")
                    
                    elif msg_type == 'emergency':
                        self.stats['emergencies_detected'] += 1
                        self.add_log(f"🚨 EMERGENCY DETECTED!", "EMERGENCY")
                        self.add_log(f"Emergency data: {parsed}", "EMERGENCY")
                        
                        # Send email if cooldown period passed
                        alert_type = 'emergency'
                        current_time = time.time()
                        
                        if alert_type not in last_email_time or \
                           (current_time - last_email_time[alert_type]) > EMAIL_COOLDOWN:
                            
                            self.add_log("📧 Sending emergency email...", "SYSTEM")
                            try:
                                if email_sender.send_emergency_email(parsed):
                                    self.add_log("✓ Emergency email sent successfully!", "SUCCESS")
                                    last_email_time[alert_type] = current_time
                                else:
                                    self.add_log("✗ Failed to send emergency email", "ERROR")
                            except Exception as e:
                                self.add_log(f"✗ Emergency email error: {str(e)}", "ERROR")
                        else:
                            cooldown_remaining = EMAIL_COOLDOWN - (current_time - last_email_time[alert_type])
                            self.add_log(f"⏱️ Emergency cooldown: {cooldown_remaining:.0f}s remaining", "INFO")
                    
                    elif msg_type == 'anomaly':
                        self.stats['anomalies_detected'] += 1
                        self.add_log(f"⚠️ ANOMALY DETECTED!", "WARNING")
                        self.add_log(f"Anomaly data: {parsed}", "WARNING")
                        
                        alert_type = 'anomaly'
                        current_time = time.time()
                        
                        if alert_type not in last_email_time or \
                           (current_time - last_email_time[alert_type]) > ANOMALY_COOLDOWN:
                            
                            self.add_log("📧 Sending anomaly email...", "SYSTEM")
                            try:
                                if email_sender.send_anomaly_email(parsed):
                                    self.add_log("✓ Anomaly email sent successfully!", "SUCCESS")
                                    last_email_time[alert_type] = current_time
                                else:
                                    self.add_log("✗ Failed to send anomaly email", "ERROR")
                            except Exception as e:
                                self.add_log(f"✗ Anomaly email error: {str(e)}", "ERROR")
                        else:
                            cooldown_remaining = ANOMALY_COOLDOWN - (current_time - last_email_time[alert_type])
                            self.add_log(f"⏱️ Anomaly cooldown: {cooldown_remaining:.0f}s remaining", "INFO")
                
                time.sleep(0.1)  # Small delay to prevent CPU spinning
            
            # Cleanup
            self.add_log("Stopping monitoring...", "SYSTEM")
            esp32.stop_reading()
            esp32.disconnect()
            self.add_log("✓ Monitoring stopped", "SUCCESS")
            self.stats['status'] = 'Stopped'
            
            # Send "Monitoring Stopped" email
            self.add_log("📧 Sending monitoring stopped notification...", "SYSTEM")
            try:
                uptime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else None
                uptime_str = f"{uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m {uptime.seconds % 60}s" if uptime else "Unknown"
                
                stop_message = f"""
═══════════════════════════════════════════════════════════
⏹️ MONITORING STOPPED
═══════════════════════════════════════════════════════════

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Device: ESP32 Sound Detector
Status: ✓ Stopped

The Arduino Sound Detector monitoring system has been stopped.

Session Statistics:
- Uptime: {uptime_str}
- Messages Processed: {self.stats['messages_processed']}
- Emergencies Detected: {self.stats['emergencies_detected']}
- Anomalies Detected: {self.stats['anomalies_detected']}

Restart the monitoring to resume detection.

═══════════════════════════════════════════════════════════
"""
                msg = MIMEMultipart()
                msg['From'] = EMAIL_USERNAME
                msg['To'] = EMERGENCY_EMAIL
                msg['Subject'] = "⏹️ Sound Detector Monitoring Stopped"
                msg['X-Priority'] = '2'
                msg.attach(MIMEText(stop_message, 'plain'))
                
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5)
                server.starttls()
                server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                server.sendmail(EMAIL_USERNAME, [EMERGENCY_EMAIL], msg.as_string())
                server.quit()
                
                self.add_log("✓ Monitoring stopped email sent!", "SUCCESS")
            except Exception as e:
                self.add_log(f"⚠️ Could not send stop email: {str(e)}", "WARNING")
            
        except Exception as e:
            self.add_log(f"Error in monitoring loop: {str(e)}", "ERROR")
            import traceback
            self.add_log(traceback.format_exc(), "ERROR")
            self.stats['status'] = f'Error: {str(e)}'
            self.running = False

# Initialize session state
if 'app' not in st.session_state:
    st.session_state.app = SoundDetectorApp()

app = st.session_state.app

# Page configuration
st.set_page_config(
    page_title="Sound Detector Monitor",
    page_icon="🔊",
    layout="wide"
)

# Title
st.title("🔊 Arduino Sound Detector - Email Integration System")
st.markdown("---")

# Control buttons
col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    if st.button("▶️ Start Monitoring", disabled=app.running, use_container_width=True):
        if not app.running:
            app.running = True
            app.stats['start_time'] = datetime.now()
            app.stats['status'] = 'Starting...'
            app.add_log("Starting monitoring system...", "SYSTEM")
            app.thread = threading.Thread(target=app.monitoring_loop, daemon=True)
            app.thread.start()
            st.rerun()

with col2:
    if st.button("⏹️ Stop Monitoring", disabled=not app.running, use_container_width=True):
        if app.running:
            app.running = False
            app.add_log("Stop requested by user", "SYSTEM")
            st.rerun()

with col3:
    status_color = 'green' if app.stats['status'] == 'Monitoring' else ('orange' if 'Starting' in app.stats['status'] else 'red')
    st.markdown(f"**Status:** :{status_color}[{app.stats['status']}]")

st.markdown("---")

# Statistics and Process Display
col_stats, col_logs = st.columns([1, 2])

with col_stats:
    st.subheader("📊 Statistics")
    
    if app.stats['start_time']:
        uptime = datetime.now() - app.stats['start_time']
        st.metric("Uptime", f"{uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m {uptime.seconds % 60}s")
    else:
        st.metric("Uptime", "Not started")
    
    st.metric("Messages Processed", app.stats['messages_processed'])
    st.metric("🚨 Emergencies Detected", app.stats['emergencies_detected'])
    st.metric("⚠️ Anomalies Detected", app.stats['anomalies_detected'])
    
    st.markdown("---")
    st.subheader("⚙️ System Info")
    st.text(f"Location: {app.stats['location']}")
    st.text(f"Baseline: {app.stats['baseline']}")
    st.text(f"Port: {ARDUINO_PORT}")
    st.text(f"Baudrate: {BAUDRATE}")
    st.text(f"ESP32 Ready: {'✓' if app.stats['esp32_ready'] else '✗'}")
    
    st.markdown("---")
    st.subheader("📧 Email Config")
    st.text(f"From: {EMAIL_USERNAME}")
    st.text(f"To: {EMERGENCY_EMAIL}")
    st.text(f"Server: {SMTP_SERVER}:{SMTP_PORT}")

with col_logs:
    st.subheader("📋 Process Log (Latest First)")
    
    # Create a container for logs with fixed height
    log_container = st.container()
    
    with log_container:
        if app.logs:
            # Show logs in reverse order (newest first)
            log_text = "\n".join(reversed(list(app.logs)))
            st.code(log_text, language=None)
        else:
            st.info("No logs yet. Start monitoring to see activity.")

# Auto-refresh when monitoring is active
if app.running:
    time.sleep(1)
    st.rerun()
