"""
Action Executor for Hey Mike! v2.0
Coordinates execution of validated commands across different action modules
"""

import logging
import time
import threading
from typing import Optional, Callable, Dict, Any, List
from enum import Enum

class ExecutionStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ActionExecutor:
    """Coordinates execution of voice commands"""
    
    def __init__(self):
        """Initialize Action Executor"""
        self.logger = logging.getLogger(__name__)
        
        # Action modules (will be imported dynamically)
        self.action_modules = {}
        self.modules_loaded = False
        
        # Execution tracking
        self.active_executions = {}
        self.execution_history = []
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0
        
        # Callbacks
        self.on_execution_started: Optional[Callable[[str, Dict[str, Any]], None]] = None
        self.on_execution_completed: Optional[Callable[[str, bool, str], None]] = None
        self.on_execution_failed: Optional[Callable[[str, str], None]] = None
        self.on_confirmation_required: Optional[Callable[[Dict[str, Any]], None]] = None
    
    def load_action_modules(self) -> bool:
        """
        Load action modules for different command types
        
        Returns:
            True if modules loaded successfully
        """
        try:
            # Import action modules
            from Actions.AppActions import AppActions
            from Actions.TerminalActions import TerminalActions
            from Actions.SystemActions import SystemActions
            from Actions.WebActions import WebActions
            from Actions.FileActions import FileActions
            
            # Initialize action modules
            self.action_modules = {
                'app_control': AppActions(),
                'terminal': TerminalActions(),
                'system_control': SystemActions(),
                'web_search': WebActions(),
                'file_management': FileActions()
            }
            
            self.modules_loaded = True
            self.logger.info("Action modules loaded successfully")
            return True
            
        except ImportError as e:
            self.logger.error(f"Failed to import action modules: {str(e)}")
            # Create placeholder modules for testing
            self._create_placeholder_modules()
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize action modules: {str(e)}")
            return False
    
    def _create_placeholder_modules(self):
        """Create placeholder modules for testing when real modules aren't available"""
        class PlaceholderModule:
            def __init__(self, module_name):
                self.module_name = module_name
                self.logger = logging.getLogger(f"Placeholder_{module_name}")
            
            def execute_action(self, action: str, parameters: Dict[str, Any]) -> tuple:
                self.logger.info(f"[PLACEHOLDER] Would execute {self.module_name}.{action} with {parameters}")
                return True, f"Placeholder execution of {action}"
            
            def can_execute(self, action: str) -> bool:
                return True
        
        self.action_modules = {
            'app_control': PlaceholderModule('AppActions'),
            'terminal': PlaceholderModule('TerminalActions'),
            'system_control': PlaceholderModule('SystemActions'),
            'web_search': PlaceholderModule('WebActions'),
            'file_management': PlaceholderModule('FileActions')
        }
        
        self.modules_loaded = True
        self.logger.warning("Using placeholder action modules - real functionality disabled")
    
    def execute_command(self, command_data: Dict[str, Any]) -> Optional[str]:
        """
        Execute a validated command
        
        Args:
            command_data: Processed command data from CommandProcessor
            
        Returns:
            Execution ID for tracking, or None if execution failed to start
        """
        if not self.modules_loaded:
            if not self.load_action_modules():
                self.logger.error("Cannot execute command - action modules not loaded")
                return None
        
        # Generate execution ID
        execution_id = f"exec_{int(time.time() * 1000)}"
        
        # Check if confirmation is required
        if command_data.get('requires_confirmation', False):
            if self.on_confirmation_required:
                self.on_confirmation_required(command_data)
            # For now, we'll proceed with execution
            # In a real implementation, this would wait for user confirmation
        
        # Start execution
        self._start_execution(execution_id, command_data)
        
        return execution_id
    
    def _start_execution(self, execution_id: str, command_data: Dict[str, Any]) -> None:
        """
        Start command execution in a separate thread
        
        Args:
            execution_id: Unique execution identifier
            command_data: Command data to execute
        """
        # Track execution
        self.active_executions[execution_id] = {
            'command_data': command_data,
            'status': ExecutionStatus.PENDING,
            'start_time': time.time(),
            'thread': None
        }
        
        # Execute in separate thread
        def execution_thread():
            self._execute_command_sync(execution_id, command_data)
        
        thread = threading.Thread(target=execution_thread, daemon=True)
        self.active_executions[execution_id]['thread'] = thread
        thread.start()
    
    def _execute_command_sync(self, execution_id: str, command_data: Dict[str, Any]) -> None:
        """
        Execute command synchronously (called from thread)
        
        Args:
            execution_id: Execution identifier
            command_data: Command data to execute
        """
        self.total_executions += 1
        
        try:
            # Update status
            self.active_executions[execution_id]['status'] = ExecutionStatus.EXECUTING
            
            if self.on_execution_started:
                self.on_execution_started(execution_id, command_data)
            
            self.logger.info(f"Executing command: {command_data['description']}")
            
            # Get appropriate action module
            intent = command_data['intent']
            action_module = self.action_modules.get(intent)
            
            if not action_module:
                raise ValueError(f"No action module for intent: {intent}")
            
            # Check if module can execute this action
            action = command_data['action']
            if hasattr(action_module, 'can_execute') and not action_module.can_execute(action):
                raise ValueError(f"Action module cannot execute: {action}")
            
            # Execute the action
            success, result_message = action_module.execute_action(action, command_data['parameters'])
            
            # Update execution tracking
            execution_time = time.time() - self.active_executions[execution_id]['start_time']
            
            if success:
                self.successful_executions += 1
                self.active_executions[execution_id]['status'] = ExecutionStatus.COMPLETED
                self.active_executions[execution_id]['result'] = result_message
                self.active_executions[execution_id]['execution_time'] = execution_time
                
                self.logger.info(f"Command executed successfully: {command_data['description']} "
                               f"(time: {execution_time:.2f}s)")
                
                if self.on_execution_completed:
                    self.on_execution_completed(execution_id, True, result_message)
            else:
                self.failed_executions += 1
                self.active_executions[execution_id]['status'] = ExecutionStatus.FAILED
                self.active_executions[execution_id]['error'] = result_message
                self.active_executions[execution_id]['execution_time'] = execution_time
                
                self.logger.error(f"Command execution failed: {command_data['description']} - {result_message}")
                
                if self.on_execution_failed:
                    self.on_execution_failed(execution_id, result_message)
            
            # Move to history
            self._move_to_history(execution_id)
            
        except Exception as e:
            self.failed_executions += 1
            error_message = str(e)
            execution_time = time.time() - self.active_executions[execution_id]['start_time']
            
            self.active_executions[execution_id]['status'] = ExecutionStatus.FAILED
            self.active_executions[execution_id]['error'] = error_message
            self.active_executions[execution_id]['execution_time'] = execution_time
            
            self.logger.error(f"Command execution error: {command_data['description']} - {error_message}")
            
            if self.on_execution_failed:
                self.on_execution_failed(execution_id, error_message)
            
            # Move to history
            self._move_to_history(execution_id)
    
    def _move_to_history(self, execution_id: str) -> None:
        """
        Move completed execution to history
        
        Args:
            execution_id: Execution identifier
        """
        if execution_id in self.active_executions:
            execution_data = self.active_executions[execution_id]
            
            # Create history entry
            history_entry = {
                'execution_id': execution_id,
                'command_description': execution_data['command_data']['description'],
                'intent': execution_data['command_data']['intent'],
                'action': execution_data['command_data']['action'],
                'status': execution_data['status'].value,
                'start_time': execution_data['start_time'],
                'execution_time': execution_data.get('execution_time', 0.0),
                'result': execution_data.get('result'),
                'error': execution_data.get('error')
            }
            
            self.execution_history.append(history_entry)
            
            # Keep only recent history
            if len(self.execution_history) > 100:
                self.execution_history = self.execution_history[-50:]
            
            # Remove from active executions
            del self.active_executions[execution_id]
    
    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel an active execution
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            True if cancellation was successful
        """
        if execution_id not in self.active_executions:
            self.logger.warning(f"Cannot cancel - execution not found: {execution_id}")
            return False
        
        execution_data = self.active_executions[execution_id]
        
        # Update status
        execution_data['status'] = ExecutionStatus.CANCELLED
        
        # Note: We can't actually stop the thread, but we mark it as cancelled
        self.logger.info(f"Execution cancelled: {execution_id}")
        
        # Move to history
        self._move_to_history(execution_id)
        
        return True
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of an execution
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Execution status data or None if not found
        """
        if execution_id in self.active_executions:
            execution_data = self.active_executions[execution_id]
            return {
                'execution_id': execution_id,
                'status': execution_data['status'].value,
                'command_description': execution_data['command_data']['description'],
                'start_time': execution_data['start_time'],
                'elapsed_time': time.time() - execution_data['start_time']
            }
        
        # Check history
        for entry in self.execution_history:
            if entry['execution_id'] == execution_id:
                return entry
        
        return None
    
    def get_active_executions(self) -> List[Dict[str, Any]]:
        """
        Get list of currently active executions
        
        Returns:
            List of active execution data
        """
        active = []
        for execution_id, execution_data in self.active_executions.items():
            active.append({
                'execution_id': execution_id,
                'status': execution_data['status'].value,
                'command_description': execution_data['command_data']['description'],
                'start_time': execution_data['start_time'],
                'elapsed_time': time.time() - execution_data['start_time']
            })
        
        return active
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics
        
        Returns:
            Dictionary with execution statistics
        """
        success_rate = (self.successful_executions / self.total_executions * 100) if self.total_executions > 0 else 0.0
        
        return {
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'failed_executions': self.failed_executions,
            'success_rate': success_rate,
            'active_executions': len(self.active_executions),
            'modules_loaded': self.modules_loaded,
            'available_modules': list(self.action_modules.keys())
        }
    
    def get_recent_executions(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent execution history
        
        Args:
            count: Number of recent executions to return
            
        Returns:
            List of recent executions
        """
        return self.execution_history[-count:] if self.execution_history else []
    
    def test_action_modules(self) -> Dict[str, Any]:
        """
        Test all action modules
        
        Returns:
            Test results for each module
        """
        if not self.modules_loaded:
            self.load_action_modules()
        
        test_results = {}
        
        for module_name, module in self.action_modules.items():
            try:
                # Test basic functionality
                if hasattr(module, 'test_module'):
                    result = module.test_module()
                    test_results[module_name] = {'status': 'passed', 'result': result}
                else:
                    test_results[module_name] = {'status': 'no_test', 'result': 'No test method available'}
            except Exception as e:
                test_results[module_name] = {'status': 'failed', 'error': str(e)}
        
        return test_results
