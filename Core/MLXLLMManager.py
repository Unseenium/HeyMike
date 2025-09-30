"""
MLX LLM Manager for Hey Mike!
Handles local LLM loading and text generation for enhancement
"""

import logging
import threading
from typing import Optional, Callable, Dict, Any

class MLXLLMManager:
    """Manages local LLM for text enhancement"""
    
    # Available LLM models optimized for Apple Silicon
    AVAILABLE_MODELS = {
        'llama-3.2-1b': {
            'name': 'Llama 3.2 1B',
            'repo': 'mlx-community/Llama-3.2-1B-Instruct-4bit',
            'size': '800MB',
            'speed': 'Very Fast',
            'quality': 'Good',
            'description': 'Fast text cleanup, recommended for Smart Mode'
        },
        'phi-3-mini': {
            'name': 'Phi-3 Mini',
            'repo': 'mlx-community/Phi-3-mini-4k-instruct-4bit',
            'size': '2.4GB',
            'speed': 'Fast',
            'quality': 'Better',
            'description': 'Higher quality enhancement, slower'
        },
        'qwen-2.5-1.5b': {
            'name': 'Qwen 2.5 1.5B',
            'repo': 'mlx-community/Qwen2.5-1.5B-Instruct-4bit',
            'size': '1.5GB',
            'speed': 'Fast',
            'quality': 'Very Good',
            'description': 'Balanced quality and speed'
        }
    }
    
    def __init__(self, model_name: str = 'llama-3.2-1b'):
        """
        Initialize MLX LLM Manager
        
        Args:
            model_name: Name of the model to load
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.is_loading = False
        self.is_loaded = False
        
        # Check if MLX is available
        try:
            import mlx.core as mx
            import mlx_lm
            from mlx_lm.sample_utils import make_sampler
            self.mlx_available = True
            self.mlx_lm = mlx_lm
            self.make_sampler = make_sampler
        except ImportError:
            self.logger.warning("MLX not available - LLM features will be disabled")
            self.mlx_available = False
            self.mlx_lm = None
            self.make_sampler = None
        
        # Callbacks
        self.on_model_loading: Optional[Callable[[str], None]] = None
        self.on_model_loaded: Optional[Callable[[str], None]] = None
        self.on_generation_start: Optional[Callable[[], None]] = None
        self.on_generation_complete: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def load_model(self, model_name: Optional[str] = None) -> bool:
        """
        Load an LLM model
        
        Args:
            model_name: Name of the model to load (uses default if None)
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        if not self.mlx_available:
            self.logger.error("MLX not available - cannot load LLM")
            if self.on_error:
                self.on_error("MLX not available for LLM processing")
            return False
        
        if model_name:
            self.model_name = model_name
        
        if self.model_name not in self.AVAILABLE_MODELS:
            self.logger.error(f"Unknown model: {self.model_name}")
            return False
        
        if self.is_loading:
            self.logger.warning("Model is already being loaded")
            return False
        
        if self.is_loaded and self.model is not None:
            self.logger.info(f"Model {self.model_name} already loaded")
            return True
        
        self.is_loading = True
        
        try:
            if self.on_model_loading:
                self.on_model_loading(self.model_name)
            
            self.logger.info(f"Loading LLM model: {self.model_name}")
            
            repo = self.AVAILABLE_MODELS[self.model_name]['repo']
            
            # Load model and tokenizer using mlx_lm
            self.model, self.tokenizer = self.mlx_lm.load(repo)
            
            self.is_loaded = True
            self.logger.info(f"Successfully loaded LLM model: {self.model_name}")
            
            if self.on_model_loaded:
                self.on_model_loaded(self.model_name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load LLM model {self.model_name}: {str(e)}")
            if self.on_error:
                self.on_error(f"Failed to load LLM: {str(e)}")
            return False
        
        finally:
            self.is_loading = False
    
    def load_model_async(self, model_name: Optional[str] = None) -> None:
        """
        Load a model asynchronously
        
        Args:
            model_name: Name of the model to load
        """
        def load_thread():
            self.load_model(model_name)
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
    
    def generate(self, prompt: str, max_tokens: int = 200, 
                temp: float = 0.3) -> Optional[str]:
        """
        Generate text using the loaded LLM
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temp: Sampling temperature (lower = more focused, 0 = argmax)
            
        Returns:
            Generated text or None if generation failed
        """
        if not self.mlx_available:
            self.logger.error("MLX not available")
            return None
        
        if not self.is_loaded or self.model is None:
            self.logger.error("No model loaded")
            return None
        
        try:
            if self.on_generation_start:
                self.on_generation_start()
            
            self.logger.debug(f"Generating text with prompt: {prompt[:50]}...")
            
            # Format prompt for instruction-following models using tokenizer chat template
            messages = [{"role": "user", "content": prompt}]
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages, 
                add_generation_prompt=True,
                tokenize=False
            )
            
            # Create sampler with temperature
            sampler = self.make_sampler(temp=temp)
            
            # Generate using mlx_lm
            response = self.mlx_lm.generate(
                model=self.model,
                tokenizer=self.tokenizer,
                prompt=formatted_prompt,
                max_tokens=max_tokens,
                sampler=sampler,
                verbose=False
            )
            
            # Extract just the generated text (remove prompt)
            generated_text = response.strip()
            
            self.logger.debug(f"Generated text: {generated_text[:50]}...")
            
            if self.on_generation_complete:
                self.on_generation_complete(generated_text)
            
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {str(e)}")
            if self.on_error:
                self.on_error(f"Text generation failed: {str(e)}")
            return None
    
    def generate_async(self, prompt: str, max_tokens: int = 200,
                      temp: float = 0.3,
                      callback: Optional[Callable[[Optional[str]], None]] = None) -> None:
        """
        Generate text asynchronously
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temp: Sampling temperature (0 = argmax, higher = more random)
            callback: Callback function to receive the result
        """
        def generate_thread():
            result = self.generate(prompt, max_tokens, temp)
            if callback:
                callback(result)
        
        thread = threading.Thread(target=generate_thread, daemon=True)
        thread.start()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the currently loaded model
        
        Returns:
            Dictionary with model information
        """
        if not self.is_loaded:
            return {'loaded': False}
        
        model_info = self.AVAILABLE_MODELS.get(self.model_name, {})
        return {
            'loaded': True,
            'name': self.model_name,
            'size': model_info.get('size', 'unknown'),
            'speed': model_info.get('speed', 'unknown'),
            'quality': model_info.get('quality', 'unknown'),
            'is_loading': self.is_loading
        }
    
    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """
        Get list of available LLM models
        
        Returns:
            Dictionary of available models with their characteristics
        """
        return self.AVAILABLE_MODELS.copy()
    
    def unload_model(self) -> None:
        """Unload the current model to free memory"""
        if self.model:
            self.logger.info(f"Unloading LLM model: {self.model_name}")
            self.model = None
            self.tokenizer = None
            self.is_loaded = False
    
    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded"""
        return self.is_loaded and self.model is not None
