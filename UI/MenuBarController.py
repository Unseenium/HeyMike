"""
Menu Bar Controller for Hey Mike!
Handles the rumps-based menu bar interface and user interactions
"""

import rumps
import logging
import threading
from typing import Optional, Dict, Any
import os
import sys

# Add Core directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Core'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Models'))

from MLXWhisperManager import MLXWhisperManager
from AudioManager import AudioManager
from HotkeyManager import HotkeyManager
from TextInsertionManager import TextInsertionManager
from AppSettings import AppSettings

# v2.0 imports
from MLXLLMManager import MLXLLMManager
from WakeWordDetector import WakeWordDetector
from CommandProcessor import CommandProcessor
from ActionExecutor import ActionExecutor
from Security.CommandValidator import CommandValidator

class HeyMikeApp(rumps.App):
    """Main Hey Mike! application with menu bar interface"""
    
    def __init__(self):
        """Initialize Hey Mike! application"""
        # Check for icon file in multiple possible locations
        icon_path = None
        possible_icon_paths = [
            "assets/icon.png",
            "Assets/icon.png", 
            "icon.png"
        ]
        
        for path in possible_icon_paths:
            if os.path.exists(path):
                icon_path = path
                break
        
        super(HeyMikeApp, self).__init__(
            "Hey Mike!",
            icon=icon_path,  # Will be None if no icon found
            title="🎤",
            quit_button=None  # We'll add our own quit button
        )
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize v1.0 managers
        self.whisper_manager = MLXWhisperManager()
        self.audio_manager = AudioManager()
        self.hotkey_manager = HotkeyManager()
        self.text_manager = TextInsertionManager()
        self.settings = AppSettings()
        
        # Initialize v2.0 managers
        self.llm_manager = MLXLLMManager()
        self.wake_word_detector = WakeWordDetector()
        self.command_processor = CommandProcessor()
        self.action_executor = ActionExecutor()
        self.command_validator = CommandValidator()
        
        # Application state
        self.is_recording = False
        self.is_processing = False
        self.current_model = 'tiny'  # Default, will be updated from settings
        
        # v2.0 state
        self.command_mode_enabled = True
        self.current_llm_model = 'llama-3.2-1b'
        self.is_command_mode = False  # Current mode: False=dictation, True=command
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Load settings first to get the correct current model
        self._load_settings_early()
        
        # Initialize menu with correct model
        self._setup_menu()
        
        # Complete initialization
        self._initialize_app()
    
    def _setup_callbacks(self):
        """Setup callbacks between managers"""
        
        # Hotkey callbacks
        self.hotkey_manager.on_record_toggle = self._toggle_recording
        self.hotkey_manager.on_cancel_recording = self._cancel_recording
        
        # Audio callbacks
        self.audio_manager.on_recording_start = self._on_recording_started
        self.audio_manager.on_recording_stop = self._on_recording_stopped
        self.audio_manager.on_audio_level = self._on_audio_level
        
        # Whisper callbacks
        self.whisper_manager.on_model_loading = self._on_model_loading
        self.whisper_manager.on_model_loaded = self._on_model_loaded
        self.whisper_manager.on_predownload_start = self._on_predownload_start
        self.whisper_manager.on_predownload_progress = self._on_predownload_progress
        self.whisper_manager.on_predownload_complete = self._on_predownload_complete
        self.whisper_manager.on_transcription_start = self._on_transcription_start
        self.whisper_manager.on_transcription_complete = self._on_transcription_complete
        
        # v2.0 LLM callbacks
        self.llm_manager.on_model_loading = self._on_llm_model_loading
        self.llm_manager.on_model_loaded = self._on_llm_model_loaded
        self.llm_manager.on_command_processing = self._on_command_processing
        self.llm_manager.on_command_processed = self._on_command_processed
        
        # v2.0 Wake word callbacks
        self.wake_word_detector.on_wake_word_detected = self._on_wake_word_detected
        
        # v2.0 Command execution callbacks
        self.action_executor.on_execution_started = self._on_execution_started
        self.action_executor.on_execution_completed = self._on_execution_completed
        self.action_executor.on_execution_failed = self._on_execution_failed
        self.action_executor.on_confirmation_required = self._on_confirmation_required
        
        # Error callbacks (v1.0 + v2.0)
        self.audio_manager.on_error = self._on_error
        self.whisper_manager.on_error = self._on_error
        self.hotkey_manager.on_error = self._on_error
        self.text_manager.on_error = self._on_error
        self.llm_manager.on_error = self._on_error
    
    def _load_settings_early(self):
        """Load settings early to get current model before menu setup"""
        try:
            self.settings.load_settings()
            self.current_model = self.settings.get('model', 'tiny')
            
            # Load v2.0 settings
            self.command_mode_enabled = self.settings.get('command_mode_enabled', True)
            self.current_llm_model = self.settings.get('llm_model', 'llama-3.2-1b')
            
            # Configure wake word detector
            confidence_threshold = self.settings.get('wake_word_confidence', 0.7)
            self.wake_word_detector.set_confidence_threshold(confidence_threshold)
            
            # Configure command validator permissions
            self.command_validator.set_user_permission('restricted_commands', 
                                                     self.settings.get('restricted_commands_enabled', False))
            self.command_validator.set_user_permission('terminal_access', 
                                                     self.settings.get('terminal_access', True))
            self.command_validator.set_user_permission('file_deletions', 
                                                     self.settings.get('file_deletions', True))
            self.command_validator.set_user_permission('system_modifications', 
                                                     self.settings.get('system_modifications', False))
            
            self.logger.debug(f"Loaded settings - Whisper: {self.current_model}, LLM: {self.current_llm_model}, Commands: {self.command_mode_enabled}")
        except Exception as e:
            self.logger.warning(f"Could not load settings early: {str(e)}")
            self.current_model = 'tiny'  # Fallback
            self.current_llm_model = 'llama-3.2-1b'  # Fallback
    
    def _setup_menu(self):
        """Setup the menu bar menu"""
        
        # Status section with better formatting
        mode_indicator = "🧠" if self.command_mode_enabled else "🎤"
        mode_text = "Command Mode" if self.command_mode_enabled else "Dictation Mode"
        self.status_item = rumps.MenuItem(f"{mode_indicator} Ready - {mode_text}", callback=None)
        self.menu.add(self.status_item)
        self.menu.add(rumps.separator)
        
        # Mode toggle (v2.0)
        if self.command_mode_enabled:
            self.mode_toggle_item = rumps.MenuItem("🎤 Switch to Dictation Only", callback=self._toggle_command_mode)
        else:
            self.mode_toggle_item = rumps.MenuItem("🧠 Enable Voice Commands", callback=self._toggle_command_mode)
        self.menu.add(self.mode_toggle_item)
        
        # Quick actions section
        self.record_item = rumps.MenuItem("🔴 Start Recording", callback=self._menu_toggle_recording)
        self.menu.add(self.record_item)
        
        # Current model display
        current_model_info = self.whisper_manager.get_available_models().get(self.current_model, {})
        model_display = f"📊 Current: {self.current_model.title()} ({current_model_info.get('size', 'unknown')})"
        self.current_model_item = rumps.MenuItem(model_display, callback=None)
        self.menu.add(self.current_model_item)
        
        self.menu.add(rumps.separator)
        
        # Model management section
        self.model_menu = rumps.MenuItem("🧠 Models")
        
        # Individual model items with better formatting
        self.model_items_map = {}  # Store references for updates
        
        for model_name, info in self.whisper_manager.get_available_models().items():
            icon = "✅" if model_name == self.current_model else "⚪"
            
            # Create callback function with proper closure
            def make_model_callback(model):
                def callback(sender):
                    self.logger.info(f"Model menu item clicked: {model}")
                    self._select_model(model)
                return callback
            
            model_item = rumps.MenuItem(
                f"{icon} {model_name.title()} - {info['size']} ({info['accuracy']})",
                callback=make_model_callback(model_name)
            )
            
            # Add to menu first, then store reference
            self.model_menu.add(model_item)
            self.model_items_map[model_name] = model_item
            
            self.logger.debug(f"Created menu item for {model_name}: {model_item}")
        
        self.model_menu.add(rumps.separator)
        self.predownload_item = rumps.MenuItem("⬇️ Download All Models", callback=self._start_predownload)
        self.model_menu.add(self.predownload_item)
        
        self.menu.add(self.model_menu)
        
        # v2.0 LLM Models menu
        if self.command_mode_enabled:
            self.llm_menu = rumps.MenuItem("🧠 LLM Models")
            
            # Current LLM model display
            current_llm_info = self.llm_manager.get_available_models().get(self.current_llm_model, {})
            llm_display = f"📊 Current: {self.current_llm_model.title()} ({current_llm_info.get('size', 'unknown')})"
            self.current_llm_item = rumps.MenuItem(llm_display, callback=None)
            self.llm_menu.add(self.current_llm_item)
            self.llm_menu.add(rumps.separator)
            
            # Individual LLM model items
            self.llm_items_map = {}
            for model_name, info in self.llm_manager.get_available_models().items():
                icon = "✅" if model_name == self.current_llm_model else "⚪"
                
                def make_llm_callback(model):
                    def callback(sender):
                        self._select_llm_model(model)
                    return callback
                
                llm_item = rumps.MenuItem(
                    f"{icon} {model_name.title()} - {info['size']} ({info['capability']})",
                    callback=make_llm_callback(model_name)
                )
                
                self.llm_menu.add(llm_item)
                self.llm_items_map[model_name] = llm_item
            
            self.menu.add(self.llm_menu)
        
        self.menu.add(rumps.separator)
        
        # Settings section with icons
        self.settings_menu = rumps.MenuItem("⚙️ Settings")
        
        hotkey_display = self.hotkey_manager.get_record_hotkey_string()
        hotkey_item = rumps.MenuItem(f"⌨️ Hotkey: {hotkey_display}", callback=self._show_hotkey_settings)
        self.settings_menu.add(hotkey_item)
        
        audio_item = rumps.MenuItem("🎙️ Audio Device", callback=self._show_audio_settings)
        self.settings_menu.add(audio_item)
        
        language_item = rumps.MenuItem("🌍 Language", callback=self._show_language_settings)
        self.settings_menu.add(language_item)
        
        self.settings_menu.add(rumps.separator)
        permissions_item = rumps.MenuItem("🔐 Check Permissions", callback=self._check_permissions_detailed)
        self.settings_menu.add(permissions_item)
        
        self.menu.add(self.settings_menu)
        self.menu.add(rumps.separator)
        
        # Help and info section
        help_menu = rumps.MenuItem("❓ Help")
        
        test_item = rumps.MenuItem("🧪 Test Text Insertion", callback=self._test_text_insertion)
        help_menu.add(test_item)
        
        about_item = rumps.MenuItem("ℹ️ About Hey Mike!", callback=self._show_about)
        help_menu.add(about_item)
        
        help_menu.add(rumps.separator)
        logs_item = rumps.MenuItem("📋 View Recent Logs", callback=self._show_logs)
        help_menu.add(logs_item)
        
        self.menu.add(help_menu)
        self.menu.add(rumps.separator)
        
        # Quit with icon
        quit_item = rumps.MenuItem("❌ Quit Hey Mike!", callback=self._quit_app)
        self.menu.add(quit_item)
    
    def _initialize_app(self):
        """Initialize the application"""
        try:
            # Settings already loaded in _load_settings_early()
            self.logger.debug(f"Initializing app with model: {self.current_model}")
            
            # Check permissions and show warnings
            self._check_permissions()
            
            # Start hotkey listener
            self.hotkey_manager.start_listening()
            
            # Load initial Whisper model asynchronously
            self.whisper_manager.load_model_async(self.current_model)
            
            # Load LLM model if command mode is enabled
            if self.command_mode_enabled:
                self.llm_manager.load_model_async(self.current_llm_model)
                
                # Load action modules
                self.action_executor.load_action_modules()
            
            # Menu already created with correct model selected - no need to update during init
            self.logger.debug(f"Menu created with current model: {self.current_model}")
            
            # Update current model display
            if hasattr(self, 'current_model_item'):
                current_model_info = self.whisper_manager.get_available_models().get(self.current_model, {})
                model_display = f"📊 Current: {self.current_model.title()} ({current_model_info.get('size', 'unknown')})"
                self.current_model_item.title = model_display
            
            # Disable automatic pre-download for now to prevent crashes
            # User can manually trigger via menu: Models -> Download All Models
            self.logger.info("Automatic pre-download disabled - use menu to download models manually")
            
            self.logger.info("Hey Mike! initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize app: {str(e)}")
            self._show_error_dialog(f"Initialization failed: {str(e)}")
    
    def _check_permissions(self):
        """Check and warn about missing permissions"""
        # Check accessibility permissions
        if not self.text_manager._check_accessibility_permissions():
            self._show_notification(
                "Permissions Required", 
                "Please grant Accessibility permissions in System Preferences → Security & Privacy → Privacy → Accessibility"
            )
        
        # Check if we can detect audio devices
        devices = self.audio_manager.get_input_devices()
        if not devices:
            self._show_notification(
                "Audio Issue", 
                "No audio input devices found. Please check microphone permissions."
            )
    
    def _toggle_recording(self):
        """Toggle recording state"""
        self.logger.info(f"Hotkey pressed! Current state - Recording: {self.is_recording}, Processing: {self.is_processing}")
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()
    
    def _start_recording(self):
        """Start audio recording"""
        if self.is_recording or self.is_processing:
            self.logger.info("Already recording or processing, ignoring start request")
            return
        
        if not self.whisper_manager.is_model_loaded():
            self.logger.warning("Model not loaded yet")
            self._show_notification("Model Loading", "Please wait for model to load")
            return
        
        if not self.text_manager.check_text_field_available():
            self.logger.warning("No text field available")
            self._show_notification("No Text Field", "Please click in a text field first")
            return
        
        self.logger.info("Starting audio recording...")
        success = self.audio_manager.start_recording()
        if success:
            self.is_recording = True
            self.hotkey_manager.set_recording_state(True)
            self._update_status("Recording...")
            self._update_menu_icon("🔴")
            self.record_item.title = "⏹️ Stop Recording"
            self._show_notification("Recording Started", "Speak now... Press hotkey again to stop")
            self.logger.info("Recording started successfully")
        else:
            self.logger.error("Failed to start recording")
            self._show_notification("Recording Failed", "Could not start audio recording")
    
    def _stop_recording(self):
        """Stop audio recording and process"""
        if not self.is_recording:
            return
        
        audio_data = self.audio_manager.stop_recording()
        self.is_recording = False
        self.hotkey_manager.set_recording_state(False)
        
        if audio_data is not None and len(audio_data) > 0:
            self._process_audio(audio_data)
        else:
            self._update_status("Ready")
            self._update_menu_icon("🎤")
            self.record_item.title = "🔴 Start Recording"
    
    def _cancel_recording(self):
        """Cancel current recording"""
        if self.is_recording:
            self.audio_manager.stop_recording()
            self.is_recording = False
            self.hotkey_manager.set_recording_state(False)
            self._update_status("Cancelled")
            self._update_menu_icon("🎤")
            self.record_item.title = "Start Recording"
    
    def _process_audio(self, audio_data):
        """Process recorded audio through Whisper and handle both dictation and command modes"""
        self.is_processing = True
        self._update_status("Processing...")
        self._update_menu_icon("⏳")
        
        # Get language preference
        language = self.settings.get('language', None)
        
        # Process asynchronously
        def process_callback(transcribed_text):
            self.is_processing = False
            self._update_menu_icon("🎤")
            self.record_item.title = "🔴 Start Recording"
            
            if transcribed_text:
                self.logger.info(f"Transcribed: {transcribed_text}")
                
                # Check if command mode is enabled and if this looks like a command
                if self.command_mode_enabled and self.wake_word_detector.is_command_mode_text(transcribed_text):
                    self._handle_voice_command(transcribed_text)
                else:
                    self._handle_dictation(transcribed_text)
            else:
                self._update_status("Transcription failed")
                self._show_notification("Error", "Transcription failed")
        
        self.whisper_manager.transcribe_audio_async(audio_data, language, process_callback)
    
    def _handle_dictation(self, text: str):
        """Handle dictation mode - insert text directly"""
        success = self.text_manager.insert_text(text)
        if success:
            self._update_status(f"Inserted: {text[:30]}...")
            self._show_notification("Text Inserted", text[:50] + ("..." if len(text) > 50 else ""))
        else:
            self._update_status("Insertion failed")
            self._show_notification("Error", "Failed to insert text")
    
    def _handle_voice_command(self, text: str):
        """Handle command mode - process voice command"""
        self.is_command_mode = True
        self._update_status("Processing command...")
        self._update_menu_icon("🧠")
        
        # Extract command from wake word text
        command_text = self.wake_word_detector.extract_command_from_text(text)
        
        if not command_text:
            self._update_status("No command found")
            self._show_notification("Command Error", "No command found after wake word")
            self.is_command_mode = False
            return
        
        self.logger.info(f"Processing voice command: {command_text}")
        
        # Process command asynchronously
        def command_callback(command_data):
            if command_data:
                self._execute_voice_command(command_data)
            else:
                self._update_status("Command interpretation failed")
                self._show_notification("Command Error", "Could not understand command")
                self.is_command_mode = False
        
        self.llm_manager.interpret_command_async(command_text, command_callback)
    
    def _execute_voice_command(self, command_data: dict):
        """Execute a processed voice command"""
        try:
            # Validate command
            validation_result, validation_message = self.command_validator.validate_command(command_data)
            
            from Security.CommandValidator import ValidationResult
            
            if validation_result == ValidationResult.REJECTED:
                self._update_status("Command rejected")
                self._show_notification("Command Rejected", validation_message)
                self.is_command_mode = False
                return
            
            elif validation_result == ValidationResult.REQUIRES_CONFIRMATION:
                # Show confirmation dialog
                response = rumps.alert(
                    title="Confirm Command",
                    message=f"Execute this command?\n\n{command_data.get('description', 'Unknown command')}\n\nReason: {validation_message}",
                    ok="✅ Execute",
                    cancel="❌ Cancel"
                )
                
                if response != 1:  # User cancelled
                    self._update_status("Command cancelled")
                    self._show_notification("Command Cancelled", "User cancelled command execution")
                    self.is_command_mode = False
                    return
            
            # Process command
            processed_command = self.command_processor.process_command(command_data)
            
            if not processed_command:
                self._update_status("Command processing failed")
                self._show_notification("Command Error", "Failed to process command")
                self.is_command_mode = False
                return
            
            # Execute command
            execution_id = self.action_executor.execute_command(processed_command)
            
            if execution_id:
                self._update_status(f"Executing: {processed_command.get('description', 'command')}")
                self._show_notification("Executing Command", processed_command.get('description', 'Unknown command'))
            else:
                self._update_status("Command execution failed")
                self._show_notification("Command Error", "Failed to execute command")
                self.is_command_mode = False
        
        except Exception as e:
            self.logger.error(f"Voice command execution error: {str(e)}")
            self._update_status("Command error")
            self._show_notification("Command Error", f"Error: {str(e)}")
            self.is_command_mode = False
    
    def _select_model(self, model_name: str):
        """Select a different Whisper model"""
        self.logger.info(f"_select_model called with: {model_name}, current: {self.current_model}")
        
        if model_name == self.current_model:
            self.logger.info(f"Model {model_name} is already selected, skipping")
            return
        
        self.logger.info(f"Switching model from {self.current_model} to {model_name}")
        
        # Update current model
        old_model = self.current_model
        self.current_model = model_name
        self.settings.set('model', model_name)
        self.settings.save_settings()
        
        # Update menu visuals
        self._update_model_menu_display()
        
        # Update current model display
        current_model_info = self.whisper_manager.get_available_models().get(model_name, {})
        model_display = f"📊 Current: {model_name.title()} ({current_model_info.get('size', 'unknown')})"
        if hasattr(self, 'current_model_item'):
            self.current_model_item.title = model_display
            self.logger.info(f"Updated current model display to: {model_display}")
        
        # Load new model
        self.whisper_manager.load_model_async(model_name)
        
        # Show notification
        self._show_notification("Model Changed", f"Switched to {model_name.title()} model")
    
    def _update_model_menu_display(self):
        """Update the visual display of model menu items"""
        try:
            self.logger.debug(f"Updating model menu display, current model: {self.current_model}")
            
            # Check if model items map exists and is populated
            if not hasattr(self, 'model_items_map') or not self.model_items_map:
                self.logger.debug("Model items map not ready - skipping update")
                return
            
            # Update each model item's title to reflect current selection
            updated_count = 0
            for model_name, menu_item in self.model_items_map.items():
                try:
                    if menu_item and hasattr(menu_item, 'title') and isinstance(menu_item.title, str):
                        icon = "✅" if model_name == self.current_model else "⚪"
                        model_info = self.whisper_manager.get_available_models().get(model_name, {})
                        new_title = f"{icon} {model_name.title()} - {model_info.get('size', 'unknown')} ({model_info.get('accuracy', 'unknown')})"
                        menu_item.title = new_title
                        updated_count += 1
                        self.logger.debug(f"Updated {model_name} menu item")
                    else:
                        self.logger.debug(f"Skipping {model_name} - menu item not ready")
                except Exception as item_error:
                    self.logger.debug(f"Could not update {model_name}: {item_error}")
                    continue
                
            self.logger.debug(f"Updated {updated_count}/{len(self.model_items_map)} model menu items")
            
        except Exception as e:
            self.logger.debug(f"Model menu update skipped: {e}")
            # Don't log as error during initialization - this is expected
    
    def _start_predownload(self, sender):
        """Start pre-downloading all models"""
        self.logger.info("Pre-download menu item clicked")
        if self.whisper_manager.is_predownloading:
            self._show_notification("Already Downloading", "Models are already being downloaded")
            return
        
        # Start the pre-download process
        self.whisper_manager.predownload_all_models()
    
    def _check_permissions_detailed(self, sender):
        """Show detailed permission status"""
        try:
            # Check microphone permission
            mic_status = "✅ Granted" if self.audio_manager.check_microphone_permission() else "❌ Not Granted"
            
            # Check accessibility permission
            acc_status = "✅ Granted" if self.text_manager._check_accessibility_permissions() else "❌ Not Granted"
            
            message = (
                "🔐 Permission Status:\\n\\n"
                f"🎙️ Microphone: {mic_status}\\n"
                f"♿ Accessibility: {acc_status}\\n\\n"
                "Both permissions are required for Hey Mike! to work properly.\\n\\n"
                "To grant permissions:\\n"
                "1. Open System Preferences → Security & Privacy\\n"
                "2. Click Privacy tab\\n"
                "3. Add Terminal to both Microphone and Accessibility"
            )
            
            rumps.alert(
                title="Permission Status",
                message=message
            )
        except Exception as e:
            self.logger.error(f"Error checking permissions: {str(e)}")
            rumps.alert(title="Error", message="Could not check permission status")
    
    def _show_logs(self, sender):
        """Show recent log entries"""
        try:
            # Get recent log entries (this is a simplified version)
            log_info = (
                "📋 Recent Activity:\\n\\n"
                f"🎤 Recording State: {'Active' if self.is_recording else 'Inactive'}\\n"
                f"⚙️ Processing State: {'Active' if self.is_processing else 'Inactive'}\\n"
                f"🧠 Current Model: {self.current_model}\\n"
                f"⬇️ Pre-download Status: {'Active' if self.whisper_manager.is_predownloading else 'Complete'}\\n\\n"
                "For detailed logs, check the terminal output."
            )
            
            rumps.alert(
                title="System Status",
                message=log_info
            )
        except Exception as e:
            self.logger.error(f"Error showing logs: {str(e)}")
            rumps.alert(title="Error", message="Could not retrieve log information")
    
    # Menu callbacks
    def _menu_toggle_recording(self, sender):
        """Menu callback for recording toggle"""
        self._toggle_recording()
    
    def _show_hotkey_settings(self, sender):
        """Show hotkey configuration dialog"""
        self.logger.info("Hotkey settings menu item clicked")
        try:
            current_hotkey = self.hotkey_manager.get_record_hotkey_string()
            message = (
                "⌨️ Hotkey Configuration\\n\\n"
                f"Current hotkey: {current_hotkey}\\n\\n"
                "Enter new hotkey combination:\\n"
                "Examples:\\n"
                "• cmd+shift+space\\n"
                "• ctrl+alt+r\\n"
                "• cmd+option+m\\n\\n"
                "New hotkey:"
            )
            
            response = rumps.Window(
                message=message,
                title="⌨️ Hotkey Settings",
                default_text=current_hotkey,
                ok="✅ Set Hotkey",
                cancel="❌ Cancel"
            ).run()
            
            if response.clicked:
                new_hotkey = HotkeyManager.parse_hotkey_string(response.text)
                if new_hotkey:
                    self.hotkey_manager.set_record_hotkey(new_hotkey)
                    self.settings.set('hotkey', response.text)
                    self.settings.save_settings()
                    self._show_notification("✅ Hotkey Updated", f"New hotkey: {response.text}")
                else:
                    self._show_notification("❌ Invalid Hotkey", "Please use format like 'cmd+shift+space'")
        except Exception as e:
            self.logger.error(f"Error in hotkey settings: {str(e)}")
            self._show_notification("❌ Error", f"Hotkey settings error: {str(e)}")
    
    def _show_audio_settings(self, sender):
        """Show audio configuration dialog"""
        self.logger.info("Audio settings menu item clicked")
        try:
            # Try to get devices, but provide fallback if it fails
            try:
                devices = self.audio_manager.get_input_devices()
                current_device = self.settings.get('audio_device', 'Default')
                
                device_list = []
                for d in devices:
                    marker = "🎙️ " if d['index'] == current_device else "   "
                    device_list.append(f"{marker}{d['index']}: {d['name']}")
                
                device_display = "\\n".join(device_list)
                message = (
                    "🎙️ Audio Device Selection\\n\\n"
                    f"Current: {current_device if current_device != 'Default' else 'System Default'}\\n\\n"
                    f"Available devices:\\n{device_display}\\n\\n"
                    "Enter device number (or leave empty for default):"
                )
            except Exception as device_error:
                self.logger.warning(f"Could not enumerate audio devices: {device_error}")
                message = (
                    "🎙️ Audio Device Selection\\n\\n"
                    "⚠️ Could not list audio devices.\\n\\n"
                    "Enter device index (or leave empty for default):"
                )
            
            response = rumps.Window(
                message=message,
                title="🎙️ Audio Settings",
                default_text="",
                ok="✅ Set Device",
                cancel="❌ Cancel"
            ).run()
            
            if response.clicked:
                try:
                    device_index = int(response.text) if response.text.strip() else None
                    if self.audio_manager.set_input_device(device_index):
                        self.settings.set('audio_device', device_index)
                        self.settings.save_settings()
                        device_name = "System Default" if device_index is None else f"Device {device_index}"
                        self._show_notification("✅ Audio Updated", f"Now using: {device_name}")
                    else:
                        self._show_notification("❌ Error", "Failed to set audio device")
                except ValueError:
                    self._show_notification("❌ Invalid Input", "Please enter a valid device number")
        except Exception as e:
            self.logger.error(f"Error in audio settings: {str(e)}")
            self._show_notification("❌ Error", f"Audio settings error: {str(e)}")
    
    def _show_language_settings(self, sender):
        """Show language configuration dialog"""
        self.logger.info("Language settings menu item clicked")
        try:
            current_lang = self.settings.get('language', 'auto')
            display_lang = current_lang if current_lang else 'auto'
            
            message = (
                "🌍 Language Configuration\\n\\n"
                f"Current: {display_lang}\\n\\n"
                "Popular language codes:\\n"
                "• auto - Automatic detection\\n"
                "• en - English\\n"
                "• es - Spanish\\n"
                "• fr - French\\n"
                "• de - German\\n"
                "• ja - Japanese\\n"
                "• zh - Chinese\\n\\n"
                "Enter language code:"
            )
            
            response = rumps.Window(
                message=message,
                title="🌍 Language Settings",
                default_text=display_lang,
                ok="✅ Set Language",
                cancel="❌ Cancel"
            ).run()
            
            if response.clicked:
                language = response.text.strip().lower()
                if language == 'auto':
                    language = None
                
                self.settings.set('language', language)
                self.settings.save_settings()
                display_text = language if language else 'auto'
                self._show_notification("✅ Language Updated", f"Language: {display_text}")
        except Exception as e:
            self.logger.error(f"Error in language settings: {str(e)}")
            self._show_notification("❌ Error", f"Language settings error: {str(e)}")
    
    def _show_about(self, sender):
        """Show about dialog"""
        self.logger.info("About dialog opened")
        try:
            model_info = self.whisper_manager.get_model_info()
            model_status = f"{model_info['name'].title()}" if model_info['loaded'] else "No model loaded"
            download_status = self.whisper_manager.get_download_status()
            
            # System information
            import sys
            import platform
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            macos_version = platform.mac_ver()[0]
            
            message = (
                "ℹ️ About Hey Mike!\\n\\n"
                "🎤 MLX Whisper Dictation System\\n"
                "Version 1.0.0 (Production Ready)\\n\\n"
                "📊 Current Status:\\n"
                f"• Model: {model_status}\\n"
                f"• Hotkey: {self.hotkey_manager.get_record_hotkey_string()}\\n"
                f"• Downloaded Models: {len(download_status['downloaded_models'])}/5\\n"
                f"• Python: {python_version}\\n"
                f"• macOS: {macos_version}\\n\\n"
                "🔒 Privacy Features:\\n"
                "• 100% offline processing\\n"
                "• No data sent to servers\\n"
                "• Local model storage\\n"
                "• Zero cloud dependencies\\n\\n"
                "⚡ Technology Stack:\\n"
                "• MLX-optimized Whisper models\\n"
                "• Apple Silicon acceleration\\n"
                "• Real-time transcription\\n"
                "• Native macOS integration\\n\\n"
                "© 2025 Unseenium Inc. Enterprise-grade dictation."
            )
            
            rumps.alert(title="About Hey Mike!", message=message)
            self.logger.info("About dialog displayed successfully")
        except Exception as e:
            self.logger.error(f"Error in about dialog: {str(e)}")
            rumps.alert(
                title="About Hey Mike!", 
                message="🎤 Hey Mike!: MLX Whisper Dictation System\\nVersion 1.0.0\\n\\n🔒 Privacy-focused offline speech-to-text"
            )
    
    def _test_text_insertion(self, sender):
        """Test text insertion functionality"""
        self.logger.info("Text insertion test initiated")
        
        try:
            # Test text to insert
            test_text = "🎤 Hey Mike! test - text insertion working!"
            
            # Show instruction to user
            response = rumps.alert(
                title="Text Insertion Test",
                message="This will test text insertion functionality.\\n\\n"
                       "1. Click OK\\n"
                       "2. Click in any text field (TextEdit, Notes, etc.)\\n"
                       "3. The test text will be inserted automatically\\n\\n"
                       "Ready to proceed?",
                ok="✅ Run Test",
                cancel="❌ Cancel"
            )
            
            if response == 1:  # OK clicked
                # Give user time to position cursor
                import threading
                import time
                
                def delayed_insertion():
                    time.sleep(2)  # 2 second delay
                    if self.text_manager.insert_text(test_text):
                        self._show_notification("✅ Test Successful", "Text insertion is working perfectly!")
                        self.logger.info("Text insertion test: SUCCESS")
                    else:
                        self._show_notification("❌ Test Failed", "Text insertion needs attention - check permissions")
                        self.logger.warning("Text insertion test: FAILED")
                
                threading.Thread(target=delayed_insertion, daemon=True).start()
                self._show_notification("Text Insertion Test", "Position cursor in text field... inserting in 2 seconds")
            else:
                self.logger.info("Text insertion test cancelled by user")
                
        except Exception as e:
            self.logger.error(f"Error in text insertion test: {str(e)}")
            self._show_notification("❌ Test Error", f"Test failed: {str(e)}")
    
    def _quit_app(self, sender):
        """Quit the application"""
        self._cleanup()
        rumps.quit_application()
    
    # Status and UI updates
    def _update_status(self, status: str):
        """Update status in menu"""
        # Add appropriate emoji based on status
        if "recording" in status.lower():
            icon = "🔴"
        elif "transcribing" in status.lower():
            icon = "⚙️"
        elif "downloading" in status.lower():
            icon = "⬇️"
        elif "loading" in status.lower():
            icon = "⏳"
        elif "ready" in status.lower():
            icon = "🎤"
        else:
            icon = "📊"
        
        self.status_item.title = f"{icon} {status}"
    
    def _update_menu_icon(self, icon: str):
        """Update menu bar icon"""
        self.title = icon
    
    def _show_notification(self, title: str, message: str):
        """Show system notification"""
        rumps.notification(title, None, message)
    
    def _show_error_dialog(self, message: str):
        """Show error dialog"""
        rumps.alert("Error", message)
    
    # Event callbacks
    def _on_recording_started(self):
        """Called when recording starts"""
        self.logger.debug("Recording started")
    
    def _on_recording_stopped(self, audio_data):
        """Called when recording stops"""
        self.logger.debug(f"Recording stopped, {len(audio_data)} samples")
    
    def _on_audio_level(self, level: float):
        """Called with audio level updates"""
        # Could be used for visual feedback
        pass
    
    def _on_model_loading(self, model_name: str):
        """Called when model starts loading"""
        self._update_status(f"Loading {model_name} model...")
        self._update_menu_icon("⏳")
    
    def _on_model_loaded(self, model_name: str):
        """Called when model finishes loading"""
        self._update_status("Ready")
        self._update_menu_icon("🎤")
        self._show_notification("Model Loaded", f"{model_name.title()} model ready")
    
    def _on_transcription_start(self):
        """Called when transcription starts"""
        self._update_status("Transcribing...")
    
    def _on_transcription_complete(self, text: str):
        """Called when transcription completes"""
        self.logger.info(f"Transcription complete: {text[:50]}...")
    
    def _on_predownload_start(self):
        """Called when pre-download starts"""
        self._update_status("Pre-downloading models...")
        self._update_menu_icon("⬇️")
        self.predownload_item.title = "Downloading Models..."
        self._show_notification("Pre-download Started", "Downloading all Whisper models for instant switching")
    
    def _on_predownload_progress(self, model_name: str, current: int, total: int):
        """Called with pre-download progress updates"""
        self._update_status(f"Downloading {model_name} ({current}/{total})...")
        self.predownload_item.title = f"Downloading {model_name} ({current}/{total})"
    
    def _on_predownload_complete(self):
        """Called when pre-download completes"""
        self._update_status("Ready")
        self._update_menu_icon("🎤")
        self.predownload_item.title = "✅ All Models Downloaded"
        self._show_notification("Pre-download Complete", "All models ready for instant switching!")
    
    def _on_error(self, error_message: str):
        """Called when an error occurs"""
        self.logger.error(f"Error: {error_message}")
        self._show_notification("Error", error_message)
    
    # v2.0 Callback methods
    
    def _on_llm_model_loading(self, model_name: str):
        """Called when LLM model starts loading"""
        self._update_status(f"Loading {model_name} LLM...")
        self._update_menu_icon("⏳")
    
    def _on_llm_model_loaded(self, model_name: str):
        """Called when LLM model finishes loading"""
        self._update_status("Ready")
        self._update_menu_icon("🧠" if self.command_mode_enabled else "🎤")
        self._show_notification("LLM Model Loaded", f"{model_name.title()} model ready for commands")
    
    def _on_command_processing(self):
        """Called when command processing starts"""
        self._update_status("Interpreting command...")
    
    def _on_command_processed(self, command_data: dict):
        """Called when command processing completes"""
        self.logger.info(f"Command processed: {command_data.get('description', 'Unknown')}")
    
    def _on_wake_word_detected(self, text: str, confidence: float, command: str):
        """Called when wake word is detected"""
        self.logger.info(f"Wake word detected (confidence: {confidence:.2f}): {command}")
    
    def _on_execution_started(self, execution_id: str, command_data: dict):
        """Called when command execution starts"""
        self.logger.info(f"Execution started: {execution_id}")
    
    def _on_execution_completed(self, execution_id: str, success: bool, message: str):
        """Called when command execution completes"""
        self.is_command_mode = False
        if success:
            self._update_status("Command completed")
            self._show_notification("Command Completed", message)
        else:
            self._update_status("Command failed")
            self._show_notification("Command Failed", message)
    
    def _on_execution_failed(self, execution_id: str, error_message: str):
        """Called when command execution fails"""
        self.is_command_mode = False
        self._update_status("Command failed")
        self._show_notification("Command Failed", error_message)
    
    def _on_confirmation_required(self, command_data: dict):
        """Called when command requires confirmation"""
        self.logger.info(f"Confirmation required for: {command_data.get('description', 'Unknown command')}")
    
    # v2.0 Menu functions
    
    def _toggle_command_mode(self, sender):
        """Toggle between dictation and command mode"""
        self.command_mode_enabled = not self.command_mode_enabled
        self.settings.set('command_mode_enabled', self.command_mode_enabled)
        self.settings.save_settings()
        
        # Update menu
        if self.command_mode_enabled:
            self.mode_toggle_item.title = "🎤 Switch to Dictation Only"
            self._update_menu_icon("🧠")
            self._show_notification("Command Mode Enabled", "Voice commands are now active")
            
            # Load LLM model if not already loaded
            if not self.llm_manager.is_model_loaded():
                self.llm_manager.load_model_async(self.current_llm_model)
            
            # Load action modules
            self.action_executor.load_action_modules()
        else:
            self.mode_toggle_item.title = "🧠 Enable Voice Commands"
            self._update_menu_icon("🎤")
            self._show_notification("Dictation Mode", "Voice commands disabled, dictation only")
        
        # Update status
        mode_text = "Command Mode" if self.command_mode_enabled else "Dictation Mode"
        mode_indicator = "🧠" if self.command_mode_enabled else "🎤"
        self.status_item.title = f"{mode_indicator} Ready - {mode_text}"
    
    def _select_llm_model(self, model_name: str):
        """Select a different LLM model"""
        self.logger.info(f"Switching LLM model from {self.current_llm_model} to {model_name}")
        
        if model_name == self.current_llm_model:
            self.logger.info(f"LLM model {model_name} is already selected")
            return
        
        # Update current model
        self.current_llm_model = model_name
        self.settings.set('llm_model', model_name)
        self.settings.save_settings()
        
        # Update menu visuals
        self._update_llm_menu_display()
        
        # Update current model display
        if hasattr(self, 'current_llm_item'):
            current_llm_info = self.llm_manager.get_available_models().get(model_name, {})
            llm_display = f"📊 Current: {model_name.title()} ({current_llm_info.get('size', 'unknown')})"
            self.current_llm_item.title = llm_display
        
        # Load new model
        self.llm_manager.load_model_async(model_name)
        
        # Show notification
        self._show_notification("LLM Model Changed", f"Switched to {model_name.title()} model")
    
    def _update_llm_menu_display(self):
        """Update the visual display of LLM menu items"""
        try:
            if not hasattr(self, 'llm_items_map') or not self.llm_items_map:
                return
            
            for model_name, menu_item in self.llm_items_map.items():
                if menu_item and hasattr(menu_item, 'title'):
                    icon = "✅" if model_name == self.current_llm_model else "⚪"
                    model_info = self.llm_manager.get_available_models().get(model_name, {})
                    new_title = f"{icon} {model_name.title()} - {model_info.get('size', 'unknown')} ({model_info.get('capability', 'unknown')})"
                    menu_item.title = new_title
        
        except Exception as e:
            self.logger.debug(f"LLM menu update skipped: {e}")
    
    def _cleanup(self):
        """Clean up resources"""
        try:
            # v1.0 cleanup
            self.hotkey_manager.cleanup()
            self.audio_manager.cleanup()
            self.whisper_manager.unload_model()
            
            # v2.0 cleanup
            if hasattr(self, 'llm_manager'):
                self.llm_manager.unload_model()
            
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")


def main():
    """Main entry point for the menu bar app"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run app
    app = HeyMikeApp()
    app.run()


if __name__ == "__main__":
    main()

