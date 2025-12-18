#include "config.h"
#include "sound_analysis.h"

// Pin definitions (ESP32 specific)
const int ANALOG_PIN = A0;  // ESP32 ADC1_CH0 (GPIO36) 
const int DIGITAL_PIN = 2;  // ESP32 GPIO2
const int LED_PIN = 2;      // ESP32 built-in LED

// Sound detection variables (ESP32 optimized)
int soundThreshold = 600;   // Higher threshold for ESP32's 12-bit ADC (0-4095)
int baselineNoise = 0;
int anomalyCount = 0;
int helpCallCount = 0;
unsigned long lastDetection = 0;
unsigned long lastHelpDetection = 0;
const int DETECTION_COOLDOWN = 8000; // 8 seconds for ESP32

// Moving average for baseline (ESP32 can handle more samples)
const int SAMPLES = 60;     // More samples for ESP32's better processing
int soundSamples[SAMPLES];
int sampleIndex = 0;

// Voice command detection buffers (ESP32 optimized)
int voiceBuffer[VOICE_BUFFER_SIZE];
int voiceBufferIndex = 0;
unsigned long voiceTimestamps[VOICE_BUFFER_SIZE];

// System status
bool systemReady = false;
unsigned long systemStartTime = 0;

// ESP32 specific variables
bool esp32Ready = false;
int adcCalibration = 0;

void setup() {
  Serial.begin(115200);  // ESP32 standard baudrate
  
  // ESP32 specific ADC configuration
  analogReadResolution(12);  // Set ESP32 ADC to 12-bit resolution
  analogSetAttenuation(ADC_11db);  // Set input range to 3.3V
  
  pinMode(DIGITAL_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Initialize voice buffer
  for (int i = 0; i < VOICE_BUFFER_SIZE; i++) {
    voiceBuffer[i] = 0;
    voiceTimestamps[i] = 0;
  }
  
  // Startup sequence
  Serial.println("=== ESP32 SOUND ANOMALY DETECTOR WITH HELP COMMAND ===");
  Serial.println("STATUS:STARTING");
  Serial.print("STATUS:DEVICE_TYPE:ESP32");
  Serial.print("STATUS:CPU_FREQ:");
  Serial.println(ESP32_CPU_FREQ);
  
  // Flash LED during startup (ESP32 style)
  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(150);
    digitalWrite(LED_PIN, LOW);
    delay(150);
  }
  
  // Calibrate baseline noise (ESP32 optimized)
  calibrateBaseline();
  
  systemReady = true;
  esp32Ready = true;
  systemStartTime = millis();
  
  Serial.println("STATUS:READY");
  Serial.print("BASELINE:");
  Serial.println(baselineNoise);
  Serial.print("THRESHOLD:");
  Serial.println(soundThreshold);
  Serial.println("HELP_DETECTION:ENABLED");
  Serial.println("=== ESP32 MONITORING STARTED ===");
  Serial.println("Say 'HELP' for emergency assistance");;
  
  // Signal ready with LED
  digitalWrite(LED_PIN, HIGH);
  delay(1000);
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  if (!systemReady || !esp32Ready) return;
  
  // ESP32 optimized analog reading with better filtering
  int analogValue = analogRead(ANALOG_PIN);
  int digitalValue = digitalRead(DIGITAL_PIN);
  
  // ESP32 ADC can be noisy, so filter extreme values
  if (analogValue < 5 || analogValue > 4090) {
    delay(20);  // Short delay for ESP32 and continue
    return;
  }
  
  // Update voice detection buffer
  updateVoiceBuffer(analogValue);
  
  // Check for HELP command first (highest priority)
  if (detectHelpCommand()) {
    handleHelpCommand(analogValue);
  }
  // Then check for general anomaly
  else if (detectAnomaly(analogValue)) {
    handleAnomalyDetection(analogValue);
  }
  
  // Update baseline continuously
  updateBaseline(analogValue);
  
  // Send periodic status updates (more frequent for ESP32)
  static unsigned long lastStatus = 0;
  if (millis() - lastStatus > STATUS_INTERVAL) {
    sendStatusUpdate();
    lastStatus = millis();
  }
  
  // Handle serial commands
  if (Serial.available()) {
    handleSerialCommand();
  }
  
  delay(30); // Faster sampling for ESP32's better processing power
}

