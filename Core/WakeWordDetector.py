"""
Wake Word Detector for Hey Mike!
Main orchestrator for hands-free voice activation using "Hey Mike" wake word
"""

import logging
import threading
import pyaudio
import numpy as np
import time
from typing import Optional, Callable, Dict, Any
from Core.VADProcessor import VADProcessor, VADInitError
from Core.RollingBuffer import RollingBuffer
from Core.MLXWhisperManager import MLXWhisperManager

class WakeWordDetector:
    """
    Wake word detection system for hands-free activation
    
    Architecture:
    1. VAD (Voice Activity Detection) - Fast pre-filter for speech
    2. Rolling Buffer - Maintains last 2-3 seconds of audio
    3. Whisper Transcription - Accurate transcription of detected speech
    4. Wake Word Detection - String matching for "hey mike"
    
    Performance Targets:
    - <500ms wake word detection latency
    - <3% battery drain per hour when listening
    - <5% false positive rate
    - 95%+ wake word detection accuracy
    """
    
    # Audio configuration (matches AudioManager)
    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 480  # 30ms chunks @ 16kHz for VAD (16000 * 0.03 = 480)
    FORMAT = pyaudio.paInt16
    
    # Wake word configuration
    WAKE_WORD = "hey mike"
    WAKE_WORD_VARIANTS = ["hey mike", "hi mike", "hay mike"]  # Common misrecognitions
    
    def __init__(
        self,
        whisper_manager: MLXWhisperManager,
        vad_aggressiveness: int = 3,
        buffer_duration: float = 3.0,
        trigger_threshold: float = 2.0
    ):
        """
        Initialize Wake Word Detector
        
        Args:
            whisper_manager: MLX Whisper Manager for transcription
            vad_aggressiveness: VAD aggressiveness level (0-3, default 3)
            buffer_duration: Rolling buffer duration in seconds (default 3.0)
            trigger_threshold: Minimum audio duration to trigger transcription (default 2.0)
        """
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.whisper_manager = whisper_manager
        self.vad_processor: Optional[VADProcessor] = None
        self.rolling_buffer: Optional[RollingBuffer] = None
        
        # PyAudio for microphone capture
        self.pyaudio_instance: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        
        # Configuration
        self.vad_aggressiveness = vad_aggressiveness
        self.buffer_duration = buffer_duration
        self.trigger_threshold = trigger_threshold
        
        # State
        self.is_listening = False
        self.is_processing = False
        self._stop_requested = False
        self._listen_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.stats = {
            'wake_words_detected': 0,
            'false_positives': 0,
            'total_chunks_processed': 0,
            'speech_chunks_detected': 0,
            'transcriptions_attempted': 0,
            'errors': 0
        }
        
        # Callbacks
        self.on_wake_word_detected: Optional[Callable[[str], None]] = None  # Called with remaining command
        self.on_listening_started: Optional[Callable[[], None]] = None
        self.on_listening_stopped: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Initialize components
        init_success = self._initialize_components()
        if not init_success:
            self.logger.error("Failed to initialize wake word detector components")
            # Set components explicitly to None for clarity
            self.vad_processor = None
            self.rolling_buffer = None
            self.pyaudio_instance = None
    
    def _initialize_components(self) -> bool:
        """
        Initialize VAD processor and rolling buffer
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize VAD processor
            self.vad_processor = VADProcessor(
                aggressiveness=self.vad_aggressiveness,
                sample_rate=self.SAMPLE_RATE
            )
            self.logger.info("VAD processor initialized")
            
            # Initialize rolling buffer
            self.rolling_buffer = RollingBuffer(
                max_duration=self.buffer_duration,
                sample_rate=self.SAMPLE_RATE,
                channels=self.CHANNELS
            )
            self.logger.info("Rolling buffer initialized")
            
            # Don't initialize PyAudio here - do it lazily when start_listening() is called
            # This avoids conflicts with AudioManager's PyAudio instance
            self.logger.info("Components initialized successfully (PyAudio will be initialized on start)")
            self.logger.info(f"DEBUG: After init - vad={self.vad_processor is not None}, buffer={self.rolling_buffer is not None}, self id={id(self)}")
            
            return True
            
        except VADInitError as e:
            self.logger.error(f"VAD initialization failed: {e}")
            if self.on_error:
                self.on_error(f"VAD initialization failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            if self.on_error:
                self.on_error(f"Wake word detector initialization failed: {e}")
            return False
    
    def start_listening(self) -> bool:
        """
        Start continuous wake word detection
        
        Returns:
            True if listening started successfully, False otherwise
        """
        if self.is_listening:
            self.logger.warning("Already listening for wake word")
            return False
        
        # Debug: Log the state of all components
        self.logger.info(f"DEBUG: start_listening called - vad_processor={self.vad_processor is not None}, rolling_buffer={self.rolling_buffer is not None}, pyaudio={self.pyaudio_instance is not None}")
        self.logger.info(f"DEBUG: self object id = {id(self)}")
        
        # Check for None explicitly (RollingBuffer has __bool__ that returns False when empty!)
        if self.vad_processor is None:
            self.logger.error("VAD processor is None - cannot start listening")
            return False
        if self.rolling_buffer is None:
            self.logger.error(f"Rolling buffer is None - cannot start listening")
            return False
        
        # Initialize PyAudio now (lazy initialization to avoid conflicts)
        if not self.pyaudio_instance:
            try:
                self.pyaudio_instance = pyaudio.PyAudio()
                self.logger.info("PyAudio initialized for wake word detection")
            except Exception as e:
                self.logger.error(f"Failed to initialize PyAudio: {e}")
                if self.on_error:
                    self.on_error(f"Failed to initialize audio: {e}")
                return False
        
        if not self.whisper_manager.is_model_loaded():
            self.logger.error("Whisper model not loaded")
            if self.on_error:
                self.on_error("Whisper model not loaded")
            return False
        
        try:
            # Reset state
            self._stop_requested = False
            self.rolling_buffer.clear()
            
            # Open audio stream
            self.stream = self.pyaudio_instance.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE,
                stream_callback=self._audio_callback
            )
            
            self.is_listening = True
            self.stream.start_stream()
            
            # Start processing thread
            self._listen_thread = threading.Thread(
                target=self._listening_loop,
                daemon=True,
                name="WakeWordDetector"
            )
            self._listen_thread.start()
            
            self.logger.info("Wake word detection started - listening for 'Hey Mike'")
            
            if self.on_listening_started:
                self.on_listening_started()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start wake word detection: {e}")
            if self.on_error:
                self.on_error(f"Failed to start wake word detection: {e}")
            return False
    
    def stop_listening(self) -> None:
        """Stop wake word detection"""
        if not self.is_listening:
            return
        
        self.logger.info("Stopping wake word detection...")
        self._stop_requested = True
        self.is_listening = False
        
        # Stop audio stream
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                self.logger.warning(f"Error stopping stream: {e}")
            self.stream = None
        
        # Wait for listening thread to finish
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=2.0)
        
        # Clear buffer
        if self.rolling_buffer:
            self.rolling_buffer.clear()
        
        self.logger.info("Wake word detection stopped")
        
        if self.on_listening_stopped:
            self.on_listening_stopped()
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """
        PyAudio callback for processing audio chunks
        
        Args:
            in_data: Audio data from microphone
            frame_count: Number of frames
            time_info: Timing information
            status: Stream status
        
        Returns:
            Tuple of (None, pyaudio.paContinue or pyaudio.paComplete)
        """
        if not self.is_listening or self._stop_requested:
            return (None, pyaudio.paComplete)
        
        try:
            self.stats['total_chunks_processed'] += 1
            
            # Check for speech using VAD
            is_speech = self.vad_processor.is_speech(in_data, chunk_duration_ms=30)
            
            if is_speech:
                self.stats['speech_chunks_detected'] += 1
                # Add to rolling buffer
                self.rolling_buffer.append(in_data)
            
        except Exception as e:
            self.logger.error(f"Error in audio callback: {e}")
            self.stats['errors'] += 1
        
        return (None, pyaudio.paContinue)
    
    def _listening_loop(self):
        """
        Main listening loop - monitors buffer and triggers transcription
        """
        self.logger.info("Wake word listening loop started")
        
        last_check_time = time.time()
        check_interval = 0.5  # Check buffer every 500ms
        
        while self.is_listening and not self._stop_requested:
            try:
                current_time = time.time()
                
                # Check buffer periodically
                if current_time - last_check_time >= check_interval:
                    last_check_time = current_time
                    
                    # Check if buffer is full enough for transcription
                    if self.rolling_buffer.is_full(threshold=self.trigger_threshold / self.buffer_duration):
                        # Only process if not already processing
                        if not self.is_processing:
                            self._process_buffer()
                
                # Sleep to avoid busy-waiting
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in listening loop: {e}")
                self.stats['errors'] += 1
                time.sleep(0.5)  # Back off on error
        
        self.logger.info("Wake word listening loop stopped")
    
    def _process_buffer(self):
        """
        Process buffered audio through Whisper and check for wake word
        """
        if self.is_processing:
            return
        
        self.is_processing = True
        self.stats['transcriptions_attempted'] += 1
        
        try:
            # Get audio from buffer
            audio_data = self.rolling_buffer.get_audio()
            
            if len(audio_data) == 0:
                self.logger.debug("Buffer empty, skipping transcription")
                self.is_processing = False
                return
            
            # Clear buffer (we've captured what we need)
            self.rolling_buffer.clear()
            
            self.logger.debug(f"Processing buffer: {len(audio_data)} samples")
            
            # Transcribe using Whisper (synchronous for now)
            text = self.whisper_manager.transcribe_audio(audio_data, language=None)
            
            if text:
                self.logger.debug(f"Transcribed: '{text}'")
                
                # Check for wake word
                result = self._detect_wake_word(text)
                
                if result['detected']:
                    self.stats['wake_words_detected'] += 1
                    self.logger.info(f"Wake word detected! Command: '{result['command']}'")
                    
                    # Trigger callback with remaining command
                    if self.on_wake_word_detected:
                        self.on_wake_word_detected(result['command'])
            
        except Exception as e:
            self.logger.error(f"Error processing buffer: {e}")
            self.stats['errors'] += 1
        
        finally:
            self.is_processing = False
    
    def _detect_wake_word(self, text: str) -> Dict[str, Any]:
        """
        Detect wake word in transcribed text and strip it
        
        Args:
            text: Transcribed text from Whisper
        
        Returns:
            Dictionary with 'detected' (bool) and 'command' (str) keys
        """
        text_lower = text.lower().strip()
        
        # Check all wake word variants
        for wake_word in self.WAKE_WORD_VARIANTS:
            # Pattern 1: Wake word at start with command
            if text_lower.startswith(wake_word):
                remaining = text_lower[len(wake_word):].strip()
                # Remove leading punctuation
                remaining = remaining.lstrip(',.!?;:')
                return {
                    'detected': True,
                    'command': remaining,
                    'wake_word_used': wake_word
                }
        
        return {'detected': False, 'command': ''}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get detection statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            **self.stats,
            'is_listening': self.is_listening,
            'is_processing': self.is_processing,
            'buffer_stats': self.rolling_buffer.get_stats() if self.rolling_buffer else {}
        }
    
    def set_vad_aggressiveness(self, level: int) -> bool:
        """
        Update VAD aggressiveness level
        
        Args:
            level: New aggressiveness level (0-3)
        
        Returns:
            True if successful, False otherwise
        """
        if self.vad_processor:
            return self.vad_processor.set_aggressiveness(level)
        return False
    
    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up wake word detector...")
        
        # Stop listening
        self.stop_listening()
        
        # Clean up PyAudio
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None
        
        self.logger.info("Wake word detector cleanup complete")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


class WakeWordError(Exception):
    """Base exception for wake word errors"""
    pass

