/**
 * Backend Client for Hey Mike!
 * Handles WebSocket connection to Python backend
 * Auto-starts backend if not running (hybrid mode)
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { spawn, ChildProcess } from 'child_process';
import { io, Socket } from 'socket.io-client';
import { TranscriptionData, LLMResult, RecordingState, ProcessingState, ModeChangedData, SettingsData, BackendSettings } from '../types';

export class BackendClient {
    private socket?: Socket;
    private config = vscode.workspace.getConfiguration('heymike');
    private reconnectTimer?: NodeJS.Timeout;
    private eventEmitter = new vscode.EventEmitter<{ event: string, data: any }>();
    public onEvent = this.eventEmitter.event;

    // Backend process management
    private backendProcess?: ChildProcess;
    private backendAutoStarted = false;
    private isCheckingBackend = false;

    constructor() {
        // Listen for configuration changes
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('heymike.backendPort')) {
                this.reconnect();
            }
        });
    }

    /**
     * Connect to backend server (with auto-start if needed)
     */
    async connect() {
        // Check if backend is already running
        const isRunning = await this.checkBackendRunning();

        if (!isRunning) {
            const shouldAutoStart = this.config.get<boolean>('autoStartBackend', true);

            if (shouldAutoStart) {
                console.log('[HeyMike] Backend not running, attempting auto-start...');
                const started = await this.startBackend();

                if (!started) {
                    vscode.window.showErrorMessage(
                        'Failed to start Hey Mike! backend. Please start it manually: python main.py',
                        'Show Instructions'
                    ).then(selection => {
                        if (selection === 'Show Instructions') {
                            vscode.env.openExternal(vscode.Uri.parse('https://github.com/Unseenium/HeyMike#setup'));
                        }
                    });
                    return;
                }

                // Wait for backend to be ready
                await this.waitForBackend();
            } else {
                vscode.window.showWarningMessage(
                    'Hey Mike! backend is not running. Auto-start is disabled.',
                    'Start Manually'
                );
                return;
            }
        }

        this.connectToBackend();
    }

    /**
     * Check if backend is running
     */
    private async checkBackendRunning(): Promise<boolean> {
        if (this.isCheckingBackend) {
            return false;
        }

        this.isCheckingBackend = true;
        const port = this.config.get<number>('backendPort', 8765);

        try {
            const response = await fetch(`http://localhost:${port}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(2000)
            });

            this.isCheckingBackend = false;

            if (response.ok) {
                console.log('[HeyMike] Backend is already running');
                return true;
            }
            return false;
        } catch (error) {
            this.isCheckingBackend = false;
            console.log('[HeyMike] Backend not running');
            return false;
        }
    }

    /**
     * Start the Python backend process
     */
    private async startBackend(): Promise<boolean> {
        try {
            const fs = require('fs');

            // Get workspace folder
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders) {
                const errorMsg = 'No workspace folder found';
                console.error(`[HeyMike] ${errorMsg}`);
                vscode.window.showErrorMessage(`Hey Mike!: ${errorMsg}`);
                return false;
            }

            // Assume HeyMike is in the workspace or parent
            const workspaceRoot = workspaceFolders[0].uri.fsPath;
            const heymikePath = workspaceRoot.includes('vscode-extension')
                ? path.dirname(workspaceRoot)  // Go up from vscode-extension/
                : workspaceRoot;               // Already in HeyMike/

            console.log(`[HeyMike] Workspace root: ${workspaceRoot}`);
            console.log(`[HeyMike] Detected HeyMike path: ${heymikePath}`);

            // Check if main.py exists
            const mainPyPath = path.join(heymikePath, 'main.py');
            if (!fs.existsSync(mainPyPath)) {
                const errorMsg = `main.py not found at: ${mainPyPath}`;
                console.error(`[HeyMike] ${errorMsg}`);
                vscode.window.showErrorMessage(`Hey Mike!: ${errorMsg}`);
                return false;
            }

            console.log(`[HeyMike] Found main.py at: ${mainPyPath}`);

            // Determine Python command (try virtual env first)
            const venvPython = path.join(process.env.HOME || '', '.virtualenvs/MagikMike/bin/python');
            const pythonCmd = fs.existsSync(venvPython) ? venvPython : 'python3';

            console.log(`[HeyMike] Using Python: ${pythonCmd}`);
            console.log(`[HeyMike] Python exists: ${fs.existsSync(pythonCmd)}`);

            // Spawn Python process
            console.log(`[HeyMike] Spawning: ${pythonCmd} main.py in ${heymikePath}`);

            this.backendProcess = spawn(pythonCmd, ['main.py'], {
                cwd: heymikePath,
                detached: false,  // Keep attached so we can manage it
                stdio: ['ignore', 'pipe', 'pipe'],
                env: { ...process.env }  // Inherit environment variables
            });

            this.backendAutoStarted = true;

            // Log output
            this.backendProcess.stdout?.on('data', (data) => {
                console.log(`[HeyMike Backend] ${data.toString().trim()}`);
            });

            this.backendProcess.stderr?.on('data', (data) => {
                console.error(`[HeyMike Backend Error] ${data.toString().trim()}`);
            });

            this.backendProcess.on('error', (error) => {
                console.error(`[HeyMike] Backend process error:`, error);
                vscode.window.showErrorMessage(`Hey Mike! backend failed to start: ${error.message}`);
                this.backendProcess = undefined;
                this.backendAutoStarted = false;
            });

            this.backendProcess.on('exit', (code, signal) => {
                console.log(`[HeyMike] Backend process exited with code ${code}, signal ${signal}`);
                if (this.backendAutoStarted && code !== 0 && code !== null) {
                    vscode.window.showWarningMessage(`Hey Mike! backend crashed (exit code: ${code})`);
                }
                this.backendProcess = undefined;
                this.backendAutoStarted = false;
            });

            console.log('[HeyMike] Backend process started successfully');
            return true;

        } catch (error: any) {
            console.error('[HeyMike] Failed to start backend - Exception:', error);
            console.error('[HeyMike] Error stack:', error.stack);
            vscode.window.showErrorMessage(`Failed to start Hey Mike! backend: ${error.message}`);
            return false;
        }
    }

    /**
     * Wait for backend to be ready
     */
    private async waitForBackend(maxWaitMs: number = 10000): Promise<boolean> {
        const startTime = Date.now();
        const checkInterval = 500;

        while (Date.now() - startTime < maxWaitMs) {
            if (await this.checkBackendRunning()) {
                console.log('[HeyMike] Backend is ready!');
                return true;
            }
            await new Promise(resolve => setTimeout(resolve, checkInterval));
        }

        console.error('[HeyMike] Backend failed to start within timeout');
        return false;
    }

    /**
     * Actually connect to the backend via WebSocket
     */
    private connectToBackend() {
        const port = this.config.get<number>('backendPort', 8765);
        const url = `http://localhost:${port}`;

        console.log(`[HeyMike] Connecting to backend at ${url}`);

        this.socket = io(url, {
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5,
            timeout: 5000
        });

        this.setupEventHandlers();
    }

    /**
     * Setup Socket.IO event handlers
     */
    private setupEventHandlers() {
        if (!this.socket) {
            return;
        }

        // Connection events
        this.socket.on('connect', () => {
            console.log('[HeyMike] Connected to backend');
            this.socket?.emit('register', {
                type: 'vscode',
                workspace: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
                version: '2.0.0'
            });
            this.emit('connect', {});
            vscode.window.showInformationMessage('✅ Hey Mike! Connected to backend');
        });

        this.socket.on('disconnect', () => {
            console.log('[HeyMike] Disconnected from backend');
            this.emit('disconnect', {});
            vscode.window.showWarningMessage('⚠️ Hey Mike! Disconnected from backend');

            // Auto-reconnect if enabled
            if (this.config.get('autoReconnect', true)) {
                this.scheduleReconnect();
            }
        });

        this.socket.on('connect_error', (error) => {
            console.error('[HeyMike] Connection error:', error.message);
            this.emit('error', { message: error.message });
        });

        // Backend events
        this.socket.on('transcription', (data: TranscriptionData) => {
            console.log('[HeyMike] Received transcription:', data);
            this.emit('transcription', data);
        });

        this.socket.on('llm_result', (result: LLMResult) => {
            console.log('[HeyMike] Received LLM result');
            this.emit('llm_result', result);
        });

        this.socket.on('recording_state', (data: RecordingState) => {
            console.log('[HeyMike] Recording state:', data.state);
            this.emit('recording_state', data);
        });

        this.socket.on('processing_state', (data: ProcessingState) => {
            console.log('[HeyMike] Processing state:', data.state);
            this.emit('processing_state', data);
        });

        this.socket.on('mode_changed', (data: ModeChangedData) => {
            console.log('[HeyMike] Mode changed:', data.mode);
            this.emit('mode_changed', data);
        });

        this.socket.on('settings_updated', (settings: SettingsData) => {
            console.log('[HeyMike] Settings updated from backend');
            this.emit('settings_updated', settings);
        });

        this.socket.on('status_update', (data: any) => {
            console.log('[HeyMike] Status update:', data);
            this.emit('status_update', data);
        });
    }

    /**
     * Emit event to listeners
     */
    private emit(event: string, data: any) {
        this.eventEmitter.fire({ event, data });
    }

    /**
     * Schedule reconnection attempt
     */
    private scheduleReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }

        this.reconnectTimer = setTimeout(() => {
            console.log('[HeyMike] Attempting to reconnect...');
            this.reconnect();
        }, 3000);
    }

    /**
     * Reconnect to backend
     */
    reconnect() {
        this.disconnect();
        this.connect();
    }

    /**
     * Disconnect from backend
     */
    disconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = undefined;
        }

        if (this.socket) {
            this.socket.disconnect();
            this.socket = undefined;
        }
    }

    /**
     * Check if connected
     */
    isConnected(): boolean {
        return this.socket?.connected ?? false;
    }

    /**
     * Update backend settings
     */
    async updateSettings(settings: BackendSettings): Promise<any> {
        try {
            const port = this.config.get<number>('backendPort', 8765);
            const response = await fetch(`http://localhost:${port}/api/settings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error: any) {
            console.error('[HeyMike] Failed to update settings:', error);
            throw new Error(`Failed to update settings: ${error.message}`);
        }
    }

    /**
     * Get current settings from backend
     */
    async getSettings(): Promise<any> {
        try {
            const port = this.config.get<number>('backendPort', 8765);
            const response = await fetch(`http://localhost:${port}/api/settings`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error: any) {
            console.error('[HeyMike] Failed to get settings:', error);
            throw new Error(`Failed to get settings: ${error.message}`);
        }
    }

    /**
     * Request code explanation from backend
     */
    async explainCode(code: string, context: any): Promise<any> {
        try {
            const port = this.config.get<number>('backendPort', 8765);
            const response = await fetch(`http://localhost:${port}/api/explain`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, context })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error: any) {
            console.error('[HeyMike] Failed to explain code:', error);
            throw new Error(`Failed to explain code: ${error.message}`);
        }
    }

    /**
     * Request transcription (manual trigger)
     */
    requestTranscription() {
        if (!this.isConnected()) {
            vscode.window.showErrorMessage('Hey Mike! is not connected to backend');
            return;
        }

        this.socket?.emit('request_transcription', {
            timestamp: Date.now()
        });
    }

    /**
     * Stop backend process if auto-started
     */
    stopBackend() {
        if (this.backendProcess && this.backendAutoStarted) {
            console.log('[HeyMike] Stopping auto-started backend process...');

            // Give it a chance to clean up gracefully
            this.backendProcess.kill('SIGTERM');

            // Force kill after 5 seconds if still running
            setTimeout(() => {
                if (this.backendProcess && !this.backendProcess.killed) {
                    console.log('[HeyMike] Force killing backend process');
                    this.backendProcess.kill('SIGKILL');
                }
            }, 5000);

            this.backendProcess = undefined;
            this.backendAutoStarted = false;
        }
    }

    /**
     * Check if backend was auto-started
     */
    isBackendAutoStarted(): boolean {
        return this.backendAutoStarted;
    }

    /**
     * Dispose resources
     */
    dispose() {
        this.disconnect();

        // Only stop backend if it was auto-started AND user wants to stop it
        // For hybrid mode, we leave standalone backends running
        const stopOnExit = this.config.get<boolean>('stopBackendOnExit', false);
        if (stopOnExit) {
            this.stopBackend();
        } else if (this.backendAutoStarted) {
            console.log('[HeyMike] Leaving auto-started backend running (standalone mode)');
        }

        this.eventEmitter.dispose();
    }
}