void updateVoiceBuffer(int soundLevel) {
  voiceBuffer[voiceBufferIndex] = soundLevel;
  voiceTimestamps[voiceBufferIndex] = millis();
  voiceBufferIndex = (voiceBufferIndex + 1) % VOICE_BUFFER_SIZE;
}

bool detectHelpCommand() {
  // HELP command characteristics:
  // 1. Sustained elevated sound (speaking)
  // 2. Multiple sound peaks (syllables)
  // 3. Duration of about 500-1000ms
  // 4. Pattern: quiet-LOUD-quiet-LOUD-quiet (HE-LP)
  
  unsigned long currentTime = millis();
  
  // Cooldown check
  if (currentTime - lastHelpDetection < HELP_COOLDOWN) {
    return false;
  }
  
  // Analyze recent sound pattern
  int peakCount = 0;
  int sustainedCount = 0;
  int voiceThreshold = baselineNoise + (DETECTION_SENSITIVITY / 2);
  int loudThreshold = baselineNoise + DETECTION_SENSITIVITY;
  
  // Count peaks and sustained sounds in buffer
  for (int i = 0; i < VOICE_BUFFER_SIZE; i++) {
    if (voiceBuffer[i] > voiceThreshold) {
      sustainedCount++;
    }
    
    // Check for peaks (syllable detection)
    if (i > 0 && i < VOICE_BUFFER_SIZE - 1) {
      if (voiceBuffer[i] > loudThreshold && 
          voiceBuffer[i] > voiceBuffer[i-1] && 
          voiceBuffer[i] > voiceBuffer[i+1]) {
        peakCount++;
      }
    }
  }
  
  // Check timing - should have recent activity
  unsigned long oldestTime = voiceTimestamps[(voiceBufferIndex + 1) % VOICE_BUFFER_SIZE];
  bool recentActivity = (currentTime - oldestTime) < 2000; // Within last 2 seconds
  
  // HELP pattern: 
  // - At least 2 peaks (HE-LP syllables)
  // - Sustained voice activity (30-60% of buffer)
  // - Recent activity
  bool hasVoicePattern = peakCount >= 2 && 
                         sustainedCount >= (VOICE_BUFFER_SIZE / 3) && 
                         sustainedCount <= (VOICE_BUFFER_SIZE * 2 / 3) &&
                         recentActivity;
  
  // Additional check: look for HE-LP pattern specifically
  bool hasHelpPattern = detectSpecificHelpPattern();
  
  return hasVoicePattern || hasHelpPattern;
}

bool detectSpecificHelpPattern() {
  // Look for two distinct sound bursts with a gap (HE - LP)
  int segment1 = 0, segment2 = 0, gap = 0;
  int threshold = baselineNoise + DETECTION_SENSITIVITY;
  
  // Divide buffer into thirds and analyze
  int third = VOICE_BUFFER_SIZE / 3;
  
  // Count active sounds in each segment
  for (int i = 0; i < third; i++) {
    if (voiceBuffer[i] > threshold) segment1++;
  }
  for (int i = third; i < 2 * third; i++) {
    if (voiceBuffer[i] < threshold) gap++;
  }
  for (int i = 2 * third; i < VOICE_BUFFER_SIZE; i++) {
    if (voiceBuffer[i] > threshold) segment2++;
  }
  
  // Pattern: sound-gap-sound (like HE-LP)
  return (segment1 >= 2 && segment2 >= 2 && gap >= 2);
}

void handleHelpCommand(int soundLevel) {
  lastHelpDetection = millis();
  helpCallCount++;
  
  // Emergency LED pattern (rapid flashing)
  for (int i = 0; i < 10; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(50);
    digitalWrite(LED_PIN, LOW);
    delay(50);
  }
  
  // Send HELP emergency alert
  Serial.println("EMERGENCY:HELP_DETECTED");
  Serial.println("EMERGENCY:START");
  Serial.print("EMERGENCY:ID:");
  Serial.println(helpCallCount);
  Serial.print("EMERGENCY:TIMESTAMP:");
  Serial.println(millis());
  Serial.print("EMERGENCY:TYPE:VOICE_HELP");
  Serial.print("EMERGENCY:SOUND_LEVEL:");
  Serial.println(soundLevel);
  Serial.print("EMERGENCY:LOCATION:");
  Serial.println(DEVICE_LOCATION);
  Serial.print("EMERGENCY:UPTIME:");
  Serial.println(getUptimeString());
  Serial.println("EMERGENCY:MESSAGE:Person needs help at location");
  Serial.println("EMERGENCY:ACTION_REQUIRED:SEND_WHATSAPP");
  Serial.print("EMERGENCY:CONTACT:");
  Serial.println(EMERGENCY_CONTACT);
  Serial.println("EMERGENCY:END");
  
  // Keep LED on for 3 seconds to indicate emergency detected
  digitalWrite(LED_PIN, HIGH);
  delay(3000);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("HELP command detected - Emergency alert sent!");
}

