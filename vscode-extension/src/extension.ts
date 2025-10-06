/**
 * Hey Mike! VS Code Extension
 * Main extension entry point
 */

import * as vscode from 'vscode';
import { BackendClient } from './connection/backendClient';
import { StatusBarManager } from './ui/statusBar';
import { QuickPickMenu } from './ui/quickPick';
import { ActionRouter } from './actions/actionRouter';
import { SettingsSync } from './settings/settingsSync';

let statusBar: StatusBarManager;
let backendClient: BackendClient;
let quickPick: QuickPickMenu;
let actionRouter: ActionRouter;
let settingsSync: SettingsSync;

/**
 * Extension activation
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('[HeyMike] Extension is now active!');

    // Initialize components
    statusBar = new StatusBarManager();
    backendClient = new BackendClient();
    quickPick = new QuickPickMenu();
    actionRouter = new ActionRouter();
    settingsSync = new SettingsSync(backendClient);

    // Setup backend event listeners
    setupBackendListeners();

    // Register commands
    registerCommands(context);

    // Connect to backend
    connectToBackend();

    // Show welcome message (only on first install)
    const hasShownWelcome = context.globalState.get('heymike.hasShownWelcome', false);
    if (!hasShownWelcome) {
        showWelcomeMessage();
        context.globalState.update('heymike.hasShownWelcome', true);
    }

    // Add to subscriptions
    context.subscriptions.push(
        statusBar,
        backendClient,
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('heymike.showStatusBar')) {
                const config = vscode.workspace.getConfiguration('heymike');
                statusBar.setVisible(config.get('showStatusBar', true));
            }
        })
    );

    console.log('[HeyMike] Extension activated successfully');
}

/**
 * Extension deactivation
 */
export function deactivate() {
    console.log('[HeyMike] Extension is being deactivated');
    backendClient?.disconnect();
}

/**
 * Setup backend event listeners
 */
function setupBackendListeners() {
    backendClient.onEvent(({ event, data }) => {
        switch (event) {
            case 'connect':
                statusBar.showReady();
                settingsSync.syncToBackend();
                break;

            case 'disconnect':
                statusBar.showDisconnected();
                break;

            case 'error':
                statusBar.showError(data.message || 'Connection error');
                break;

            case 'transcription':
                actionRouter.handleTranscription(data);
                break;

            case 'llm_result':
                actionRouter.handleLLMResult(data);
                break;

            case 'recording_state':
                if (data.state === 'recording') {
                    statusBar.showRecording();
                } else {
                    statusBar.showReady();
                }
                break;

            case 'processing_state':
                if (data.state === 'processing') {
                    statusBar.showProcessing(data.message || 'Processing...');
                } else {
                    statusBar.showReady();
                }
                break;

            case 'mode_changed':
                if (data.mode === 'smart') {
                    statusBar.showSmartMode();
                } else if (data.mode === 'action') {
                    statusBar.showActionMode();
                }
                // Sync mode to VS Code settings
                const config = vscode.workspace.getConfiguration('heymike');
                config.update('currentMode', data.mode, true);
                break;

            case 'settings_updated':
                settingsSync.syncFromBackend();
                break;

            case 'status_update':
                // Handle general status updates
                console.log('[HeyMike] Status update:', data);
                break;
        }
    });
}

/**
 * Register VS Code commands
 */
