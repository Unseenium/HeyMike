"""
Wake Word Detector for Hey Mike! v2.0
Detects "Hey Mike!" wake word to activate command mode
"""

import logging
import re
from typing import Optional, Callable, List, Set
import time

class WakeWordDetector:
    """Detects wake words in transcribed text to activate command mode"""
    
    # Wake word patterns (case-insensitive)
    WAKE_PATTERNS = [
        # Primary patterns
        r'\bhey\s+mike\b',
        r'\bhey\s+mic\b',
        r'\bhey\s+mick\b',
        
        # Alternative patterns
        r'\bhi\s+mike\b',
        r'\bhello\s+mike\b',
        
        # Shortened patterns
        r'\bmike\b',  # When used at start of sentence
        
        # Common misheard patterns
        r'\bhey\s+magic\b',
        r'\bhey\s+make\b',
        r'\bhey\s+my\b',
    ]
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.9
    MEDIUM_CONFIDENCE_THRESHOLD = 0.7
    LOW_CONFIDENCE_THRESHOLD = 0.5
    
    def __init__(self):
        """Initialize Wake Word Detector"""
        self.logger = logging.getLogger(__name__)
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = []
        for pattern in self.WAKE_PATTERNS:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self.compiled_patterns.append((pattern, compiled))
            except re.error as e:
                self.logger.error(f"Failed to compile pattern {pattern}: {e}")
        
        # Detection settings
        self.min_confidence = self.LOW_CONFIDENCE_THRESHOLD
        self.require_sentence_start = False  # Whether wake word must be at sentence start
        
        # Statistics
        self.total_detections = 0
        self.false_positives = 0
        self.detection_history = []
        
        # Callbacks
        self.on_wake_word_detected: Optional[Callable[[str, float, str], None]] = None
        self.on_false_positive: Optional[Callable[[str], None]] = None
    
    def detect_wake_word(self, text: str) -> Optional[dict]:
        """
        Detect wake word in transcribed text
        
        Args:
            text: Transcribed text to analyze
            
        Returns:
            Dictionary with detection info or None if no wake word found
        """
        if not text or not text.strip():
            return None
        
        text = text.strip()
        self.logger.debug(f"Analyzing text for wake word: '{text}'")
        
        best_match = None
        highest_confidence = 0.0
        
        for pattern_str, compiled_pattern in self.compiled_patterns:
            match = compiled_pattern.search(text)
            if match:
                # Calculate confidence based on pattern specificity and position
                confidence = self._calculate_confidence(text, match, pattern_str)
                
                if confidence > highest_confidence and confidence >= self.min_confidence:
                    highest_confidence = confidence
                    best_match = {
                        'pattern': pattern_str,
                        'match_text': match.group(),
                        'confidence': confidence,
                        'start_pos': match.start(),
                        'end_pos': match.end(),
                        'full_text': text
                    }
        
        if best_match:
            # Extract command part (text after wake word)
            command_start = best_match['end_pos']
            command_text = text[command_start:].strip()
            
            # Remove common punctuation and filler words
            command_text = self._clean_command_text(command_text)
            
            best_match['command_text'] = command_text
            best_match['has_command'] = bool(command_text)
            
            # Log detection
            self.total_detections += 1
            self.detection_history.append({
                'timestamp': time.time(),
                'text': text,
                'confidence': highest_confidence,
                'command': command_text
            })
            
            # Keep only recent history
            if len(self.detection_history) > 100:
                self.detection_history = self.detection_history[-50:]
            
            self.logger.info(f"Wake word detected: '{best_match['match_text']}' "
                           f"(confidence: {highest_confidence:.2f}, command: '{command_text}')")
            
            if self.on_wake_word_detected:
                self.on_wake_word_detected(text, highest_confidence, command_text)
            
            return best_match
        
        return None
    
    def _calculate_confidence(self, text: str, match: re.Match, pattern: str) -> float:
        """
        Calculate confidence score for a wake word match
        
        Args:
            text: Full text
            match: Regex match object
            pattern: Pattern that matched
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = 0.5
        
        # Pattern-specific confidence adjustments
        pattern_confidence = {
            r'\bhey\s+mike\b': 1.0,      # Perfect match
            r'\bhey\s+mic\b': 0.9,       # Common mishearing
            r'\bhey\s+mick\b': 0.9,      # Common mishearing
            r'\bhi\s+mike\b': 0.8,       # Alternative greeting
            r'\bhello\s+mike\b': 0.8,    # Alternative greeting
            r'\bmike\b': 0.6,            # Ambiguous without "hey"
            r'\bhey\s+magic\b': 0.7,     # Common mishearing
            r'\bhey\s+make\b': 0.6,      # Possible mishearing
            r'\bhey\s+my\b': 0.5,        # Weak match
        }
        
        confidence = pattern_confidence.get(pattern, base_confidence)
        
        # Position bonus: wake word at start is more likely intentional
        if match.start() == 0:
            confidence += 0.1
        elif match.start() <= 5:  # Near start
            confidence += 0.05
        
        # Length penalty: very short text might be accidental
        if len(text.strip()) < 10:
            confidence -= 0.1
        
        # Context bonus: if followed by command-like text
        command_part = text[match.end():].strip()
        if self._looks_like_command(command_part):
            confidence += 0.1
        
        # Ensure confidence is in valid range
        return max(0.0, min(1.0, confidence))
    
    def _looks_like_command(self, text: str) -> bool:
        """
        Check if text looks like a command
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text appears to be a command
        """
        if not text:
            return False
        
        # Command indicators
        command_words = [
            'open', 'close', 'start', 'stop', 'run', 'launch', 'quit',
            'search', 'find', 'look', 'show', 'display',
            'create', 'make', 'new', 'delete', 'remove',
            'go', 'navigate', 'move', 'copy', 'paste',
            'take', 'capture', 'screenshot', 'record',
            'play', 'pause', 'volume', 'mute',
            'help', 'tell', 'what', 'how', 'when', 'where'
        ]
        
        text_lower = text.lower()
        words = text_lower.split()
        
        # Check if first few words contain command indicators
        first_words = words[:3] if len(words) >= 3 else words
        return any(word in command_words for word in first_words)
    
    def _clean_command_text(self, text: str) -> str:
        """
        Clean command text by removing filler words and punctuation
        
        Args:
            text: Raw command text
            
        Returns:
            Cleaned command text
        """
        if not text:
            return ""
        
        # Remove common filler words at the start
        filler_words = ['um', 'uh', 'er', 'ah', 'well', 'so', 'like', 'you know']
        words = text.split()
        
        # Remove leading filler words
        while words and words[0].lower().rstrip('.,!?') in filler_words:
            words.pop(0)
        
        cleaned = ' '.join(words)
        
        # Remove leading punctuation
        cleaned = re.sub(r'^[^\w\s]+', '', cleaned)
        
        return cleaned.strip()
    
    def is_command_mode_text(self, text: str) -> bool:
        """
        Quick check if text should trigger command mode
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains wake word
        """
        detection = self.detect_wake_word(text)
        return detection is not None and detection['confidence'] >= self.min_confidence
    
    def extract_command_from_text(self, text: str) -> Optional[str]:
        """
        Extract just the command part from text containing wake word
        
        Args:
            text: Full text with wake word
            
        Returns:
            Command text or None if no wake word found
        """
        detection = self.detect_wake_word(text)
        if detection and detection['has_command']:
            return detection['command_text']
        return None
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Set minimum confidence threshold for wake word detection
        
        Args:
            threshold: Confidence threshold (0.0 to 1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.min_confidence = threshold
            self.logger.info(f"Wake word confidence threshold set to {threshold}")
        else:
            self.logger.error(f"Invalid confidence threshold: {threshold}")
    
    def get_detection_stats(self) -> dict:
        """
        Get wake word detection statistics
        
        Returns:
            Dictionary with detection statistics
        """
        recent_detections = [d for d in self.detection_history 
                           if time.time() - d['timestamp'] < 3600]  # Last hour
        
        return {
            'total_detections': self.total_detections,
            'false_positives': self.false_positives,
            'recent_detections': len(recent_detections),
            'average_confidence': sum(d['confidence'] for d in recent_detections) / len(recent_detections) if recent_detections else 0.0,
            'current_threshold': self.min_confidence
        }
    
    def test_patterns(self) -> List[dict]:
        """
        Test all wake word patterns with sample text
        
        Returns:
            List of test results
        """
        test_cases = [
            "Hey Mike, open Chrome",
            "Hey mic, what's the weather?",
            "Hi Mike, search for Python tutorials",
            "Mike, take a screenshot",
            "Hey magic, play music",
            "Hey make a new file",
            "Hello Mike, show me the time",
            "Just talking about Mike",  # Should not match
            "Hey there Mike",  # Should not match
        ]
        
        results = []
        for test_text in test_cases:
            detection = self.detect_wake_word(test_text)
            results.append({
                'text': test_text,
                'detected': detection is not None,
                'confidence': detection['confidence'] if detection else 0.0,
                'command': detection['command_text'] if detection else None
            })
        
        return results
