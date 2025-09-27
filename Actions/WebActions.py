"""
Web Actions for Hey Mike! v2.0
Handles web search and browser control commands
"""

import logging
import subprocess
import urllib.parse
from typing import Dict, Any, Tuple

class WebActions:
    """Handles web search and browser control commands"""
    
    def __init__(self):
        """Initialize Web Actions"""
        self.logger = logging.getLogger(__name__)
        
        # Default search engines
        self.search_engines = {
            'google': 'https://www.google.com/search?q={}',
            'bing': 'https://www.bing.com/search?q={}',
            'duckduckgo': 'https://duckduckgo.com/?q={}',
            'yahoo': 'https://search.yahoo.com/search?p={}',
        }
        
        # Site-specific search patterns
        self.site_searches = {
            'github': 'https://github.com/search?q={}',
            'stackoverflow': 'https://stackoverflow.com/search?q={}',
            'youtube': 'https://www.youtube.com/results?search_query={}',
            'wikipedia': 'https://en.wikipedia.org/wiki/Special:Search?search={}',
            'reddit': 'https://www.reddit.com/search/?q={}',
            'twitter': 'https://twitter.com/search?q={}',
            'amazon': 'https://www.amazon.com/s?k={}',
        }
        
        # Default browser preference
        self.default_browser = 'Google Chrome'
    
    def execute_action(self, action: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute a web action
        
        Args:
            action: Action to execute
            parameters: Action parameters
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if action == 'web_search':
                return self._web_search(parameters)
            elif action == 'open_url':
                return self._open_url(parameters)
            elif action == 'site_search':
                return self._site_search(parameters)
            else:
                return False, f"Unknown web action: {action}"
                
        except Exception as e:
            self.logger.error(f"Web action failed: {str(e)}")
            return False, f"Web action failed: {str(e)}"
    
    def _web_search(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Perform a web search
        
        Args:
            parameters: Must contain 'query', optionally 'engine'
            
        Returns:
            Tuple of (success, message)
        """
        query = parameters.get('query', '').strip()
        if not query:
            return False, "No search query provided"
        
        engine = parameters.get('engine', 'google').lower()
        browser = parameters.get('browser', self.default_browser)
        
        # Get search URL
        if engine in self.search_engines:
            search_url = self.search_engines[engine].format(urllib.parse.quote_plus(query))
        else:
            # Default to Google
            search_url = self.search_engines['google'].format(urllib.parse.quote_plus(query))
        
        try:
            # Open search in browser
            result = subprocess.run(
                ['open', '-a', browser, search_url],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"Opened search for '{query}' using {engine}")
                return True, f"Searched for '{query}' using {engine}"
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                self.logger.error(f"Failed to open search: {error_msg}")
                return False, f"Failed to open search: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout opening search for '{query}'"
        except Exception as e:
            return False, f"Error opening search: {str(e)}"
    
    def _open_url(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Open a specific URL
        
        Args:
            parameters: Must contain 'url', optionally 'browser'
            
        Returns:
            Tuple of (success, message)
        """
        url = parameters.get('url', '').strip()
        if not url:
            return False, "No URL provided"
        
        browser = parameters.get('browser', self.default_browser)
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            result = subprocess.run(
                ['open', '-a', browser, url],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"Opened URL: {url}")
                return True, f"Opened {url}"
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                self.logger.error(f"Failed to open URL: {error_msg}")
                return False, f"Failed to open URL: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout opening URL: {url}"
        except Exception as e:
            return False, f"Error opening URL: {str(e)}"
    
    def _site_search(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Search on a specific site
        
        Args:
            parameters: Must contain 'query' and 'site', optionally 'browser'
            
        Returns:
            Tuple of (success, message)
        """
        query = parameters.get('query', '').strip()
        site = parameters.get('site', '').strip().lower()
        
        if not query:
            return False, "No search query provided"
        if not site:
            return False, "No site specified"
        
        browser = parameters.get('browser', self.default_browser)
        
        # Get site search URL
        if site in self.site_searches:
            search_url = self.site_searches[site].format(urllib.parse.quote_plus(query))
        else:
            # Fallback to Google site search
            site_query = f"site:{site} {query}"
            search_url = self.search_engines['google'].format(urllib.parse.quote_plus(site_query))
        
        try:
            result = subprocess.run(
                ['open', '-a', browser, search_url],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"Searched '{query}' on {site}")
                return True, f"Searched '{query}' on {site}"
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                self.logger.error(f"Failed to open site search: {error_msg}")
                return False, f"Failed to open site search: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, f"Timeout opening site search for '{query}' on {site}"
        except Exception as e:
            return False, f"Error opening site search: {str(e)}"
    
    def can_execute(self, action: str) -> bool:
        """
        Check if this module can execute the given action
        
        Args:
            action: Action to check
            
        Returns:
            True if action is supported
        """
        supported_actions = ['web_search', 'open_url', 'site_search']
        return action in supported_actions
    
    def test_module(self) -> Dict[str, Any]:
        """
        Test the web actions module
        
        Returns:
            Test results
        """
        test_results = {
            'module_name': 'WebActions',
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'details': []
        }
        
        # Test 1: URL encoding
        test_results['tests_run'] += 1
        try:
            query = "hello world"
            encoded = urllib.parse.quote_plus(query)
            if encoded == "hello+world":
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'url_encoding', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'url_encoding', 'status': 'failed', 'error': f'Expected "hello+world", got "{encoded}"'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'url_encoding', 'status': 'failed', 'error': str(e)})
        
        # Test 2: Search engine URLs
        test_results['tests_run'] += 1
        try:
            google_url = self.search_engines['google'].format('test')
            if 'google.com' in google_url and 'test' in google_url:
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'search_engine_urls', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'search_engine_urls', 'status': 'failed', 'error': f'Invalid Google URL: {google_url}'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'search_engine_urls', 'status': 'failed', 'error': str(e)})
        
        # Test 3: Can execute check
        test_results['tests_run'] += 1
        try:
            can_search = self.can_execute('web_search')
            can_invalid = self.can_execute('invalid_action')
            if can_search and not can_invalid:
                test_results['tests_passed'] += 1
                test_results['details'].append({'test': 'can_execute', 'status': 'passed'})
            else:
                test_results['tests_failed'] += 1
                test_results['details'].append({'test': 'can_execute', 'status': 'failed', 'error': 'Unexpected can_execute results'})
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['details'].append({'test': 'can_execute', 'status': 'failed', 'error': str(e)})
        
        return test_results
