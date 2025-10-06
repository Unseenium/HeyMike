"""
VS Code Bridge for Hey Mike!
Provides WebSocket and HTTP bridge between Python backend and VS Code extension
"""

import logging
import threading
from typing import Optional, Dict, Any
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS

class VSCodeBridge:
    """Manages WebSocket and HTTP communication with VS Code extension"""
    
    def __init__(self, port: int = 8765):
        """
        Initialize VS Code Bridge
        
        Args:
            port: Port for Flask server (default: 8765)
        """
        self.logger = logging.getLogger(__name__)
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for HTTP requests
        
        # Initialize SocketIO with CORS support
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=False,
            engineio_logger=False
        )
        
        self.connected_clients = set()
        self.settings_callback = None
        self.running = False
        self.server_thread = None
        
        self._setup_routes()
        self._setup_socket_events()
        
        self.logger.info(f"VSCodeBridge initialized on port {port}")
    
    def _setup_routes(self):
        """Setup HTTP REST API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'clients_connected': len(self.connected_clients)
            })
        
        @self.app.route('/api/settings', methods=['GET'])
        def get_settings():
            """Get current settings from backend"""
            try:
                # This will be provided by MenuBarController
                if self.settings_callback:
                    settings = self.settings_callback()
                    return jsonify(settings)
                else:
                    return jsonify({'error': 'Settings not available'}), 500
            except Exception as e:
                self.logger.error(f"Error getting settings: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/settings', methods=['POST'])
        def update_settings():
            """Update backend settings from VS Code"""
            try:
                new_settings = request.get_json()
                self.logger.info(f"Received settings update: {new_settings}")
                
                # Emit to all connected clients
                self.socketio.emit('settings_updated', new_settings)
                
                return jsonify({'status': 'success', 'settings': new_settings})
            except Exception as e:
                self.logger.error(f"Error updating settings: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/models', methods=['GET'])
        def get_models():
            """Get available models"""
            return jsonify({
                'whisper': ['tiny', 'base', 'small', 'medium', 'large'],
                'text_llm': ['llama-3.2-1b', 'phi-3-mini', 'qwen-2.5-1.5b'],
                'code_llm': ['deepseek-coder-1.3b', 'qwen-2.5-coder-3b', 'qwen-2.5-coder-7b', 'deepseek-coder-6.7b']
            })
        
        @self.app.route('/api/explain', methods=['POST'])
        def explain_code():
            """Explain code (placeholder for v2.0.1)"""
            try:
                data = request.get_json()
                code = data.get('code', '')
                context = data.get('context', {})
                
                self.logger.info(f"Code explanation requested for {len(code)} chars")
                
                # Placeholder response (will be implemented with Code LLM in v2.0.1)
                return jsonify({
                    'explanation': f"Code explanation feature coming in v2.0.1! (Received {len(code)} characters of code)",
                    'code': code,
                    'context': context
                })
            except Exception as e:
                self.logger.error(f"Error explaining code: {e}")
                return jsonify({'error': str(e)}), 500
    
    def _setup_socket_events(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            self.logger.info(f"Client connected: {request.sid}")
            self.connected_clients.add(request.sid)
            emit('connected', {'status': 'success', 'message': 'Connected to Hey Mike! backend'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            self.logger.info(f"Client disconnected: {request.sid}")
            self.connected_clients.discard(request.sid)
        
        @self.socketio.on('register')
        def handle_register(data):
            """Handle client registration"""
            self.logger.info(f"Client registered: {data}")
            emit('registered', {'status': 'success'})
        
        @self.socketio.on('request_transcription')
        def handle_request_transcription(data):
            """Handle manual transcription request"""
            self.logger.info(f"Transcription requested: {data}")
            # This would trigger recording in MenuBarController
            # For now, just acknowledge
            emit('status_update', {'status': 'Transcription request received'})
    
    def start(self):
        """Start the Flask-SocketIO server in a background thread"""
        if self.running:
            self.logger.warning("Bridge already running")
            return
        
        self.running = True
        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True,
            name="VSCodeBridge"
        )
        self.server_thread.start()
        self.logger.info(f"VSCodeBridge started on port {self.port}")
    
    def _run_server(self):
        """Run the Flask-SocketIO server"""
        try:
            self.socketio.run(
                self.app,
                host='127.0.0.1',
                port=self.port,
                debug=False,
                use_reloader=False,
                allow_unsafe_werkzeug=True  # For development
            )
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            self.running = False
    
    def stop(self):
        """Stop the Flask-SocketIO server"""
        self.running = False
        # SocketIO will stop when the thread exits
        self.logger.info("VSCodeBridge stopped")
    
    def set_settings_callback(self, callback):
        """
        Set callback function to get current settings
        
        Args:
            callback: Function that returns current settings dict
        """
        self.settings_callback = callback
    
    # Event emission methods (called by MenuBarController)
    
    def send_transcription(self, text: str, mode: str, context: Optional[Dict] = None):
        """
        Send transcription to VS Code
        
        Args:
            text: Transcribed text
            mode: Current mode ('smart' or 'action')
            context: Additional context
        """
        if not self.connected_clients:
            self.logger.debug("No clients connected, skipping transcription send")
            return
        
        data = {
            'text': text,
            'mode': mode,
            'context': context or {
                'timestamp': self._get_timestamp(),
            }
        }
        
        self.logger.info(f"Sending transcription to VS Code: {len(text)} chars, mode: {mode}")
        self.socketio.emit('transcription', data)
    
    def send_llm_result(self, result: Dict[str, Any]):
        """
        Send LLM result to VS Code
        
        Args:
            result: LLM result dict (explanation, code, etc.)
        """
        if not self.connected_clients:
            return
        
        self.logger.info("Sending LLM result to VS Code")
        self.socketio.emit('llm_result', result)
    
    def send_status_update(self, status: str, details: Optional[Dict] = None):
        """
        Send status update to VS Code
        
        Args:
            status: Status message
            details: Additional details
        """
        if not self.connected_clients:
            return
        
        data = {
            'status': status,
            'details': details or {},
            'timestamp': self._get_timestamp()
        }
        
        self.socketio.emit('status_update', data)
    
    def send_recording_state(self, state: str):
        """
        Send recording state change to VS Code
        
        Args:
            state: 'recording' or 'ready'
        """
        if not self.connected_clients:
            return
        
        data = {
            'state': state,
            'timestamp': self._get_timestamp()
        }
        
        self.logger.debug(f"Sending recording state: {state}")
        self.socketio.emit('recording_state', data)
    
    def send_processing_state(self, state: str, message: Optional[str] = None):
        """
        Send processing state change to VS Code
        
        Args:
            state: 'processing' or 'ready'
            message: Optional status message
        """
        if not self.connected_clients:
            return
        
        data = {
            'state': state,
            'message': message,
            'timestamp': self._get_timestamp()
        }
        
        self.logger.debug(f"Sending processing state: {state}")
        self.socketio.emit('processing_state', data)
    
    def send_mode_change(self, mode: str):
        """
        Send mode change to VS Code
        
        Args:
            mode: New mode ('smart' or 'action')
        """
        if not self.connected_clients:
            return
        
        data = {
            'mode': mode,
            'timestamp': self._get_timestamp()
        }
        
        self.logger.info(f"Sending mode change: {mode}")
        self.socketio.emit('mode_changed', data)
    
    def is_connected(self) -> bool:
        """Check if any VS Code clients are connected"""
        return len(self.connected_clients) > 0
    
    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds"""
        import time
        return int(time.time() * 1000)