void calibrateBaseline() {
  Serial.println("CALIBRATION:START");
  Serial.println("Please remain quiet during ESP32 calibration...");
  digitalWrite(LED_PIN, HIGH);
  
  long sum = 0;
  int validSamples = 0;
  
  // ESP32 optimized calibration with noise filtering
  for (int i = 0; i < SAMPLES; i++) {
    int reading = analogRead(ANALOG_PIN);
    
    // Filter out extreme values (ESP32 ADC can be noisy)
    if (reading > 10 && reading < 4000) {  // Valid range for ESP32 12-bit ADC
      soundSamples[i] = reading;
      sum += reading;
      validSamples++;
    } else {
      // Use previous valid reading or default
      soundSamples[i] = (i > 0) ? soundSamples[i-1] : 200;
      sum += soundSamples[i];
      validSamples++;
    }
    
    // Progress indicator (faster for ESP32)
    if (i % 8 == 0) {
      Serial.print("CALIBRATION:PROGRESS:");
      Serial.println((i * 100) / SAMPLES);
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    }
    delay(60);  // Slightly faster calibration for ESP32
  }
  
  if (validSamples > 0) {
    baselineNoise = sum / validSamples;
  } else {
    baselineNoise = 200;  // Safe default for ESP32
  }
  
  soundThreshold = baselineNoise + DETECTION_SENSITIVITY;
  
  digitalWrite(LED_PIN, LOW);
  Serial.println("CALIBRATION:COMPLETE");
  Serial.println("ESP32 calibrated - You can now say 'HELP' for emergency assistance");
  Serial.print("ESP32_BASELINE:");
  Serial.println(baselineNoise);
  Serial.print("ESP32_THRESHOLD:");
  Serial.println(soundThreshold);
}

void updateBaseline(int newSample) {
  soundSamples[sampleIndex] = newSample;
  sampleIndex = (sampleIndex + 1) % SAMPLES;
  
  // Adaptive baseline - recalculate every 25 samples
  if (sampleIndex % 25 == 0) {
    long sum = 0;
    for (int i = 0; i < SAMPLES; i++) {
      sum += soundSamples[i];
    }
    int newBaseline = sum / SAMPLES;
    
    // Gradual baseline adaptation (prevents sudden changes)
    if (abs(newBaseline - baselineNoise) < 50) {
      baselineNoise = (baselineNoise * 3 + newBaseline) / 4;
      soundThreshold = baselineNoise + DETECTION_SENSITIVITY;
    }
  }
}

bool detectAnomaly(int soundLevel) {
  // Multiple detection methods
  bool isLoudSpike = soundLevel > soundThreshold;
  
  // Sudden change detection
  static int lastLevel = 0;
  bool isSuddenChange = abs(soundLevel - lastLevel) > (DETECTION_SENSITIVITY * 1.5);
  lastLevel = soundLevel;
  
  // Sustained loud noise
  static int loudCounter = 0;
  if (soundLevel > (baselineNoise + DETECTION_SENSITIVITY/2)) {
    loudCounter++;
  } else {
    loudCounter = max(0, loudCounter - 1);
  }
  bool isSustained = loudCounter > 10;
  
  // Pattern-based detection
  static int patternBuffer[5];
  static int patternIndex = 0;
  patternBuffer[patternIndex] = soundLevel;
  patternIndex = (patternIndex + 1) % 5;
  bool isPattern = detectSoundPattern(patternBuffer, 5, baselineNoise);
  
  // Cooldown check
  bool cooldownExpired = (millis() - lastDetection) > DETECTION_COOLDOWN;
  
  return (isLoudSpike || isSuddenChange || isSustained || isPattern) && cooldownExpired;
}

