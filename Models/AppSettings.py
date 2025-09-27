"""
App Settings for Hey Mike!
Handles configuration persistence and management
"""

import os
import json
import logging
from typing import Any, Dict, Optional

class AppSettings:
    """Manages application settings and configuration"""
    
    def __init__(self, settings_file: str = "heymike_settings.json"):
        """
        Initialize App Settings
        
        Args:
            settings_file: Path to settings file
        """
        self.settings_file = os.path.expanduser(f"~/.{settings_file}")
        self.logger = logging.getLogger(__name__)
        
        # Default settings
        self.default_settings = {
            # v1.0 settings
            'model': 'tiny',
            'language': None,  # Auto-detect
            'hotkey': 'cmd+shift+space',
            'audio_device': None,  # Default device
            'max_recording_duration': 30.0,
            'silence_duration': 2.0,
            'silence_threshold': 500,
            'insertion_method': 'auto',
            'add_space_after': True,
            'add_space_before': False,
            'audio_feedback': True,
            'notifications': True,
            'first_run': True,
            
            # v2.0 settings - Voice Commands
            'command_mode_enabled': True,
            'llm_model': 'llama-3.2-1b',
            'wake_word_confidence': 0.7,
            'command_confirmation_required': True,
            'restricted_commands_enabled': False,
            'always_listening': False,
            'command_timeout': 30.0,
            
            # v2.0 permissions
            'terminal_access': True,
            'file_deletions': True,
            'system_modifications': False,
            'network_access': True,
        }
        
        # Current settings
        self.settings = self.default_settings.copy()
    
    def load_settings(self) -> bool:
        """
        Load settings from file
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults (in case new settings were added)
                self.settings = self.default_settings.copy()
                self.settings.update(loaded_settings)
                
                self.logger.info(f"Settings loaded from {self.settings_file}")
                return True
            else:
                self.logger.info("No settings file found, using defaults")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load settings: {str(e)}")
            self.settings = self.default_settings.copy()
            return False
    
    def save_settings(self) -> bool:
        """
        Save settings to file
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            self.logger.info(f"Settings saved to {self.settings_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save settings: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        self.logger.debug(f"Setting {key} = {value}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings
        
        Returns:
            Dictionary of all settings
        """
        return self.settings.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        self.logger.info("Settings reset to defaults")
    
    def export_settings(self, file_path: str) -> bool:
        """
        Export settings to a file
        
        Args:
            file_path: Path to export file
            
        Returns:
            True if exported successfully, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            self.logger.info(f"Settings exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export settings: {str(e)}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """
        Import settings from a file
        
        Args:
            file_path: Path to import file
            
        Returns:
            True if imported successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                imported_settings = json.load(f)
            
            # Validate and merge settings
            for key, value in imported_settings.items():
                if key in self.default_settings:
                    self.settings[key] = value
            
            self.logger.info(f"Settings imported from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import settings: {str(e)}")
            return False
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first run
        
        Returns:
            True if first run, False otherwise
        """
        return self.get('first_run', True)
    
    def mark_first_run_complete(self) -> None:
        """Mark first run as complete"""
        self.set('first_run', False)
        self.save_settings()
    
    def get_model_settings(self) -> Dict[str, Any]:
        """
        Get model-related settings
        
        Returns:
            Dictionary of model settings
        """
        return {
            'model': self.get('model'),
            'language': self.get('language')
        }
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """
        Get audio-related settings
        
        Returns:
            Dictionary of audio settings
        """
        return {
            'audio_device': self.get('audio_device'),
            'max_recording_duration': self.get('max_recording_duration'),
            'silence_duration': self.get('silence_duration'),
            'silence_threshold': self.get('silence_threshold'),
            'audio_feedback': self.get('audio_feedback')
        }
    
    def get_hotkey_settings(self) -> Dict[str, Any]:
        """
        Get hotkey-related settings
        
        Returns:
            Dictionary of hotkey settings
        """
        return {
            'hotkey': self.get('hotkey')
        }
    
    def get_text_settings(self) -> Dict[str, Any]:
        """
        Get text insertion-related settings
        
        Returns:
            Dictionary of text settings
        """
        return {
            'insertion_method': self.get('insertion_method'),
            'add_space_after': self.get('add_space_after'),
            'add_space_before': self.get('add_space_before')
        }
    
    def validate_settings(self) -> bool:
        """
        Validate current settings
        
        Returns:
            True if all settings are valid, False otherwise
        """
        try:
            # Validate model
            valid_models = ['tiny', 'base', 'small', 'medium', 'large']
            if self.get('model') not in valid_models:
                self.logger.warning(f"Invalid model: {self.get('model')}")
                return False
            
            # Validate numeric settings
            numeric_settings = ['max_recording_duration', 'silence_duration', 'silence_threshold']
            for setting in numeric_settings:
                value = self.get(setting)
                if not isinstance(value, (int, float)) or value <= 0:
                    self.logger.warning(f"Invalid {setting}: {value}")
                    return False
            
            # Validate boolean settings
            boolean_settings = ['add_space_after', 'add_space_before', 'audio_feedback', 'notifications']
            for setting in boolean_settings:
                value = self.get(setting)
                if not isinstance(value, bool):
                    self.logger.warning(f"Invalid {setting}: {value}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Settings validation failed: {str(e)}")
            return False

