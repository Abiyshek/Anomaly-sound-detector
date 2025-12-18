#ifndef SOUND_ANALYSIS_H
#define SOUND_ANALYSIS_H

bool detectSoundPattern(int* samples, int count, int baselineNoise) {
  if (count < 3) return false;
  
  // Check for repeated spikes pattern (ESP32 12-bit ADC optimized)
  int spikes = 0;
  int threshold = baselineNoise + (DETECTION_SENSITIVITY / 2);
  
  for (int i = 1; i < count - 1; i++) {
    if (samples[i] > threshold &&
        samples[i] > samples[i-1] && samples[i] > samples[i+1]) {
      spikes++;
    }
  }
  
  return spikes >= 2; // Multiple spikes indicate pattern
}

// Detect voice command patterns (ESP32 optimized)
bool detectVoicePattern(int* samples, int count, int baseline) {
  if (count < 5) return false;
  
  // ESP32 voice threshold adjusted for 12-bit ADC
  int voiceThreshold = baseline + VOICE_SENSITIVITY_THRESHOLD;
  int activeCount = 0;
  int peakCount = 0;
  
  // Count voice-level sounds and peaks
  for (int i = 0; i < count; i++) {
    if (samples[i] > voiceThreshold) {
      activeCount++;
    }
    
    // Count peaks (syllables) - ESP32 optimized
    if (i > 0 && i < count - 1) {
      if (samples[i] > voiceThreshold && 
          samples[i] > samples[i-1] && 
          samples[i] > samples[i+1]) {
        peakCount++;
      }
    }
  }
  
  // Voice pattern: sustained activity with multiple peaks
  float activeRatio = (float)activeCount / count;
  return (activeRatio > 0.3 && activeRatio < 0.8 && peakCount >= 2);
}

// Analyze syllable patterns for HELP detection
bool analyzeHelpSyllables(int* samples, int count, int baseline) {
  int threshold = baseline + VOICE_SENSITIVITY_THRESHOLD;
  bool inSyllable = false;
  int syllableCount = 0;
  int syllableLength = 0;
  int gapLength = 0;
  
  for (int i = 0; i < count; i++) {
    if (samples[i] > threshold) {
      if (!inSyllable) {
        // Start of new syllable
        if (syllableCount > 0 && gapLength >= 1 && gapLength <= 4) {
          // Valid gap between syllables
        }
        syllableCount++;
        inSyllable = true;
        syllableLength = 1;
        gapLength = 0;
      } else {
        syllableLength++;
      }
    } else {
      if (inSyllable) {
        // End of syllable
        inSyllable = false;
        syllableLength = 0;
      }
      gapLength++;
    }
  }
  
  // HELP has 2 syllables: HE-LP
  return (syllableCount >= 2 && syllableCount <= 3);
}

// Calculate voice command confidence
float calculateVoiceConfidence(int* samples, int count, int baseline) {
  float confidence = 0.0;
  
  // Check for voice pattern
  if (!detectVoicePattern(samples, count, baseline)) {
    return 0.0;
  }
  
  // Analyze syllable structure
  if (analyzeHelpSyllables(samples, count, baseline)) {
    confidence += 0.4;
  }
  
  // Check duration (HELP should be quick, ~0.5-1 second)
  confidence += 0.3;
  
  // Check for sustained voice activity
  int voiceThreshold = baseline + VOICE_SENSITIVITY_THRESHOLD;
  int activeCount = 0;
  for (int i = 0; i < count; i++) {
    if (samples[i] > voiceThreshold) activeCount++;
  }
  
  float activeRatio = (float)activeCount / count;
  if (activeRatio >= 0.3 && activeRatio <= 0.7) {
    confidence += 0.3;
  }
  
  return min(confidence, 1.0);
}

// Calculate sound intensity trend
int getSoundTrend(int* samples, int count) {
  if (count < 2) return 0;
  
  int increasing = 0, decreasing = 0;
  for (int i = 1; i < count; i++) {
    if (samples[i] > samples[i-1]) increasing++;
    if (samples[i] < samples[i-1]) decreasing++;
  }
  
  if (increasing > decreasing) return 1;   // Rising trend
  if (decreasing > increasing) return -1;  // Falling trend
  return 0; // Stable
}

// Advanced anomaly scoring
float calculateAnomalyScore(int currentLevel, int baseline, int* recentSamples, int sampleCount) {
  float score = 0.0;
  
  // Level-based scoring
  float levelScore = (float)(currentLevel - baseline) / DETECTION_SENSITIVITY;
  score += levelScore * 0.4;
  
  // Variance-based scoring
  float variance = 0;
  for (int i = 0; i < sampleCount; i++) {
    float diff = recentSamples[i] - baseline;
    variance += diff * diff;
  }
  variance /= sampleCount;
  score += (variance / (DETECTION_SENSITIVITY * DETECTION_SENSITIVITY)) * 0.3;
  
  // Pattern-based scoring
  if (detectSoundPattern(recentSamples, sampleCount, baseline)) {
    score += 0.3;
  }
  
  return score;
}

#endif