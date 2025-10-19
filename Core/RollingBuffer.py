"""
Rolling Buffer for Hey Mike! Wake Word Detection
Maintains a circular buffer of recent audio for Whisper transcription
"""

import logging
import numpy as np
from collections import deque
from typing import Optional

class RollingBuffer:
    """
    Circular audio buffer for wake word detection
    
    Maintains the last N seconds of audio in memory for transcription
    when voice activity is detected by VAD.
    
    Performance:
    - Memory: ~100KB for 3 seconds @ 16kHz
    - Storage: RAM only, never written to disk
    - Cleared: After each detection attempt
    
    Privacy: Temporary buffer, automatically cleared, no persistence
    """
    
    def __init__(
        self, 
        max_duration: float = 3.0, 
        sample_rate: int = 16000,
        channels: int = 1
    ):
        """
        Initialize rolling buffer
        
        Args:
            max_duration: Maximum buffer duration in seconds
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1 for mono, 2 for stereo)
        """
        self.logger = logging.getLogger(__name__)
        self.max_duration = max_duration
        self.sample_rate = sample_rate
        self.channels = channels
        
        # Calculate maximum buffer size in samples
        self.max_samples = int(max_duration * sample_rate * channels)
        
        # Create circular buffer using deque (efficient for append/popleft)
        self.buffer = deque(maxlen=self.max_samples)
        
        # Track total samples added (for debugging)
        self.total_samples_added = 0
        
        # Calculate memory footprint (approximate)
        memory_mb = (self.max_samples * 2) / (1024 * 1024)  # 2 bytes per sample (int16)
        
        self.logger.info(
            f"RollingBuffer initialized: {max_duration}s @ {sample_rate}Hz, "
            f"max_samples={self.max_samples}, memory≈{memory_mb:.2f}MB"
        )
    
    def append(self, audio_chunk: bytes) -> None:
        """
        Add audio chunk to buffer
        
        Args:
            audio_chunk: Raw audio data as bytes (16-bit PCM)
        """
        # Convert bytes to numpy array (int16)
        try:
            samples = np.frombuffer(audio_chunk, dtype=np.int16)
            
            # Add samples to buffer (deque automatically removes oldest when full)
            self.buffer.extend(samples)
            self.total_samples_added += len(samples)
            
        except Exception as e:
            self.logger.error(f"Error appending to buffer: {e}")
    
    def is_full(self, threshold: float = 0.66) -> bool:
        """
        Check if buffer has enough audio for transcription
        
        Args:
            threshold: Minimum fill ratio (0.0-1.0) to consider buffer "full"
                      Default 0.66 = 2 seconds for a 3 second buffer
        
        Returns:
            True if buffer is sufficiently filled, False otherwise
        """
        current_samples = len(self.buffer)
        required_samples = int(self.max_samples * threshold)
        return current_samples >= required_samples
    
    def get_audio(self) -> np.ndarray:
        """
        Get buffered audio as numpy array
        
        Returns:
            Numpy array of audio samples (float32, normalized to [-1, 1])
        """
        if not self.buffer:
            self.logger.warning("Buffer is empty")
            return np.array([], dtype=np.float32)
        
        # Convert deque to numpy array
        audio_array = np.array(self.buffer, dtype=np.int16)
        
        # Convert to float32 and normalize to [-1, 1] for Whisper
        audio_float = audio_array.astype(np.float32) / 32768.0
        
        duration_sec = len(audio_array) / self.sample_rate
        self.logger.debug(
            f"Retrieved audio: {len(audio_array)} samples, {duration_sec:.2f}s"
        )
        
        return audio_float
    
    def get_audio_bytes(self) -> bytes:
        """
        Get buffered audio as raw bytes (int16)
        
        Returns:
            Raw audio data as bytes
        """
        if not self.buffer:
            return b''
        
        # Convert deque to numpy array and then to bytes
        audio_array = np.array(self.buffer, dtype=np.int16)
        return audio_array.tobytes()
    
    def clear(self) -> None:
        """Clear the buffer"""
        samples_before = len(self.buffer)
        self.buffer.clear()
        self.logger.debug(f"Buffer cleared ({samples_before} samples removed)")
    
    def get_duration(self) -> float:
        """
        Get current buffer duration in seconds
        
        Returns:
            Duration in seconds
        """
        return len(self.buffer) / self.sample_rate
    
    def get_fill_ratio(self) -> float:
        """
        Get buffer fill ratio
        
        Returns:
            Fill ratio (0.0-1.0)
        """
        return len(self.buffer) / self.max_samples if self.max_samples > 0 else 0.0
    
    def get_stats(self) -> dict:
        """
        Get buffer statistics for debugging/monitoring
        
        Returns:
            Dictionary with buffer statistics
        """
        return {
            'current_samples': len(self.buffer),
            'max_samples': self.max_samples,
            'fill_ratio': self.get_fill_ratio(),
            'duration_seconds': self.get_duration(),
            'max_duration_seconds': self.max_duration,
            'total_samples_added': self.total_samples_added,
            'sample_rate': self.sample_rate,
            'channels': self.channels
        }
    
    def __len__(self) -> int:
        """Return number of samples in buffer"""
        return len(self.buffer)
    
    def __bool__(self) -> bool:
        """Return True if buffer has samples"""
        return len(self.buffer) > 0


class BufferOverflowError(Exception):
    """Exception raised when buffer overflow occurs (should not happen with deque)"""
    pass

