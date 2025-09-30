"""
Hotkey Manager for Hey Mike!
Handles global keyboard shortcuts for recording control
"""

import logging
from typing import Optional, Callable, Dict, Set
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import threading

class HotkeyManager:
    """Manages global hotkeys for Hey Mike!"""
    
    # Default hotkey combinations
    DEFAULT_HOTKEY = {Key.cmd, Key.shift, Key.space}
    
    # Mode-specific hotkeys (Cmd+Option+Number)
    # Use virtual keycodes (vk) which are hardware-based and don't change with modifiers
    # vk codes for US keyboard: 1=18, 2=19
    MODE_HOTKEYS = {
        'smart': {Key.cmd, Key.alt, 18},      # Cmd+Option+1 (Smart transcription with auto-enhancement)
        'action': {Key.cmd, Key.alt, 19}      # Cmd+Option+2 (Voice commands)
    }
    
    def __init__(self):
        """Initialize Hotkey Manager"""
        self.logger = logging.getLogger(__name__)
        self.listener = None
        self.is_listening = False
        
        # Current hotkey configuration
        self.record_hotkey = self.DEFAULT_HOTKEY.copy()
        self.cancel_hotkey = {Key.esc}
        self.mode_hotkeys = self.MODE_HOTKEYS.copy()
        
        # Currently pressed keys
        self.pressed_keys: Set[Key] = set()
        
        # Callbacks
        self.on_record_toggle: Optional[Callable[[], None]] = None
        self.on_cancel_recording: Optional[Callable[[], None]] = None
        self.on_mode_change: Optional[Callable[[str], None]] = None  # New: mode change callback
        self.on_error: Optional[Callable[[str], None]] = None
        
        # State tracking
        self.recording_active = False
        self.current_mode = 'smart'  # Default mode
    
    def start_listening(self) -> bool:
        """
        Start listening for global hotkeys
        
        Returns:
            True if listening started successfully, False otherwise
        """
        if self.is_listening:
            self.logger.warning("Already listening for hotkeys")
            return True
        
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            
            self.listener.start()
            self.is_listening = True
            self.logger.info("Started listening for global hotkeys")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start hotkey listener: {str(e)}")
            if self.on_error:
                self.on_error(f"Failed to start hotkey listener: {str(e)}")
            return False
    
    def stop_listening(self):
        """Stop listening for global hotkeys"""
        if not self.is_listening:
            return
        
        try:
            if self.listener:
                self.listener.stop()
                # Wait for listener thread to finish
                try:
                    self.listener.join(timeout=1.0)
                except Exception:
                    pass
                self.listener = None
            
            self.is_listening = False
            self.pressed_keys.clear()
            self.logger.info("Stopped listening for global hotkeys")
            
        except Exception as e:
            self.logger.error(f"Error stopping hotkey listener: {str(e)}")
    
    def _on_key_press(self, key):
        """
        Handle key press events
        
        Args:
            key: The pressed key
        """
        try:
            # Add key to pressed set
            self.pressed_keys.add(key)
            
            # DEBUG: Log key presses
            self.logger.debug(f"Key pressed: {repr(key)}, Pressed keys: {[repr(k) for k in self.pressed_keys]}")
            
            # Check for hotkey matches
            self._check_hotkey_combinations()
            
        except Exception as e:
            self.logger.error(f"Error in key press handler: {str(e)}")
    
    def _on_key_release(self, key):
        """
        Handle key release events
        
        Args:
            key: The released key
        """
        try:
            # Remove key from pressed set
            self.pressed_keys.discard(key)
            
        except Exception as e:
            self.logger.error(f"Error in key release handler: {str(e)}")
    
    def _check_hotkey_combinations(self):
        """Check if any configured hotkey combinations are currently pressed"""
        
        # Check mode-switching hotkeys first (priority)
        for mode_name, mode_keys in self.mode_hotkeys.items():
            # DEBUG: Log mode hotkey checking
            if len(self.pressed_keys) >= len(mode_keys):
                self.logger.debug(f"Checking mode '{mode_name}': need {[repr(k) for k in mode_keys]}, have {[repr(k) for k in self.pressed_keys]}")
            
            if self._is_hotkey_pressed(mode_keys):
                if mode_name != self.current_mode:
                    self.logger.info(f"Mode switch detected: {self.current_mode} → {mode_name}")
                    old_mode = self.current_mode
                    self.current_mode = mode_name
                    if self.on_mode_change:
                        # Create callback with proper closure
                        def mode_callback(m=mode_name):
                            self.on_mode_change(m)
                        threading.Thread(
                            target=mode_callback, 
                            daemon=True
                        ).start()
                return  # Don't check other hotkeys
        
        # Check record toggle hotkey
        if self._is_hotkey_pressed(self.record_hotkey):
            self.logger.debug("Record toggle hotkey detected")
            if self.on_record_toggle:
                # Use threading to prevent blocking the hotkey listener
                threading.Thread(target=self.on_record_toggle, daemon=True).start()
        
        # Check cancel recording hotkey (only when recording)
        elif self.recording_active and self._is_hotkey_pressed(self.cancel_hotkey):
            self.logger.debug("Cancel recording hotkey detected")
            if self.on_cancel_recording:
                threading.Thread(target=self.on_cancel_recording, daemon=True).start()
    
    def _is_hotkey_pressed(self, hotkey_set: Set) -> bool:
        """
        Check if a specific hotkey combination is currently pressed
        
        Args:
            hotkey_set: Set of keys/vk codes that should be pressed
            
        Returns:
            True if the hotkey combination is pressed, False otherwise
        """
        # Build a set of currently pressed keys including vk codes
        pressed_keys_with_vk = set()
        for key in self.pressed_keys:
            pressed_keys_with_vk.add(key)
            # Also add vk (virtual keycode) if it exists
            if hasattr(key, 'vk') and key.vk is not None:
                pressed_keys_with_vk.add(key.vk)
        
        # Check if all required keys/vk codes are pressed
        return hotkey_set.issubset(pressed_keys_with_vk)
    
    def set_record_hotkey(self, keys: Set) -> bool:
        """
        Set the hotkey combination for record toggle
        
        Args:
            keys: Set of keys for the hotkey combination
            
        Returns:
            True if hotkey set successfully, False otherwise
        """
        try:
            if not keys:
                self.logger.error("Empty hotkey combination")
                return False
            
            # Validate keys
            for key in keys:
                if not isinstance(key, (Key, KeyCode)):
                    self.logger.error(f"Invalid key type: {type(key)}")
                    return False
            
            self.record_hotkey = keys.copy()
            self.logger.info(f"Record hotkey set to: {self._hotkey_to_string(keys)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set record hotkey: {str(e)}")
            if self.on_error:
                self.on_error(f"Failed to set hotkey: {str(e)}")
            return False
    
    def set_cancel_hotkey(self, keys: Set) -> bool:
        """
        Set the hotkey combination for cancel recording
        
        Args:
            keys: Set of keys for the hotkey combination
            
        Returns:
            True if hotkey set successfully, False otherwise
        """
        try:
            if not keys:
                self.logger.error("Empty hotkey combination")
                return False
            
            self.cancel_hotkey = keys.copy()
            self.logger.info(f"Cancel hotkey set to: {self._hotkey_to_string(keys)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set cancel hotkey: {str(e)}")
            return False
    
    def _hotkey_to_string(self, keys: Set) -> str:
        """
        Convert a hotkey set to a human-readable string
        
        Args:
            keys: Set of keys
            
        Returns:
            String representation of the hotkey
        """
        key_names = []
        
        for key in keys:
            if hasattr(key, 'name'):
                key_names.append(key.name)
            elif hasattr(key, 'char') and key.char:
                key_names.append(key.char)
            else:
                key_names.append(str(key))
        
        return ' + '.join(sorted(key_names))
    
    def get_record_hotkey_string(self) -> str:
        """Get string representation of current record hotkey"""
        return self._hotkey_to_string(self.record_hotkey)
    
    def get_cancel_hotkey_string(self) -> str:
        """Get string representation of current cancel hotkey"""
        return self._hotkey_to_string(self.cancel_hotkey)
    
    def set_recording_state(self, is_recording: bool):
        """
        Update the recording state for hotkey behavior
        
        Args:
            is_recording: True if currently recording, False otherwise
        """
        self.recording_active = is_recording
        self.logger.debug(f"Recording state set to: {is_recording}")
    
    def get_current_mode(self) -> str:
        """
        Get the current mode
        
        Returns:
            Current mode name ('smart' or 'action')
        """
        return self.current_mode
    
    def set_mode(self, mode: str) -> bool:
        """
        Manually set the current mode
        
        Args:
            mode: Mode name to set
            
        Returns:
            True if mode is valid and set, False otherwise
        """
        if mode in self.mode_hotkeys:
            old_mode = self.current_mode
            self.current_mode = mode
            self.logger.info(f"Mode manually set: {old_mode} → {mode}")
            return True
        else:
            self.logger.error(f"Invalid mode: {mode}")
            return False
    
    def get_mode_hotkey_string(self, mode: str) -> Optional[str]:
        """
        Get string representation of a mode's hotkey
        
        Args:
            mode: Mode name
            
        Returns:
            String representation or None if mode not found
        """
        if mode in self.mode_hotkeys:
            return self._hotkey_to_string(self.mode_hotkeys[mode])
        return None
    
    def get_all_mode_hotkeys(self) -> Dict[str, str]:
        """
        Get all mode hotkeys as strings
        
        Returns:
            Dictionary mapping mode names to hotkey strings
        """
        return {
            mode: self._hotkey_to_string(keys)
            for mode, keys in self.mode_hotkeys.items()
        }
    
    @staticmethod
    def parse_hotkey_string(hotkey_string: str) -> Optional[Set]:
        """
        Parse a hotkey string into a set of keys
        
        Args:
            hotkey_string: String like "cmd+shift+space"
            
        Returns:
            Set of keys or None if parsing failed
        """
        try:
            key_names = [name.strip().lower() for name in hotkey_string.split('+')]
            keys = set()
            
            key_mapping = {
                'cmd': Key.cmd,
                'command': Key.cmd,
                'ctrl': Key.ctrl,
                'control': Key.ctrl,
                'alt': Key.alt,
                'option': Key.alt,
                'shift': Key.shift,
                'space': Key.space,
                'enter': Key.enter,
                'return': Key.enter,
                'tab': Key.tab,
                'esc': Key.esc,
                'escape': Key.esc,
                'backspace': Key.backspace,
                'delete': Key.delete,
                'up': Key.up,
                'down': Key.down,
                'left': Key.left,
                'right': Key.right,
                'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
                'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
                'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
            }
            
            for key_name in key_names:
                if key_name in key_mapping:
                    keys.add(key_mapping[key_name])
                elif len(key_name) == 1 and key_name.isalnum():
                    # Single character key
                    keys.add(KeyCode.from_char(key_name))
                else:
                    # Unknown key
                    return None
            
            return keys if keys else None
            
        except Exception:
            return None
    
    def reset_to_default(self):
        """Reset hotkeys to default configuration"""
        self.record_hotkey = self.DEFAULT_HOTKEY.copy()
        self.cancel_hotkey = {Key.esc}
        self.logger.info("Hotkeys reset to default configuration")
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_listening()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

