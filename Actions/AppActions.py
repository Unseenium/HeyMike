"""
App Actions for Hey Mike! v2.0
Handles application control commands
"""

import logging
import subprocess
import time
from typing import Dict, Any, Tuple, List

class AppActions:
    """Handles application control commands"""
    
    def __init__(self):
        """Initialize App Actions"""
        self.logger = logging.getLogger(__name__)
        
        # Common application mappings
        self.app_mappings = {
            # Browsers
            'chrome': 'Google Chrome',
            'safari': 'Safari',
            'firefox': 'Firefox',
            'edge': 'Microsoft Edge',
            
            # Development
            'vscode': 'Visual Studio Code',
            'code': 'Visual Studio Code',
            'xcode': 'Xcode',
            'terminal': 'Terminal',
            'iterm': 'iTerm',
            
            # Productivity
            'finder': 'Finder',
            'notes': 'Notes',
            'mail': 'Mail',
            'calendar': 'Calendar',
            'calculator': 'Calculator',
            'textedit': 'TextEdit',
            
            # Creative
            'photoshop': 'Adobe Photoshop',
            'illustrator': 'Adobe Illustrator',
            'sketch': 'Sketch',
            'figma': 'Figma',
            
            # Communication
            'slack': 'Slack',
            'discord': 'Discord',
            'zoom': 'zoom.us',
            'teams': 'Microsoft Teams',
            
            # Media
            'spotify': 'Spotify',
            'music': 'Music',
            'vlc': 'VLC',
            'quicktime': 'QuickTime Player',
        }
    
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute an application control action
        
        Args:
            action: Action to execute
            parameters: Action parameters
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if action == 'launch_app':
                return self._launch_app(parameters)
            elif action == 'quit_app':
                return self._quit_app(parameters)
            elif action == 'force_quit_app':
                return self._force_quit_app(parameters)
            elif action == 'switch_app':
                return self._switch_app(parameters)
            else:
                return False, f"Unknown app action: {action}"
                
        except Exception as e:
            self.logger.error(f"App action failed: {str(e)}")
            return False, f"App action failed: {str(e)}"
    
    def _launch_app(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Launch an application
        
        Args:
            parameters: Must contain 'app_name'
            
        Returns:
            Tuple of (success, message)
        """
        app_name = parameters.get('app_name', '').strip()
        if not app_name:
            return False, "No app name provided"
        
        # Normalize app name
        normalized_name = self._normalize_app_name(app_name)
        
        try:
            # Use 'open' command to launch the app
            result = subprocess.run(
                ['open', '-a', normalized_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully launched app: {normalized_name}")
                return True, f"Launched {normalized_name}"
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                self.logger.error(f"Failed to launch {normalized_name}: {error_msg}")
                return False, f"Failed to launch {normalized_name}: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout launching {normalized_name}"
        except Exception as e:
            return False, f"Error launching {normalized_name}: {str(e)}"
    
    def _quit_app(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Quit an application gracefully
        
        Args:
            parameters: Must contain 'app_name'
            
        Returns:
            Tuple of (success, message)
        """
        app_name = parameters.get('app_name', '').strip()
        if not app_name:
            return False, "No app name provided"
        
        normalized_name = self._normalize_app_name(app_name)
        
        try:
            # Use AppleScript to quit the app gracefully
            applescript = f'''
            tell application "{normalized_name}"
                quit
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully quit app: {normalized_name}")
                return True, f"Quit {normalized_name}"
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                self.logger.error(f"Failed to quit {normalized_name}: {error_msg}")
                return False, f"Failed to quit {normalized_name}: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout quitting {normalized_name}"
        except Exception as e:
            return False, f"Error quitting {normalized_name}: {str(e)}"
    
    def _force_quit_app(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Force quit an application
        
        Args:
            parameters: Must contain 'app_name'
            
        Returns:
            Tuple of (success, message)
        """
        app_name = parameters.get('app_name', '').strip()
        if not app_name:
            return False, "No app name provided"
        
        normalized_name = self._normalize_app_name(app_name)
        
        try:
            # Use pkill to force quit
            result = subprocess.run(
                ['pkill', '-f', normalized_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # pkill returns 0 if processes were killed, 1 if no processes found
            if result.returncode in [0, 1]:
                self.logger.info(f"Force quit attempted for: {normalized_name}")
                return True, f"Force quit {normalized_name}"
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                return False, f"Failed to force quit {normalized_name}: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout force quitting {normalized_name}"
        except Exception as e:
            return False, f"Error force quitting {normalized_name}: {str(e)}"
    
    def _switch_app(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Switch to an application (bring to front)
        
        Args:
            parameters: Must contain 'app_name'
            
        Returns:
            Tuple of (success, message)
        """
        app_name = parameters.get('app_name', '').strip()
        if not app_name:
            return False, "No app name provided"
        
        normalized_name = self._normalize_app_name(app_name)
        
        try:
            # Use AppleScript to activate the app
            applescript = f'''
            tell application "{normalized_name}"
                activate
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully switched to app: {normalized_name}")
                return True, f"Switched to {normalized_name}"
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                self.logger.error(f"Failed to switch to {normalized_name}: {error_msg}")
                return False, f"Failed to switch to {normalized_name}: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout switching to {normalized_name}"
        except Exception as e:
            return False, f"Error switching to {normalized_name}: {str(e)}"
    
    def _normalize_app_name(self, app_name: str) -> str:
        """
        Normalize app name using common mappings
        
        Args:
            app_name: Raw app name from voice command
            
        Returns:
            Normalized app name
        """
        app_name_lower = app_name.lower().strip()
        
        # Check direct mappings
        if app_name_lower in self.app_mappings:
            return self.app_mappings[app_name_lower]
        
        # Check partial matches
        for key, value in self.app_mappings.items():
            if key in app_name_lower or app_name_lower in key:
                return value
        
        # Return original name with proper capitalization
        return app_name.title()
    
    def can_execute(self, action: str) -> bool:
        """
        Check if this module can execute the given action
        
        Args:
            action: Action to check
            
        Returns:
            True if action is supported
        """
        supported_actions = ['launch_app', 'quit_app', 'force_quit_app', 'switch_app']
        return action in supported_actions
    
    def get_running_apps(self) -> List[str]:
        """
        Get list of currently running applications
        
        Returns:
            List of running app names
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to get name of every process whose background only is false'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse the AppleScript output
                apps_str = result.stdout.strip()
                if apps_str:
                    # Remove the outer braces and split by comma
                    apps_str = apps_str.strip('{}')
                    apps = [app.strip().strip('"') for app in apps_str.split(',')]
                    return apps
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get running apps: {str(e)}")
            return []
    
    def test_module(self) -> Dict[str, Any]:
        """
        Test the app actions module
        
        Returns:
            Test results
        """
        test_results = {
            'module_name': 'AppActions',
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'details': []
        }
        
        # Test 1: App name normalization
        test_results['tests_run'] += 1
        try:
            normalized = self._normalize_app_name('chrome')
            if normalized == 'Google Chrome':
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'app_normalization', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'app_normalization', 'status': 'failed', 'error': f'Expected "Google Chrome", got "{normalized}"'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'app_normalization', 'status': 'failed', 'error': str(e)})
        
        # Test 2: Can execute check
        test_results['tests_run'] += 1
        try:
            can_launch = self.can_execute('launch_app')
            can_invalid = self.can_execute('invalid_action')
            if can_launch and not can_invalid:
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'can_execute', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'can_execute', 'status': 'failed', 'error': 'Unexpected can_execute results'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'can_execute', 'status': 'failed', 'error': str(e)})
        
        # Test 3: Get running apps
        test_results['tests_run'] += 1
        try:
            running_apps = self.get_running_apps()
            if isinstance(running_apps, list):
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'get_running_apps', 'status': 'passed', 'result': f'Found {len(running_apps)} apps'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'get_running_apps', 'status': 'failed', 'error': 'Did not return list'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'get_running_apps', 'status': 'failed', 'error': str(e)})
        
        return test_results