void handleAnomalyDetection(int soundLevel) {
  lastDetection = millis();
  anomalyCount++;
  
  // Alert LED pattern
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(150);
    digitalWrite(LED_PIN, LOW);
    delay(150);
  }
  
  // Calculate severity
  int severity = calculateSeverity(soundLevel, baselineNoise);
  String severityText = getSeverityText(severity);
  
  // Send structured alert
  Serial.println("ALERT:START");
  Serial.print("ALERT:ID:");
  Serial.println(anomalyCount);
  Serial.print("ALERT:TIMESTAMP:");
  Serial.println(millis());
  Serial.print("ALERT:LEVEL:");
  Serial.println(soundLevel);
  Serial.print("ALERT:BASELINE:");
  Serial.println(baselineNoise);
  Serial.print("ALERT:DIFFERENCE:");
  Serial.println(soundLevel - baselineNoise);
  Serial.print("ALERT:SEVERITY:");
  Serial.println(severityText);
  Serial.print("ALERT:LOCATION:");
  Serial.println(DEVICE_LOCATION);
  Serial.print("ALERT:UPTIME:");
  Serial.println(getUptimeString());
  Serial.println("ALERT:END");
  
  // Keep LED on for severity indication
  digitalWrite(LED_PIN, HIGH);
  delay(severity * 500); // Longer flash for higher severity
  digitalWrite(LED_PIN, LOW);
}

int calculateSeverity(int currentLevel, int baseline) {
  int difference = currentLevel - baseline;
  
  if (difference > DETECTION_SENSITIVITY * 3) return 3; // Critical
  if (difference > DETECTION_SENSITIVITY * 2) return 2; // High
  if (difference > DETECTION_SENSITIVITY) return 1;     // Medium
  return 0; // Low
}

String getSeverityText(int severity) {
  switch (severity) {
    case 3: return "CRITICAL";
    case 2: return "HIGH";
    case 1: return "MEDIUM";
    default: return "LOW";
  }
}

void sendStatusUpdate() {
  Serial.println("STATUS:UPDATE");
  Serial.print("STATUS:UPTIME:");
  Serial.println(getUptimeString());
  Serial.print("STATUS:BASELINE:");
  Serial.println(baselineNoise);
  Serial.print("STATUS:THRESHOLD:");
  Serial.println(soundThreshold);
  Serial.print("STATUS:ALERTS:");
  Serial.println(anomalyCount);
  Serial.print("STATUS:HELP_CALLS:");
  Serial.println(helpCallCount);
  Serial.print("STATUS:CURRENT_LEVEL:");
  Serial.println(analogRead(ANALOG_PIN));
  Serial.print("STATUS:FREE_MEMORY:");
  Serial.println(getFreeMemory());
}

String getUptimeString() {
  unsigned long uptime = millis() - systemStartTime;
  unsigned long seconds = uptime / 1000;
  unsigned long minutes = seconds / 60;
  unsigned long hours = minutes / 60;
  
  return String(hours) + "h:" + String(minutes % 60) + "m:" + String(seconds % 60) + "s";
}

void handleSerialCommand() {
  String command = Serial.readStringUntil('\n');
  command.trim();
  command.toUpperCase();
  
  if (command == "STATUS") {
    sendStatusUpdate();
  }
  else if (command == "RESET") {
    anomalyCount = 0;
    helpCallCount = 0;
    calibrateBaseline();
    Serial.println("COMMAND:RESET:COMPLETE");
  }
  else if (command == "BASELINE") {
    calibrateBaseline();
    Serial.println("COMMAND:BASELINE:COMPLETE");
  }
  else if (command.startsWith("SENSITIVITY:")) {
    int newSensitivity = command.substring(12).toInt();
    if (newSensitivity > 0 && newSensitivity < 500) {
      soundThreshold = baselineNoise + newSensitivity;
      Serial.print("COMMAND:SENSITIVITY:SET:");
      Serial.println(newSensitivity);
    }
  }
  else if (command == "TEST") {
    Serial.println("ALERT:START");
    Serial.println("ALERT:ID:TEST");
    Serial.println("ALERT:TYPE:MANUAL_TEST");
    Serial.println("ALERT:SEVERITY:LOW");
    Serial.println("ALERT:END");
  }
  else if (command == "TESTHELP") {
    Serial.println("EMERGENCY:HELP_DETECTED");
    Serial.println("Testing HELP emergency system...");
    handleHelpCommand(analogRead(ANALOG_PIN));
  }
  else {
    Serial.print("COMMAND:UNKNOWN:");
    Serial.println(command);
  }
}

// Simple free memory check
int getFreeMemory() {
  extern int __heap_start, *__brkval;

  int v;
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
}