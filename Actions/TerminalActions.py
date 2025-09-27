"""
Terminal Actions for Hey Mike! v2.0
Handles terminal and shell command execution
"""

import logging
import subprocess
import os
import shlex
from typing import Dict, Any, Tuple, List

class TerminalActions:
    """Handles terminal and shell command execution"""
    
    def __init__(self):
        """Initialize Terminal Actions"""
        self.logger = logging.getLogger(__name__)
        
        # Current working directory tracking
        self.current_directory = os.path.expanduser("~")
        
        # Dangerous command patterns to block
        self.dangerous_patterns = [
            'rm -rf /',
            'sudo rm -rf',
            'format',
            'mkfs',
            'dd if=',
            '> /dev/',
            'chmod -R 777 /',
            'chown -R root /',
        ]
        
        # Safe commands that don't need special handling
        self.safe_commands = [
            'ls', 'pwd', 'cd', 'mkdir', 'touch', 'cat', 'less', 'more',
            'grep', 'find', 'which', 'whereis', 'man', 'history',
            'echo', 'date', 'whoami', 'id', 'uname', 'uptime',
            'ps', 'top', 'df', 'du', 'free', 'mount',
        ]
    
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute a terminal action
        
        Args:
            action: Action to execute
            parameters: Action parameters
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if action == 'run_command':
                return self._run_command(parameters)
            elif action == 'change_directory':
                return self._change_directory(parameters)
            elif action == 'list_files':
                return self._list_files(parameters)
            elif action == 'create_directory':
                return self._create_directory(parameters)
            else:
                return False, f"Unknown terminal action: {action}"
                
        except Exception as e:
            self.logger.error(f"Terminal action failed: {str(e)}")
            return False, f"Terminal action failed: {str(e)}"
    
    def _run_command(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Run a shell command
        
        Args:
            parameters: Must contain 'command', optionally 'directory'
            
        Returns:
            Tuple of (success, message)
        """
        command = parameters.get('command', '').strip()
        if not command:
            return False, "No command provided"
        
        directory = parameters.get('directory', self.current_directory)
        
        # Security check
        if not self._is_command_safe(command):
            return False, f"Command blocked for security: {command}"
        
        try:
            # Parse command safely
            cmd_parts = shlex.split(command)
            
            # Execute command
            result = subprocess.run(
                cmd_parts,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Prepare output
            output_lines = []
            if result.stdout:
                output_lines.append(f"Output: {result.stdout.strip()}")
            if result.stderr:
                output_lines.append(f"Error: {result.stderr.strip()}")
            
            if result.returncode == 0:
                self.logger.info(f"Command executed successfully: {command}")
                output = "\n".join(output_lines) if output_lines else "Command completed successfully"
                return True, output
            else:
                self.logger.warning(f"Command failed with code {result.returncode}: {command}")
                output = "\n".join(output_lines) if output_lines else f"Command failed with exit code {result.returncode}"
                return False, output
                
        except subprocess.TimeoutExpired:
            return False, f"Command timed out: {command}"
        except Exception as e:
            return False, f"Error executing command: {str(e)}"
    
    def _change_directory(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Change current directory
        
        Args:
            parameters: Must contain 'path'
            
        Returns:
            Tuple of (success, message)
        """
        path = parameters.get('path', '').strip()
        if not path:
            return False, "No path provided"
        
        # Handle special paths
        if path == '~':
            path = os.path.expanduser("~")
        elif path == '..':
            path = os.path.dirname(self.current_directory)
        elif not os.path.isabs(path):
            # Relative path
            path = os.path.join(self.current_directory, path)
        
        # Normalize path
        path = os.path.normpath(path)
        
        try:
            if os.path.exists(path) and os.path.isdir(path):
                self.current_directory = path
                self.logger.info(f"Changed directory to: {path}")
                return True, f"Changed directory to {path}"
            else:
                return False, f"Directory does not exist: {path}"
                
        except Exception as e:
            return False, f"Error changing directory: {str(e)}"
    
    def _list_files(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        List files in a directory
        
        Args:
            parameters: Optionally contains 'path', 'show_hidden'
            
        Returns:
            Tuple of (success, message)
        """
        path = parameters.get('path', self.current_directory)
        show_hidden = parameters.get('show_hidden', False)
        
        try:
            if not os.path.exists(path):
                return False, f"Path does not exist: {path}"
            
            if not os.path.isdir(path):
                return False, f"Path is not a directory: {path}"
            
            # List directory contents
            items = os.listdir(path)
            
            # Filter hidden files if requested
            if not show_hidden:
                items = [item for item in items if not item.startswith('.')]
            
            # Sort items
            items.sort()
            
            # Separate directories and files
            directories = []
            files = []
            
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    directories.append(f"📁 {item}")
                else:
                    files.append(f"📄 {item}")
            
            # Format output
            output_lines = [f"Contents of {path}:"]
            output_lines.extend(directories)
            output_lines.extend(files)
            
            if not items:
                output_lines.append("(empty directory)")
            
            self.logger.info(f"Listed {len(items)} items in {path}")
            return True, "\n".join(output_lines)
            
        except Exception as e:
            return False, f"Error listing files: {str(e)}"
    
    def _create_directory(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Create a directory
        
        Args:
            parameters: Must contain 'name', optionally 'path'
            
        Returns:
            Tuple of (success, message)
        """
        name = parameters.get('name', '').strip()
        if not name:
            return False, "No directory name provided"
        
        base_path = parameters.get('path', self.current_directory)
        full_path = os.path.join(base_path, name)
        
        try:
            os.makedirs(full_path, exist_ok=False)
            self.logger.info(f"Created directory: {full_path}")
            return True, f"Created directory: {full_path}"
            
        except FileExistsError:
            return False, f"Directory already exists: {full_path}"
        except Exception as e:
            return False, f"Error creating directory: {str(e)}"
    
    def _is_command_safe(self, command: str) -> bool:
        """
        Check if a command is safe to execute
        
        Args:
            command: Command to check
            
        Returns:
            True if command is safe
        """
        command_lower = command.lower().strip()
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern in command_lower:
                self.logger.warning(f"Blocked dangerous command pattern: {pattern}")
                return False
        
        # Check for sudo commands (require special handling)
        if command_lower.startswith('sudo'):
            self.logger.warning("Sudo commands require explicit permission")
            return False
        
        # Check for commands that modify system files
        system_paths = ['/bin/', '/usr/', '/etc/', '/var/', '/sys/', '/proc/']
        for path in system_paths:
            if path in command_lower and ('rm' in command_lower or 'del' in command_lower):
                self.logger.warning(f"Blocked system file modification: {command}")
                return False
        
        return True
    
    def get_current_directory(self) -> str:
        """
        Get current working directory
        
        Returns:
            Current directory path
        """
        return self.current_directory
    
    def can_execute(self, action: str) -> bool:
        """
        Check if this module can execute the given action
        
        Args:
            action: Action to check
            
        Returns:
            True if action is supported
        """
        supported_actions = ['run_command', 'change_directory', 'list_files', 'create_directory']
        return action in supported_actions
    
    def test_module(self) -> Dict[str, Any]:
        """
        Test the terminal actions module
        
        Returns:
            Test results
        """
        test_results = {
            'module_name': 'TerminalActions',
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'details': []
        }
        
        # Test 1: Command safety check
        test_results['tests_run'] += 1
        try:
            safe_cmd = self._is_command_safe('ls -la')
            dangerous_cmd = self._is_command_safe('rm -rf /')
            if safe_cmd and not dangerous_cmd:
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'command_safety', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'command_safety', 'status': 'failed', 'error': f'Safe: {safe_cmd}, Dangerous: {dangerous_cmd}'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'command_safety', 'status': 'failed', 'error': str(e)})
        
        # Test 2: Directory operations
        test_results['tests_run'] += 1
        try:
            current_dir = self.get_current_directory()
            if os.path.exists(current_dir):
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'directory_operations', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'directory_operations', 'status': 'failed', 'error': f'Current directory does not exist: {current_dir}'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'directory_operations', 'status': 'failed', 'error': str(e)})
        
        # Test 3: Can execute check
        test_results['tests_run'] += 1
        try:
            can_run = self.can_execute('run_command')
            can_invalid = self.can_execute('invalid_action')
            if can_run and not can_invalid:
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'can_execute', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'can_execute', 'status': 'failed', 'error': 'Unexpected can_execute results'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'can_execute', 'status': 'failed', 'error': str(e)})
        
        return test_results
