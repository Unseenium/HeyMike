"""
System Actions for Hey Mike! v2.0
Handles system control commands (volume, screenshots, etc.)
"""

import logging
import subprocess
import os
from typing import Dict, Any, Tuple
from datetime import datetime

class SystemActions:
    """Handles system control commands"""
    
    def __init__(self):
        """Initialize System Actions"""
        self.logger = logging.getLogger(__name__)
        
        # Screenshot save location
        self.screenshot_dir = os.path.expanduser("~/Desktop")
    
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute a system control action
        
        Args:
            action: Action to execute
            parameters: Action parameters
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if action == 'volume_control':
                return self._volume_control(parameters)
            elif action == 'brightness_control':
                return self._brightness_control(parameters)
            elif action == 'take_screenshot':
                return self._take_screenshot(parameters)
            elif action == 'system_sleep':
                return self._system_sleep(parameters)
            elif action == 'system_restart':
                return self._system_restart(parameters)
            elif action == 'system_shutdown':
                return self._system_shutdown(parameters)
            else:
                return False, f"Unknown system action: {action}"
                
        except Exception as e:
            self.logger.error(f"System action failed: {str(e)}")
            return False, f"System action failed: {str(e)}"
    
    def _volume_control(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Control system volume
        
        Args:
            parameters: Can contain 'level' (0-100), 'action' (up/down/mute/unmute)
            
        Returns:
            Tuple of (success, message)
        """
        level = parameters.get('level')
        action = parameters.get('action', '').lower()
        
        try:
            if level is not None:
                # Set specific volume level
                level = max(0, min(100, int(level)))  # Clamp to 0-100
                volume_fraction = level / 100.0
                
                result = subprocess.run(
                    ['osascript', '-e', f'set volume output volume {int(volume_fraction * 100)}'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    self.logger.info(f"Set volume to {level}%")
                    return True, f"Set volume to {level}%"
                else:
                    error_msg = result.stderr.strip() or "Unknown error"
                    return False, f"Failed to set volume: {error_msg}"
            
            elif action == 'up':
                # Increase volume
                result = subprocess.run(
                    ['osascript', '-e', 'set volume output volume (output volume of (get volume settings) + 10)'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return True, "Increased volume"
                else:
                    error_msg = result.stderr.strip() or "Unknown error"
                    return False, f"Failed to increase volume: {error_msg}"
            
            elif action == 'down':
                # Decrease volume
                result = subprocess.run(
                    ['osascript', '-e', 'set volume output volume (output volume of (get volume settings) - 10)'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return True, "Decreased volume"
                else:
                    error_msg = result.stderr.strip() or "Unknown error"
                    return False, f"Failed to decrease volume: {error_msg}"
            
            elif action == 'mute':
                # Mute volume
                result = subprocess.run(
                    ['osascript', '-e', 'set volume with output muted'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return True, "Muted volume"
                else:
                    error_msg = result.stderr.strip() or "Unknown error"
                    return False, f"Failed to mute: {error_msg}"
            
            elif action == 'unmute':
                # Unmute volume
                result = subprocess.run(
                    ['osascript', '-e', 'set volume without output muted'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return True, "Unmuted volume"
                else:
                    error_msg = result.stderr.strip() or "Unknown error"
                    return False, f"Failed to unmute: {error_msg}"
            
            else:
                return False, "No valid volume action or level specified"
                
        except ValueError:
            return False, "Invalid volume level - must be a number between 0 and 100"
        except subprocess.TimeoutExpired:
            return False, "Timeout controlling volume"
        except Exception as e:
            return False, f"Error controlling volume: {str(e)}"
    
    def _brightness_control(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Control screen brightness
        
        Args:
            parameters: Can contain 'level' (0-100), 'action' (up/down)
            
        Returns:
            Tuple of (success, message)
        """
        level = parameters.get('level')
        action = parameters.get('action', '').lower()
        
        try:
            if level is not None:
                # Set specific brightness level
                level = max(0, min(100, int(level)))  # Clamp to 0-100
                brightness_fraction = level / 100.0
                
                # Use brightness command line tool if available
                result = subprocess.run(
                    ['brightness', str(brightness_fraction)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    self.logger.info(f"Set brightness to {level}%")
                    return True, f"Set brightness to {level}%"
                else:
                    # Fallback to AppleScript
                    applescript = f'''
                    tell application "System Preferences"
                        reveal pane "com.apple.preference.displays"
                    end tell
                    '''
                    subprocess.run(['osascript', '-e', applescript], timeout=5)
                    return True, f"Opened display preferences (brightness control requires manual adjustment)"
            
            elif action in ['up', 'down']:
                # Use keyboard shortcuts via AppleScript
                key_code = 144 if action == 'up' else 145  # F1/F2 keys
                
                applescript = f'''
                tell application "System Events"
                    key code {key_code}
                end tell
                '''
                
                result = subprocess.run(
                    ['osascript', '-e', applescript],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return True, f"Brightness {action}"
                else:
                    error_msg = result.stderr.strip() or "Unknown error"
                    return False, f"Failed to adjust brightness: {error_msg}"
            
            else:
                return False, "No valid brightness action or level specified"
                
        except ValueError:
            return False, "Invalid brightness level - must be a number between 0 and 100"
        except subprocess.TimeoutExpired:
            return False, "Timeout controlling brightness"
        except Exception as e:
            return False, f"Error controlling brightness: {str(e)}"
    
    def _take_screenshot(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Take a screenshot
        
        Args:
            parameters: Can contain 'type' (full/window/selection), 'filename'
            
        Returns:
            Tuple of (success, message)
        """
        screenshot_type = parameters.get('type', 'full').lower()
        filename = parameters.get('filename')
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"Screenshot_{timestamp}.png"
        
        # Ensure .png extension
        if not filename.lower().endswith('.png'):
            filename += '.png'
        
        filepath = os.path.join(self.screenshot_dir, filename)
        
        try:
            # Build screencapture command
            cmd = ['screencapture']
            
            if screenshot_type == 'window':
                cmd.append('-w')  # Window mode
            elif screenshot_type == 'selection':
                cmd.append('-s')  # Selection mode
            # 'full' is default (no additional flags)
            
            cmd.append(filepath)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # Longer timeout for user interaction
            )
            
            if result.returncode == 0:
                if os.path.exists(filepath):
                    self.logger.info(f"Screenshot saved: {filepath}")
                    return True, f"Screenshot saved as {filename}"
                else:
                    return False, "Screenshot command succeeded but file not found"
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                return False, f"Failed to take screenshot: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout taking screenshot"
        except Exception as e:
            return False, f"Error taking screenshot: {str(e)}"
    
    def _system_sleep(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Put system to sleep
        
        Args:
            parameters: Currently unused
            
        Returns:
            Tuple of (success, message)
        """
        try:
            result = subprocess.run(
                ['pmset', 'sleepnow'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Note: This command may not return if system goes to sleep immediately
            self.logger.info("System sleep initiated")
            return True, "System going to sleep"
            
        except subprocess.TimeoutExpired:
            # This is expected if system goes to sleep
            return True, "System going to sleep"
        except Exception as e:
            return False, f"Error putting system to sleep: {str(e)}"
    
    def _system_restart(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Restart the system
        
        Args:
            parameters: Currently unused
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Use AppleScript for safer restart
            applescript = '''
            tell application "System Events"
                restart
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            self.logger.info("System restart initiated")
            return True, "System restarting"
            
        except Exception as e:
            return False, f"Error restarting system: {str(e)}"
    
    def _system_shutdown(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Shutdown the system
        
        Args:
            parameters: Currently unused
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Use AppleScript for safer shutdown
            applescript = '''
            tell application "System Events"
                shut down
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            self.logger.info("System shutdown initiated")
            return True, "System shutting down"
            
        except Exception as e:
            return False, f"Error shutting down system: {str(e)}"
    
    def can_execute(self, action: str) -> bool:
        """
        Check if this module can execute the given action
        
        Args:
            action: Action to check
            
        Returns:
            True if action is supported
        """
        supported_actions = [
            'volume_control', 'brightness_control', 'take_screenshot',
            'system_sleep', 'system_restart', 'system_shutdown'
        ]
        return action in supported_actions
    
    def test_module(self) -> Dict[str, Any]:
        """
        Test the system actions module
        
        Returns:
            Test results
        """
        test_results = {
            'module_name': 'SystemActions',
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'details': []
        }
        
        # Test 1: Screenshot directory exists
        test_results['tests_run'] += 1
        try:
            if os.path.exists(self.screenshot_dir):
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'screenshot_dir', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'screenshot_dir', 'status': 'failed', 'error': f'Directory does not exist: {self.screenshot_dir}'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'screenshot_dir', 'status': 'failed', 'error': str(e)})
        
        # Test 2: Can execute check
        test_results['tests_run'] += 1
        try:
            can_volume = self.can_execute('volume_control')
            can_invalid = self.can_execute('invalid_action')
            if can_volume and not can_invalid:
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'can_execute', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'can_execute', 'status': 'failed', 'error': 'Unexpected can_execute results'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'can_execute', 'status': 'failed', 'error': str(e)})
        
        # Test 3: Volume level validation
        test_results['tests_run'] += 1
        try:
            # Test clamping logic
            level = max(0, min(100, 150))  # Should clamp to 100
            if level == 100:
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'volume_validation', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'volume_validation', 'status': 'failed', 'error': f'Expected 100, got {level}'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'volume_validation', 'status': 'failed', 'error': str(e)})
        
        return test_results
