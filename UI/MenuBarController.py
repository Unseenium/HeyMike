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
from MLXLLMManager import MLXLLMManager
from TextEnhancer import TextEnhancer
from VSCodeBridge import VSCodeBridge
from AppSettings import AppSettings
# Note: NoteClassifier excluded - Phase 2 feature only
from TranscriptionHistory import TranscriptionHistory

class HeyMikeApp(rumps.App):
    """Main Hey Mike! application with menu bar interface"""
    
    def __init__(self):
        """Initialize Hey Mike! application"""
        # Set up logging first
        self.logger = logging.getLogger(__name__)
        
        # Use simple emoji icon - always visible, no custom icon needed
        super(HeyMikeApp, self).__init__(
            "Hey Mike!",
            icon=None,
            title="🎤",  # Simple mic emoji
            quit_button=None
        )
        
        self.logger.info("✅ Using emoji icon: 🎤")
        
        # CRITICAL: Hide Dock icon (menu bar only app)
        # Must be set AFTER rumps.App.__init__() which creates/resets NSApplication
        try:
            from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
            app = NSApplication.sharedApplication()
            app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
            self.logger.info("Dock icon hidden successfully")
        except Exception as e:
            self.logger.warning(f"Could not hide Dock icon: {e}")
        
        # Use simple emoji icon (SF Symbols don't work well with rumps programmatically)
        # Emoji is clean, simple, and works perfectly across all macOS versions
        
        # Initialize managers
        self.whisper_manager = MLXWhisperManager()
        self.audio_manager = AudioManager()
        self.hotkey_manager = HotkeyManager()
        self.text_manager = TextInsertionManager()
        self.settings = AppSettings()
        
        # Initialize visual overlay manager (Phase 1) - thread-safe
        self.overlay_manager = None
        self.qt_app = None
        try:
            from PyQt6.QtWidgets import QApplication
            from UI.OverlayManager import OverlayManager
            
            # Get or create QApplication instance
            self.qt_app = QApplication.instance()
            if self.qt_app is None:
                self.logger.warning("QApplication not found - creating new instance")
                self.qt_app = QApplication([])
            
            self.qt_app.setQuitOnLastWindowClosed(False)
            
            self.overlay_manager = OverlayManager()
            if self.overlay_manager.is_available():
                # Pass overlay to audio manager for amplitude updates
                self.audio_manager.set_overlay(self.overlay_manager)
                self.logger.info("Visual overlay manager initialized successfully")
            else:
                self.logger.info("Visual overlay not available")
        except ImportError:
            self.logger.info("PyQt6 not available - visual overlay disabled")
        except Exception as e:
            self.logger.warning(f"Failed to initialize visual overlay: {e}")
        
        # Initialize LLM and text enhancement
        self.llm_manager = MLXLLMManager()
        self.text_enhancer = TextEnhancer(self.llm_manager)
        # Note: NoteClassifier not used in Phase 1 (Action Mode deferred to Phase 2)
        # self.note_classifier = NoteClassifier(self.llm_manager)
        
        # Initialize transcription history (Hybrid approach: Option 5)
        self.transcription_history = TranscriptionHistory(max_items=10)
        
        # Initialize VS Code Bridge (v2.0+)
        # Initialize VS Code Bridge (Phase 2 feature)
        # Gracefully degrade if SocketIO fails in bundled app
        try:
            self.vscode_bridge = VSCodeBridge(port=8765)
            self.vscode_bridge.set_settings_callback(self._get_settings_for_vscode)
            self.logger.info("VSCodeBridge initialized successfully")
        except Exception as e:
            self.vscode_bridge = None
            self.logger.warning(f"VSCodeBridge initialization failed (Phase 2 feature): {e}")
            self.logger.info("App will continue without VS Code extension support")
        
        # Application state
        self.is_recording = False
        self.is_processing = False
        self.current_model = 'tiny'  # Default, will be updated from settings
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Load settings first to get the correct current model
        self._load_settings_early()
        
        # Initialize menu with correct model
        self._setup_menu()
        
        # Complete initialization
        self._initialize_app()
        
        # Load LLM asynchronously if enhancement is enabled
        if self.settings.get('enhance_text', True):
            llm_model = self.settings.get('llm_model', 'llama-3.2-1b')
            self.logger.info(f"Loading LLM model for text enhancement: {llm_model}")
            self.llm_manager.load_model_async(llm_model)
    
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
        
        # Error callbacks
        self.audio_manager.on_error = self._on_error
        self.whisper_manager.on_error = self._on_error
        self.hotkey_manager.on_error = self._on_error
        self.text_manager.on_error = self._on_error
    
    def _load_settings_early(self):
        """Load settings early to get current model before menu setup"""
        try:
            self.settings.load_settings()
            self.current_model = self.settings.get('model', 'tiny')
            self.logger.debug(f"Loaded current model from settings: {self.current_model}")
        except Exception as e:
            self.logger.warning(f"Could not load settings early: {str(e)}")
            self.current_model = 'tiny'  # Fallback
    
    
    def _set_sf_symbol_icon(self):
        """
        Set SF Symbol icon after rumps initialization.
        Uses simple "mic" outline icon.
        """
        try:
            from AppKit import NSImage
            
            # Debug: Check what attributes exist
            self.logger.info(f"Has _app: {hasattr(self, '_app')}")
            if hasattr(self, '_app'):
                self.logger.info(f"_app value: {self._app}")
                self.logger.info(f"_app type: {type(self._app)}")
            
            # Use SF Symbol "mic" (clean outline microphone)
            symbol_name = "mic"
            image = NSImage.imageWithSystemSymbolName_accessibilityDescription_(
                symbol_name, 
                "Hey Mike! - Voice Dictation"
            )
            
            self.logger.info(f"Image created: {image is not None}")
            
            if image and hasattr(self, '_app') and self._app:
                # Set size for menu bar
                image.setSize_((18, 18))
                # Set as template for dark mode support
                image.setTemplate_(True)
                
                # Set on status bar button
                button = self._app.button()
                self.logger.info(f"Button: {button}")
                if button:
                    button.setImage_(image)
                    self.title = None  # Clear text
                    self.logger.info(f"✅ Using SF Symbol: {symbol_name}")
                else:
                    self.logger.warning("Could not access status bar button")
            else:
                self.logger.warning(f"SF Symbols not available - image: {image is not None}, has _app: {hasattr(self, '_app')}")
                
        except Exception as e:
            self.logger.error(f"Error setting SF Symbol: {e}", exc_info=True)
    
    def _setup_audio_device_menu(self):
        """Setup audio device submenu with clickable device options"""
        self._refresh_audio_device_menu()
    
    def _refresh_audio_device_menu(self):
        """Refresh the audio device menu with current devices (handles hot-plugging)"""
        try:
            # Clear existing items (only if already initialized)
            if hasattr(self.audio_menu, '_menu') and self.audio_menu._menu is not None:
                self.audio_menu.clear()
            self.audio_items_map.clear()
            
            # Get devices - this should work even if empty
            devices = self.audio_manager.get_input_devices()
            self.logger.debug(f"Found {len(devices)} audio input devices")
            
            # Log each device for debugging
            for d in devices:
                self.logger.debug(f"  Device {d['index']}: {d['name']} ({d['channels']} channels, {d['sample_rate']} Hz)")
            
            current_device = self.settings.get('audio_device', 'Default')
            
            # Add system default option
            is_default = current_device == 'Default' or current_device is None
            check = "✓ " if is_default else "   "
            
            def make_default_callback():
                def callback(sender):
                    self._select_audio_device(None)
                return callback
            
            default_item = rumps.MenuItem(f"{check}🔊 System Default", callback=make_default_callback())
            self.audio_menu.add(default_item)
            self.audio_items_map['default'] = default_item
            
            if devices:
                self.audio_menu.add(rumps.separator)
                
                # Add each device
                for d in devices:
                    is_current = d['index'] == current_device
                    check = "✓ " if is_current else "   "
                    
                    def make_device_callback(device_index, device_name):
                        def callback(sender):
                            self._select_audio_device(device_index)
                        return callback
                    
                    device_item = rumps.MenuItem(
                        f"{check}🎙️ {d['name']}",
                        callback=make_device_callback(d['index'], d['name'])
                    )
                    self.audio_menu.add(device_item)
                    self.audio_items_map[d['index']] = device_item
                
                self.logger.debug(f"✅ Audio device menu populated with {len(devices)} devices")
            else:
                self.audio_menu.add(rumps.separator)
                no_devices_item = rumps.MenuItem("⚠️ No microphones found", callback=None)
                self.audio_menu.add(no_devices_item)
                self.logger.warning("No audio input devices found")
            
            # Add auto-refresh status info at the bottom
            self.audio_menu.add(rumps.separator)
            info_item = rumps.MenuItem("ℹ️ Updates automatically", callback=None)
            self.audio_menu.add(info_item)
                    
        except Exception as e:
            self.logger.error(f"Error refreshing audio device menu: {e}", exc_info=True)
            # Clear menu and show error (only if menu is initialized)
            if hasattr(self.audio_menu, '_menu') and self.audio_menu._menu is not None:
                self.audio_menu.clear()
            error_item = rumps.MenuItem(f"⚠️ Error: {str(e)[:50]}", callback=None)
            self.audio_menu.add(error_item)
    
    @rumps.timer(10)  # Auto-refresh every 10 seconds
    def _auto_refresh_audio_devices(self, _):
        """Automatically refresh audio device list to detect hot-plugged devices"""
        try:
            # Only refresh if the menu has been initialized
            if hasattr(self, 'audio_menu') and hasattr(self, 'audio_items_map'):
                old_device_count = len(self.audio_items_map) - 1  # -1 for the 'default' item
                
                # Reinitialize PyAudio to detect hot-plugged devices (Bluetooth, USB, etc.)
                self.audio_manager.refresh_device_list()
                
                # Rebuild the menu with updated device list
                self._refresh_audio_device_menu()
                new_device_count = len(self.audio_items_map) - 1
                
                # Log if devices changed
                if new_device_count != old_device_count:
                    self.logger.info(f"🔄 Audio devices changed: {old_device_count} → {new_device_count}")
        except Exception as e:
            self.logger.debug(f"Auto-refresh audio devices error: {e}")
    
    def _setup_language_menu(self):
        """Setup language submenu with clickable language options"""
        try:
            current_lang = self.settings.get('language', None)
            
            # Common languages with flags
            languages = {
                None: ('🌍 Auto-Detect', 'Automatic'),
                'en': ('🇺🇸 English', 'English'),
                'es': ('🇪🇸 Spanish', 'Español'),
                'fr': ('🇫🇷 French', 'Français'),
                'de': ('🇩🇪 German', 'Deutsch'),
                'it': ('🇮🇹 Italian', 'Italiano'),
                'pt': ('🇧🇷 Portuguese', 'Português'),
                'ru': ('🇷🇺 Russian', 'Русский'),
                'ja': ('🇯🇵 Japanese', '日本語'),
                'ko': ('🇰🇷 Korean', '한국어'),
                'zh': ('🇨🇳 Chinese', '中文'),
                'ar': ('🇸🇦 Arabic', 'العربية'),
                'hi': ('🇮🇳 Hindi', 'हिन्दी'),
            }
            
            for lang_code, (display_name, native_name) in languages.items():
                is_current = lang_code == current_lang
                check = "✓ " if is_current else "   "
                
                def make_lang_callback(code):
                    def callback(sender):
                        self._select_language(code)
                    return callback
                
                lang_item = rumps.MenuItem(
                    f"{check}{display_name}",
                    callback=make_lang_callback(lang_code)
                )
                self.language_menu.add(lang_item)
                self.language_items_map[lang_code] = lang_item
                
        except Exception as e:
            self.logger.warning(f"Could not setup language menu: {e}")
    
    def _setup_menu(self):
        """Setup the menu bar menu"""
        
        # Status section with better formatting
        self.status_item = rumps.MenuItem("🎤 Ready", callback=None)
        self.menu.add(self.status_item)
        self.menu.add(rumps.separator)
        
        # Quick actions section
        self.record_item = rumps.MenuItem("🔴 Start Recording", callback=self._menu_toggle_recording)
        self.menu.add(self.record_item)
        
        # Current model display (not clickable, just informational)
        current_model_info = self.whisper_manager.get_available_models().get(self.current_model, {})
        model_display = f"🌟 Current: {self.current_model.title()} - {current_model_info.get('size', 'unknown')}"
        self.current_model_item = rumps.MenuItem(model_display, callback=None)
        self.menu.add(self.current_model_item)
        
        self.menu.add(rumps.separator)
        
        # Recent Transcriptions submenu (Hybrid approach: Option 5)
        self.history_menu = rumps.MenuItem("📋 Recent Transcriptions")
        # Add placeholder item (will be updated after first transcription)
        empty_item = rumps.MenuItem("(No recent transcriptions)", callback=None)
        self.history_menu.add(empty_item)
        self.menu.add(self.history_menu)
        
        self.menu.add(rumps.separator)
        
        # Model management section
        self.model_menu = rumps.MenuItem("🧠 Models")
        
        # Individual model items with better formatting
        self.model_items_map = {}  # Store references for updates
        
        for model_name, info in self.whisper_manager.get_available_models().items():
            # Use same icons as LLM Models for consistency
            icon = "✅" if model_name == self.current_model else "⚪"
            
            # Create callback function with proper closure
            def make_model_callback(model):
                def callback(sender):
                    self._select_model(model)
                return callback
            
            model_item = rumps.MenuItem(
                f"{icon} {model_name.title()} - {info['size']} ({info['accuracy']})",
                callback=make_model_callback(model_name)
            )
            
            # Add to menu first, then store reference
            self.model_menu.add(model_item)
            self.model_items_map[model_name] = model_item
        
        self.model_menu.add(rumps.separator)
        self.predownload_item = rumps.MenuItem("⬇️ Download All Models", callback=self._start_predownload)
        self.model_menu.add(self.predownload_item)
        
        self.menu.add(self.model_menu)
        self.menu.add(rumps.separator)
        
        # LLM Model selection section
        self.llm_menu = rumps.MenuItem("🧠 LLM Model")
        self.llm_items_map = {}  # Store references for updates
        
        # Get current LLM model
        current_llm = self.settings.get('llm_model', 'llama-3.2-1b')
        
        # Get available LLM models
        available_llms = self.llm_manager.get_available_models()
        
        for llm_name, info in available_llms.items():
            is_current = llm_name == current_llm
            icon = "✅" if is_current else "⚪"
            
            # Create callback function with proper closure
            def make_llm_callback(model):
                def callback(sender):
                    self._select_llm_model(model)
                return callback
            
            llm_item = rumps.MenuItem(
                f"{icon} {info.get('name', llm_name)} - {info.get('size', '?')} ({info.get('speed', '?')})",
                callback=make_llm_callback(llm_name)
            )
            
            self.llm_menu.add(llm_item)
            self.llm_items_map[llm_name] = llm_item
            
            self.logger.debug(f"Created LLM menu item for {llm_name}: {llm_item}")
        
        self.menu.add(self.llm_menu)
        self.menu.add(rumps.separator)
        
        # Text Enhancement toggle (simplified to just ON/OFF)
        enhance_enabled = self.settings.get('enhance_text', True)
        status_icon = "✅" if enhance_enabled else "❌"
        self.enhancement_toggle = rumps.MenuItem(
            f"✨ Text Enhancement: {status_icon} {'ON' if enhance_enabled else 'OFF'}",
            callback=self._toggle_enhancement
        )
        self.menu.add(self.enhancement_toggle)
        self.menu.add(rumps.separator)
        
        # Settings section with icons
        self.settings_menu = rumps.MenuItem("⚙️ Settings")
        
        hotkey_display = self.hotkey_manager.get_record_hotkey_string()
        hotkey_item = rumps.MenuItem(f"⌨️ Hotkey: {hotkey_display}", callback=self._show_hotkey_settings)
        self.settings_menu.add(hotkey_item)
        
        # Audio Device submenu with clickable options (auto-refreshes on open)
        self.audio_menu = rumps.MenuItem("🎙️ Audio Device")
        self.audio_items_map = {}
        self._setup_audio_device_menu()
        
        # Store reference to audio menu for automatic refresh
        # Note: rumps doesn't have a "menu opened" callback, so we use the refresh button
        self.settings_menu.add(self.audio_menu)
        
        # Language submenu with clickable options
        self.language_menu = rumps.MenuItem("🌍 Language")
        self.language_items_map = {}
        self._setup_language_menu()
        self.settings_menu.add(self.language_menu)
        
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
            # Qt event processing will be handled by @rumps.timer method below
            if self.qt_app:
                self.qt_event_count = 0
                self.logger.info("Qt event processing timer will start with app")
            
            # Settings already loaded in _load_settings_early()
            self.logger.debug(f"Initializing app with model: {self.current_model}")
            
            # Check permissions and show warnings
            self._check_permissions()
            
            # Start hotkey listener
            self.hotkey_manager.start_listening()
            self.logger.info("Hotkey listener started")
            
            # Load initial model asynchronously
            self.whisper_manager.load_model_async(self.current_model)
            
            # Start VS Code Bridge server (Phase 2 feature)
            if self.vscode_bridge:
                self.logger.info("Starting VS Code Bridge server on port 8765")
                self.vscode_bridge.start()
                self.logger.info("VS Code Bridge started - VS Code extension can now connect")
            
            # Menu already created with correct model selected - no need to update during init
            self.logger.debug(f"Menu created with current model: {self.current_model}")
            
            # Update current model display
            if hasattr(self, 'current_model_item'):
                current_model_info = self.whisper_manager.get_available_models().get(self.current_model, {})
                model_display = f"🌟 Current: {self.current_model.title()} - {current_model_info.get('size', 'unknown')}"
                self.current_model_item.title = model_display
            
            # Disable automatic pre-download for now to prevent crashes
            # User can manually trigger via menu: Models -> Download All Models
            self.logger.info("Automatic pre-download disabled - use menu to download models manually")
            
            self.logger.info("Hey Mike! initialized successfully")
            
            # Show welcome notification so user knows app started
            rumps.notification(
                title="Hey Mike! Started",
                subtitle="Look for 🎤 in your menu bar",
                message="Press Cmd+Shift+Space to start recording",
                sound=False
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize app: {str(e)}")
            self._show_error_dialog(f"Initialization failed: {str(e)}")
    
    def _check_permissions(self):
        """Check and warn about missing permissions (only once per session)"""
        try:
            import sys
            
            # Check if user has dismissed this alert in settings
            dismissed = self.settings.get('permission_alert_dismissed', False)
            if dismissed:
                self.logger.debug("Permission alert dismissed by user, skipping check")
                return
            
            # Check accessibility permissions (critical for hotkeys)
            has_accessibility = False
            try:
                has_accessibility = self.text_manager._check_accessibility_permissions()
            except Exception as e:
                self.logger.error(f"Could not check accessibility permissions: {e}")
            
            # For bundled apps, show a prominent alert on first launch
            is_bundled = getattr(sys, 'frozen', False)
            
            if not has_accessibility:
                if is_bundled:
                    # Show alert dialog for bundled apps (more visible than notification)
                    self.logger.warning("⚠️ Accessibility permission not granted - hotkeys will not work!")
                    response = rumps.alert(
                        title="⚠️ Permissions Required",
                        message=(
                            "Hotkeys won't work without Accessibility permission!\n\n"
                            "To enable:\n"
                            "1. System Settings → Privacy & Security → Accessibility\n"
                            "2. Click 🔒 to unlock\n"
                            "3. Add \"Hey Mike!\" and enable it\n"
                            "4. Restart the app\n\n"
                            "Click 'Open Settings' to go there now.\n"
                            "Or click 'Don't Show Again' to dismiss permanently."
                        ),
                        ok="Open Settings",
                        cancel="Don't Show Again"
                    )
                    if response == 1:  # OK clicked - Open Settings
                        try:
                            import subprocess
                            subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])
                        except Exception as e:
                            self.logger.error(f"Could not open System Settings: {e}")
                    elif response == 0:  # Cancel clicked - Don't show again
                        self.settings.set('permission_alert_dismissed', True)
                        self.settings.save_settings()
                        self.logger.info("User dismissed permission alert permanently")
                else:
                    # For development/terminal runs, just show notification (once)
                    self._show_notification(
                        "Permissions Required", 
                        "Please grant Accessibility permissions in System Settings"
                    )
            
            # Check if we can detect audio devices
            try:
                devices = self.audio_manager.get_input_devices()
                if not devices:
                    self._show_notification(
                        "Audio Issue", 
                        "No audio input devices found. Please check microphone permissions."
                    )
            except Exception as e:
                self.logger.error(f"Could not check audio devices: {e}")
                
        except Exception as e:
            self.logger.error(f"Permission check failed: {e}", exc_info=True)
    
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
        
        # Show visual overlay (thread-safe via signals)
        if self.overlay_manager:
            self.overlay_manager.show_recording()
        
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
        """Cancel current recording or processing"""
        # Edge case 1: Cancel during recording
        if self.is_recording:
            self.logger.info("Cancelling recording...")
            self.audio_manager.stop_recording()
            self.is_recording = False
            self.hotkey_manager.set_recording_state(False)
            
            # Show cancelled state in overlay (thread-safe)
            if self.overlay_manager:
                self.overlay_manager.show_cancelled()
            
            self._update_status("Cancelled")
            self._update_menu_icon("🎤")
            self.record_item.title = "Start Recording"
            
            self.logger.info("Recording cancelled by user (Esc)")
        
        # Edge case 2: Cancel during processing/transcription
        elif self.is_processing:
            self.logger.info("Cancelling transcription...")
            self.is_processing = False
            
            # Show cancelled state in overlay (thread-safe)
            if self.overlay_manager:
                self.overlay_manager.show_cancelled()
            
            self._update_status("Cancelled")
            self._update_menu_icon("🎤")
            self.record_item.title = "Start Recording"
            
            self.logger.info("Transcription cancelled by user (Esc)")
        
        # Edge case 3: Multiple Esc presses (already idle)
        else:
            self.logger.debug("Cancel requested but not recording/processing - ignoring")
    
    def _process_audio(self, audio_data):
        """Process recorded audio through Whisper based on current mode"""
        self.is_processing = True
        self._update_status("Transcribing...")
        self._update_menu_icon("⏳")
        
        # Show processing state in overlay (thread-safe)
        if self.overlay_manager:
            self.overlay_manager.show_processing()
        
        # Get language preference
        language = self.settings.get('language', None)
        
        # Process asynchronously
        def process_callback(raw_text):
            # Check if cancelled during processing
            if not self.is_processing:
                self.logger.debug("Transcription completed but was cancelled - discarding result")
                return
            
            if raw_text:
                # Check if text enhancement is enabled
                enhance_enabled = self.settings.get('enhance_text', True)
                
                if enhance_enabled and self.llm_manager.is_model_loaded():
                    # Auto-detect language - only enhance English
                    is_english = self._is_likely_english(raw_text)
                    if is_english:
                        # Enhance English text
                        self.logger.info(f"English detected, enhancing: {raw_text[:50]}...")
                        self._enhance_and_insert(raw_text)
                    else:
                        # Non-English: direct paste
                        self.logger.info(f"Non-English detected, direct paste: {raw_text[:50]}...")
                        self._insert_text(raw_text, raw_text)
                else:
                    # Enhancement disabled or LLM not loaded: direct paste
                    self.logger.info(f"Enhancement disabled or LLM not ready, direct paste: {raw_text[:50]}...")
                    self._insert_text(raw_text, raw_text)
                    
            else:
                self.is_processing = False
                self._update_menu_icon("🎤")
                self.record_item.title = "🔴 Start Recording"
                self._update_status("Transcription failed")
                self._show_notification("Error", "Transcription failed")
        
        self.whisper_manager.transcribe_audio_async(audio_data, language, process_callback)
    
    def _enhance_and_insert(self, raw_text: str):
        """Enhance text with LLM and insert"""
        self._update_status("Enhancing...")
        
        def enhance_callback(enhanced_text):
            # Check if cancelled during enhancement
            if not self.is_processing:
                self.logger.debug("Enhancement completed but was cancelled - discarding result")
                return
            
            self._insert_text(raw_text, enhanced_text)
        
        # Enhance asynchronously
        self.text_enhancer.enhance_async(raw_text, enhance_callback)
    
    def _insert_text(self, raw_text: str, final_text: str, note_data: Optional[Dict[str, Any]] = None, action_intent: Optional[Dict[str, Any]] = None):
        """Insert text and update UI (sends to VS Code if connected, otherwise local insertion)"""
        self.is_processing = False
        self._update_menu_icon("🎤")
        self.record_item.title = "🔴 Start Recording"
        
        # Show complete state in overlay (thread-safe)
        if self.overlay_manager:
            self.overlay_manager.show_complete()
        
        # Send processing state to VS Code
        if self.vscode_bridge:
            self.vscode_bridge.send_processing_state('ready')
        
        # Check if VS Code is connected
        if self.vscode_bridge and self.vscode_bridge.is_connected():
            # Send transcription to VS Code extension
            self.logger.info("VS Code connected - sending transcription to extension")
            
            # Build context with note data if available
            context = {
                'raw_text': raw_text,
                'was_enhanced': raw_text != final_text,
                'language': self.settings.get('language', 'auto')
            }
            
            # Add note classification if available
            if note_data:
                context['note'] = note_data
                self.logger.info(f"Including note data: type={note_data.get('type')}, explicit={note_data.get('explicit')}")
            
            # Add action intent if available (for future actions like explain, search, etc.)
            if action_intent:
                context['action_intent'] = action_intent
                self.logger.info(f"Including action intent: {action_intent.get('intent')}")
            
            if self.vscode_bridge:
                self.vscode_bridge.send_transcription(
                text=final_text,
                mode='voice_note',  # Simple mode for Mac app (modes handled by VS Code extension)
                context=context
            )
            
            # Show notification
            was_enhanced = raw_text != final_text and self.settings.get('enhance_text', True)
            notification_prefix = "✨ Sent to VS Code (Enhanced)" if was_enhanced else "Sent to VS Code"
            self._update_status(f"Sent to VS Code: {final_text[:30]}...")
            self._show_notification(
                notification_prefix,
                final_text[:100] + ("..." if len(final_text) > 100 else "")
            )
            
            if was_enhanced:
                self.logger.info(f"Original: {raw_text}")
                self.logger.info(f"Enhanced: {final_text}")
        else:
            # Fallback to local text insertion (no VS Code connected)
            # Hybrid approach: Always copies to clipboard, tries to auto-insert
            self.logger.info("VS Code not connected - using local text insertion (hybrid approach)")
            result = self.text_manager.insert_text(final_text)
            
            was_enhanced = raw_text != final_text and self.settings.get('enhance_text', True)
            
            # Add to history
            self.transcription_history.add(
                text=final_text,
                raw_text=raw_text,
                was_enhanced=was_enhanced
            )
            self._update_history_menu()  # Update menu with new item
            
            # Handle different insertion statuses
            if result['status'] == 'inserted':
                # Success: Text inserted AND in clipboard
                notification_prefix = "✨ Enhanced & Inserted 📋" if was_enhanced else "Text Inserted 📋"
                
                self._update_status(f"Inserted: {final_text[:30]}... 📋")
                self._show_notification(
                    notification_prefix, 
                    f"{final_text[:80]}... (also in clipboard)"
                )
                
                # Log if enhanced
                if was_enhanced:
                    self.logger.info(f"Original: {raw_text}")
                    self.logger.info(f"Enhanced: {final_text}")
                    self.logger.info("Text inserted successfully (also in clipboard)")
                
            elif result['status'] == 'clipboard_only':
                # Failed to insert, but in clipboard
                notification_prefix = "📋 Copied to Clipboard"
                
                self._update_status("In clipboard - press Cmd+V to paste")
                self._show_notification(
                    notification_prefix,
                    "No text field focused. Press Cmd+V to paste manually."
                )
                
                self.logger.warning("Text insertion failed - text in clipboard for manual paste")
                
            else:
                # Complete failure (rare)
                self._update_status("Failed to copy text")
                self._show_notification("Error", "Failed to process text")
    
    def _select_model(self, model_name: str):
        """Select a different Whisper model"""
        if model_name == self.current_model:
            self.logger.debug(f"Model {model_name} is already selected, skipping")
            return
        
        self.logger.info(f"Switching Whisper model: {self.current_model} → {model_name}")
        
        # Update current model
        old_model = self.current_model
        self.current_model = model_name
        self.settings.set('model', model_name)
        self.settings.save_settings()
        
        # Update menu visuals
        self._update_model_menu_display()
        
        # Update current model display with star icon
        current_model_info = self.whisper_manager.get_available_models().get(model_name, {})
        model_display = f"🌟 Current: {model_name.title()} - {current_model_info.get('size', 'unknown')}"
        if hasattr(self, 'current_model_item'):
            self.current_model_item.title = model_display
        
        # Load new model
        self.whisper_manager.load_model_async(model_name)
        
        # Show notification
        self._show_notification("Model Changed", f"Switched to {model_name.title()} model")
    
    def _select_llm_model(self, model_name: str):
        """Select a different LLM model for text enhancement"""
        self.logger.info(f"_select_llm_model called with: {model_name}")
        
        current_llm = self.settings.get('llm_model', 'llama-3.2-1b')
        
        if model_name == current_llm:
            self.logger.info(f"LLM model {model_name} is already selected, skipping")
            return
        
        self.logger.info(f"Switching LLM model from {current_llm} to {model_name}")
        
        # Show loading notification
        available_llms = self.llm_manager.get_available_models()
        model_info = available_llms.get(model_name, {})
        model_display_name = model_info.get('name', model_name)
        
        self._show_notification(
            "Loading LLM Model", 
            f"Switching to {model_display_name}..."
        )
        
        # Update settings
        self.settings.set('llm_model', model_name)
        self.settings.save_settings()
        
        # Update menu visuals
        self._update_llm_menu_display(model_name)
        
        # Unload current model and load new one
        self.llm_manager.unload_model()
        self.llm_manager.load_model_async(model_name)
        
        # Show success notification
        self._show_notification(
            "LLM Model Changed", 
            f"Switched to {model_display_name}\n{model_info.get('size', '?')} - {model_info.get('speed', '?')}"
        )
    
    def _update_llm_menu_display(self, current_model: str):
        """Update LLM menu to show current selection"""
        self.logger.debug(f"Updating LLM menu display, current: {current_model}")
        
        for model_name, menu_item in self.llm_items_map.items():
            # Get model info
            available_llms = self.llm_manager.get_available_models()
            info = available_llms.get(model_name, {})
            
            # Update checkmark
            is_current = model_name == current_model
            icon = "✅" if is_current else "⚪"
            
            # Update menu item title
            menu_item.title = f"{icon} {info.get('name', model_name)} - {info.get('size', '?')} ({info.get('speed', '?')})"
            
            self.logger.debug(f"Updated LLM menu item {model_name}: {menu_item.title}")
    
    def _update_model_menu_display(self):
        """Update the visual display of model menu items"""
        try:
            self.logger.debug(f"Updating model menu display, current model: {self.current_model}")
            
            # Check if model items map exists and is populated
            if not hasattr(self, 'model_items_map'):
                self.logger.warning("model_items_map attribute doesn't exist")
                return
            
            if not self.model_items_map:
                self.logger.warning("model_items_map is empty")
                return
            
            # Update each model item's title to reflect current selection
            updated_count = 0
            for model_name, menu_item in self.model_items_map.items():
                try:
                    # NOTE: rumps.MenuItem evaluates to False in boolean context!
                    # Must use 'is None' instead of 'if not menu_item'
                    if menu_item is None:
                        self.logger.warning(f"Menu item for {model_name} is None")
                        continue
                    
                    if not hasattr(menu_item, 'title'):
                        self.logger.warning(f"Menu item for {model_name} has no title attribute")
                        continue
                    
                    # rumps MenuItem.title is a property, just set it directly
                    icon = "✅" if model_name == self.current_model else "⚪"
                    model_info = self.whisper_manager.get_available_models().get(model_name, {})
                    new_title = f"{icon} {model_name.title()} - {model_info.get('size', 'unknown')} ({model_info.get('accuracy', 'unknown')})"
                    menu_item.title = new_title
                    updated_count += 1
                    
                except Exception as item_error:
                    self.logger.error(f"Could not update menu item for {model_name}: {item_error}")
                    continue
                
            self.logger.debug(f"Updated {updated_count}/{len(self.model_items_map)} model menu items")
            
        except Exception as e:
            self.logger.error(f"Model menu update failed: {e}", exc_info=True)
    
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
            import sys
            import subprocess
            
            # Check microphone permission (by checking if we can enumerate devices)
            try:
                devices = self.audio_manager.get_input_devices()
                mic_status = "✅ Granted" if len(devices) > 0 else "⚠️ No devices found"
            except Exception as e:
                mic_status = f"❌ Error: {str(e)[:30]}"
            
            # Check accessibility permission (needed for hotkeys)
            try:
                acc_status = "✅ Granted" if self.text_manager._check_accessibility_permissions() else "❌ Not Granted"
            except Exception as e:
                acc_status = f"❌ Error: {str(e)[:30]}"
            
            # Detect if running as bundled app
            is_bundled = getattr(sys, 'frozen', False)
            app_name = "Hey Mike!" if is_bundled else "Terminal (or your IDE)"
            
            # Build message
            status_icons = "✅✅" if (mic_status.startswith("✅") and acc_status.startswith("✅")) else "❌"
            
            message = (
                f"{status_icons} Permission Status:\n\n"
                f"🎙️  Microphone: {mic_status}\n"
                f"⌨️  Accessibility: {acc_status}\n"
                f"   (Required for hotkeys)\n\n"
            )
            
            if not acc_status.startswith("✅"):
                message += (
                    "⚠️ HOTKEYS WON'T WORK without Accessibility!\n\n"
                    "To fix:\n"
                    f"1. System Settings → Privacy & Security → Accessibility\n"
                    f"2. Click 🔒 to unlock\n"
                    f"3. Add \"{app_name}\" and enable it\n"
                    f"4. Restart the app\n\n"
                    "Click OK to open System Settings →"
                )
            elif not mic_status.startswith("✅"):
                message += (
                    "⚠️ RECORDING WON'T WORK without Microphone!\n\n"
                    "To fix:\n"
                    f"1. System Settings → Privacy & Security → Microphone\n"
                    f"2. Add \"{app_name}\" and enable it\n"
                    f"3. Restart the app\n\n"
                    "Click OK to open System Settings →"
                )
            else:
                message += "✅ All permissions granted! You're good to go!"
            
            response = rumps.alert(
                title="🔐 Permission Check",
                message=message,
                ok="Open Settings" if not (acc_status.startswith("✅") and mic_status.startswith("✅")) else "OK",
                cancel="Close" if not (acc_status.startswith("✅") and mic_status.startswith("✅")) else None
            )
            
            # Open System Settings if user clicked OK and permissions are missing
            if response == 1 and not (acc_status.startswith("✅") and mic_status.startswith("✅")):
                try:
                    if not acc_status.startswith("✅"):
                        subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])
                    elif not mic_status.startswith("✅"):
                        subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"])
                except Exception as e:
                    self.logger.error(f"Could not open System Settings: {e}")
            
            # If permissions are granted, offer to reset the alert flag
            if acc_status.startswith("✅") and mic_status.startswith("✅"):
                dismissed = self.settings.get('permission_alert_dismissed', False)
                if dismissed:
                    reset = rumps.alert(
                        title="Re-enable Permission Alert?",
                        message="All permissions granted! Would you like to re-enable the startup permission alert?",
                        ok="Yes, Re-enable",
                        cancel="No, Keep Disabled"
                    )
                    if reset == 1:
                        self.settings.set('permission_alert_dismissed', False)
                        self.settings.save_settings()
                        self.logger.info("Permission alert re-enabled")
                        rumps.alert(title="✅ Done", message="Permission alert will show again on next launch")
                    
        except Exception as e:
            self.logger.error(f"Error checking permissions: {str(e)}")
            rumps.alert(title="Error", message="Could not check permission status")
    
    def _show_logs(self, sender):
        """Show recent log entries"""
        try:
            # Get recent log entries (this is a simplified version)
            log_info = (
                "📋 Recent Activity:\n\n"
                f"🎤 Recording State: {'Active' if self.is_recording else 'Inactive'}\n"
                f"⚙️ Processing State: {'Active' if self.is_processing else 'Inactive'}\n"
                f"🧠 Current Model: {self.current_model}\n"
                f"⬇️ Pre-download Status: {'Active' if self.whisper_manager.is_predownloading else 'Complete'}\n\n"
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
        """Show hotkey configuration dialog with interactive recorder"""
        self.logger.info("Hotkey settings menu item clicked")
        try:
            from PyQt6.QtWidgets import QApplication
            from UI.HotkeyRecorder import HotkeyRecorderDialog
            
            # Ensure we have QApplication
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            current_hotkey = self.hotkey_manager.get_record_hotkey_string()
            
            # Show the hotkey recorder dialog
            dialog = HotkeyRecorderDialog(current_hotkey=current_hotkey)
            result = dialog.exec()
            
            if result == dialog.DialogCode.Accepted:
                new_hotkey_string = dialog.get_hotkey()
                if new_hotkey_string:
                    # Convert display format to internal format
                    # "Cmd + Shift + Space" -> "cmd+shift+space"
                    internal_format = new_hotkey_string.lower().replace(" + ", "+").replace("cmd", "cmd")
                    
                    # Parse and validate
                    new_hotkey = HotkeyManager.parse_hotkey_string(internal_format)
                    if new_hotkey:
                        self.hotkey_manager.set_record_hotkey(new_hotkey)
                        self.settings.set('hotkey', internal_format)
                        self.settings.save_settings()
                        self._show_notification("✅ Hotkey Updated", f"New hotkey: {new_hotkey_string}")
                        self.logger.info(f"Hotkey updated to: {new_hotkey_string}")
                        
                        # Update menu display
                        hotkey_display = self.hotkey_manager.get_record_hotkey_string()
                        # Find and update the hotkey menu item
                        for item in self.settings_menu.values():
                            if hasattr(item, 'title') and 'Hotkey:' in str(item.title):
                                item.title = f"⌨️ Hotkey: {hotkey_display}"
                                break
                    else:
                        self._show_notification("❌ Invalid Hotkey", "Could not set hotkey. Please try again.")
                        self.logger.error(f"Failed to parse hotkey: {internal_format}")
            else:
                self.logger.info("Hotkey configuration cancelled")
                
        except ImportError:
            self.logger.warning("PyQt6 not available - falling back to text input")
            # Fallback to text input if PyQt6 is not available
            self._show_hotkey_settings_fallback(sender)
        except Exception as e:
            self.logger.error(f"Error in hotkey settings: {str(e)}")
            self._show_notification("❌ Error", f"Hotkey settings error: {str(e)}")
    
    def _show_hotkey_settings_fallback(self, sender):
        """Fallback hotkey settings using text input (if PyQt6 unavailable)"""
        current_hotkey = self.hotkey_manager.get_record_hotkey_string()
        message = (
            "⌨️ Hotkey Configuration\n\n"
            f"Current hotkey: {current_hotkey}\n\n"
            "Enter new hotkey combination:\n"
            "Examples: cmd+shift+space, ctrl+alt+r\n\n"
            "New hotkey:"
        )
        
        response = rumps.Window(
            message=message,
            title="⌨️ Hotkey Settings",
            default_text=current_hotkey,
            ok="✅ Set",
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
    
    def _select_audio_device(self, device_index):
        """Select an audio input device"""
        self.logger.info(f"Audio device selected: {device_index}")
        try:
            if self.audio_manager.set_input_device(device_index):
                self.settings.set('audio_device', device_index if device_index is not None else 'Default')
                self.settings.save_settings()
                
                # Update menu display
                self._update_audio_device_menu_display(device_index)
                
                # Show notification
                if device_index is None:
                    device_name = "System Default"
                else:
                    devices = self.audio_manager.get_input_devices()
                    device_name = next((d['name'] for d in devices if d['index'] == device_index), f"Device {device_index}")
                
                self._show_notification("✅ Audio Device Changed", f"Now using: {device_name}")
                self.logger.info(f"Audio device set to: {device_name}")
            else:
                self._show_notification("❌ Error", "Failed to set audio device")
                
        except Exception as e:
            self.logger.error(f"Error selecting audio device: {str(e)}")
            self._show_notification("❌ Error", f"Audio device error: {str(e)}")
    
    def _update_audio_device_menu_display(self, current_device):
        """Update audio device menu to show current selection"""
        try:
            # Since we now refresh the entire menu on selection, just call refresh
            # This ensures the device list is always up-to-date
            self._refresh_audio_device_menu()
            self.logger.debug(f"Audio menu updated: current_device={current_device}")
            
        except Exception as e:
            self.logger.debug(f"Audio menu update skipped: {e}")
    
    def _select_language(self, language_code):
        """Select a language for transcription"""
        self.logger.info(f"Language selected: {language_code}")
        try:
            self.settings.set('language', language_code)
            self.settings.save_settings()
            
            # Update menu display
            self._update_language_menu_display(language_code)
            
            # Show notification
            language_names = {
                None: '🌍 Auto-Detect',
                'en': '🇺🇸 English',
                'es': '🇪🇸 Spanish',
                'fr': '🇫🇷 French',
                'de': '🇩🇪 German',
                'it': '🇮🇹 Italian',
                'pt': '🇧🇷 Portuguese',
                'ru': '🇷🇺 Russian',
                'ja': '🇯🇵 Japanese',
                'ko': '🇰🇷 Korean',
                'zh': '🇨🇳 Chinese',
                'ar': '🇸🇦 Arabic',
                'hi': '🇮🇳 Hindi',
            }
            
            lang_display = language_names.get(language_code, f"Language: {language_code}")
            self._show_notification("✅ Language Changed", lang_display)
            self.logger.info(f"Language set to: {language_code}")
            
        except Exception as e:
            self.logger.error(f"Error selecting language: {str(e)}")
            self._show_notification("❌ Error", f"Language selection error: {str(e)}")
    
    def _update_language_menu_display(self, current_lang):
        """Update language menu to show current selection"""
        try:
            for lang_code, menu_item in self.language_items_map.items():
                is_current = lang_code == current_lang
                check = "✓ " if is_current else "   "
                
                # Get original display name
                language_names = {
                    None: '🌍 Auto-Detect',
                    'en': '🇺🇸 English',
                    'es': '🇪🇸 Spanish',
                    'fr': '🇫🇷 French',
                    'de': '🇩🇪 German',
                    'it': '🇮🇹 Italian',
                    'pt': '🇧🇷 Portuguese',
                    'ru': '🇷🇺 Russian',
                    'ja': '🇯🇵 Japanese',
                    'ko': '🇰🇷 Korean',
                    'zh': '🇨🇳 Chinese',
                    'ar': '🇸🇦 Arabic',
                    'hi': '🇮🇳 Hindi',
                }
                
                display_name = language_names.get(lang_code, str(lang_code))
                menu_item.title = f"{check}{display_name}"
            
            self.logger.debug(f"Language menu updated: current_lang={current_lang}")
            
        except Exception as e:
            self.logger.debug(f"Language menu update skipped: {e}")
    
    def _is_likely_english(self, text: str) -> bool:
        """
        Simple heuristic to detect if text is likely English
        Can be improved with proper language detection library
        """
        # Common English words
        common_english_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their'
        }
        
        # Convert to lowercase and split into words
        words = text.lower().split()
        if not words:
            return True  # Empty text, assume English
        
        # Count how many common English words appear
        english_word_count = sum(1 for word in words if word.strip('.,!?;:') in common_english_words)
        
        # If more than 20% are common English words, consider it English
        ratio = english_word_count / len(words)
        return ratio > 0.2
    
    def _toggle_enhancement(self, sender):
        """Toggle text enhancement on/off"""
        self.logger.info("Enhancement toggle clicked")
        try:
            current_state = self.settings.get('enhance_text', True)
            new_state = not current_state
            
            # Update settings
            self.settings.set('enhance_text', new_state)
            self.settings.save_settings()
            
            # Update text enhancer
            self.text_enhancer.set_enabled(new_state)
            
            # Update menu display
            status_icon = "✅" if new_state else "❌"
            self.enhancement_toggle.title = f"✨ Text Enhancement: {status_icon} {'ON' if new_state else 'OFF'}"
            
            # Show notification
            if new_state:
                self._show_notification("✨ Enhancement Enabled", "Grammar, punctuation, and filler words will be fixed")
                self.logger.info("Enhancement enabled")
            else:
                self._show_notification("Enhancement Disabled", "Raw transcription will be used")
                self.logger.info("Enhancement disabled")
                
        except Exception as e:
            self.logger.error(f"Error toggling enhancement: {str(e)}")
            self._show_notification("❌ Error", f"Enhancement toggle error: {str(e)}")
    
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
                "ℹ️ About Hey Mike!\n\n"
                "🎤 AI-Enhanced Voice Dictation\n"
                "Version 2.0.0 with Text Enhancement\n\n"
                "📊 Current Status:\n"
                f"• Whisper Model: {model_status}\n"
                f"• Enhancement: {'✅ Enabled' if self.settings.get('enhance_text') else '❌ Disabled'}\n"
                f"• Hotkey: {self.hotkey_manager.get_record_hotkey_string()}\n"
                f"• Python: {python_version}\n"
                f"• macOS: {macos_version}\n\n"
                "✨ What's New in v2.0:\n"
                "• AI text enhancement with LLM\n"
                "• Automatic punctuation & grammar\n"
                "• Filler word removal\n"
                "• Multiple enhancement styles\n\n"
                "🔒 Privacy Features:\n"
                "• 100% offline processing\n"
                "• No data sent to servers\n"
                "• Local AI models\n"
                "• Zero cloud dependencies\n\n"
                "© 2025 Unseenium Inc."
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
                message="This will test text insertion functionality.\n\n"
                       "1. Click OK\n"
                       "2. Click in any text field (TextEdit, Notes, etc.)\n"
                       "3. The test text will be inserted automatically\n\n"
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
    
    @rumps.timer(0.033)  # ~30 FPS for Qt event processing
    def process_qt_events(self, _):
        """Process Qt events periodically to keep overlay responsive"""
        if hasattr(self, 'qt_app') and self.qt_app:
            self.qt_app.processEvents()
            if hasattr(self, 'qt_event_count'):
                self.qt_event_count += 1
                if self.qt_event_count == 1:
                    self.logger.info("✅ Qt events are being processed by rumps timer!")
    
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
        """
        Update menu bar icon (for state changes).
        When using SF Symbol, we keep the icon and don't change it.
        """
        # With SF Symbol, we don't change the icon - it stays as mic.fill
        # The overlay provides visual feedback instead
        # If you want to change icon based on state, we could swap SF Symbols here
        pass
    
    def _update_history_menu(self):
        """Update the Recent Transcriptions submenu with latest items"""
        # Clear existing items (check if menu is initialized first)
        try:
            self.history_menu.clear()
        except (AttributeError, TypeError):
            # Menu not fully initialized yet, skip update
            return
        
        # Check if history is empty
        if self.transcription_history.is_empty():
            empty_item = rumps.MenuItem("(No recent transcriptions)", callback=None)
            self.history_menu.add(empty_item)
            return
        
        # Get menu items from history
        menu_items = self.transcription_history.get_menu_items(max_display=5)
        
        for item in menu_items:
            # Create callback with proper closure
            def make_callback(text=item['text']):
                return lambda _: self._paste_from_history(text)
            
            history_item = rumps.MenuItem(item['title'], callback=make_callback())
            self.history_menu.add(history_item)
        
        # Add separator and clear option
        if len(menu_items) > 0:
            self.history_menu.add(rumps.separator)
            clear_item = rumps.MenuItem("🗑️ Clear History", callback=self._clear_history)
            self.history_menu.add(clear_item)
    
    def _paste_from_history(self, text: str):
        """Paste text from history (copies to clipboard and pastes)"""
        self.logger.info(f"Pasting from history: {text[:50]}...")
        
        # Copy to clipboard
        from Cocoa import NSPasteboard, NSStringPboardType
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        pasteboard.setString_forType_(text, NSStringPboardType)
        
        # Try to paste
        result = self.text_manager.insert_text(text)
        
        if result['status'] == 'inserted':
            self._show_notification("Pasted from History", f"{len(text)} characters")
            self._update_status("Pasted from history 📋")
        else:
            self._show_notification("Copied to Clipboard", "Press Cmd+V to paste")
            self._update_status("In clipboard - press Cmd+V")
    
    def _clear_history(self, _):
        """Clear transcription history"""
        self.transcription_history.clear()
        self._update_history_menu()
        self.logger.info("Transcription history cleared")
    
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
        # Notify VS Code extension
        if self.vscode_bridge:
            self.vscode_bridge.send_recording_state('recording')
    
    def _on_recording_stopped(self, audio_data):
        """Called when recording stops"""
        self.logger.debug(f"Recording stopped, {len(audio_data)} samples")
        # Notify VS Code extension
        if self.vscode_bridge:
            self.vscode_bridge.send_recording_state('ready')
            self.vscode_bridge.send_processing_state('processing', 'Transcribing...')
    
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
    
    def _get_settings_for_vscode(self) -> Dict[str, Any]:
        """Get current settings for VS Code extension"""
        return {
            'model': self.current_model,
            'llm_model': self.settings.get('llm_model', 'llama-3.2-1b'),
            'enhance_text': self.settings.get('enhance_text', True),
            'language': self.settings.get('language', None)
        }
    
    def _cleanup(self):
        """Clean up resources"""
        try:
            self.logger.info("Starting cleanup...")
            
            # Stop VS Code Bridge
            if hasattr(self, 'vscode_bridge'):
                self.logger.info("Stopping VS Code Bridge...")
                if self.vscode_bridge:
                    self.vscode_bridge.stop()
            
            # Stop hotkey listener first
            self.hotkey_manager.cleanup()
            
            # Stop audio recording if active
            if self.audio_manager:
                self.audio_manager.cleanup()
            
            # Unload models to free memory
            if self.whisper_manager:
                self.whisper_manager.unload_model()
            
            if self.llm_manager:
                self.llm_manager.unload_model()
            
            self.logger.info("Cleanup completed successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")


def main():
    """Main entry point for the menu bar app"""
    # NOTE: Logging is already configured by main.py's setup_logging()
    # This function is called FROM main.py after logging is set up
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("MenuBarController main() starting")
    logger.info("=" * 60)
    
    try:
        # Create and run app
        logger.info("Creating HeyMikeApp instance...")
        app = HeyMikeApp()
        logger.info("HeyMikeApp created successfully, starting run loop...")
        app.run()
        logger.info("App run loop exited normally")
    except Exception as e:
        logger.error(f"FATAL ERROR in main(): {e}", exc_info=True)
        # Show error dialog
        try:
            import rumps
            rumps.alert(
                title="Hey Mike! Error",
                message=f"Failed to start: {str(e)}",
                ok="Quit"
            )
        except:
            pass
        raise


if __name__ == "__main__":
    main()

