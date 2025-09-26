"""
MLX Whisper Manager for Hey Mike!
Handles MLX-optimized Whisper model loading and inference
"""

import os
import threading
import logging
from typing import Optional, Callable, Dict, Any
import mlx_whisper
import numpy as np

class MLXWhisperManager:
    """Manages MLX Whisper models for speech recognition"""
    
    # Available model sizes with their characteristics
    MODEL_SIZES = {
        'tiny': {'size': '39MB', 'speed': 'fastest', 'accuracy': 'basic'},
        'base': {'size': '74MB', 'speed': 'fast', 'accuracy': 'good'},
        'small': {'size': '244MB', 'speed': 'medium', 'accuracy': 'better'},
        'medium': {'size': '769MB', 'speed': 'slow', 'accuracy': 'very good'},
        'large': {'size': '1550MB', 'speed': 'slowest', 'accuracy': 'best'}
    }
    
    def __init__(self, model_dir: str = "Models/WhisperModels"):
        """
        Initialize MLX Whisper Manager
        
        Args:
            model_dir: Directory to store downloaded models
        """
        self.model_dir = model_dir
        self.current_model = None
        self.current_model_name = None
        self.is_loading = False
        self.logger = logging.getLogger(__name__)
        
        # Model repository mapping
        self.model_repos = {
            'tiny': 'mlx-community/whisper-tiny-mlx',
            'base': 'mlx-community/whisper-base-mlx', 
            'small': 'mlx-community/whisper-small-mlx',
            'medium': 'mlx-community/whisper-medium-mlx',
            'large': 'mlx-community/whisper-large-v3-mlx'
        }
        
        # Track downloaded models
        self.downloaded_models = set()
        self.is_predownloading = False
        
        # Ensure model directory exists
        os.makedirs(model_dir, exist_ok=True)
        
        # Callbacks for status updates
        self.on_model_loading: Optional[Callable[[str], None]] = None
        self.on_model_loaded: Optional[Callable[[str], None]] = None
        self.on_predownload_start: Optional[Callable[[], None]] = None
        self.on_predownload_progress: Optional[Callable[[str, int, int], None]] = None
        self.on_predownload_complete: Optional[Callable[[], None]] = None
        self.on_transcription_start: Optional[Callable[[], None]] = None
        self.on_transcription_complete: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def load_model(self, model_name: str = 'base') -> bool:
        """
        Load a Whisper model
        
        Args:
            model_name: Name of the model to load (tiny, base, small, medium, large)
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        if model_name not in self.MODEL_SIZES:
            self.logger.error(f"Unknown model size: {model_name}")
            if self.on_error:
                self.on_error(f"Unknown model size: {model_name}")
            return False
        
        if self.is_loading:
            self.logger.warning("Model is already being loaded")
            return False
        
        # If same model is already loaded, return True
        if self.current_model and self.current_model_name == model_name:
            return True
        
        self.is_loading = True
        
        try:
            if self.on_model_loading:
                self.on_model_loading(model_name)
            
            self.logger.info(f"Loading Whisper model: {model_name}")
            
            # Set the current model using the repository mapping
            self.current_model_name = model_name
            self.current_model = self.model_repos[model_name]
            
            self.logger.info(f"Successfully set model: {model_name}")
            
            if self.on_model_loaded:
                self.on_model_loaded(model_name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {str(e)}")
            if self.on_error:
                self.on_error(f"Failed to load model: {str(e)}")
            return False
        
        finally:
            self.is_loading = False
    
    def load_model_async(self, model_name: str = 'base') -> None:
        """
        Load a model asynchronously
        
        Args:
            model_name: Name of the model to load
        """
        def load_thread():
            self.load_model(model_name)
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
    
    def predownload_all_models(self) -> None:
        """
        Pre-download all Whisper models for instant switching
        This runs in the background and downloads models one by one
        """
        if self.is_predownloading:
            self.logger.warning("Models are already being pre-downloaded")
            return
        
        def predownload_thread():
            self.is_predownloading = True
            
            try:
                if self.on_predownload_start:
                    self.on_predownload_start()
                
                self.logger.info("Starting pre-download of all Whisper models...")
                
                # Download models in order of size (smallest first)
                model_order = ['tiny', 'base', 'small', 'medium', 'large']
                total_models = len(model_order)
                
                for i, model_name in enumerate(model_order, 1):
                    if model_name in self.downloaded_models:
                        self.logger.info(f"Model {model_name} already downloaded, skipping")
                        continue
                    
                    try:
                        if self.on_predownload_progress:
                            self.on_predownload_progress(model_name, i, total_models)
                        
                        self.logger.info(f"Pre-downloading model {model_name} ({i}/{total_models})...")
                        
                        # Download by attempting a small transcription
                        # This forces MLX Whisper to download and cache the model
                        dummy_audio = np.zeros(16000, dtype=np.float32)  # 1 second of silence
                        
                        # Add timeout and better error handling
                        import signal
                        
                        def timeout_handler(signum, frame):
                            raise TimeoutError("Model download timeout")
                        
                        # Set 60 second timeout for model download
                        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(60)
                        
                        try:
                            result = mlx_whisper.transcribe(
                                dummy_audio,
                                path_or_hf_repo=self.model_repos[model_name],
                                verbose=False
                            )
                        finally:
                            signal.alarm(0)  # Cancel the alarm
                            signal.signal(signal.SIGALRM, old_handler)  # Restore old handler
                        
                        self.downloaded_models.add(model_name)
                        self.logger.info(f"Successfully pre-downloaded model: {model_name}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to pre-download model {model_name}: {str(e)}")
                        # Continue with next model even if one fails
                        continue
                
                self.logger.info(f"Pre-download complete! Downloaded {len(self.downloaded_models)} models")
                
                if self.on_predownload_complete:
                    self.on_predownload_complete()
                    
            except Exception as e:
                self.logger.error(f"Pre-download process failed: {str(e)}")
                if self.on_error:
                    self.on_error(f"Pre-download failed: {str(e)}")
            
            finally:
                self.is_predownloading = False
        
        thread = threading.Thread(target=predownload_thread, daemon=True)
        thread.start()
    
    def get_download_status(self) -> Dict[str, Any]:
        """
        Get the current download status of all models
        
        Returns:
            Dictionary with download status information
        """
        return {
            'is_predownloading': self.is_predownloading,
            'downloaded_models': list(self.downloaded_models),
            'total_models': len(self.model_repos),
            'download_progress': len(self.downloaded_models) / len(self.model_repos) * 100
        }
    
    def transcribe_audio(self, audio_data: np.ndarray, language: Optional[str] = None) -> Optional[str]:
        """
        Transcribe audio data using the loaded model
        
        Args:
            audio_data: Audio data as numpy array (16kHz, mono)
            language: Optional language hint for better accuracy
            
        Returns:
            Transcribed text or None if transcription failed
        """
        if not self.current_model:
            self.logger.error("No model loaded")
            if self.on_error:
                self.on_error("No model loaded")
            return None
        
        if self.is_loading:
            self.logger.warning("Model is still loading")
            return None
        
        try:
            if self.on_transcription_start:
                self.on_transcription_start()
            
            self.logger.debug("Starting transcription")
            
            # Prepare transcription options
            options = {}
            if language:
                options['language'] = language
            
            # Transcribe using MLX Whisper
            result = mlx_whisper.transcribe(
                audio_data,
                path_or_hf_repo=self.current_model,
                **options
            )
            
            # Extract text from result
            text = result.get('text', '').strip()
            
            self.logger.debug(f"Transcription complete: {len(text)} characters")
            
            if self.on_transcription_complete:
                self.on_transcription_complete(text)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {str(e)}")
            if self.on_error:
                self.on_error(f"Transcription failed: {str(e)}")
            return None
    
    def transcribe_audio_async(self, audio_data: np.ndarray, 
                             language: Optional[str] = None,
                             callback: Optional[Callable[[Optional[str]], None]] = None) -> None:
        """
        Transcribe audio asynchronously
        
        Args:
            audio_data: Audio data as numpy array
            language: Optional language hint
            callback: Callback function to receive the result
        """
        def transcribe_thread():
            result = self.transcribe_audio(audio_data, language)
            if callback:
                callback(result)
        
        thread = threading.Thread(target=transcribe_thread, daemon=True)
        thread.start()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the currently loaded model
        
        Returns:
            Dictionary with model information
        """
        if not self.current_model_name:
            return {'loaded': False}
        
        model_info = self.MODEL_SIZES.get(self.current_model_name, {})
        return {
            'loaded': True,
            'name': self.current_model_name,
            'size': model_info.get('size', 'unknown'),
            'speed': model_info.get('speed', 'unknown'),
            'accuracy': model_info.get('accuracy', 'unknown'),
            'is_loading': self.is_loading
        }
    
    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """
        Get list of available model sizes
        
        Returns:
            Dictionary of available models with their characteristics
        """
        return self.MODEL_SIZES.copy()
    
    def unload_model(self) -> None:
        """Unload the current model to free memory"""
        if self.current_model:
            self.logger.info(f"Unloading model: {self.current_model_name}")
            self.current_model = None
            self.current_model_name = None
    
    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded"""
        return self.current_model is not None and not self.is_loading

