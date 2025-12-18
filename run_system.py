#!/usr/bin/env python3
"""
Simple startup script for Arduino Sound Detector
"""

import os
import sys

def main():
    print("Arduino Sound Detector with WhatsApp Integration")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('python_whatsapp'):
        print("Error: python_whatsapp directory not found!")
        print("Please run this script from the arduino_sound_detector directory")
        return
    
    # Change to python directory and run
    os.chdir('python_whatsapp')
    
    # Check for test argument
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        print("Running WhatsApp test...")
        os.system('python main.py test')
    else:
        print("Starting full integration...")
        os.system('python main.py')

if __name__ == "__main__":
    main()