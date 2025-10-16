"""
Text Enhancer for Hey Mike!
Uses LLM to improve transcribed text quality
"""

import logging
from typing import Optional, Dict, Any
from Core.MLXLLMManager import MLXLLMManager

class TextEnhancer:
    """Enhances transcribed text using local LLM"""
    
    # Simple enhancement prompt (restored from working version)
    ENHANCEMENT_PROMPT = """Fix this transcribed speech by adding punctuation, fixing capitalization, and removing filler words (um, uh, like, you know). Output ONLY the corrected text, nothing else.

{text}"""
    
    def __init__(self, llm_manager: Optional[MLXLLMManager] = None):
        """
        Initialize Text Enhancer
        
        Args:
            llm_manager: MLX LLM Manager instance (creates new if None)
        """
        self.logger = logging.getLogger(__name__)
        self.llm = llm_manager or MLXLLMManager()
        self.enabled = True
        
        # Performance tracking
        self.enhancement_count = 0
        self.total_enhancement_time = 0.0
    
    def enhance(self, text: str) -> str:
        """
        Enhance transcribed text with LLM
        
        Args:
            text: Raw transcribed text
            
        Returns:
            Enhanced text, or original if enhancement fails/disabled
        """
        # Return original if disabled
        if not self.enabled:
            self.logger.debug("Enhancement disabled, returning original text")
            return text
        
        # Return original if text is too short
        if len(text.strip()) < 5:
            self.logger.debug("Text too short for enhancement")
            return text
        
        # Check if LLM is available
        if not self.llm.is_model_loaded():
            self.logger.warning("LLM not loaded, returning original text")
            return text
        
        try:
            import time
            start_time = time.time()
            
            # Create prompt
            prompt = self.ENHANCEMENT_PROMPT.format(text=text)
            
            self.logger.info("Enhancing text")
            self.logger.debug(f"Original: {text}")
            
            # Generate enhanced text
            enhanced = self.llm.generate(
                prompt=prompt,
                max_tokens=len(text.split()) * 2 + 50,  # Roughly 2x words + buffer
                temp=0.3  # Low temperature for consistency
            )
            
            if enhanced:
                # Clean up the response (remove any extra formatting)
                enhanced = enhanced.strip()
                
                # Remove common LLM artifacts
                enhanced = self._clean_llm_output(enhanced)
                
                # Track performance
                elapsed = time.time() - start_time
                self.enhancement_count += 1
                self.total_enhancement_time += elapsed
                
                self.logger.info(f"Enhanced text in {elapsed:.2f}s")
                self.logger.debug(f"Enhanced: {enhanced}")
                
                return enhanced
            else:
                self.logger.warning("LLM returned empty result, using original")
                return text
                
        except Exception as e:
            self.logger.error(f"Enhancement failed: {str(e)}")
            return text
    
    def enhance_async(self, text: str, callback: Optional[callable] = None) -> None:
        """
        Enhance text asynchronously
        
        Args:
            text: Raw transcribed text
            callback: Callback function that receives enhanced text
        """
        import threading
        
        def enhance_thread():
            enhanced = self.enhance(text)
            if callback:
                callback(enhanced)
        
        thread = threading.Thread(target=enhance_thread, daemon=True)
        thread.start()
    
    def _clean_llm_output(self, text: str) -> str:
        """
        Clean up LLM output artifacts
        
        Args:
            text: Raw LLM output
            
        Returns:
            Cleaned text
        """
        # Remove common LLM prefixes (case-insensitive, check first line)
        lines = text.split('\n')
        first_line_lower = lines[0].lower().strip()
        
        preamble_phrases = [
            "here's", "here is", "improved version", "corrected", 
            "cleaned", "fixed", "professional version", "revised"
        ]
        
        # If first line is a preamble, remove it
        if any(phrase in first_line_lower for phrase in preamble_phrases):
            if len(lines) > 1:
                text = '\n'.join(lines[1:])
        
        text = text.strip()
        
        # Remove excessive line breaks (LLM sometimes adds them)
        # Replace multiple newlines with single space
        text = ' '.join(line.strip() for line in text.split('\n') if line.strip())
        
        # Remove markdown formatting
        text = text.replace("**", "").replace("__", "").replace("*", "")
        
        # Remove quotes if the entire text is quoted
        if (text.startswith('"') and text.endswith('"')) or \
           (text.startswith("'") and text.endswith("'")):
            text = text[1:-1].strip()
        
        # Remove any remaining leading/trailing colons or dashes
        text = text.strip(':-').strip()
        
        return text
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable text enhancement"""
        self.enabled = enabled
        self.logger.info(f"Text enhancement {'enabled' if enabled else 'disabled'}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get enhancement statistics
        
        Returns:
            Dictionary with enhancement stats
        """
        avg_time = (self.total_enhancement_time / self.enhancement_count 
                   if self.enhancement_count > 0 else 0.0)
        
        return {
            'enabled': self.enabled,
            'enhancement_count': self.enhancement_count,
            'total_time': self.total_enhancement_time,
            'average_time': avg_time
        }
