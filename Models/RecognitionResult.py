"""
Recognition Result for MagikMike
Data models for speech recognition results and processing
"""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class RecognitionResult:
    """Represents the result of a speech recognition operation"""
    
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None
    processing_time: Optional[float] = None
    model_used: Optional[str] = None
    audio_duration: Optional[float] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        """Set timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary
        
        Returns:
            Dictionary representation of the result
        """
        return {
            'text': self.text,
            'confidence': self.confidence,
            'language': self.language,
            'processing_time': self.processing_time,
            'model_used': self.model_used,
            'audio_duration': self.audio_duration,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecognitionResult':
        """
        Create from dictionary
        
        Args:
            data: Dictionary with result data
            
        Returns:
            RecognitionResult instance
        """
        return cls(**data)
    
    def is_valid(self) -> bool:
        """
        Check if the result is valid
        
        Returns:
            True if result has text, False otherwise
        """
        return bool(self.text and self.text.strip())
    
    def get_summary(self) -> str:
        """
        Get a summary string of the result
        
        Returns:
            Summary string
        """
        summary_parts = []
        
        if self.text:
            text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
            summary_parts.append(f"Text: {text_preview}")
        
        if self.confidence is not None:
            summary_parts.append(f"Confidence: {self.confidence:.2f}")
        
        if self.language:
            summary_parts.append(f"Language: {self.language}")
        
        if self.processing_time is not None:
            summary_parts.append(f"Processing: {self.processing_time:.2f}s")
        
        if self.model_used:
            summary_parts.append(f"Model: {self.model_used}")
        
        return " | ".join(summary_parts)


class RecognitionSession:
    """Manages a session of recognition results"""
    
    def __init__(self):
        """Initialize recognition session"""
        self.results = []
        self.session_start = time.time()
        self.total_audio_duration = 0.0
        self.total_processing_time = 0.0
    
    def add_result(self, result: RecognitionResult) -> None:
        """
        Add a recognition result to the session
        
        Args:
            result: Recognition result to add
        """
        self.results.append(result)
        
        if result.audio_duration:
            self.total_audio_duration += result.audio_duration
        
        if result.processing_time:
            self.total_processing_time += result.processing_time
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics
        
        Returns:
            Dictionary with session statistics
        """
        if not self.results:
            return {
                'total_results': 0,
                'session_duration': time.time() - self.session_start,
                'total_audio_duration': 0.0,
                'total_processing_time': 0.0,
                'average_processing_time': 0.0,
                'total_characters': 0,
                'average_confidence': 0.0
            }
        
        # Calculate statistics
        total_characters = sum(len(r.text) for r in self.results)
        confidences = [r.confidence for r in self.results if r.confidence is not None]
        average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        average_processing_time = self.total_processing_time / len(self.results) if self.results else 0.0
        
        return {
            'total_results': len(self.results),
            'session_duration': time.time() - self.session_start,
            'total_audio_duration': self.total_audio_duration,
            'total_processing_time': self.total_processing_time,
            'average_processing_time': average_processing_time,
            'total_characters': total_characters,
            'average_confidence': average_confidence
        }
    
    def get_recent_results(self, count: int = 10) -> list:
        """
        Get recent recognition results
        
        Args:
            count: Number of recent results to return
            
        Returns:
            List of recent recognition results
        """
        return self.results[-count:] if self.results else []
    
    def clear_session(self) -> None:
        """Clear all results and reset session"""
        self.results.clear()
        self.session_start = time.time()
        self.total_audio_duration = 0.0
        self.total_processing_time = 0.0
    
    def export_session(self) -> Dict[str, Any]:
        """
        Export session data
        
        Returns:
            Dictionary with complete session data
        """
        return {
            'session_start': self.session_start,
            'results': [result.to_dict() for result in self.results],
            'stats': self.get_session_stats()
        }

