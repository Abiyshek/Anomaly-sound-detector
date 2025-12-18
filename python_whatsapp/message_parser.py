from datetime import datetime

class ArduinoMessageParser:
    def __init__(self):
        self.in_emergency_block = False
        self.in_alert_block = False
        self.current_emergency = {}
        self.current_alert = {}
    
    def parse_message(self, message):
        """Parse a single message line from Arduino"""
        message = message.strip()
        
        if not message:
            return None
        
        # Handle immediate emergency detection - this should trigger immediately
        if message == "EMERGENCY:HELP_DETECTED":
            return {
                'type': 'emergency',
                'emergency_type': 'HELP',
                'subtype': 'help_detected_immediate',
                'timestamp': datetime.now().isoformat(),
                'immediate': True,
                'level': 999  # High priority
            }
        
        # Handle emergency block start/end
        elif message == "EMERGENCY:START":
            self.in_emergency_block = True
            self.current_emergency = {
                'type': 'emergency',
                'timestamp': datetime.now().isoformat()
            }
            return None
        
        elif message == "EMERGENCY:END":
            if self.in_emergency_block:
                self.in_emergency_block = False
                result = self.current_emergency.copy()
                self.current_emergency = {}
                return result
            return None
        
        # Handle alert block start/end
        elif message == "ALERT:START":
            self.in_alert_block = True
            self.current_alert = {
                'type': 'anomaly',
                'timestamp': datetime.now().isoformat()
            }
            return None
        
        elif message == "ALERT:END":
            if self.in_alert_block:
                self.in_alert_block = False
                result = self.current_alert.copy()
                self.current_alert = {}
                return result
            return None
        
        # Parse data fields within blocks
        elif ":" in message:
            return self._parse_data_field(message)
        
        return None
    
    def _parse_data_field(self, message):
        """Parse data fields like EMERGENCY:LOCATION:Home Office"""
        parts = message.split(":", 2)
        
        if len(parts) < 2:
            return None
        
        category = parts[0]
        field = parts[1]
        value = parts[2] if len(parts) > 2 else ""
        
        # Handle emergency data
        if category == "EMERGENCY" and self.in_emergency_block:
            field_lower = field.lower()
            
            if field_lower == 'id':
                self.current_emergency['emergency_id'] = value
            elif field_lower == 'timestamp':
                self.current_emergency['arduino_timestamp'] = value
            elif field_lower == 'type':
                self.current_emergency['emergency_type'] = value
                self.current_emergency['subtype'] = value
            elif field_lower == 'sound_level':
                try:
                    self.current_emergency['level'] = int(value)
                except:
                    self.current_emergency['level'] = value
            elif field_lower == 'location':
                self.current_emergency['location'] = value
            elif field_lower == 'uptime':
                self.current_emergency['uptime'] = value
            elif field_lower == 'message':
                self.current_emergency['message'] = value
            elif field_lower == 'contact':
                self.current_emergency['emergency_contact'] = value
        
        # Handle alert data
        elif category == "ALERT" and self.in_alert_block:
            field_lower = field.lower()
            
            if field_lower == 'id':
                self.current_alert['alert_id'] = value
            elif field_lower == 'timestamp':
                self.current_alert['arduino_timestamp'] = value
            elif field_lower == 'level':
                try:
                    self.current_alert['level'] = int(value)
                except:
                    self.current_alert['level'] = value
            elif field_lower == 'baseline':
                try:
                    self.current_alert['baseline'] = int(value)
                except:
                    self.current_alert['baseline'] = value
            elif field_lower == 'difference':
                try:
                    self.current_alert['difference'] = int(value)
                except:
                    self.current_alert['difference'] = value
            elif field_lower == 'severity':
                self.current_alert['severity'] = value
            elif field_lower == 'location':
                self.current_alert['location'] = value
            elif field_lower == 'uptime':
                self.current_alert['uptime'] = value
        
        # Handle status messages
        elif category == "STATUS":
            return {
                'type': 'status',
                'field': field.lower(),
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
        
        return None