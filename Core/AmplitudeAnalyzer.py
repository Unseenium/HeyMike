"""
Amplitude Analyzer for Hey Mike!
Processes audio chunks and calculates real-time amplitude for waveform visualization
"""

import numpy as np
import logging
from typing import Callable, Optional


class AmplitudeAnalyzer:
    """Analyzes audio chunks and calculates normalized amplitude values"""
    
    def __init__(self, callback: Optional[Callable[[float], None]] = None):
        """
        Initialize Amplitude Analyzer
        
        Args:
            callback: Function to call with normalized amplitude (0.0-1.0)
        """
        self.logger = logging.getLogger(__name__)
        self.callback = callback
        
        # Audio format constants
        self.max_amplitude = 32768.0  # int16 max value
        
        # Smoothing for less jittery visualization
        self.smoothing_factor = 0.15  # Very low = very responsive (was 0.3)
        self.last_amplitude = 0.0
        
        # Amplification for better visual response
        self.amplification = 5.0  # Strong boost for dramatic oscillations (was 3.5)
        
        self.logger.info("AmplitudeAnalyzer initialized")
    
    def process_chunk(self, audio_chunk: bytes) -> float:
        """
        Process audio chunk and calculate normalized amplitude
        
        Args:
            audio_chunk: Raw audio bytes (int16 format)
            
        Returns:
            Normalized amplitude (0.0-1.0)
        """
        try:
            # Convert bytes to numpy array (int16 format)
            audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
            
            # Handle empty or invalid audio data
            if len(audio_data) == 0:
                return 0.0
            
            # Calculate RMS (Root Mean Square) for amplitude
            # Convert to float to avoid overflow
            audio_float = audio_data.astype(np.float64)
            rms = np.sqrt(np.mean(audio_float ** 2))
            
            # Normalize to 0.0-1.0 range
            normalized = min(rms / self.max_amplitude, 1.0)
            
            # Apply amplification for better visual response (voice is often quiet)
            amplified = min(normalized * self.amplification, 1.0)
            
            # Apply power scaling for more dynamic range (makes it more "punchy")
            # Raises low values more than high values for dramatic oscillations
            if amplified > 0.0:
                powered = np.power(amplified, 0.6)  # Lower = more dramatic (was 0.7)
            else:
                powered = 0.0
            
            # Apply smoothing to reduce jitter (but keep responsiveness)
            smoothed = self._smooth(powered)
            
            # Call callback if provided
            if self.callback:
                self.callback(smoothed)
            
            return smoothed
            
        except Exception as e:
            self.logger.error(f"Error processing audio chunk: {e}")
            return 0.0
    
    def _smooth(self, value: float) -> float:
        """
        Apply exponential smoothing to amplitude values
        
        Args:
            value: Current amplitude value
            
        Returns:
            Smoothed amplitude value
        """
        # Exponential moving average
        smoothed = (self.smoothing_factor * self.last_amplitude + 
                   (1 - self.smoothing_factor) * value)
        self.last_amplitude = smoothed
        return smoothed
    
    def reset(self):
        """Reset smoothing state"""
        self.last_amplitude = 0.0
        self.logger.debug("AmplitudeAnalyzer reset")
    
    def set_callback(self, callback: Callable[[float], None]):
        """
        Set or update the callback function
        
        Args:
            callback: Function to call with amplitude values
        """
        self.callback = callback
        self.logger.debug("Callback updated")


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create analyzer with test callback
    def print_amplitude(amp: float):
        bars = int(amp * 20)
        print(f"Amplitude: {amp:.2f} | {'█' * bars}")
    
    analyzer = AmplitudeAnalyzer(callback=print_amplitude)
    
    # Test with synthetic audio data
    print("\nTesting with synthetic audio...")
    for i in range(10):
        # Create test audio chunk (simulated voice amplitude)
        amplitude = (np.sin(i * 0.5) * 0.5 + 0.5) * 0.8  # 0.0 to 0.8
        test_audio = (np.random.randn(1024) * amplitude * 15000).astype(np.int16)
        test_chunk = test_audio.tobytes()
        
        # Process
        result = analyzer.process_chunk(test_chunk)
        print(f"  Frame {i}: amplitude={amplitude:.2f}, result={result:.2f}")
    
    print("\nAmplitudeAnalyzer test complete!")
