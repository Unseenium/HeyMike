"""
Text Insertion Manager for Hey Mike!
Handles inserting transcribed text at cursor position using macOS Accessibility APIs
"""

import logging
from typing import Optional, Callable
import time
import Quartz
from Cocoa import NSPasteboard, NSStringPboardType
from ApplicationServices import AXUIElementCreateSystemWide, AXUIElementCopyAttributeValue, kAXFocusedUIElementAttribute

class TextInsertionManager:
    """Manages text insertion at cursor position using Accessibility APIs"""
    
    def __init__(self):
        """Initialize Text Insertion Manager"""
        self.logger = logging.getLogger(__name__)
        
        # Callbacks
        self.on_text_inserted: Optional[Callable[[str], None]] = None
        self.on_insertion_failed: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Clipboard behavior (Hybrid approach: always keep text in clipboard)
        self.always_copy_to_clipboard = True  # Option 5: Never lose text
        
        # Check accessibility permissions on initialization
        self._check_accessibility_permissions()
    
    def _check_accessibility_permissions(self) -> bool:
        """
        Check if accessibility permissions are granted
        
        Returns:
            True if permissions are granted, False otherwise
        """
        try:
            # Try to access the system-wide accessibility element
            system_element = AXUIElementCreateSystemWide()
            error = AXUIElementCopyAttributeValue(system_element, kAXFocusedUIElementAttribute, None)
            
            if error == 0:
                self.logger.info("Accessibility permissions are granted")
                return True
            else:
                self.logger.warning("Accessibility permissions may not be granted")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to check accessibility permissions: {str(e)}")
            return False
    
    def insert_text(self, text: str, method: str = 'auto') -> dict:
        """
        Insert text at the current cursor position (Hybrid approach: always copies to clipboard)
        
        Args:
            text: Text to insert
            method: Method to use ('paste', 'type', 'auto')
                   - 'paste': Use clipboard and Cmd+V
                   - 'type': Simulate typing each character
                   - 'auto': Choose best method based on text length
            
        Returns:
            dict with status:
                - {'status': 'inserted', 'text': text} - Text inserted successfully (also in clipboard)
                - {'status': 'clipboard_only', 'text': text} - Failed to insert, but in clipboard
                - {'status': 'failed', 'text': text} - Complete failure
        """
        if not text:
            self.logger.warning("Empty text provided for insertion")
            return {'status': 'failed', 'text': ''}
        
        # Clean up the text
        text = text.strip()
        if not text:
            return {'status': 'failed', 'text': ''}
        
        # Step 1: ALWAYS copy to clipboard first (Hybrid approach)
        clipboard_success = self._copy_to_clipboard_permanent(text)
        if not clipboard_success:
            self.logger.error("Failed to copy to clipboard")
            return {'status': 'failed', 'text': text}
        
        self.logger.info(f"Text copied to clipboard ({len(text)} chars)")
        
        # Step 2: Try to auto-insert at cursor
        insertion_success = False
        
        if method == 'auto':
            # Try paste first, then typing if that fails
            insertion_success = self._insert_via_paste_command(text)
            if not insertion_success:
                self.logger.info("Paste command failed, trying typing method")
                insertion_success = self._insert_via_typing(text)
        elif method == 'paste':
            insertion_success = self._insert_via_paste_command(text)
        elif method == 'type':
            insertion_success = self._insert_via_typing(text)
        else:
            self.logger.error(f"Unknown insertion method: {method}")
            # Text is still in clipboard though
            return {'status': 'clipboard_only', 'text': text}
        
        # Step 3: Return status
        if insertion_success:
            self.logger.info(f"Successfully inserted {len(text)} characters using {method} (also in clipboard)")
            if self.on_text_inserted:
                self.on_text_inserted(text)
            return {'status': 'inserted', 'text': text}
        else:
            self.logger.warning(f"Failed to insert text, but it's in clipboard for manual paste")
            if self.on_insertion_failed:
                self.on_insertion_failed(f"Insertion failed - text in clipboard")
            return {'status': 'clipboard_only', 'text': text}
    
    def _copy_to_clipboard_permanent(self, text: str) -> bool:
        """
        Copy text to clipboard permanently (Hybrid approach: don't restore original)
        
        Args:
            text: Text to copy
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            success = pasteboard.setString_forType_(text, NSStringPboardType)
            
            if success:
                self.logger.debug(f"Text copied to clipboard ({len(text)} chars)")
                return True
            else:
                self.logger.error("Failed to set clipboard content")
                return False
            
        except Exception as e:
            self.logger.error(f"Clipboard copy failed: {str(e)}")
            return False
    
    def _insert_via_paste_command(self, text: str) -> bool:
        """
        Insert text by sending Cmd+V (assumes text already in clipboard)
        
        Args:
            text: Text to insert (for logging only, should already be in clipboard)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Small delay to ensure clipboard is ready
            time.sleep(0.05)
            
            # Send Cmd+V to paste
            success = self._send_paste_command()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Paste command failed: {str(e)}")
            return False
    
    def _insert_via_clipboard(self, text: str) -> bool:
        """
        DEPRECATED: Use _copy_to_clipboard_permanent + _insert_via_paste_command instead
        Legacy method kept for compatibility
        """
        self.logger.warning("_insert_via_clipboard is deprecated, use new hybrid approach")
        return self._insert_via_paste_command(text)
    
    def _insert_via_typing(self, text: str) -> bool:
        """
        Insert text by simulating typing
        
        Args:
            text: Text to insert
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create key events for each character
            for char in text:
                if not self._type_character(char):
                    return False
                # Small delay between characters to avoid overwhelming the system
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Typing insertion failed: {str(e)}")
            return False
    
    def _send_paste_command(self) -> bool:
        """
        Send Cmd+V key combination
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create Cmd+V key event
            cmd_v_down = Quartz.CGEventCreateKeyboardEvent(None, 9, True)  # V key down
            cmd_v_up = Quartz.CGEventCreateKeyboardEvent(None, 9, False)   # V key up
            
            # Set Cmd modifier
            Quartz.CGEventSetFlags(cmd_v_down, Quartz.kCGEventFlagMaskCommand)
            Quartz.CGEventSetFlags(cmd_v_up, Quartz.kCGEventFlagMaskCommand)
            
            # Post events
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, cmd_v_down)
            time.sleep(0.01)  # Small delay between key down and up
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, cmd_v_up)
            
            self.logger.debug("Sent Cmd+V key combination")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send paste command: {str(e)}")
            return False
    
    def _type_character(self, char: str) -> bool:
        """
        Type a single character
        
        Args:
            char: Character to type
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert character to key code
            key_code = self._char_to_keycode(char)
            if key_code is None:
                self.logger.warning(f"Cannot convert character to keycode: {char}")
                return False
            
            # Create key events
            key_down = Quartz.CGEventCreateKeyboardEvent(None, key_code, True)
            key_up = Quartz.CGEventCreateKeyboardEvent(None, key_code, False)
            
            # Handle special characters that need shift
            if self._needs_shift(char):
                Quartz.CGEventSetFlags(key_down, Quartz.kCGEventFlagMaskShift)
                Quartz.CGEventSetFlags(key_up, Quartz.kCGEventFlagMaskShift)
            
            # Post events
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_down)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_up)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to type character '{char}': {str(e)}")
            return False
    
    def _char_to_keycode(self, char: str) -> Optional[int]:
        """
        Convert character to macOS key code
        
        Args:
            char: Character to convert
            
        Returns:
            Key code or None if not found
        """
        # Basic character to keycode mapping
        char_map = {
            'a': 0, 'b': 11, 'c': 8, 'd': 2, 'e': 14, 'f': 3, 'g': 5, 'h': 4,
            'i': 34, 'j': 38, 'k': 40, 'l': 37, 'm': 46, 'n': 45, 'o': 31,
            'p': 35, 'q': 12, 'r': 15, 's': 1, 't': 17, 'u': 32, 'v': 9,
            'w': 13, 'x': 7, 'y': 16, 'z': 6,
            '1': 18, '2': 19, '3': 20, '4': 21, '5': 23, '6': 22, '7': 26,
            '8': 28, '9': 25, '0': 29,
            ' ': 49,  # Space
            '\n': 36, # Return
            '\t': 48, # Tab
            '.': 47, ',': 43, ';': 41, "'": 39, '[': 33, ']': 30,
            '\\': 42, '=': 24, '-': 27, '`': 50, '/': 44
        }
        
        return char_map.get(char.lower())
    
    def _needs_shift(self, char: str) -> bool:
        """
        Check if character needs shift modifier
        
        Args:
            char: Character to check
            
        Returns:
            True if shift is needed, False otherwise
        """
        shift_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+{}|:"<>?')
        return char in shift_chars
    
    def insert_text_with_formatting(self, text: str, add_space_before: bool = False, 
                                  add_space_after: bool = True) -> bool:
        """
        Insert text with optional formatting
        
        Args:
            text: Text to insert
            add_space_before: Whether to add space before text
            add_space_after: Whether to add space after text
            
        Returns:
            True if successful, False otherwise
        """
        formatted_text = text
        
        if add_space_before:
            formatted_text = ' ' + formatted_text
        
        if add_space_after:
            formatted_text = formatted_text + ' '
        
        return self.insert_text(formatted_text)
    
    def test_insertion(self) -> bool:
        """
        Test text insertion with a simple message
        
        Returns:
            True if test successful, False otherwise
        """
        test_text = "Hey Mike! test insertion"
        return self.insert_text(test_text)
    
    def get_focused_application(self) -> Optional[str]:
        """
        Get the name of the currently focused application
        
        Returns:
            Application name or None if not available
        """
        try:
            # This is a simplified version - could be enhanced to get actual app name
            system_element = AXUIElementCreateSystemWide()
            error = AXUIElementCopyAttributeValue(system_element, kAXFocusedUIElementAttribute, None)
            
            if error == 0:
                return "Unknown Application"  # Placeholder
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get focused application: {str(e)}")
            return None
    
    def check_text_field_available(self) -> bool:
        """
        Check if a text field is currently available for input
        
        Returns:
            True if text field is available, False otherwise
        """
        # Always return True for now - let the insertion method handle the actual check
        return True

