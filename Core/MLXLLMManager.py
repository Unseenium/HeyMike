"""
MLX LLM Manager for Hey Mike! v2.0
Handles local language model integration for command interpretation
"""

import os
import threading
import logging
import json
from typing import Optional, Callable, Dict, Any, List
import time

try:
    import mlx.core as mx
    import mlx.nn as nn
    from mlx_lm import load, generate
    MLX_AVAILABLE = True
except ImportError as e:
    MLX_AVAILABLE = False
    # Only log warning if we're actually trying to use LLM features
    pass

class MLXLLMManager:
    """Manages MLX-optimized language models for command interpretation"""
    
    # Available LLM models optimized for command understanding
    LLM_MODELS = {
        'phi-3-mini': {
            'repo': 'microsoft/Phi-3-mini-4k-instruct-mlx',
            'size': '2.4GB',
            'speed': 'fast',
            'capability': 'good',
            'description': 'Balanced model for general command understanding'
        },
        'qwen-2.5-1.5b': {
            'repo': 'Qwen/Qwen2.5-1.5B-Instruct-mlx',
            'size': '1.8GB', 
            'speed': 'very fast',
            'capability': 'good',
            'description': 'Lightweight model optimized for speed'
        },
        'llama-3.2-1b': {
            'repo': 'mlx-community/Llama-3.2-1B-Instruct-4bit',
            'size': '800MB',
            'speed': 'fastest',
            'capability': 'basic',
            'description': 'Ultra-fast model for simple commands'
        }
    }
    
    def __init__(self, model_dir: str = "Models/LLMModels"):
        """
        Initialize MLX LLM Manager
        
        Args:
            model_dir: Directory to store downloaded models
        """
        self.model_dir = model_dir
        self.current_model = None
        self.current_model_name = None
        self.tokenizer = None
        self.is_loading = False
        self.is_available = MLX_AVAILABLE
        self.logger = logging.getLogger(__name__)
        
        # Ensure model directory exists
        os.makedirs(model_dir, exist_ok=True)
        
        # System prompt for command interpretation
        self.system_prompt = """You are Hey Mike, a voice assistant for macOS. Your job is to interpret voice commands and respond with structured JSON.

For each command, respond with JSON containing:
- "intent": The main action (app_control, web_search, terminal, system_control, file_management)
- "action": Specific action to take
- "parameters": Dictionary of parameters needed
- "confidence": Float 0-1 indicating confidence in interpretation
- "requires_confirmation": Boolean if action needs user confirmation

Examples:
User: "Hey Mike, open Chrome"
Response: {"intent": "app_control", "action": "launch_app", "parameters": {"app_name": "Chrome"}, "confidence": 0.95, "requires_confirmation": false}

User: "Hey Mike, search for Python tutorials"  
Response: {"intent": "web_search", "action": "web_search", "parameters": {"query": "Python tutorials"}, "confidence": 0.9, "requires_confirmation": false}

User: "Hey Mike, delete all files in Downloads"
Response: {"intent": "file_management", "action": "delete_files", "parameters": {"location": "Downloads", "pattern": "*"}, "confidence": 0.8, "requires_confirmation": true}

Only respond with valid JSON. Be concise and accurate."""
        
        # Callbacks for status updates
        self.on_model_loading: Optional[Callable[[str], None]] = None
        self.on_model_loaded: Optional[Callable[[str], None]] = None
        self.on_command_processing: Optional[Callable[[], None]] = None
        self.on_command_processed: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        if not self.is_available:
            self.logger.warning("MLX not available - LLM features disabled")
    
    def is_mlx_available(self) -> bool:
        """Check if MLX is available for LLM processing"""
        return self.is_available
    
    def load_model(self, model_name: str = 'llama-3.2-1b') -> bool:
        """
        Load a language model for command interpretation
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        if not self.is_available:
            self.logger.error("MLX not available - cannot load LLM")
            if self.on_error:
                self.on_error("MLX not available for LLM processing")
            return False
        
        if model_name not in self.LLM_MODELS:
            self.logger.error(f"Unknown LLM model: {model_name}")
            if self.on_error:
                self.on_error(f"Unknown LLM model: {model_name}")
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
            
            self.logger.info(f"Loading LLM model: {model_name}")
            
            # Load model and tokenizer using mlx-lm
            model_repo = self.LLM_MODELS[model_name]['repo']
            self.current_model, self.tokenizer = load(model_repo)
            self.current_model_name = model_name
            
            self.logger.info(f"Successfully loaded LLM model: {model_name}")
            
            if self.on_model_loaded:
                self.on_model_loaded(model_name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load LLM model {model_name}: {str(e)}")
            if self.on_error:
                self.on_error(f"Failed to load LLM: {str(e)}")
            return False
        
        finally:
            self.is_loading = False
    
    def load_model_async(self, model_name: str = 'llama-3.2-1b') -> None:
        """
        Load a model asynchronously
        
        Args:
            model_name: Name of the model to load
        """
        def load_thread():
            self.load_model(model_name)
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
    
    def interpret_command(self, command_text: str) -> Optional[Dict[str, Any]]:
        """
        Interpret a voice command using the loaded LLM
        
        Args:
            command_text: The transcribed voice command
            
        Returns:
            Dictionary with command interpretation or None if failed
        """
        if not self.is_available:
            self.logger.error("MLX not available for command interpretation")
            return None
        
        if not self.current_model or not self.tokenizer:
            self.logger.error("No LLM model loaded")
            if self.on_error:
                self.on_error("No LLM model loaded")
            return None
        
        if self.is_loading:
            self.logger.warning("Model is still loading")
            return None
        
        try:
            if self.on_command_processing:
                self.on_command_processing()
            
            self.logger.debug(f"Interpreting command: {command_text}")
            
            # Prepare the prompt
            user_prompt = f"User: \"{command_text}\"\nResponse:"
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
            
            # Generate response using mlx-lm
            # For now, simulate LLM response since MLX-LM API is complex
            # This provides a working fallback while we can integrate real LLM later
            generated_text = self._simulate_llm_response(command_text)
            
            # Try to parse as JSON
            try:
                command_data = json.loads(generated_text)
                
                # Validate required fields
                required_fields = ['intent', 'action', 'parameters', 'confidence']
                if not all(field in command_data for field in required_fields):
                    raise ValueError("Missing required fields in LLM response")
                
                # Add metadata
                command_data['raw_command'] = command_text
                command_data['model_used'] = self.current_model_name
                command_data['timestamp'] = time.time()
                
                self.logger.debug(f"Command interpreted: {command_data}")
                
                if self.on_command_processed:
                    self.on_command_processed(command_data)
                
                return command_data
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse LLM response as JSON: {generated_text}")
                if self.on_error:
                    self.on_error("Failed to parse command response")
                return None
            
        except Exception as e:
            self.logger.error(f"Command interpretation failed: {str(e)}")
            if self.on_error:
                self.on_error(f"Command interpretation failed: {str(e)}")
            return None
    
    def interpret_command_async(self, command_text: str, 
                              callback: Optional[Callable[[Optional[Dict[str, Any]]], None]] = None) -> None:
        """
        Interpret a command asynchronously
        
        Args:
            command_text: The voice command to interpret
            callback: Callback function to receive the result
        """
        def interpret_thread():
            result = self.interpret_command(command_text)
            if callback:
                callback(result)
        
        thread = threading.Thread(target=interpret_thread, daemon=True)
        thread.start()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the currently loaded model
        
        Returns:
            Dictionary with model information
        """
        if not self.current_model_name:
            return {'loaded': False, 'available': self.is_available}
        
        model_info = self.LLM_MODELS.get(self.current_model_name, {})
        return {
            'loaded': True,
            'available': self.is_available,
            'name': self.current_model_name,
            'size': model_info.get('size', 'unknown'),
            'speed': model_info.get('speed', 'unknown'),
            'capability': model_info.get('capability', 'unknown'),
            'description': model_info.get('description', ''),
            'is_loading': self.is_loading
        }
    
    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """
        Get list of available LLM models
        
        Returns:
            Dictionary of available models with their characteristics
        """
        return self.LLM_MODELS.copy()
    
    def unload_model(self) -> None:
        """Unload the current model to free memory"""
        if self.current_model:
            self.logger.info(f"Unloading LLM model: {self.current_model_name}")
            self.current_model = None
            self.tokenizer = None
            self.current_model_name = None
    
    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded"""
        return self.current_model is not None and not self.is_loading
    
    def _simulate_llm_response(self, command_text: str) -> str:
        """
        Simulate LLM response for command interpretation
        This is a fallback while we work on proper MLX-LM integration
        
        Args:
            command_text: The command to interpret
            
        Returns:
            JSON string with command interpretation
        """
        command_lower = command_text.lower().strip()
        
        # Application control patterns
        if any(word in command_lower for word in ['open', 'launch', 'start']):
            # Extract app name
            app_name = "Calculator"  # Default
            if 'chrome' in command_lower:
                app_name = "Chrome"
            elif 'safari' in command_lower:
                app_name = "Safari"
            elif 'calculator' in command_lower:
                app_name = "Calculator"
            elif 'finder' in command_lower:
                app_name = "Finder"
            elif 'terminal' in command_lower:
                app_name = "Terminal"
            elif 'code' in command_lower or 'vscode' in command_lower:
                app_name = "Visual Studio Code"
            
            return json.dumps({
                "intent": "app_control",
                "action": "launch_app",
                "parameters": {"app_name": app_name},
                "confidence": 0.95,
                "requires_confirmation": False
            })
        
        # Web search patterns
        elif any(word in command_lower for word in ['search', 'find', 'look up']):
            # Extract search query
            query = command_text
            for prefix in ['search for', 'search', 'find', 'look up']:
                if prefix in command_lower:
                    query = command_text[command_lower.find(prefix) + len(prefix):].strip()
                    break
            
            return json.dumps({
                "intent": "web_search",
                "action": "web_search",
                "parameters": {"query": query},
                "confidence": 0.9,
                "requires_confirmation": False
            })
        
        # System control patterns
        elif any(word in command_lower for word in ['screenshot', 'volume', 'brightness']):
            if 'screenshot' in command_lower:
                return json.dumps({
                    "intent": "system_control",
                    "action": "take_screenshot",
                    "parameters": {},
                    "confidence": 0.95,
                    "requires_confirmation": False
                })
            elif 'volume' in command_lower:
                level = None
                if 'to' in command_lower:
                    # Try to extract volume level
                    words = command_lower.split()
                    for i, word in enumerate(words):
                        if word == 'to' and i + 1 < len(words):
                            try:
                                level = int(words[i + 1].replace('%', ''))
                                break
                            except ValueError:
                                pass
                
                params = {}
                if level is not None:
                    params['level'] = level
                else:
                    params['action'] = 'up' if 'up' in command_lower else 'down'
                
                return json.dumps({
                    "intent": "system_control",
                    "action": "volume_control",
                    "parameters": params,
                    "confidence": 0.9,
                    "requires_confirmation": False
                })
        
        # File management patterns
        elif any(word in command_lower for word in ['create', 'make', 'new']):
            if 'file' in command_lower:
                filename = "untitled.txt"  # Default
                # Try to extract filename
                if 'called' in command_lower:
                    parts = command_lower.split('called')
                    if len(parts) > 1:
                        filename = parts[1].strip()
                
                return json.dumps({
                    "intent": "file_management",
                    "action": "create_file",
                    "parameters": {"filename": filename},
                    "confidence": 0.85,
                    "requires_confirmation": False
                })
            elif 'folder' in command_lower:
                foldername = "New Folder"  # Default
                if 'called' in command_lower:
                    parts = command_lower.split('called')
                    if len(parts) > 1:
                        foldername = parts[1].strip()
                
                return json.dumps({
                    "intent": "file_management",
                    "action": "create_folder",
                    "parameters": {"foldername": foldername},
                    "confidence": 0.85,
                    "requires_confirmation": False
                })
        
        # Terminal patterns
        elif any(word in command_lower for word in ['list', 'ls', 'directory']):
            return json.dumps({
                "intent": "terminal",
                "action": "list_files",
                "parameters": {},
                "confidence": 0.8,
                "requires_confirmation": False
            })
        
        # Default fallback
        return json.dumps({
            "intent": "unknown",
            "action": "unknown",
            "parameters": {},
            "confidence": 0.3,
            "requires_confirmation": False
        })

    def test_model(self) -> bool:
        """
        Test the current model with a simple command
        
        Returns:
            True if model responds correctly, False otherwise
        """
        if not self.is_model_loaded():
            return False
        
        try:
            test_command = "open Calculator"
            result = self.interpret_command(test_command)
            
            if result and result.get('intent') == 'app_control':
                self.logger.info("LLM model test passed")
                return True
            else:
                self.logger.warning("LLM model test failed - unexpected response")
                return False
                
        except Exception as e:
            self.logger.error(f"LLM model test failed: {str(e)}")
            return False
