"""
Command Processor for Hey Mike! v2.0
Handles command interpretation, validation, and routing
"""

import logging
import time
from typing import Optional, Callable, Dict, Any, List
from enum import Enum

class CommandIntent(Enum):
    """Supported command intents"""
    APP_CONTROL = "app_control"
    WEB_SEARCH = "web_search"
    TERMINAL = "terminal"
    SYSTEM_CONTROL = "system_control"
    FILE_MANAGEMENT = "file_management"
    UNKNOWN = "unknown"

class CommandSafety(Enum):
    """Command safety levels"""
    SAFE = "safe"           # Auto-execute
    CAUTION = "caution"     # Confirm first
    RESTRICTED = "restricted"  # Require explicit enable

class CommandProcessor:
    """Processes and validates voice commands"""
    
    def __init__(self):
        """Initialize Command Processor"""
        self.logger = logging.getLogger(__name__)
        
        # Command processing statistics
        self.total_commands = 0
        self.successful_commands = 0
        self.failed_commands = 0
        self.command_history = []
        
        # Safety configuration
        self.safety_rules = self._initialize_safety_rules()
        self.restricted_commands_enabled = False
        
        # Callbacks
        self.on_command_processed: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_command_validated: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_command_rejected: Optional[Callable[[str, str], None]] = None
        self.on_confirmation_required: Optional[Callable[[Dict[str, Any]], None]] = None
    
    def _initialize_safety_rules(self) -> Dict[str, Dict[str, CommandSafety]]:
        """Initialize command safety rules"""
        return {
            CommandIntent.APP_CONTROL.value: {
                'launch_app': CommandSafety.SAFE,
                'quit_app': CommandSafety.CAUTION,
                'force_quit_app': CommandSafety.RESTRICTED,
                'switch_app': CommandSafety.SAFE,
            },
            CommandIntent.WEB_SEARCH.value: {
                'web_search': CommandSafety.SAFE,
                'open_url': CommandSafety.SAFE,
                'download_file': CommandSafety.CAUTION,
            },
            CommandIntent.TERMINAL.value: {
                'run_command': CommandSafety.CAUTION,
                'change_directory': CommandSafety.SAFE,
                'list_files': CommandSafety.SAFE,
                'sudo_command': CommandSafety.RESTRICTED,
                'rm_command': CommandSafety.RESTRICTED,
            },
            CommandIntent.SYSTEM_CONTROL.value: {
                'volume_control': CommandSafety.SAFE,
                'brightness_control': CommandSafety.SAFE,
                'take_screenshot': CommandSafety.SAFE,
                'system_sleep': CommandSafety.CAUTION,
                'system_restart': CommandSafety.RESTRICTED,
                'system_shutdown': CommandSafety.RESTRICTED,
            },
            CommandIntent.FILE_MANAGEMENT.value: {
                'create_file': CommandSafety.SAFE,
                'create_folder': CommandSafety.SAFE,
                'move_file': CommandSafety.CAUTION,
                'copy_file': CommandSafety.SAFE,
                'delete_file': CommandSafety.CAUTION,
                'delete_folder': CommandSafety.RESTRICTED,
            }
        }
    
    def process_command(self, command_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process and validate a command from LLM interpretation
        
        Args:
            command_data: Command data from LLM interpretation
            
        Returns:
            Processed command data or None if invalid/rejected
        """
        self.total_commands += 1
        
        try:
            # Validate command structure
            if not self._validate_command_structure(command_data):
                self.failed_commands += 1
                return None
            
            # Enrich command with metadata
            enriched_command = self._enrich_command(command_data)
            
            # Determine safety level
            safety_level = self._determine_safety_level(enriched_command)
            enriched_command['safety_level'] = safety_level.value
            
            # Apply safety validation
            if not self._validate_command_safety(enriched_command):
                self.failed_commands += 1
                return None
            
            # Check if confirmation is required
            if safety_level == CommandSafety.CAUTION:
                enriched_command['requires_confirmation'] = True
                if self.on_confirmation_required:
                    self.on_confirmation_required(enriched_command)
            
            # Log successful processing
            self.successful_commands += 1
            self._log_command(enriched_command)
            
            if self.on_command_processed:
                self.on_command_processed(enriched_command)
            
            return enriched_command
            
        except Exception as e:
            self.logger.error(f"Command processing failed: {str(e)}")
            self.failed_commands += 1
            return None
    
    def _validate_command_structure(self, command_data: Dict[str, Any]) -> bool:
        """
        Validate that command has required structure
        
        Args:
            command_data: Command data to validate
            
        Returns:
            True if structure is valid
        """
        required_fields = ['intent', 'action', 'parameters', 'confidence']
        
        for field in required_fields:
            if field not in command_data:
                self.logger.error(f"Missing required field: {field}")
                if self.on_command_rejected:
                    self.on_command_rejected(str(command_data), f"Missing field: {field}")
                return False
        
        # Validate intent
        try:
            CommandIntent(command_data['intent'])
        except ValueError:
            self.logger.error(f"Invalid intent: {command_data['intent']}")
            if self.on_command_rejected:
                self.on_command_rejected(str(command_data), f"Invalid intent: {command_data['intent']}")
            return False
        
        # Validate confidence
        confidence = command_data.get('confidence', 0.0)
        if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
            self.logger.error(f"Invalid confidence: {confidence}")
            if self.on_command_rejected:
                self.on_command_rejected(str(command_data), f"Invalid confidence: {confidence}")
            return False
        
        # Validate parameters
        if not isinstance(command_data['parameters'], dict):
            self.logger.error("Parameters must be a dictionary")
            if self.on_command_rejected:
                self.on_command_rejected(str(command_data), "Parameters must be a dictionary")
            return False
        
        return True
    
    def _enrich_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich command with additional metadata
        
        Args:
            command_data: Original command data
            
        Returns:
            Enriched command data
        """
        enriched = command_data.copy()
        
        # Add processing metadata
        enriched['processed_at'] = time.time()
        enriched['command_id'] = f"cmd_{int(time.time() * 1000)}"
        
        # Normalize intent and action
        enriched['intent'] = enriched['intent'].lower()
        enriched['action'] = enriched['action'].lower()
        
        # Add command description for logging
        enriched['description'] = self._generate_command_description(enriched)
        
        return enriched
    
    def _generate_command_description(self, command_data: Dict[str, Any]) -> str:
        """
        Generate human-readable command description
        
        Args:
            command_data: Command data
            
        Returns:
            Human-readable description
        """
        intent = command_data['intent']
        action = command_data['action']
        params = command_data['parameters']
        
        if intent == CommandIntent.APP_CONTROL.value:
            if action == 'launch_app':
                return f"Launch {params.get('app_name', 'unknown app')}"
            elif action == 'quit_app':
                return f"Quit {params.get('app_name', 'unknown app')}"
        
        elif intent == CommandIntent.WEB_SEARCH.value:
            if action == 'web_search':
                return f"Search for '{params.get('query', 'unknown query')}'"
            elif action == 'open_url':
                return f"Open URL: {params.get('url', 'unknown URL')}"
        
        elif intent == CommandIntent.TERMINAL.value:
            if action == 'run_command':
                return f"Run terminal command: {params.get('command', 'unknown command')}"
            elif action == 'change_directory':
                return f"Change directory to {params.get('path', 'unknown path')}"
        
        elif intent == CommandIntent.SYSTEM_CONTROL.value:
            if action == 'volume_control':
                return f"Set volume to {params.get('level', 'unknown level')}"
            elif action == 'take_screenshot':
                return "Take screenshot"
        
        elif intent == CommandIntent.FILE_MANAGEMENT.value:
            if action == 'create_file':
                return f"Create file: {params.get('filename', 'unknown file')}"
            elif action == 'delete_file':
                return f"Delete file: {params.get('filename', 'unknown file')}"
        
        return f"{intent}: {action}"
    
    def _determine_safety_level(self, command_data: Dict[str, Any]) -> CommandSafety:
        """
        Determine safety level for a command
        
        Args:
            command_data: Command data
            
        Returns:
            Safety level for the command
        """
        intent = command_data['intent']
        action = command_data['action']
        
        # Get safety rules for this intent
        intent_rules = self.safety_rules.get(intent, {})
        
        # Get safety level for this specific action
        safety_level = intent_rules.get(action, CommandSafety.CAUTION)
        
        # Additional safety checks based on parameters
        params = command_data['parameters']
        
        # Terminal commands with dangerous patterns
        if intent == CommandIntent.TERMINAL.value:
            command = params.get('command', '').lower()
            dangerous_patterns = ['rm -rf', 'sudo rm', 'format', 'mkfs', 'dd if=']
            if any(pattern in command for pattern in dangerous_patterns):
                safety_level = CommandSafety.RESTRICTED
        
        # File operations on system directories
        if intent == CommandIntent.FILE_MANAGEMENT.value:
            path = params.get('path', '').lower()
            system_paths = ['/system', '/usr', '/bin', '/sbin', '/etc']
            if any(path.startswith(sys_path) for sys_path in system_paths):
                safety_level = CommandSafety.RESTRICTED
        
        return safety_level
    
    def _validate_command_safety(self, command_data: Dict[str, Any]) -> bool:
        """
        Validate command against safety rules
        
        Args:
            command_data: Command data to validate
            
        Returns:
            True if command is allowed to execute
        """
        safety_level = CommandSafety(command_data['safety_level'])
        
        # Always allow safe commands
        if safety_level == CommandSafety.SAFE:
            return True
        
        # Allow caution commands (they'll require confirmation)
        if safety_level == CommandSafety.CAUTION:
            return True
        
        # Only allow restricted commands if explicitly enabled
        if safety_level == CommandSafety.RESTRICTED:
            if not self.restricted_commands_enabled:
                self.logger.warning(f"Restricted command blocked: {command_data['description']}")
                if self.on_command_rejected:
                    self.on_command_rejected(
                        command_data['description'],
                        "Restricted commands are disabled"
                    )
                return False
        
        return True
    
    def _log_command(self, command_data: Dict[str, Any]) -> None:
        """
        Log command to history
        
        Args:
            command_data: Command data to log
        """
        log_entry = {
            'timestamp': command_data['processed_at'],
            'command_id': command_data['command_id'],
            'description': command_data['description'],
            'intent': command_data['intent'],
            'action': command_data['action'],
            'safety_level': command_data['safety_level'],
            'confidence': command_data['confidence']
        }
        
        self.command_history.append(log_entry)
        
        # Keep only recent history
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-50:]
        
        self.logger.info(f"Command processed: {command_data['description']} "
                        f"(safety: {command_data['safety_level']}, "
                        f"confidence: {command_data['confidence']:.2f})")
    
    def enable_restricted_commands(self, enabled: bool) -> None:
        """
        Enable or disable restricted commands
        
        Args:
            enabled: Whether to enable restricted commands
        """
        self.restricted_commands_enabled = enabled
        self.logger.info(f"Restricted commands {'enabled' if enabled else 'disabled'}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get command processing statistics
        
        Returns:
            Dictionary with processing statistics
        """
        success_rate = (self.successful_commands / self.total_commands * 100) if self.total_commands > 0 else 0.0
        
        return {
            'total_commands': self.total_commands,
            'successful_commands': self.successful_commands,
            'failed_commands': self.failed_commands,
            'success_rate': success_rate,
            'restricted_commands_enabled': self.restricted_commands_enabled,
            'recent_commands': len([cmd for cmd in self.command_history 
                                  if time.time() - cmd['timestamp'] < 3600])
        }
    
    def get_recent_commands(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent command history
        
        Args:
            count: Number of recent commands to return
            
        Returns:
            List of recent commands
        """
        return self.command_history[-count:] if self.command_history else []
    
    def clear_history(self) -> None:
        """Clear command history"""
        self.command_history.clear()
        self.logger.info("Command history cleared")
    
    def test_command_validation(self) -> List[Dict[str, Any]]:
        """
        Test command validation with sample commands
        
        Returns:
            List of test results
        """
        test_commands = [
            {
                'intent': 'app_control',
                'action': 'launch_app',
                'parameters': {'app_name': 'Chrome'},
                'confidence': 0.95
            },
            {
                'intent': 'terminal',
                'action': 'run_command',
                'parameters': {'command': 'rm -rf /'},
                'confidence': 0.8
            },
            {
                'intent': 'system_control',
                'action': 'take_screenshot',
                'parameters': {},
                'confidence': 0.9
            },
            {
                'intent': 'invalid_intent',
                'action': 'test',
                'parameters': {},
                'confidence': 0.7
            }
        ]
        
        results = []
        for cmd in test_commands:
            processed = self.process_command(cmd)
            results.append({
                'input': cmd,
                'processed': processed is not None,
                'safety_level': processed['safety_level'] if processed else None,
                'description': processed['description'] if processed else None
            })
        
        return results
