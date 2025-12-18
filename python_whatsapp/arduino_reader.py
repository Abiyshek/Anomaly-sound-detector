import serial
import time
import threading
from queue import Queue, Empty

class ArduinoReader:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.message_queue = Queue()
        self.is_connected = False
        self.is_reading = False
        self.read_thread = None
    
    def connect(self):
        """Connect to Arduino/ESP32 via serial port"""
        try:
            print(f"Attempting to connect to ESP32/Arduino on {self.port}...")
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            
            # Wait for ESP32 to initialize (ESP32 needs more time than Arduino)
            if self.baudrate >= 115200:  # Assume ESP32 if high baudrate
                print("Detected ESP32 mode - waiting for initialization...")
                time.sleep(3)  # ESP32 needs more time
            else:
                time.sleep(2)  # Standard Arduino timing
            
            if self.serial_connection.is_open:
                self.is_connected = True
                print(f"✓ Successfully connected to ESP32/Arduino on {self.port}")
                return True
            else:
                print(f"✗ Failed to open port {self.port}")
                return False
                
        except serial.SerialException as e:
            print(f"✗ Serial connection error: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected connection error: {e}")
            return False
    
    def start_reading(self):
        """Start reading messages from Arduino in background thread"""
        if not self.is_connected:
            print("✗ Cannot start reading - Arduino not connected")
            return False
        
        if self.is_reading:
            print("Already reading from Arduino")
            return True
        
        self.is_reading = True
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()
        print("✓ Started reading from Arduino")
        return True
    
    def _read_loop(self):
        """Background thread that continuously reads from Arduino"""
        print("Arduino reading thread started")
        
        while self.is_reading and self.is_connected:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline()
                    decoded_line = line.decode('utf-8', errors='ignore').strip()
                    
                    if decoded_line:
                        # Add to queue for processing
                        self.message_queue.put(decoded_line)
                        # Also print to console for debugging
                        print(f"Arduino: {decoded_line}")
                
                time.sleep(0.01)  # Small delay to prevent high CPU usage
                
            except serial.SerialException as e:
                print(f"✗ Serial read error: {e}")
                self.is_connected = False
                break
            except Exception as e:
                print(f"✗ Read loop error: {e}")
                break
        
        print("Arduino reading thread stopped")
    
    def get_message(self, timeout=1.0):
        """Get next message from Arduino (blocking with timeout)"""
        try:
            return self.message_queue.get(timeout=timeout)
        except Empty:
            return None
    
    def send_command(self, command):
        """Send command to Arduino"""
        if not self.is_connected or not self.serial_connection:
            print("✗ Cannot send command - Arduino not connected")
            return False
        
        try:
            command_with_newline = f"{command}\n"
            self.serial_connection.write(command_with_newline.encode('utf-8'))
            self.serial_connection.flush()
            print(f"✓ Sent command to Arduino: {command}")
            return True
        except Exception as e:
            print(f"✗ Error sending command: {e}")
            return False
    
    def stop_reading(self):
        """Stop reading from Arduino"""
        self.is_reading = False
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)
    
    def disconnect(self):
        """Disconnect from Arduino"""
        self.stop_reading()
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        
        self.is_connected = False
        print("✓ Disconnected from Arduino")
    
    def test_connection(self):
        """Test if Arduino is responding"""
        if not self.is_connected:
            return False
        
        # Send status command
        if self.send_command("STATUS"):
            # Wait for response
            start_time = time.time()
            while time.time() - start_time < 3:
                message = self.get_message(timeout=0.5)
                if message and "STATUS:" in message:
                    print("✓ Arduino connection test passed")
                    return True
            
            print("✗ Arduino not responding to commands")
            return False
        
        return False