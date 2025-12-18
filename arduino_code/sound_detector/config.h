#ifndef CONFIG_H
#define CONFIG_H

// Device Configuration
#define DEVICE_LOCATION "Home Office"    // CHANGE THIS TO YOUR LOCATION
#define DEVICE_ID "ESP32_SOUND_001"
#define EMERGENCY_CONTACT "+91 6374724269"  // CHANGE THIS TO EMERGENCY CONTACT

// ESP32 Pin Configuration (Different from Arduino)
#define ANALOG_PIN A0                    // ESP32 ADC1_CH0 (GPIO36)
#define DIGITAL_PIN 2                    // ESP32 GPIO2
#define LED_PIN 2                        // ESP32 built-in LED (GPIO2)

// Alternative ESP32 pins you can use:
// ADC1: GPIO32, GPIO33, GPIO34, GPIO35, GPIO36, GPIO37, GPIO38, GPIO39
// ADC2: GPIO0, GPIO2, GPIO4, GPIO12, GPIO13, GPIO14, GPIO15, GPIO25, GPIO26, GPIO27

// Sound Detection Settings (Optimized for ESP32)
#define DETECTION_SENSITIVITY 150        // ESP32 ADC is 12-bit (0-4095), adjust accordingly
#define BASELINE_SAMPLES 50
#define COOLDOWN_PERIOD 8000             // 8 seconds (ESP32 processes faster)

// Voice Command Settings (ESP32 optimized)
#define VOICE_SENSITIVITY_THRESHOLD 100  // Adjusted for ESP32 ADC range
#define HELP_COOLDOWN 4000               // 4 seconds (ESP32 faster processing)
#define VOICE_BUFFER_SIZE 25             // Larger buffer for ESP32's memory
#define MIN_VOICE_DURATION 400           // Shorter duration for ESP32's faster sampling

// Status Update Interval
#define STATUS_INTERVAL 180000           // 3 minutes (more frequent for ESP32)

// Serial Communication (ESP32 supports higher baudrates)
#define BAUD_RATE 115200                 // ESP32 standard baudrate (faster than Arduino)
#define SERIAL_TIMEOUT 500               // Shorter timeout for ESP32

// ESP32 Specific Settings
#define ADC_RESOLUTION 12                // ESP32 ADC resolution (12-bit = 0-4095)
#define ADC_VREF 3300                    // ESP32 reference voltage in mV
#define SAMPLE_RATE 8000                 // ESP32 can handle higher sample rates
#define ESP32_CPU_FREQ 240               // ESP32 CPU frequency in MHz

// WiFi Settings (ESP32 feature - for future enhancement)
#define ENABLE_WIFI false                // Set to true if you want WiFi features
#define WIFI_SSID "YourWiFiNetwork"      // CHANGE THIS if enabling WiFi
#define WIFI_PASSWORD "YourPassword"     // CHANGE THIS if enabling WiFi

#endif
