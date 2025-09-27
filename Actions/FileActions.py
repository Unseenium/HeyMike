"""
File Actions for Hey Mike! v2.0
Handles file management commands
"""

import logging
import os
import shutil
from typing import Dict, Any, Tuple
from datetime import datetime

class FileActions:
    """Handles file management commands"""
    
    def __init__(self):
        """Initialize File Actions"""
        self.logger = logging.getLogger(__name__)
        
        # Default working directory
        self.working_directory = os.path.expanduser("~")
        
        # Protected system directories
        self.protected_dirs = [
            '/System', '/usr', '/bin', '/sbin', '/etc', '/var/root',
            '/private/etc', '/private/var', '/Library/System'
        ]
    
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute a file management action
        
        Args:
            action: Action to execute
            parameters: Action parameters
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if action == 'create_file':
                return self._create_file(parameters)
            elif action == 'create_folder':
                return self._create_folder(parameters)
            elif action == 'move_file':
                return self._move_file(parameters)
            elif action == 'copy_file':
                return self._copy_file(parameters)
            elif action == 'delete_file':
                return self._delete_file(parameters)
            elif action == 'delete_folder':
                return self._delete_folder(parameters)
            elif action == 'rename_file':
                return self._rename_file(parameters)
            else:
                return False, f"Unknown file action: {action}"
                
        except Exception as e:
            self.logger.error(f"File action failed: {str(e)}")
            return False, f"File action failed: {str(e)}"
    
    def _create_file(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Create a new file
        
        Args:
            parameters: Must contain 'filename', optionally 'path', 'content'
            
        Returns:
            Tuple of (success, message)
        """
        filename = parameters.get('filename', '').strip()
        if not filename:
            return False, "No filename provided"
        
        path = parameters.get('path', self.working_directory)
        content = parameters.get('content', '')
        
        # Create full path
        if not os.path.isabs(filename):
            filepath = os.path.join(path, filename)
        else:
            filepath = filename
        
        # Security check
        if not self._is_path_safe(filepath):
            return False, f"Cannot create file in protected location: {filepath}"
        
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Create file
            with open(filepath, 'w') as f:
                f.write(content)
            
            self.logger.info(f"Created file: {filepath}")
            return True, f"Created file: {filepath}"
            
        except Exception as e:
            return False, f"Error creating file: {str(e)}"
    
    def _create_folder(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Create a new folder
        
        Args:
            parameters: Must contain 'foldername', optionally 'path'
            
        Returns:
            Tuple of (success, message)
        """
        foldername = parameters.get('foldername', '').strip()
        if not foldername:
            return False, "No folder name provided"
        
        path = parameters.get('path', self.working_directory)
        
        # Create full path
        if not os.path.isabs(foldername):
            folderpath = os.path.join(path, foldername)
        else:
            folderpath = foldername
        
        # Security check
        if not self._is_path_safe(folderpath):
            return False, f"Cannot create folder in protected location: {folderpath}"
        
        try:
            os.makedirs(folderpath, exist_ok=False)
            self.logger.info(f"Created folder: {folderpath}")
            return True, f"Created folder: {folderpath}"
            
        except FileExistsError:
            return False, f"Folder already exists: {folderpath}"
        except Exception as e:
            return False, f"Error creating folder: {str(e)}"
    
    def _move_file(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Move a file or folder
        
        Args:
            parameters: Must contain 'source' and 'destination'
            
        Returns:
            Tuple of (success, message)
        """
        source = parameters.get('source', '').strip()
        destination = parameters.get('destination', '').strip()
        
        if not source or not destination:
            return False, "Source and destination paths required"
        
        # Make paths absolute if needed
        if not os.path.isabs(source):
            source = os.path.join(self.working_directory, source)
        if not os.path.isabs(destination):
            destination = os.path.join(self.working_directory, destination)
        
        # Security checks
        if not self._is_path_safe(source) or not self._is_path_safe(destination):
            return False, "Cannot move files in protected locations"
        
        try:
            if not os.path.exists(source):
                return False, f"Source does not exist: {source}"
            
            # Create destination directory if needed
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            shutil.move(source, destination)
            self.logger.info(f"Moved {source} to {destination}")
            return True, f"Moved {os.path.basename(source)} to {destination}"
            
        except Exception as e:
            return False, f"Error moving file: {str(e)}"
    
    def _copy_file(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Copy a file or folder
        
        Args:
            parameters: Must contain 'source' and 'destination'
            
        Returns:
            Tuple of (success, message)
        """
        source = parameters.get('source', '').strip()
        destination = parameters.get('destination', '').strip()
        
        if not source or not destination:
            return False, "Source and destination paths required"
        
        # Make paths absolute if needed
        if not os.path.isabs(source):
            source = os.path.join(self.working_directory, source)
        if not os.path.isabs(destination):
            destination = os.path.join(self.working_directory, destination)
        
        # Security checks
        if not self._is_path_safe(source) or not self._is_path_safe(destination):
            return False, "Cannot copy files in protected locations"
        
        try:
            if not os.path.exists(source):
                return False, f"Source does not exist: {source}"
            
            # Create destination directory if needed
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            
            self.logger.info(f"Copied {source} to {destination}")
            return True, f"Copied {os.path.basename(source)} to {destination}"
            
        except Exception as e:
            return False, f"Error copying file: {str(e)}"
    
    def _delete_file(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Delete a file
        
        Args:
            parameters: Must contain 'filename' or 'path'
            
        Returns:
            Tuple of (success, message)
        """
        filename = parameters.get('filename', '').strip()
        filepath = parameters.get('path', '').strip()
        
        if not filename and not filepath:
            return False, "No file specified"
        
        # Determine full path
        if filepath:
            if not os.path.isabs(filepath):
                filepath = os.path.join(self.working_directory, filepath)
        else:
            if not os.path.isabs(filename):
                filepath = os.path.join(self.working_directory, filename)
            else:
                filepath = filename
        
        # Security check
        if not self._is_path_safe(filepath):
            return False, f"Cannot delete file in protected location: {filepath}"
        
        try:
            if not os.path.exists(filepath):
                return False, f"File does not exist: {filepath}"
            
            if os.path.isdir(filepath):
                return False, f"Path is a directory, use delete_folder instead: {filepath}"
            
            os.remove(filepath)
            self.logger.info(f"Deleted file: {filepath}")
            return True, f"Deleted file: {os.path.basename(filepath)}"
            
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    def _delete_folder(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Delete a folder
        
        Args:
            parameters: Must contain 'foldername' or 'path'
            
        Returns:
            Tuple of (success, message)
        """
        foldername = parameters.get('foldername', '').strip()
        folderpath = parameters.get('path', '').strip()
        
        if not foldername and not folderpath:
            return False, "No folder specified"
        
        # Determine full path
        if folderpath:
            if not os.path.isabs(folderpath):
                folderpath = os.path.join(self.working_directory, folderpath)
        else:
            if not os.path.isabs(foldername):
                folderpath = os.path.join(self.working_directory, foldername)
            else:
                folderpath = foldername
        
        # Security check
        if not self._is_path_safe(folderpath):
            return False, f"Cannot delete folder in protected location: {folderpath}"
        
        try:
            if not os.path.exists(folderpath):
                return False, f"Folder does not exist: {folderpath}"
            
            if not os.path.isdir(folderpath):
                return False, f"Path is not a directory: {folderpath}"
            
            shutil.rmtree(folderpath)
            self.logger.info(f"Deleted folder: {folderpath}")
            return True, f"Deleted folder: {os.path.basename(folderpath)}"
            
        except Exception as e:
            return False, f"Error deleting folder: {str(e)}"
    
    def _rename_file(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Rename a file or folder
        
        Args:
            parameters: Must contain 'old_name' and 'new_name', optionally 'path'
            
        Returns:
            Tuple of (success, message)
        """
        old_name = parameters.get('old_name', '').strip()
        new_name = parameters.get('new_name', '').strip()
        path = parameters.get('path', self.working_directory)
        
        if not old_name or not new_name:
            return False, "Both old and new names required"
        
        # Create full paths
        old_path = os.path.join(path, old_name)
        new_path = os.path.join(path, new_name)
        
        # Security checks
        if not self._is_path_safe(old_path) or not self._is_path_safe(new_path):
            return False, "Cannot rename files in protected locations"
        
        try:
            if not os.path.exists(old_path):
                return False, f"File does not exist: {old_name}"
            
            if os.path.exists(new_path):
                return False, f"Target name already exists: {new_name}"
            
            os.rename(old_path, new_path)
            self.logger.info(f"Renamed {old_name} to {new_name}")
            return True, f"Renamed {old_name} to {new_name}"
            
        except Exception as e:
            return False, f"Error renaming file: {str(e)}"
    
    def _is_path_safe(self, path: str) -> bool:
        """
        Check if a path is safe for file operations
        
        Args:
            path: Path to check
            
        Returns:
            True if path is safe
        """
        # Normalize path
        normalized_path = os.path.normpath(os.path.abspath(path))
        
        # Check against protected directories
        for protected_dir in self.protected_dirs:
            if normalized_path.startswith(protected_dir):
                self.logger.warning(f"Blocked operation on protected path: {normalized_path}")
                return False
        
        return True
    
    def can_execute(self, action: str) -> bool:
        """
        Check if this module can execute the given action
        
        Args:
            action: Action to check
            
        Returns:
            True if action is supported
        """
        supported_actions = [
            'create_file', 'create_folder', 'move_file', 'copy_file',
            'delete_file', 'delete_folder', 'rename_file'
        ]
        return action in supported_actions
    
    def test_module(self) -> Dict[str, Any]:
        """
        Test the file actions module
        
        Returns:
            Test results
        """
        test_results = {
            'module_name': 'FileActions',
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'details': []
        }
        
        # Test 1: Path safety check
        test_results['tests_run'] += 1
        try:
            safe_path = self._is_path_safe('/Users/test/document.txt')
            unsafe_path = self._is_path_safe('/System/test.txt')
            if safe_path and not unsafe_path:
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'path_safety', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'path_safety', 'status': 'failed', 'error': f'Safe: {safe_path}, Unsafe: {unsafe_path}'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'path_safety', 'status': 'failed', 'error': str(e)})
        
        # Test 2: Working directory exists
        test_results['tests_run'] += 1
        try:
            if os.path.exists(self.working_directory):
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'working_directory', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'working_directory', 'status': 'failed', 'error': f'Working directory does not exist: {self.working_directory}'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'working_directory', 'status': 'failed', 'error': str(e)})
        
        # Test 3: Can execute check
        test_results['tests_run'] += 1
        try:
            can_create = self.can_execute('create_file')
            can_invalid = self.can_execute('invalid_action')
            if can_create and not can_invalid:
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'can_execute', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'can_execute', 'status': 'failed', 'error': 'Unexpected can_execute results'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'can_execute', 'status': 'failed', 'error': str(e)})
        
        return test_results
