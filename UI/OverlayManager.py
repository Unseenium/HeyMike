"""
Thread-Safe Overlay Manager for Hey Mike!
Marshals all overlay operations to the main Qt thread
"""

import logging
from typing import Optional

try:
    from PyQt6.QtCore import QObject, pyqtSignal, QTimer
    from UI.OverlayWindow import VoiceOverlay
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    QObject = object


class OverlayManager(QObject if PYQT_AVAILABLE else object):
    """Thread-safe manager for visual overlay that marshals calls to main thread"""
    
    # Signals for thread-safe communication (only if PyQt6 available)
    if PYQT_AVAILABLE:
        _signal_show_recording = pyqtSignal()
        _signal_show_processing = pyqtSignal()
        _signal_show_complete = pyqtSignal()
        _signal_show_cancelled = pyqtSignal()
        _signal_update_amplitude = pyqtSignal(float)
        _signal_hide = pyqtSignal()
    
    def __init__(self):
        """Initialize Overlay Manager"""
        if PYQT_AVAILABLE:
            super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.overlay: Optional[VoiceOverlay] = None
        
        if PYQT_AVAILABLE:
            try:
                # Create overlay on main thread
                self.overlay = VoiceOverlay()
                
                # Connect signals to overlay methods (main thread)
                self._signal_show_recording.connect(self._do_show_recording)
                self._signal_show_processing.connect(self._do_show_processing)
                self._signal_show_complete.connect(self._do_show_complete)
                self._signal_show_cancelled.connect(self._do_show_cancelled)
                self._signal_update_amplitude.connect(self._do_update_amplitude)
                self._signal_hide.connect(self._do_hide)
                
                self.logger.info("OverlayManager initialized with VoiceOverlay")
            except Exception as e:
                self.logger.error(f"Failed to initialize overlay: {e}")
                self.overlay = None
        else:
            self.logger.info("PyQt6 not available - overlay disabled")
    
    def show_recording(self):
        """Show recording state (thread-safe)"""
        if self.overlay and PYQT_AVAILABLE:
            try:
                # Emit signal to show on main thread
                self._signal_show_recording.emit()
            except Exception as e:
                self.logger.warning(f"Failed to emit show_recording signal: {e}")
    
    def show_processing(self):
        """Show processing state (thread-safe)"""
        if self.overlay and PYQT_AVAILABLE:
            try:
                # Emit signal to show on main thread
                self._signal_show_processing.emit()
            except Exception as e:
                self.logger.warning(f"Failed to emit show_processing signal: {e}")
    
    def show_complete(self):
        """Show complete state (thread-safe)"""
        if self.overlay and PYQT_AVAILABLE:
            try:
                # Emit signal to show on main thread
                self._signal_show_complete.emit()
            except Exception as e:
                self.logger.warning(f"Failed to emit show_complete signal: {e}")
    
    def show_cancelled(self):
        """Show cancelled state (thread-safe)"""
        if self.overlay and PYQT_AVAILABLE:
            try:
                # Emit signal to show on main thread
                self._signal_show_cancelled.emit()
            except Exception as e:
                self.logger.warning(f"Failed to emit show_cancelled signal: {e}")
    
    def update_amplitude(self, amplitude: float):
        """Update waveform amplitude (thread-safe)"""
        if self.overlay and PYQT_AVAILABLE:
            try:
                # Emit signal to update on main thread
                self._signal_update_amplitude.emit(amplitude)
            except Exception as e:
                # Don't log - too noisy
                pass
    
    def hide(self):
        """Hide overlay (thread-safe)"""
        if self.overlay and PYQT_AVAILABLE:
            try:
                # Emit signal to hide on main thread
                self._signal_hide.emit()
            except Exception as e:
                self.logger.warning(f"Failed to emit hide signal: {e}")
    
    # Slot methods (run on main thread)
    def _do_show_recording(self):
        """Show recording state (main thread)"""
        if self.overlay:
            try:
                self.overlay.show_recording()
            except Exception as e:
                self.logger.error(f"Failed to show recording: {e}")
    
    def _do_show_processing(self):
        """Show processing state (main thread)"""
        if self.overlay:
            try:
                self.overlay.show_processing()
            except Exception as e:
                self.logger.error(f"Failed to show processing: {e}")
    
    def _do_show_complete(self):
        """Show complete state (main thread)"""
        if self.overlay:
            try:
                self.overlay.show_complete()
            except Exception as e:
                self.logger.error(f"Failed to show complete: {e}")
    
    def _do_show_cancelled(self):
        """Show cancelled state (main thread)"""
        if self.overlay:
            try:
                self.overlay.show_cancelled()
            except Exception as e:
                self.logger.error(f"Failed to show cancelled: {e}")
    
    def _do_update_amplitude(self, amplitude: float):
        """Update amplitude (main thread)"""
        if self.overlay:
            try:
                self.overlay.update_amplitude(amplitude)
            except Exception as e:
                # Don't log - too noisy
                pass
    
    def _do_hide(self):
        """Hide overlay (main thread)"""
        if self.overlay:
            try:
                self.overlay.hide_overlay()
            except Exception as e:
                self.logger.error(f"Failed to hide overlay: {e}")
    
    def is_available(self) -> bool:
        """Check if overlay is available"""
        return self.overlay is not None
