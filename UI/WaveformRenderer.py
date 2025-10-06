"""
Waveform Renderer for Hey Mike!
Renders animated waveform bars using PyQt6
"""

from collections import deque
from typing import List
import logging

try:
    from PyQt6.QtCore import QRect
    from PyQt6.QtGui import QPainter, QColor, QPen
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("WARNING: PyQt6 not installed. Install with: pip install PyQt6>=6.5.0")


class WaveformRenderer:
    """Renders animated waveform visualization from amplitude data"""
    
    def __init__(self, bar_count: int = 35):
        """
        Initialize Waveform Renderer
        
        Args:
            bar_count: Number of bars to display (default: 35 for smoother look)
        """
        if not PYQT_AVAILABLE:
            raise ImportError("PyQt6 is required for WaveformRenderer. Install with: pip install PyQt6>=6.5.0")
        
        self.logger = logging.getLogger(__name__)
        
        # Configuration - bigger, more dynamic bars
        self.bar_count = bar_count
        self.bar_width = 4
        self.bar_gap = 3
        self.max_height = 75  # Even taller for dramatic effect (was 70)
        self.min_height = 8    # Higher minimum for better visibility (was 6)
        
        # Amplitude buffers (circular buffer for smooth animation)
        self.amplitudes = deque([0.0] * bar_count, maxlen=bar_count)
        self.target_amplitudes = deque([0.0] * bar_count, maxlen=bar_count)
        
        # Very aggressive interpolation for instant, snappy response
        self.interpolation_factor = 0.85  # Near-instant response (was 0.6)
        
        # Colors - vibrant cyan to purple gradient
        self.color_start = QColor(0, 217, 255)      # Cyan
        self.color_end = QColor(191, 64, 255)       # Purple
        
        self.logger.info(f"WaveformRenderer initialized with {bar_count} bars")
    
    def add_amplitude(self, amplitude: float):
        """
        Add new amplitude value to the waveform
        
        Args:
            amplitude: Normalized amplitude (0.0-1.0)
        """
        # Clamp to valid range
        amplitude = max(0.0, min(1.0, amplitude))
        
        # Add to target buffer (what we're animating towards)
        self.target_amplitudes.append(amplitude)
        
        # Interpolate current amplitudes towards targets
        self._interpolate()
    
    def _interpolate(self):
        """Smooth interpolation between current and target amplitudes"""
        # Only interpolate the last value (most recent addition)
        if len(self.amplitudes) > 0 and len(self.target_amplitudes) > 0:
            current = self.amplitudes[-1]
            target = self.target_amplitudes[-1]
            
            # Exponential smoothing
            interpolated = current + (target - current) * self.interpolation_factor
            
            # Update current amplitudes
            self.amplitudes.append(interpolated)
    
    def render(self, painter: QPainter, rect: QRect):
        """
        Render waveform bars
        
        Args:
            painter: QPainter instance for drawing
            rect: Rectangle to draw within
        """
        if not PYQT_AVAILABLE:
            return
        
        # Enable antialiasing for smooth bars
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate total width of all bars
        total_width = (self.bar_width + self.bar_gap) * self.bar_count - self.bar_gap
        
        # Center the waveform horizontally
        start_x = rect.x() + (rect.width() - total_width) // 2
        center_y = rect.y() + rect.height() // 2
        
        # Draw each bar
        for i, amp in enumerate(self.amplitudes):
            # Calculate bar height with minimum for visibility
            height = max(self.min_height, int(amp * self.max_height))
            
            # Position (centered vertically)
            x = start_x + i * (self.bar_width + self.bar_gap)
            y = center_y - height // 2
            
            # Get color from gradient
            color = self._get_gradient_color(i)
            
            # Add dramatic brightness boost based on amplitude
            # Also add a "pulse" effect - bars get brighter AND more saturated
            brightness_factor = 1.0 + (amp * 0.8)  # Up to 80% brighter for drama
            
            # Make colors more vibrant at high amplitudes
            saturation_boost = 1.0 + (amp * 0.3)
            bright_color = QColor(
                min(255, int(color.red() * brightness_factor * saturation_boost)),
                min(255, int(color.green() * brightness_factor * saturation_boost)),
                min(255, int(color.blue() * brightness_factor * saturation_boost))
            )
            
            # Draw rounded rectangle bar (more rounded corners)
            painter.setBrush(bright_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, self.bar_width, height, 2, 2)
    
    def _get_gradient_color(self, index: int) -> QColor:
        """
        Generate gradient color for bar at index
        
        Args:
            index: Bar index (0 to bar_count-1)
            
        Returns:
            QColor for this bar
        """
        # Calculate position in gradient (0.0 to 1.0)
        ratio = index / max(1, self.bar_count - 1)
        
        # Interpolate RGB values
        r = int(self.color_start.red() + ratio * (self.color_end.red() - self.color_start.red()))
        g = int(self.color_start.green() + ratio * (self.color_end.green() - self.color_start.green()))
        b = int(self.color_start.blue() + ratio * (self.color_end.blue() - self.color_start.blue()))
        
        return QColor(r, g, b)
    
    def reset(self):
        """Reset waveform to idle state"""
        self.amplitudes = deque([0.0] * self.bar_count, maxlen=self.bar_count)
        self.target_amplitudes = deque([0.0] * self.bar_count, maxlen=self.bar_count)
        self.logger.debug("Waveform reset")
    
    def set_colors(self, color_start: str, color_end: str):
        """
        Set gradient colors
        
        Args:
            color_start: Starting color (hex string, e.g. "#6495ED")
            color_end: Ending color (hex string, e.g. "#9370DB")
        """
        self.color_start = QColor(color_start)
        self.color_end = QColor(color_end)
        self.logger.debug(f"Colors updated: {color_start} -> {color_end}")


# Test mode
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QWidget
    from PyQt6.QtCore import QTimer
    import math
    
    logging.basicConfig(level=logging.DEBUG)
    
    class TestWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Waveform Renderer Test")
            self.setGeometry(100, 100, 400, 150)
            
            self.renderer = WaveformRenderer(bar_count=20)
            
            # Timer for animation
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_waveform)
            self.timer.start(33)  # ~30 FPS
            
            self.frame = 0
        
        def update_waveform(self):
            # Simulate voice amplitude (sine wave)
            amplitude = (math.sin(self.frame * 0.1) + 1) / 2  # 0.0 to 1.0
            self.renderer.add_amplitude(amplitude)
            self.frame += 1
            self.update()  # Trigger repaint
        
        def paintEvent(self, event):
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 217))  # Dark background
            self.renderer.render(painter, self.rect())
    
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
