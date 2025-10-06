"""
Voice Note Classifier for Hey Mike!
Detects trigger words and uses LLM to classify note types
"""

import logging
import json
import re
from typing import Optional, Dict, Any
from Core.MLXLLMManager import MLXLLMManager

class NoteClassifier:
    """Classifies voice commands for note capture using trigger words and LLM"""
    
    # Trigger word patterns - Keep it simple!
    # Only match explicit "capture:" at start, let LLM handle natural language
    TRIGGER_PATTERNS = {
        'capture': r'^capture[:\s]+(.+)',  # Explicit: "capture: description" or "capture bug: description"
    }
    
    # Explicit type patterns (e.g., "capture bug: description")
    EXPLICIT_TYPE_PATTERNS = {
        'bug': r'^capture\s+bug[:\s]+(.+)',
        'todo': r'^capture\s+(?:todo|task)[:\s]+(.+)',
        'question': r'^capture\s+question[:\s]+(.+)',
        'note': r'^capture\s+note[:\s]+(.+)',
        'enhancement': r'^capture\s+(?:enhancement|idea)[:\s]+(.+)',
    }
    
    def __init__(self, llm_manager: Optional[MLXLLMManager] = None):
        """
        Initialize Note Classifier
        
        Args:
            llm_manager: MLX LLM Manager instance (uses existing if None)
        """
        self.logger = logging.getLogger(__name__)
        self.llm = llm_manager or MLXLLMManager()
        
    def detect_trigger(self, text: str) -> Optional[str]:
        """
        Detect if text contains an explicit trigger word at the start
        
        Args:
            text: Transcribed text
            
        Returns:
            Trigger word if found, None otherwise
        """
        text_lower = text.lower().strip()
        
        for trigger, pattern in self.TRIGGER_PATTERNS.items():
            if re.match(pattern, text_lower, re.IGNORECASE):
                self.logger.info(f"Detected explicit trigger: {trigger}")
                return trigger
                
        return None
    
    def _clean_description(self, text: str) -> str:
        """
        Clean up description by removing filler words and meta instructions
        
        Args:
            text: Raw description text
            
        Returns:
            Cleaned description
        """
        # Remove common filler words and meta instructions
        filler_patterns = [
            r'\b(please|um|uh|like|you know)\b',
            r'\b(let .+ know|tell .+ |remind me to)\b',
            r'\b(about this|on this)\s*$',
            r'^\s*we\s+(?:need|should|must|want)\s+to\s+',  # "we need to" at start
        ]
        
        cleaned = text
        for pattern in filler_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove trailing punctuation artifacts
        cleaned = re.sub(r'\s+[,.]$', '', cleaned)
        
        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned
    
    def parse_capture_command(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse a capture command and classify the note type
        
        Args:
            text: Full transcribed text with trigger word
            
        Returns:
            Dict with 'type', 'description', and 'explicit' if parsed successfully
        """
        text_lower = text.lower().strip()
        
        # Check for explicit type first (e.g., "capture bug: ...")
        for note_type, pattern in self.EXPLICIT_TYPE_PATTERNS.items():
            match = re.match(pattern, text_lower, re.IGNORECASE)
            if match:
                description = self._clean_description(match.group(1).strip())
                self.logger.info(f"Explicit type detected: {note_type}")
                return {
                    'type': note_type,
                    'description': description,
                    'explicit': True
                }
        
        # Check for general capture at start (e.g., "capture: ...")
        match = re.match(self.TRIGGER_PATTERNS['capture'], text_lower, re.IGNORECASE)
        if match:
            description = self._clean_description(match.group(1).strip())
            
            # Use LLM to classify the type
            note_type = self.classify_note_type(description)
            
            return {
                'type': note_type,
                'description': description,
                'explicit': False
            }
        
        return None
    
    def classify_note_type(self, description: str) -> str:
        """
        Use LLM to classify the note type from description
        
        Args:
            description: Note description text
            
        Returns:
            Note type: 'bug', 'todo', 'question', 'note', or 'enhancement'
        """
        # If LLM not available, default to 'note'
        if not self.llm.is_model_loaded():
            self.logger.warning("LLM not loaded, defaulting to 'note' type")
            return 'note'
        
        try:
            # Prompt for classification
            prompt = f'''Classify this developer note into ONE category.

Note: "{description}"

Categories:
- bug: Error, issue, problem, broken, not working
- todo: Task, action item, need to do, should do
- question: Why, how, what, unclear, wondering
- enhancement: Improve, optimize, better, refactor, upgrade
- note: General observation, comment, reminder

Respond with ONLY the category name (bug/todo/question/enhancement/note). No explanation.

Category:'''

            # Get LLM response
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=10,
                temp=0.1  # Low temperature for consistent classification
            )
            
            # Extract classification from response
            classification = response.strip().lower()
            
            # Validate classification
            valid_types = ['bug', 'todo', 'question', 'enhancement', 'note']
            if classification in valid_types:
                self.logger.info(f"LLM classified as: {classification}")
                return classification
            else:
                # Try to find valid type in response
                for valid_type in valid_types:
                    if valid_type in classification:
                        self.logger.info(f"LLM classified as: {valid_type} (extracted)")
                        return valid_type
                
                # Default to 'note' if unclear
                self.logger.warning(f"Unclear classification: {classification}, defaulting to 'note'")
                return 'note'
                
        except Exception as e:
            self.logger.error(f"LLM classification failed: {e}, defaulting to 'note'")
            return 'note'
    
    def detect_intent_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Use LLM to detect intent when no explicit trigger word is found
        
        Args:
            text: Transcribed text
            
        Returns:
            Dict with 'intent', 'confidence', 'type', and 'description' if detected
        """
        # Only use LLM if it's loaded
        if not self.llm.is_model_loaded():
            self.logger.warning("LLM not loaded, cannot detect intent")
            return None
        
        try:
            # Prompt for intent detection  
            prompt = f'''Classify this voice command. Respond with ONLY valid JSON.

Text: "{text}"

If text contains "capture", "note", "bug", "todo", "save", "remember" → capture_note
If text contains "explain", "what does" → explain_code
If text contains "search", "find" → search_code
If text contains "open", "navigate", "go to" → navigate_file
Otherwise → paste_text

For capture_note, extract a CLEAN, CONCISE description:
1. Remove trigger words ("capture", "please", "note this", "save this")
2. Remove filler words ("um", "uh", "like", "you know")
3. Remove meta instructions ("let X know", "tell team", "remind me")
4. Remove weak preambles ("we need to", "we should", "we want to")
5. Keep only the core issue/task
6. Make it actionable and clear

Also classify type:
- bug: error, issue, problem, wrong, broken, confusing
- todo: need to, should, must, task, action
- question: why, how, what, wondering
- enhancement: improve, better, refactor, optimize
- note: general observation

IMPORTANT: Extract and CLEAN the description from the actual text above!

Example format:
{{"intent": "capture_note", "confidence": 0.95, "note_type": "bug", "description": "<cleaned core issue>"}}

Now classify and extract the text above. Respond with ONLY the JSON object:'''

            # Get LLM response
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=100,
                temp=0.1  # Low temperature for consistent classification
            )
            
            # Parse JSON response
            try:
                # Extract JSON from response (LLM might add extra text)
                json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                else:
                    result = json.loads(response.strip())
                
                # Validate response
                intent = result.get('intent', 'paste_text')
                confidence = float(result.get('confidence', 0.0))
                
                self.logger.info(f"LLM intent: {intent} (confidence: {confidence:.2f})")
                
                # Only return if confidence is high enough (>0.6)
                if confidence >= 0.6:
                    # If it's a capture_note intent, extract note type
                    if intent == 'capture_note':
                        note_type = result.get('note_type', 'note')
                        description = result.get('description', text).strip()
                        
                        # Apply fallback cleanup (in case LLM didn't clean properly)
                        description = self._clean_description(description)
                        
                        return {
                            'intent': 'capture_note',
                            'type': note_type,
                            'description': description,
                            'confidence': confidence,
                            'explicit': False
                        }
                    else:
                        # Other intents (explain, search, navigate)
                        return {
                            'intent': intent,
                            'description': result.get('description', text).strip(),
                            'confidence': confidence
                        }
                else:
                    self.logger.info(f"Confidence too low ({confidence:.2f} < 0.6), defaulting to paste")
                    return None
                    
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse LLM JSON response: {e}")
                self.logger.debug(f"LLM response: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"LLM intent detection failed: {e}")
            return None
    
    def smart_detect_intent(self, text: str) -> Dict[str, Any]:
        """
        Smart hybrid intent detection: Regex (fast) → LLM (flexible)
        
        Args:
            text: Transcribed text
            
        Returns:
            Dict with intent information
        """
        # Stage 1: Fast path - Check for explicit trigger words (regex)
        trigger = self.detect_trigger(text)
        
        if trigger == 'capture':
            # Parse with regex first
            capture_data = self.parse_capture_command(text)
            if capture_data:
                capture_data['method'] = 'regex'
                self.logger.info(f"Intent detected via regex: capture_note (type: {capture_data['type']})")
                return {
                    'intent': 'capture_note',
                    'data': capture_data,
                    'method': 'regex'
                }
        
        # Stage 2: Slow path - Use LLM for natural language understanding
        self.logger.info("No explicit trigger found, trying LLM intent detection...")
        llm_intent = self.detect_intent_with_llm(text)
        
        if llm_intent:
            if llm_intent['intent'] == 'capture_note':
                llm_intent['method'] = 'llm'
                return {
                    'intent': 'capture_note',
                    'data': {
                        'type': llm_intent['type'],
                        'description': llm_intent['description'],
                        'explicit': False,
                        'confidence': llm_intent['confidence']
                    },
                    'method': 'llm'
                }
            else:
                # Other intents (explain, search, navigate)
                return {
                    'intent': llm_intent['intent'],
                    'data': llm_intent,
                    'method': 'llm'
                }
        
        # Stage 3: Default - Paste text
        self.logger.info("No intent detected, defaulting to paste")
        return {
            'intent': 'paste_text',
            'data': {'text': text},
            'method': 'default'
        }
