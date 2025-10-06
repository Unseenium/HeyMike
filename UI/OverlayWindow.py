"""
Visual Recording Overlay for Hey Mike!
PyQt6-based floating overlay with waveform visualization
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

try:
    from PyQt6.QtWidgets import QWidget, QApplication
    from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve, pyqtProperty
    from PyQt6.QtGui import QPainter, QColor, QFont, QPen
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("WARNING: PyQt6 not installed. Install with: pip install PyQt6>=6.5.0")

from UI.WaveformRenderer import WaveformRenderer


class VoiceOverlay(QWidget):
    """Floating overlay window for voice recording visualization"""
    
    # States
    STATE_HIDDEN = 'hidden'
    STATE_RECORDING = 'recording'
    STATE_PROCESSING = 'processing'
    STATE_COMPLETE = 'complete'
    STATE_CANCELLED = 'cancelled'
    
    def __init__(self):
        """Initialize Voice Overlay"""
        if not PYQT_AVAILABLE:
            raise ImportError("PyQt6 is required for VoiceOverlay. Install with: pip install PyQt6>=6.5.0")
        
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        
        # State
        self.state = self.STATE_HIDDEN
        self._opacity = 0.0  # For fade animation
        
        # Recording timer
        self.recording_start_time: Optional[datetime] = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_timer)
        
        # Components
        self.waveform_renderer = WaveformRenderer(bar_count=35)  # More bars for smoother animation
        
        # Setup window
        self._setup_window()
        self._setup_animation()
        
        self.logger.info("VoiceOverlay initialized")
    
    # Event handler removed - no longer needed after fixing signal bug
    
    def _setup_window(self):
        """Configure window properties"""
        # Window flags: Use SplashScreen - designed for persistent overlays
        # Neither Popup nor ToolTip work on macOS - both have auto-hide issues
        # SplashScreen is designed to stay visible without stealing focus
        self.setWindowFlags(
            Qt.WindowType.SplashScreen |  # CRITICAL: Persistent overlay, no auto-hide
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowDoesNotAcceptFocus |
            Qt.WindowType.WindowTransparentForInput
        )
        
        # Transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # Don't activate on show
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)  # macOS: keep as tool window
        self.setAttribute(Qt.WidgetAttribute.WA_X11DoNotAcceptFocus)  # Extra focus prevention
        
        # Size - taller for bigger waveform
        self.setFixedSize(280, 100)
        
        # Position at bottom-center
        self._position_bottom_center()
        
        self.logger.debug("Window configured: 280x100, bottom-center")
    
    def _position_bottom_center(self):
        """Position window at bottom-center of screen"""
        try:
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = screen.height() - self.height() - 60  # 60px from bottom
            self.move(x, y)
            self.logger.debug(f"Positioned at ({x}, {y})")
        except Exception as e:
            self.logger.error(f"Failed to position window: {e}")
            # Fallback position
            self.move(100, 100)
    
    def _setup_animation(self):
        """Setup fade in/out animations"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_animation.setDuration(200)  # 200ms
    
    # Property for animation
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)
    
    windowOpacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def show_recording(self):
        """Show overlay in recording state"""
        if self.state == self.STATE_RECORDING:
            self.logger.debug("Already in recording state, ignoring")
            return  # Already recording
        
        self.logger.info("Showing overlay in recording state")
        
        # Stop any running animations AND disconnect their signals
        if self.fade_animation.state() == QPropertyAnimation.State.Running:
            self.fade_animation.stop()
            try:
                self.fade_animation.finished.disconnect()
            except:
                pass
        
        self.state = self.STATE_RECORDING
        self.recording_start_time = datetime.now()
        
        # Reset waveform
        self.waveform_renderer.reset()
        
        # Start timer for recording duration and animations
        self.timer.start(50)  # Update every 50ms for smoother animation
        
        # Fade in
        self._fade_in()
    
    def show_processing(self):
        """Show overlay in processing state"""
        self.logger.info("Showing overlay in processing state")
        self.state = self.STATE_PROCESSING
        
        # Keep timer running for spinner animation
        if not self.timer.isActive():
            self.timer.start(50)
        
        # Update display
        self.update()
    
    def show_complete(self):
        """Show complete state and fade out"""
        self.logger.info("Showing overlay in complete state")
        self.state = self.STATE_COMPLETE
        self.update()
        
        # Fade out after brief pause
        QTimer.singleShot(500, self._fade_out)
    
    def show_cancelled(self):
        """Show cancelled state and fade out"""
        self.logger.info("Showing overlay in cancelled state")
        self.state = self.STATE_CANCELLED
        self.timer.stop()  # Stop any animations
        self.update()
        
        # Fade out after brief pause (same as complete)
        QTimer.singleShot(500, self._fade_out)
    
    def hide_overlay(self):
        """Hide overlay immediately"""
        self.logger.info("Hiding overlay")
        self.state = self.STATE_HIDDEN
        self.timer.stop()
        self.hide()
    
    def _fade_in(self):
        """Fade in animation - completely non-intrusive"""
        # CRITICAL: Disconnect any previous signal connections
        # The fade_out animation connects finished→hide_overlay
        # We MUST disconnect it before fade_in, or hide_overlay will be called when fade_in finishes!
        try:
            self.fade_animation.finished.disconnect()
            self.logger.debug("Disconnected previous finished signal from fade_out")
        except:
            pass  # No signal to disconnect
        
        # Use setVisible instead of show() to avoid window activation
        self.setVisible(True)
        
        # Start fade animation (no signal connection)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
        self.logger.debug(f"Fade in started - opacity: {self.windowOpacity}")
    
    def _fade_out(self):
        """Fade out animation"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        
        # Disconnect any previous connections to avoid multiple calls
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
        
        # Connect to hide when fade completes
        self.fade_animation.finished.connect(self.hide_overlay)
        self.fade_animation.start()
        self.logger.debug("Fade out animation started")
    
    def update_amplitude(self, amplitude: float):
        """
        Update waveform with new amplitude value
        
        Args:
            amplitude: Normalized amplitude (0.0-1.0)
        """
        if self.state == self.STATE_RECORDING:
            self.waveform_renderer.add_amplitude(amplitude)
            self.update()  # Trigger repaint
    
    def _update_timer(self):
        """Update recording duration timer"""
        if self.recording_start_time:
            self.update()  # Trigger repaint to update timer display
    
    def _get_recording_duration(self) -> str:
        """Get formatted recording duration (MM:SS)"""
        if not self.recording_start_time:
            return "0:00"
        
        elapsed = datetime.now() - self.recording_start_time
        total_seconds = int(elapsed.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def paintEvent(self, event):
        """Custom painting for overlay"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        self._draw_background(painter)
        
        # Draw content based on state
        if self.state == self.STATE_RECORDING:
            self._draw_recording_state(painter)
        elif self.state == self.STATE_PROCESSING:
            self._draw_processing_state(painter)
        elif self.state == self.STATE_COMPLETE:
            self._draw_complete_state(painter)
        elif self.state == self.STATE_CANCELLED:
            self._draw_cancelled_state(painter)
    
    def _draw_background(self, painter: QPainter):
        """Draw semi-transparent rounded background"""
        # Background color (darker for better contrast)
        painter.setBrush(QColor(0, 0, 0, 230))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)
    
    def _draw_recording_state(self, painter: QPainter):
        """Draw recording state UI - minimal, waveform-focused"""
        rect = self.rect()
        
        # Small pulsing recording dot (top-left corner)
        pulse = abs((datetime.now().microsecond / 1000000.0) * 2 - 1)  # 0.0 to 1.0 and back
        dot_opacity = int(150 + 105 * pulse)  # Pulse between 150-255
        painter.setBrush(QColor(255, 59, 48, dot_opacity))  # iOS red
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(12, 12, 8, 8)
        
        # Large waveform (centered, takes most of the space)
        waveform_rect = QRect(10, 25, rect.width() - 20, rect.height() - 35)
        self.waveform_renderer.render(painter, waveform_rect)
    
    def _draw_processing_state(self, painter: QPainter):
        """Draw processing state UI - animated spinner"""
        # Animated circular spinner
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 18
        
        # Rotate based on time
        rotation_ms = datetime.now().microsecond // 1000  # 0-999
        rotation = (rotation_ms * 360 // 1000) % 360
        
        # Draw rotating arc
        painter.setPen(QPen(QColor(100, 149, 237), 3, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2, 
                       rotation * 16, 270 * 16)  # 270 degree arc
    
    def _draw_complete_state(self, painter: QPainter):
        """Draw complete state UI - checkmark"""
        # Green checkmark
        painter.setPen(QPen(QColor(52, 199, 89), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Checkmark shape
        painter.drawLine(center_x - 12, center_y, center_x - 4, center_y + 8)
        painter.drawLine(center_x - 4, center_y + 8, center_x + 12, center_y - 8)
    
    def _draw_cancelled_state(self, painter: QPainter):
        """Draw cancelled state UI - red X"""
        # Red X
        painter.setPen(QPen(QColor(255, 59, 48), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # X shape (larger than checkmark for visibility)
        size = 15
        painter.drawLine(center_x - size, center_y - size, center_x + size, center_y + size)
        painter.drawLine(center_x + size, center_y - size, center_x - size, center_y + size)


# Test mode
if __name__ == "__main__":
    import sys
    import math
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app = QApplication(sys.argv)
    
    # Create overlay
    overlay = VoiceOverlay()
    
    # Test: Show recording state
    overlay.show_recording()
    
    # Simulate voice amplitude updates
    frame = 0
    def update_amplitude():
        global frame
        amplitude = (math.sin(frame * 0.1) + 1) / 2
        overlay.update_amplitude(amplitude)
        frame += 1
    
    # Timer for amplitude updates
    timer = QTimer()
    timer.timeout.connect(update_amplitude)
    timer.start(33)  # ~30 FPS
    
    # Test: Transition to processing after 5 seconds
    QTimer.singleShot(5000, overlay.show_processing)
    
    # Test: Transition to complete after 7 seconds
    QTimer.singleShot(7000, overlay.show_complete)
    
    sys.exit(app.exec())
