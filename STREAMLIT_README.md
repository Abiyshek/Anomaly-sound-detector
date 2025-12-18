# 🔊 Arduino Sound Detector - Streamlit GUI

A modern web-based interface for monitoring Arduino/ESP32 sound detection with email alerts.

## Features

- **Start/Stop Control**: Easy-to-use buttons to control monitoring
- **Live Process Display**: Real-time logs showing system activity
- **Statistics Dashboard**: Track messages, emergencies, and anomalies
- **Email Integration**: Automatic email alerts for emergencies and anomalies
- **Auto-refresh**: Interface updates automatically while monitoring

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Settings

Edit `python_whatsapp/config.py`:

```python
# Email Settings
EMAIL_USERNAME = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'  # Gmail App Password
EMERGENCY_EMAIL = 'recipient@example.com'

# Arduino/ESP32 Settings
ARDUINO_PORT = 'COM3'  # Adjust for your system
BAUDRATE = 115200
```

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the App Password in config.py

### 3. Run the Streamlit App

```bash
streamlit run streamlit_app.py
```

The app will open in your default browser at http://localhost:8501

## Usage

1. **Start Monitoring**: Click the "▶️ Start Monitoring" button
2. **View Logs**: Watch the Process Log section for real-time activity
3. **Check Stats**: Monitor emergencies and anomalies in the Statistics panel
4. **Stop Monitoring**: Click the "⏹️ Stop Monitoring" button when done

## Interface Layout

### Control Panel
- **Start/Stop Buttons**: Control the monitoring system
- **Status Indicator**: Shows current system state

### Statistics Panel (Left)
- Uptime counter
- Messages processed
- Emergencies detected
- Anomalies detected
- System information (location, baseline, port, etc.)

### Process Log (Right)
- Real-time log display
- Color-coded message types:
  - `[SYSTEM]`: System operations
  - `[SUCCESS]`: Successful operations
  - `[INFO]`: General information
  - `[WARNING]`: Warnings and anomalies
  - `[EMERGENCY]`: Critical alerts
  - `[ERROR]`: Error messages

## Troubleshooting

### ESP32 Not Connecting
- Check USB cable connection
- Verify correct COM port in config.py
- Try alternative ports (app will auto-detect)
- Ensure ESP32 firmware is uploaded

### Email Not Sending
- Verify email credentials in config.py
- Check internet connection
- For Gmail: Ensure App Password is used (not regular password)
- Check SMTP server settings

### Logs Not Updating
- The page auto-refreshes every second when monitoring
- Check browser console for errors
- Try manually refreshing the page

## Original Command-Line Version

The original command-line version is still available:

```bash
python run_system.py
```

## Project Structure

```
arduino_whatsapp_integration/
├── streamlit_app.py          # Streamlit GUI (NEW)
├── run_system.py              # Original CLI version
├── requirements.txt           # Python dependencies
├── python_whatsapp/
│   ├── main.py               # Main integration logic
│   ├── arduino_reader.py     # Serial communication
│   ├── message_parser.py     # Message parsing
│   ├── email_sender.py       # Email functionality
│   └── config.py             # Configuration
└── arduino_code/
    └── sound_detector/       # ESP32/Arduino firmware
```

## Features Comparison

| Feature | Streamlit GUI | CLI Version |
|---------|--------------|-------------|
| Start/Stop Control | ✅ Button | ❌ Ctrl+C only |
| Live Log Display | ✅ Web UI | ✅ Terminal |
| Statistics Dashboard | ✅ Visual | ⚠️ Text only |
| Auto-refresh | ✅ Yes | ❌ Manual |
| Multiple Sessions | ✅ Browser tabs | ❌ One terminal |
| Remote Access | ✅ Network access | ❌ Local only |

## License

MIT License

## Support

For issues and questions, please check the logs in the Process Log section and refer to the troubleshooting guide above.
