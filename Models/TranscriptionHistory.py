"""
Transcription History for Hey Mike!
Keeps track of recent transcriptions for easy reuse
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from collections import deque


class TranscriptionHistory:
    """Manages history of recent transcriptions"""
    
    def __init__(self, max_items: int = 10):
        """
        Initialize Transcription History
        
        Args:
            max_items: Maximum number of items to keep (default: 10)
        """
        self.logger = logging.getLogger(__name__)
        self.max_items = max_items
        self.history: deque = deque(maxlen=max_items)
        self.logger.info(f"TranscriptionHistory initialized (max {max_items} items)")
    
    def add(self, text: str, raw_text: Optional[str] = None, was_enhanced: bool = False):
        """
        Add a transcription to history
        
        Args:
            text: Final transcribed/enhanced text
            raw_text: Original raw transcription (optional)
            was_enhanced: Whether text was AI-enhanced
        """
        if not text or not text.strip():
            self.logger.debug("Ignoring empty transcription")
            return
        
        # Create history item
        item = {
            'text': text.strip(),
            'raw_text': raw_text.strip() if raw_text else text.strip(),
            'was_enhanced': was_enhanced,
            'timestamp': datetime.now(),
            'length': len(text.strip())
        }
        
        # Add to history (newest first)
        self.history.appendleft(item)
        self.logger.debug(f"Added to history: {text[:50]}... (total: {len(self.history)} items)")
    
    def get_recent(self, count: int = 5) -> List[Dict]:
        """
        Get recent transcriptions
        
        Args:
            count: Number of items to return (default: 5)
            
        Returns:
            List of recent transcription items (newest first)
        """
        return list(self.history)[:count]
    
    def get_all(self) -> List[Dict]:
        """Get all transcriptions in history"""
        return list(self.history)
    
    def get_item(self, index: int) -> Optional[Dict]:
        """
        Get specific item by index
        
        Args:
            index: Index (0 = newest)
            
        Returns:
            History item or None if index out of range
        """
        try:
            return list(self.history)[index]
        except IndexError:
            return None
    
    def clear(self):
        """Clear all history"""
        self.history.clear()
        self.logger.info("History cleared")
    
    def get_menu_items(self, max_display: int = 5) -> List[Dict[str, str]]:
        """
        Get formatted menu items for display
        
        Args:
            max_display: Maximum items to display
            
        Returns:
            List of dicts with 'title' and 'text' for each item
        """
        items = []
        for i, item in enumerate(list(self.history)[:max_display]):
            text = item['text']
            
            # Truncate long text for menu display
            max_len = 60
            if len(text) > max_len:
                display_text = text[:max_len] + "..."
            else:
                display_text = text
            
            # Add timestamp for context
            time_str = item['timestamp'].strftime("%H:%M")
            
            # Add enhancement indicator
            indicator = "✨ " if item['was_enhanced'] else ""
            
            items.append({
                'title': f"{indicator}{display_text} ({time_str})",
                'text': text,  # Full text for clipboard
                'index': i
            })
        
        return items
    
    def is_empty(self) -> bool:
        """Check if history is empty"""
        return len(self.history) == 0
    
    def size(self) -> int:
        """Get current number of items in history"""
        return len(self.history)


if __name__ == '__main__':
    # Simple test
    logging.basicConfig(level=logging.DEBUG)
    
    history = TranscriptionHistory(max_items=5)
    
    # Add some test items
    history.add("This is a test transcription", was_enhanced=False)
    history.add("This is an enhanced transcription with AI cleanup", 
                raw_text="um this is like an enhanced thing with AI",
                was_enhanced=True)
    history.add("Another test message")
    
    # Get recent items
    print("\nRecent items:")
    for item in history.get_recent(3):
        print(f"- {item['text'][:50]}... ({item['timestamp'].strftime('%H:%M:%S')})")
    
    # Get menu items
    print("\nMenu items:")
    for menu_item in history.get_menu_items():
        print(f"- {menu_item['title']}")
    
    print(f"\nHistory size: {history.size()}")
