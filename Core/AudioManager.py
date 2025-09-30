"""
Audio Manager for Hey Mike!
Handles microphone input and audio processing
"""

import pyaudio
import numpy as np
import threading
import logging
import time
from typing import Optional, Callable, List
import queue

class AudioManager:
    """Manages audio recording and processing for speech recognition"""
    
    # Audio configuration
    SAMPLE_RATE = 16000  # Whisper expects 16kHz
    CHANNELS = 1         # Mono audio
    CHUNK_SIZE = 1024    # Audio buffer size
    FORMAT = pyaudio.paInt16  # 16-bit audio
    
    # Safety limits
    MAX_RECORDING_DURATION = 300.0  # 5 minutes (increased from 30s)
    MAX_BUFFER_SIZE = 100 * 1024 * 1024  # 100MB max audio buffer (safety limit)
    
    def __init__(self):
        """Initialize Audio Manager"""
        self.pyaudio_instance = None
        self.stream = None
        self.is_recording = False
        self.audio_buffer = []  # Use list of numpy arrays instead of Queue
        self.buffer_lock = threading.Lock()  # Thread-safe access
        self.recording_thread = None
        self.logger = logging.getLogger(__name__)
        
        # Audio settings
        self.input_device_index = None
        self.silence_threshold = 500  # Amplitude threshold for silence detection
        self.max_recording_duration = self.MAX_RECORDING_DURATION  # Maximum recording time
        self.silence_duration = 2.0  # Seconds of silence before auto-stop
        self.current_buffer_size = 0  # Track buffer size in bytes
        
        # Callbacks
        self.on_recording_start: Optional[Callable[[], None]] = None
        self.on_recording_stop: Optional[Callable[[np.ndarray], None]] = None
        self.on_audio_level: Optional[Callable[[float], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Initialize PyAudio
        self._initialize_audio()
    
    def _initialize_audio(self) -> bool:
        """
        Initialize PyAudio instance
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            self.logger.info("PyAudio initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize PyAudio: {str(e)}")
            if self.on_error:
                self.on_error(f"Audio initialization failed: {str(e)}")
            return False
    
    def get_input_devices(self) -> List[dict]:
        """
        Get list of available audio input devices
        
        Returns:
            List of dictionaries containing device information
        """
        devices = []
        if not self.pyaudio_instance:
            return devices
        
        try:
            device_count = self.pyaudio_instance.get_device_count()
            
            for i in range(device_count):
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                
                # Only include input devices
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': int(device_info['defaultSampleRate'])
                    })
        
        except Exception as e:
            self.logger.error(f"Failed to enumerate audio devices: {str(e)}")
        
        return devices
    
    def set_input_device(self, device_index: Optional[int]) -> bool:
        """
        Set the audio input device
        
        Args:
            device_index: Index of the device to use, None for default
            
        Returns:
            True if device set successfully, False otherwise
        """
        if self.is_recording:
            self.logger.warning("Cannot change device while recording")
            return False
        
        try:
            # Test the device by trying to open a stream
            if device_index is not None:
                test_stream = self.pyaudio_instance.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.SAMPLE_RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=self.CHUNK_SIZE
                )
                test_stream.close()
            
            self.input_device_index = device_index
            self.logger.info(f"Audio input device set to index: {device_index}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set input device {device_index}: {str(e)}")
            if self.on_error:
                self.on_error(f"Failed to set audio device: {str(e)}")
            return False
    
    def start_recording(self) -> bool:
        """
        Start audio recording
        
        Returns:
            True if recording started successfully, False otherwise
        """
        if self.is_recording:
            self.logger.warning("Already recording")
            return False
        
        if not self.pyaudio_instance:
            self.logger.error("PyAudio not initialized")
            return False
        
        try:
            # Clear audio buffer before starting
            self._clear_buffer()
            
            # Open audio stream
            self.stream = self.pyaudio_instance.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.CHUNK_SIZE,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            self.stream.start_stream()
            
            # Start recording thread for silence detection and auto-stop
            self.recording_thread = threading.Thread(target=self._recording_monitor, daemon=True)
            self.recording_thread.start()
            
            self.logger.info("Recording started")
            
            if self.on_recording_start:
                self.on_recording_start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {str(e)}")
            if self.on_error:
                self.on_error(f"Failed to start recording: {str(e)}")
            return False
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """
        Stop audio recording and return recorded audio
        
        Returns:
            Numpy array containing recorded audio data, or None if failed
        """
        if not self.is_recording:
            self.logger.warning("Not currently recording")
            return None
        
        try:
            self.is_recording = False
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=1.0)
            
            # Collect all audio data from buffer (thread-safe)
            with self.buffer_lock:
                if not self.audio_buffer:
                    self.logger.warning("No audio data recorded")
                    self._clear_buffer()
                    return None
                
                # Concatenate all numpy arrays efficiently
                audio_array = np.concatenate(self.audio_buffer, axis=0)
                
                # Log buffer stats
                buffer_size_mb = self.current_buffer_size / 1024 / 1024
                duration_sec = len(audio_array) / self.SAMPLE_RATE
                self.logger.info(
                    f"Recording stopped: {len(audio_array)} samples, "
                    f"{duration_sec:.1f}s, {buffer_size_mb:.1f}MB"
                )
                
                # Clear buffer
                self._clear_buffer()
            
            # Convert to float32 and normalize to [-1, 1] range
            audio_array = audio_array.astype(np.float32)
            if audio_array.max() > 0:
                audio_array = audio_array / 32768.0  # Convert from int16 to float32
            
            if self.on_recording_stop:
                self.on_recording_stop(audio_array)
            
            return audio_array
            
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {str(e)}", exc_info=True)
            self._clear_buffer()  # Ensure cleanup even on error
            if self.on_error:
                self.on_error(f"Failed to stop recording: {str(e)}")
            return None
    
    def _clear_buffer(self):
        """Clear audio buffer and reset size counter"""
        self.audio_buffer.clear()
        self.current_buffer_size = 0
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """
        PyAudio callback for processing audio chunks
        
        Args:
            in_data: Audio data from microphone
            frame_count: Number of frames
            time_info: Timing information
            status: Stream status
            
        Returns:
            Tuple of (None, pyaudio.paContinue)
        """
        if self.is_recording:
            # Convert bytes to numpy array
            audio_chunk = np.frombuffer(in_data, dtype=np.int16)
            
            # Check buffer size limit (safety check)
            chunk_size = audio_chunk.nbytes
            if self.current_buffer_size + chunk_size > self.MAX_BUFFER_SIZE:
                self.logger.warning(f"Buffer size limit reached ({self.MAX_BUFFER_SIZE/1024/1024:.1f}MB), stopping recording")
                # Stop recording gracefully
                self.is_recording = False
                return (None, pyaudio.paComplete)
            
            # Add to buffer (thread-safe) - keep as numpy array for efficiency
            with self.buffer_lock:
                self.audio_buffer.append(audio_chunk.copy())  # Copy to avoid data corruption
                self.current_buffer_size += chunk_size
            
            # Calculate audio level for visual feedback
            if self.on_audio_level:
                audio_level = np.abs(audio_chunk).mean()
                self.on_audio_level(float(audio_level))
        
        return (None, pyaudio.paContinue)
    
    def _recording_monitor(self):
        """Monitor recording for silence detection and auto-stop"""
        start_time = time.time()
        last_sound_time = start_time
        warning_shown = False
        
        while self.is_recording:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Warn when approaching limit (at 80% of max duration)
            if not warning_shown and elapsed > (self.max_recording_duration * 0.8):
                remaining = self.max_recording_duration - elapsed
                self.logger.warning(
                    f"Approaching max recording duration: {remaining:.0f}s remaining"
                )
                warning_shown = True
            
            # Check maximum recording duration
            if elapsed > self.max_recording_duration:
                self.logger.warning(
                    f"Maximum recording duration ({self.max_recording_duration:.0f}s) reached, stopping"
                )
                # Gracefully stop recording
                self.stop_recording()
                if self.on_error:
                    self.on_error(
                        f"Recording stopped: maximum duration "
                        f"({self.max_recording_duration:.0f}s) reached"
                    )
                break
            
            # Simple silence detection based on recent audio levels
            # This is a basic implementation - could be enhanced with more sophisticated VAD
            
            time.sleep(0.1)  # Check every 100ms
    
    def set_silence_threshold(self, threshold: int):
        """Set the silence detection threshold"""
        self.silence_threshold = threshold
        self.logger.debug(f"Silence threshold set to: {threshold}")
    
    def set_max_recording_duration(self, duration: float):
        """Set maximum recording duration in seconds"""
        self.max_recording_duration = duration
        self.logger.debug(f"Max recording duration set to: {duration}s")
    
    def set_silence_duration(self, duration: float):
        """Set silence duration before auto-stop in seconds"""
        self.silence_duration = duration
        self.logger.debug(f"Silence duration set to: {duration}s")
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.is_recording:
            self.stop_recording()
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None
            self.logger.info("Audio resources cleaned up")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