function registerCommands(context: vscode.ExtensionContext) {
    // Start recording (triggers backend hotkey)
    context.subscriptions.push(
        vscode.commands.registerCommand('heymike.startRecording', () => {
            if (!backendClient.isConnected()) {
                vscode.window.showErrorMessage('Hey Mike! is not connected. Please start the backend.');
                return;
            }
            vscode.window.showInformationMessage('🎙️ Use Cmd+Shift+Space to record (global hotkey)');
        })
    );

    // Show quick pick menu
    context.subscriptions.push(
        vscode.commands.registerCommand('heymike.showQuickPick', () => {
            quickPick.show();
        })
    );

    // Switch to Smart Mode
    context.subscriptions.push(
        vscode.commands.registerCommand('heymike.switchToSmartMode', async () => {
            const config = vscode.workspace.getConfiguration('heymike');
            await config.update('currentMode', 'smart', true);
            statusBar.showSmartMode();
            vscode.window.showInformationMessage('📝 Switched to Smart Mode (Cmd+Opt+1)');
        })
    );

    // Switch to Action Mode
    context.subscriptions.push(
        vscode.commands.registerCommand('heymike.switchToActionMode', async () => {
            const config = vscode.workspace.getConfiguration('heymike');
            await config.update('currentMode', 'action', true);
            statusBar.showActionMode();
            vscode.window.showInformationMessage('⚡ Switched to Action Mode (Cmd+Opt+2)');
        })
    );

    // Explain code
    context.subscriptions.push(
        vscode.commands.registerCommand('heymike.explainCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const selection = editor.selection;
            const code = editor.document.getText(selection);

            if (!code) {
                vscode.window.showWarningMessage('No code selected');
                return;
            }

            if (!backendClient.isConnected()) {
                vscode.window.showErrorMessage('Hey Mike! backend is not connected');
                return;
            }

            try {
                statusBar.showProcessing('Explaining code...');
                const result = await backendClient.explainCode(code, {
                    language: editor.document.languageId,
                    file: editor.document.fileName
                });

                actionRouter.handleLLMResult(result);
                statusBar.showReady();
            } catch (error: any) {
                statusBar.showError('Explanation failed');
                vscode.window.showErrorMessage(`Failed to explain code: ${error.message}`);
            }
        })
    );

    // Search code
    context.subscriptions.push(
        vscode.commands.registerCommand('heymike.searchCode', async () => {
            const query = await vscode.window.showInputBox({
                placeHolder: 'What are you looking for?',
                prompt: 'Describe what you want to find in your code'
            });

            if (query) {
                await vscode.commands.executeCommand('workbench.action.findInFiles', {
                    query: query,
                    isRegex: false
                });
            }
        })
    );

    // Open settings
    context.subscriptions.push(
        vscode.commands.registerCommand('heymike.openSettings', () => {
            vscode.commands.executeCommand('workbench.action.openSettings', 'heymike');
        })
    );

    // Open voice notes
    context.subscriptions.push(
        vscode.commands.registerCommand('heymike.openNotes', () => {
            actionRouter.openNotes();
        })
    );
}

/**
 * Connect to backend server
 */
async function connectToBackend() {
    try {
        console.log('[HeyMike] Initializing backend connection...');

        // Show connecting status
        statusBar.showCustomStatus('$(sync~spin)', 'Checking backend...', 30000);

        // Connect (will auto-start if needed)
        await backendClient.connect();

        console.log('[HeyMike] Backend connection initialized');
    } catch (error: any) {
        console.error('[HeyMike] Failed to connect to backend:', error);
        statusBar.showDisconnected();

        vscode.window.showErrorMessage(
            'Hey Mike! backend connection failed.',
            'Retry',
            'Open Instructions'
        ).then(selection => {
            if (selection === 'Retry') {
                connectToBackend();
            } else if (selection === 'Open Instructions') {
                vscode.env.openExternal(vscode.Uri.parse('https://github.com/Unseenium/HeyMike#setup'));
            }
        });
    }
}

/**
 * Show welcome message on first install
 */
function showWelcomeMessage() {
    vscode.window.showInformationMessage(
        '👋 Welcome to Hey Mike! - AI Voice Coding Assistant',
        'Get Started',
        'Open Settings'
    ).then(selection => {
        if (selection === 'Get Started') {
            vscode.env.openExternal(vscode.Uri.parse('https://github.com/Unseenium/HeyMike#quick-start'));
        } else if (selection === 'Open Settings') {
            vscode.commands.executeCommand('heymike.openSettings');
        }
    });
}
