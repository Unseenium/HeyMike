"""
Command Validator for Hey Mike! v2.0
Provides comprehensive validation and safety checks for voice commands
"""

import logging
import re
import os
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum

class ValidationResult(Enum):
    """Validation result types"""
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    REQUIRES_PERMISSION = "requires_permission"

class CommandValidator:
    """Validates voice commands for safety and security"""
    
    def __init__(self):
        """Initialize Command Validator"""
        self.logger = logging.getLogger(__name__)
        
        # Validation rules
        self.validation_rules = self._initialize_validation_rules()
        
        # User permissions
        self.user_permissions = {
            'restricted_commands': False,
            'system_modifications': False,
            'file_deletions': True,
            'terminal_access': True,
            'network_access': True
        }
        
        # Validation statistics
        self.total_validations = 0
        self.approved_commands = 0
        self.rejected_commands = 0
        self.confirmation_required = 0
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation rules for different command types"""
        return {
            'app_control': {
                'launch_app': {
                    'risk_level': 'low',
                    'required_params': ['app_name'],
                    'validation_func': self._validate_app_launch
                },
                'quit_app': {
                    'risk_level': 'medium',
                    'required_params': ['app_name'],
                    'validation_func': self._validate_app_quit
                },
                'force_quit_app': {
                    'risk_level': 'high',
                    'required_params': ['app_name'],
                    'validation_func': self._validate_force_quit
                }
            },
            'web_search': {
                'web_search': {
                    'risk_level': 'low',
                    'required_params': ['query'],
                    'validation_func': self._validate_web_search
                },
                'open_url': {
                    'risk_level': 'medium',
                    'required_params': ['url'],
                    'validation_func': self._validate_url_open
                }
            },
            'terminal': {
                'run_command': {
                    'risk_level': 'high',
                    'required_params': ['command'],
                    'validation_func': self._validate_terminal_command
                },
                'change_directory': {
                    'risk_level': 'low',
                    'required_params': ['path'],
                    'validation_func': self._validate_directory_change
                }
            },
            'system_control': {
                'volume_control': {
                    'risk_level': 'low',
                    'required_params': [],
                    'validation_func': self._validate_volume_control
                },
                'take_screenshot': {
                    'risk_level': 'low',
                    'required_params': [],
                    'validation_func': self._validate_screenshot
                },
                'system_restart': {
                    'risk_level': 'critical',
                    'required_params': [],
                    'validation_func': self._validate_system_restart
                },
                'system_shutdown': {
                    'risk_level': 'critical',
                    'required_params': [],
                    'validation_func': self._validate_system_shutdown
                }
            },
            'file_management': {
                'create_file': {
                    'risk_level': 'low',
                    'required_params': ['filename'],
                    'validation_func': self._validate_file_create
                },
                'delete_file': {
                    'risk_level': 'medium',
                    'required_params': ['filename'],
                    'validation_func': self._validate_file_delete
                },
                'delete_folder': {
                    'risk_level': 'high',
                    'required_params': ['foldername'],
                    'validation_func': self._validate_folder_delete
                }
            }
        }
    
    def validate_command(self, command_data: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """
        Validate a command for safety and security
        
        Args:
            command_data: Command data to validate
            
        Returns:
            Tuple of (validation_result, message)
        """
        self.total_validations += 1
        
        try:
            intent = command_data.get('intent', '')
            action = command_data.get('action', '')
            parameters = command_data.get('parameters', {})
            confidence = command_data.get('confidence', 0.0)
            
            # Basic structure validation
            if not intent or not action:
                self.rejected_commands += 1
                return ValidationResult.REJECTED, "Missing intent or action"
            
            # Confidence threshold check
            if confidence < 0.7:
                self.rejected_commands += 1
                return ValidationResult.REJECTED, f"Low confidence: {confidence:.2f}"
            
            # Get validation rules for this command
            intent_rules = self.validation_rules.get(intent, {})
            action_rules = intent_rules.get(action, {})
            
            if not action_rules:
                self.rejected_commands += 1
                return ValidationResult.REJECTED, f"Unknown command: {intent}.{action}"
            
            # Check required parameters
            required_params = action_rules.get('required_params', [])
            for param in required_params:
                if param not in parameters or not parameters[param]:
                    self.rejected_commands += 1
                    return ValidationResult.REJECTED, f"Missing required parameter: {param}"
            
            # Run specific validation function
            validation_func = action_rules.get('validation_func')
            if validation_func:
                result, message = validation_func(parameters)
                if result != ValidationResult.APPROVED:
                    if result == ValidationResult.REJECTED:
                        self.rejected_commands += 1
                    elif result == ValidationResult.REQUIRES_CONFIRMATION:
                        self.confirmation_required += 1
                    return result, message
            
            # Check risk level and permissions
            risk_level = action_rules.get('risk_level', 'medium')
            permission_result, permission_message = self._check_permissions(intent, action, risk_level)
            
            if permission_result != ValidationResult.APPROVED:
                if permission_result == ValidationResult.REJECTED:
                    self.rejected_commands += 1
                elif permission_result == ValidationResult.REQUIRES_CONFIRMATION:
                    self.confirmation_required += 1
                return permission_result, permission_message
            
            # Command approved
            self.approved_commands += 1
            self.logger.info(f"Command validated: {intent}.{action}")
            return ValidationResult.APPROVED, "Command validated successfully"
            
        except Exception as e:
            self.rejected_commands += 1
            self.logger.error(f"Validation error: {str(e)}")
            return ValidationResult.REJECTED, f"Validation error: {str(e)}"
    
    def _check_permissions(self, intent: str, action: str, risk_level: str) -> Tuple[ValidationResult, str]:
        """
        Check user permissions for command execution
        
        Args:
            intent: Command intent
            action: Command action
            risk_level: Risk level (low/medium/high/critical)
            
        Returns:
            Tuple of (validation_result, message)
        """
        # Critical commands require explicit permission
        if risk_level == 'critical':
            if not self.user_permissions.get('restricted_commands', False):
                return ValidationResult.REQUIRES_PERMISSION, "Critical commands require explicit permission"
        
        # High risk commands require confirmation
        if risk_level == 'high':
            return ValidationResult.REQUIRES_CONFIRMATION, "High-risk command requires confirmation"
        
        # Check specific permissions
        if intent == 'terminal' and not self.user_permissions.get('terminal_access', True):
            return ValidationResult.REJECTED, "Terminal access is disabled"
        
        if intent == 'file_management' and action.startswith('delete'):
            if not self.user_permissions.get('file_deletions', True):
                return ValidationResult.REJECTED, "File deletion is disabled"
        
        return ValidationResult.APPROVED, "Permissions check passed"
    
    # Specific validation functions
    
    def _validate_app_launch(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate app launch command"""
        app_name = parameters.get('app_name', '').strip()
        
        # Check for suspicious app names
        suspicious_apps = ['sudo', 'rm', 'format', 'diskutil']
        if app_name.lower() in suspicious_apps:
            return ValidationResult.REJECTED, f"Suspicious app name: {app_name}"
        
        return ValidationResult.APPROVED, "App launch validated"
    
    def _validate_app_quit(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate app quit command"""
        app_name = parameters.get('app_name', '').strip()
        
        # Check for critical system apps
        critical_apps = ['Finder', 'System Preferences', 'Activity Monitor']
        if app_name in critical_apps:
            return ValidationResult.REQUIRES_CONFIRMATION, f"Quitting {app_name} may affect system stability"
        
        return ValidationResult.APPROVED, "App quit validated"
    
    def _validate_force_quit(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate force quit command"""
        # Force quit always requires confirmation
        return ValidationResult.REQUIRES_CONFIRMATION, "Force quit requires confirmation"
    
    def _validate_web_search(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate web search command"""
        query = parameters.get('query', '').strip()
        
        # Check for potentially harmful search terms
        harmful_terms = ['hack', 'crack', 'pirate', 'illegal']
        query_lower = query.lower()
        
        for term in harmful_terms:
            if term in query_lower:
                return ValidationResult.REQUIRES_CONFIRMATION, f"Search contains potentially harmful term: {term}"
        
        return ValidationResult.APPROVED, "Web search validated"
    
    def _validate_url_open(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate URL open command"""
        url = parameters.get('url', '').strip()
        
        # Check for suspicious URLs
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Basic URL validation
        suspicious_patterns = ['localhost', '127.0.0.1', 'file://', 'javascript:']
        url_lower = url.lower()
        
        for pattern in suspicious_patterns:
            if pattern in url_lower:
                return ValidationResult.REQUIRES_CONFIRMATION, f"Suspicious URL pattern: {pattern}"
        
        return ValidationResult.APPROVED, "URL validated"
    
    def _validate_terminal_command(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate terminal command"""
        command = parameters.get('command', '').strip()
        command_lower = command.lower()
        
        # Dangerous command patterns
        dangerous_patterns = [
            'rm -rf /', 'sudo rm', 'format', 'mkfs', 'dd if=',
            'chmod -R 777 /', 'chown -R root', '> /dev/',
            'curl | sh', 'wget | sh', 'eval'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return ValidationResult.REJECTED, f"Dangerous command pattern: {pattern}"
        
        # Commands requiring confirmation
        confirmation_patterns = ['sudo', 'rm ', 'del ', 'kill ', 'pkill']
        
        for pattern in confirmation_patterns:
            if command_lower.startswith(pattern) or f' {pattern}' in command_lower:
                return ValidationResult.REQUIRES_CONFIRMATION, f"Command requires confirmation: {pattern}"
        
        return ValidationResult.APPROVED, "Terminal command validated"
    
    def _validate_directory_change(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate directory change command"""
        path = parameters.get('path', '').strip()
        
        # Check for system directories
        system_dirs = ['/System', '/usr', '/bin', '/sbin', '/etc']
        
        for sys_dir in system_dirs:
            if path.startswith(sys_dir):
                return ValidationResult.REQUIRES_CONFIRMATION, f"Accessing system directory: {sys_dir}"
        
        return ValidationResult.APPROVED, "Directory change validated"
    
    def _validate_volume_control(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate volume control command"""
        level = parameters.get('level')
        
        if level is not None:
            try:
                level_int = int(level)
                if level_int < 0 or level_int > 100:
                    return ValidationResult.REJECTED, "Volume level must be between 0 and 100"
            except ValueError:
                return ValidationResult.REJECTED, "Invalid volume level"
        
        return ValidationResult.APPROVED, "Volume control validated"
    
    def _validate_screenshot(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate screenshot command"""
        # Screenshots are generally safe
        return ValidationResult.APPROVED, "Screenshot validated"
    
    def _validate_system_restart(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate system restart command"""
        return ValidationResult.REQUIRES_CONFIRMATION, "System restart requires confirmation"
    
    def _validate_system_shutdown(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate system shutdown command"""
        return ValidationResult.REQUIRES_CONFIRMATION, "System shutdown requires confirmation"
    
    def _validate_file_create(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate file creation command"""
        filename = parameters.get('filename', '').strip()
        path = parameters.get('path', '')
        
        # Check for system paths
        if path:
            system_paths = ['/System', '/usr', '/bin', '/sbin', '/etc']
            for sys_path in system_paths:
                if path.startswith(sys_path):
                    return ValidationResult.REJECTED, f"Cannot create files in system directory: {sys_path}"
        
        # Check for suspicious file extensions
        suspicious_extensions = ['.sh', '.command', '.app', '.pkg', '.dmg']
        for ext in suspicious_extensions:
            if filename.lower().endswith(ext):
                return ValidationResult.REQUIRES_CONFIRMATION, f"Creating executable file: {ext}"
        
        return ValidationResult.APPROVED, "File creation validated"
    
    def _validate_file_delete(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate file deletion command"""
        filename = parameters.get('filename', '').strip()
        path = parameters.get('path', '')
        
        # Always require confirmation for file deletion
        return ValidationResult.REQUIRES_CONFIRMATION, f"File deletion requires confirmation: {filename}"
    
    def _validate_folder_delete(self, parameters: Dict[str, Any]) -> Tuple[ValidationResult, str]:
        """Validate folder deletion command"""
        foldername = parameters.get('foldername', '').strip()
        
        # Folder deletion is high risk
        return ValidationResult.REQUIRES_CONFIRMATION, f"Folder deletion requires confirmation: {foldername}"
    
    def set_user_permission(self, permission: str, enabled: bool) -> bool:
        """
        Set a user permission
        
        Args:
            permission: Permission name
            enabled: Whether to enable the permission
            
        Returns:
            True if permission was set successfully
        """
        if permission in self.user_permissions:
            self.user_permissions[permission] = enabled
            self.logger.info(f"Permission {permission} set to {enabled}")
            return True
        else:
            self.logger.error(f"Unknown permission: {permission}")
            return False
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Get validation statistics
        
        Returns:
            Dictionary with validation statistics
        """
        success_rate = (self.approved_commands / self.total_validations * 100) if self.total_validations > 0 else 0.0
        
        return {
            'total_validations': self.total_validations,
            'approved_commands': self.approved_commands,
            'rejected_commands': self.rejected_commands,
            'confirmation_required': self.confirmation_required,
            'success_rate': success_rate,
            'user_permissions': self.user_permissions.copy()
        }
    
    def reset_stats(self) -> None:
        """Reset validation statistics"""
        self.total_validations = 0
        self.approved_commands = 0
        self.rejected_commands = 0
        self.confirmation_required = 0
        self.logger.info("Validation statistics reset")
