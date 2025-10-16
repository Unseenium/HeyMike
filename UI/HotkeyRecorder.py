"""
Hotkey Recorder Dialog
A PyQt6 dialog for capturing keyboard shortcuts by having the user press them
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent, QFont
import logging

class HotkeyRecorderDialog(QDialog):
    """Dialog for recording hotkey combinations"""
    
    # Map Qt key codes to human-readable names
    KEY_NAMES = {
        Qt.Key.Key_Control: 'Ctrl',
        Qt.Key.Key_Shift: 'Shift',
        Qt.Key.Key_Alt: 'Alt',
        Qt.Key.Key_Meta: 'Cmd',  # Command key on macOS
        Qt.Key.Key_Space: 'Space',
        Qt.Key.Key_Return: 'Return',
        Qt.Key.Key_Enter: 'Enter',
        Qt.Key.Key_Tab: 'Tab',
        Qt.Key.Key_Backspace: 'Backspace',
        Qt.Key.Key_Escape: 'Esc',
    }
    
    def __init__(self, current_hotkey: str = "", parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.current_hotkey = current_hotkey
        self.captured_hotkey = None
        self.pressed_keys = set()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("⌨️  Hotkey Recorder")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        # Make window stay on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🎹 Record Hotkey")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Current hotkey display
        current_label = QLabel(f"Current: {self.current_hotkey}")
        current_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        current_label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(current_label)
        
        # Instructions
        instructions = QLabel(
            "Press the key combination you want to use.\n"
            "Try: Cmd+Shift+Space, Ctrl+Alt+R, etc."
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("color: #666; font-size: 13px; margin: 10px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Captured keys display (big and prominent)
        self.keys_label = QLabel("Waiting for input...")
        keys_font = QFont()
        keys_font.setPointSize(24)
        keys_font.setBold(True)
        self.keys_label.setFont(keys_font)
        self.keys_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.keys_label.setStyleSheet(
            "background-color: #2a2a2a; "
            "border: 2px solid #4a4a4a; "
            "border-radius: 10px; "
            "padding: 30px; "
            "color: #00aaff; "
            "min-height: 80px;"
        )
        layout.addWidget(self.keys_label)
        
        # Status message
        self.status_label = QLabel("Hold all keys, then release to confirm")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #888; font-size: 12px; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.cancel_button = QPushButton("❌ Cancel")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setStyleSheet(
            "QPushButton { "
            "background-color: #555; "
            "border: none; "
            "border-radius: 5px; "
            "color: white; "
            "font-size: 14px; "
            "padding: 10px 20px; "
            "} "
            "QPushButton:hover { background-color: #666; }"
        )
        self.cancel_button.clicked.connect(self.reject)
        
        self.accept_button = QPushButton("✅ Set Hotkey")
        self.accept_button.setMinimumHeight(40)
        self.accept_button.setEnabled(False)  # Disabled until hotkey is captured
        self.accept_button.setStyleSheet(
            "QPushButton { "
            "background-color: #0066cc; "
            "border: none; "
            "border-radius: 5px; "
            "color: white; "
            "font-size: 14px; "
            "font-weight: bold; "
            "padding: 10px 20px; "
            "} "
            "QPushButton:hover { background-color: #0077dd; } "
            "QPushButton:disabled { background-color: #333; color: #666; }"
        )
        self.accept_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.accept_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus to capture keys
        self.setFocus()
        
    def keyPressEvent(self, event: QKeyEvent):
        """Capture key press events"""
        key = event.key()
        
        # Ignore just modifier keys being pressed alone
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            self.pressed_keys.add(key)
            self._update_display()
            return
        
        # Ignore Escape key (used for canceling)
        if key == Qt.Key.Key_Escape:
            self.reject()
            return
        
        # Add the actual key
        self.pressed_keys.add(key)
        self._update_display()
        
        # If we have at least one modifier + one actual key, enable accept
        has_modifier = any(k in self.pressed_keys for k in 
                          [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta])
        has_actual_key = any(k not in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta] 
                            for k in self.pressed_keys)
        
        if has_modifier and has_actual_key:
            self.status_label.setText("✅ Release keys to confirm this hotkey")
            self.status_label.setStyleSheet("color: #00aa00; font-size: 12px; font-weight: bold;")
            
    def keyReleaseEvent(self, event: QKeyEvent):
        """Capture key release - finalize the hotkey when all keys are released"""
        key = event.key()
        
        # Check if we had a valid combination before releasing
        if self.pressed_keys:
            has_modifier = any(k in self.pressed_keys for k in 
                              [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta])
            has_actual_key = any(k not in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta] 
                                for k in self.pressed_keys)
            
            if has_modifier and has_actual_key:
                # Valid combination - save it and enable accept button
                self.captured_hotkey = self._keys_to_string()
                self.accept_button.setEnabled(True)
                self.status_label.setText(f"✅ Captured: {self.captured_hotkey} - Click 'Set Hotkey' to save")
                self.status_label.setStyleSheet("color: #00aa00; font-size: 13px; font-weight: bold;")
                self.logger.info(f"Hotkey captured: {self.captured_hotkey}")
        
        # Remove the released key
        if key in self.pressed_keys:
            self.pressed_keys.discard(key)
            
        # If all keys released and we have a captured hotkey, keep displaying it
        if not self.pressed_keys and self.captured_hotkey:
            self.keys_label.setText(self.captured_hotkey)
            self.keys_label.setStyleSheet(
                "background-color: #1a3a1a; "
                "border: 2px solid #00aa00; "
                "border-radius: 10px; "
                "padding: 30px; "
                "color: #00ff00; "
                "min-height: 80px;"
            )
        elif not self.pressed_keys:
            self.keys_label.setText("Waiting for input...")
            self.keys_label.setStyleSheet(
                "background-color: #2a2a2a; "
                "border: 2px solid #4a4a4a; "
                "border-radius: 10px; "
                "padding: 30px; "
                "color: #00aaff; "
                "min-height: 80px;"
            )
    
    def _update_display(self):
        """Update the display with currently pressed keys"""
        if not self.pressed_keys:
            self.keys_label.setText("Waiting for input...")
            return
        
        display_text = self._keys_to_string()
        self.keys_label.setText(display_text)
        
    def _keys_to_string(self) -> str:
        """Convert pressed keys to a readable string"""
        if not self.pressed_keys:
            return ""
        
        # Order: Cmd/Ctrl, Shift, Alt, then the actual key
        parts = []
        
        # Check modifiers in order
        if Qt.Key.Key_Meta in self.pressed_keys:  # Cmd key
            parts.append("Cmd")
        if Qt.Key.Key_Control in self.pressed_keys:
            parts.append("Ctrl")
        if Qt.Key.Key_Shift in self.pressed_keys:
            parts.append("Shift")
        if Qt.Key.Key_Alt in self.pressed_keys:
            parts.append("Alt")
        
        # Add the actual key
        for key in self.pressed_keys:
            if key not in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta]:
                if key in self.KEY_NAMES:
                    parts.append(self.KEY_NAMES[key])
                elif 32 <= key <= 126:  # Printable ASCII
                    parts.append(chr(key).upper())
                else:
                    parts.append(f"Key{key}")
        
        return " + ".join(parts)
    
    def get_hotkey(self) -> str:
        """Get the captured hotkey string"""
        return self.captured_hotkey or ""

