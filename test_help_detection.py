#!/usr/bin/env python3
"""
Test script for HELP detection - bypasses email setup
This will help you understand when to scream HELP for testing
"""

import sys
import time
import os

# Add python_whatsapp to path
sys.path.append('python_whatsapp')

from arduino_reader import ArduinoReader
from message_parser import ArduinoMessageParser

class HelpDetectionTester:
    def __init__(self):
        self.arduino = ArduinoReader('COM5', 9600, 1)  # Using your Arduino port
        self.parser = ArduinoMessageParser()
        self.running = False
        self.help_detected_count = 0
        
    def setup(self):
        """Setup Arduino connection for testing"""
        print("=" * 60)
        print("🎤 ARDUINO HELP DETECTION TESTER")
        print("=" * 60)
        print("This will test HELP voice command detection without email")
        print("Make sure your Arduino has the sound detector code uploaded!")
        print()
        
        # Try to connect to Arduino
        if not self.arduino.connect():
            print("❌ Failed to connect to Arduino on COM5!")
            print("\n🔧 Arduino Setup Checklist:")
            print("1. Arduino is connected via USB")
            print("2. Arduino code from 'arduino_code/sound_detector/sound_detector.ino' is uploaded")
            print("3. Sound sensor is connected to pin A0")
            print("4. Arduino is powered on")
            return False
        
        # Start reading from Arduino
        if not self.arduino.start_reading():
            print("❌ Failed to start reading from Arduino")
            return False
            
        print("✅ Arduino connected successfully!")
        print("\n🎯 HELP DETECTION TEST INSTRUCTIONS:")
        print("1. Wait for Arduino to show 'READY' status")
        print("2. When I say 'NOW', scream 'HELP' loudly into your sound sensor")
        print("3. I'll tell you if the system detected it correctly")
        print("4. We'll test different volume levels and timing")
        print("\n📊 Monitoring Arduino output...")
        print("-" * 60)
        
        return True
    
    def test_help_detection(self):
        """Monitor Arduino and guide user through HELP testing"""
        if not self.setup():
            return
            
        self.running = True
        baseline_established = False
        ready_for_test = False
        test_phase = 1
        last_instruction_time = 0
        
        print("🔍 Waiting for Arduino to establish baseline...")
        
        try:
            while self.running:
                # Check for new messages
                while not self.arduino.message_queue.empty():
                    message = self.arduino.message_queue.get()
                    parsed = self.parser.parse_message(message)
                    
                    # Print all Arduino messages for debugging
                    print(f"Arduino: {message}")
                    
                    # Check for system status
                    if "STATUS:READY" in message:
                        baseline_established = True
                        ready_for_test = True
                        print("\n✅ Arduino is READY!")
                        print("🎯 Baseline noise level established")
                        last_instruction_time = time.time()
                    
                    elif "BASELINE:" in message:
                        baseline = message.split(":")[1]
                        print(f"📊 Baseline noise level: {baseline}")
                    
                    elif "HELP_DETECTION:ENABLED" in message:
                        print("🎤 HELP voice detection is ENABLED")
                    
                    # Check for HELP detection
                    elif parsed and parsed.get('type') == 'EMERGENCY':
                        self.help_detected_count += 1
                        print(f"\n🚨 HELP DETECTED! (Detection #{self.help_detected_count})")
                        print(f"   Sound Level: {parsed.get('sound_level', 'N/A')}")
                        print(f"   Location: {parsed.get('location', 'N/A')}")
                        print("   ✅ EXCELLENT! Your HELP command was detected!")
                        print("   💡 This would trigger an emergency email in full mode")
                        
                        # Give feedback and prepare for next test
                        if self.help_detected_count < 3:
                            print(f"\n🎯 Great! Let's try test #{self.help_detected_count + 1}")
                            print("   Try varying your distance from the sensor or volume")
                            last_instruction_time = time.time()
                        else:
                            print("\n🎉 HELP Detection Testing Complete!")
                            print(f"   Successfully detected HELP {self.help_detected_count} times!")
                            print("   Your system is working perfectly!")
                            self.running = False
                            break
                    
                    elif parsed and parsed.get('type') == 'ANOMALY':
                        severity = parsed.get('severity', 'UNKNOWN')
                        sound_level = parsed.get('sound_level', 'N/A')
                        print(f"🔊 Sound anomaly detected: {severity} (Level: {sound_level})")
                        print("   This is normal background noise detection")
                
                # Give testing instructions at appropriate times
                current_time = time.time()
                if ready_for_test and (current_time - last_instruction_time) > 10:
                    if test_phase == 1:
                        print(f"\n🎤 TEST {test_phase}: NOW! Scream 'HELP' loudly into your sound sensor!")
                        print("   (Make sure you're close to the microphone/sound sensor)")
                        test_phase += 1
                        last_instruction_time = current_time
                    elif test_phase == 2 and self.help_detected_count == 0:
                        print(f"\n🎤 TEST {test_phase}: Try again! Scream 'HELP' even LOUDER!")
                        print("   (Move closer to the sensor if possible)")
                        test_phase += 1
                        last_instruction_time = current_time
                    elif test_phase == 3 and self.help_detected_count == 0:
                        print(f"\n🎤 TEST {test_phase}: One more try! Make a very loud sudden noise!")
                        print("   (Clap your hands loudly near the sensor as a test)")
                        test_phase += 1
                        last_instruction_time = current_time
                
                time.sleep(0.1)  # Small delay
                
        except KeyboardInterrupt:
            print("\n\n🛑 Testing stopped by user")
        finally:
            self.arduino.disconnect()
            print("\n📋 TEST SUMMARY:")
            print(f"   HELP detections: {self.help_detected_count}")
            if self.help_detected_count > 0:
                print("   ✅ System is working correctly!")
                print("   🚀 You can now configure email and run the full system")
            else:
                print("   ⚠️  No HELP commands detected")
                print("   💡 Try adjusting DETECTION_SENSITIVITY in Arduino config.h")
                print("   💡 Make sure sound sensor is properly connected to pin A0")

def main():
    tester = HelpDetectionTester()
    tester.test_help_detection()

if __name__ == "__main__":
    main()