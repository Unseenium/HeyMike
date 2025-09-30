/**
 * Action Router for Hey Mike!
 * Routes transcriptions and commands to appropriate actions
 */

import * as vscode from 'vscode';
import { TranscriptionData, LLMResult } from '../types';

export class ActionRouter {

    /**
     * Handle transcription from backend
     */
    async handleTranscription(data: TranscriptionData) {
        console.log(`[HeyMike] Routing transcription - Mode: ${data.mode}, Text: "${data.text.substring(0, 100)}"`);

        if (data.mode === 'smart') {
            console.log('[HeyMike] Using Smart Mode (direct insertion)');
            await this.handleSmartMode(data);
        } else if (data.mode === 'action') {
            console.log('[HeyMike] Using Action Mode (command parsing)');
            await this.handleActionMode(data);
        } else {
            console.warn(`[HeyMike] Unknown mode: ${data.mode}, defaulting to Smart Mode`);
            await this.handleSmartMode(data);
        }
    }

    /**
     * Handle Smart Mode transcription (insert text)
     */
    private async handleSmartMode(data: TranscriptionData) {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor to insert text');
            return;
        }

        // Insert text at cursor position
        await editor.edit(editBuilder => {
            editBuilder.insert(editor.selection.active, data.text);
        });

        // Show notification
        vscode.window.setStatusBarMessage(
            `✅ Inserted: ${data.text.substring(0, 50)}${data.text.length > 50 ? '...' : ''}`,
            3000
        );
    }

    /**
     * Handle Action Mode transcription (interpret as command)
     */
    private async handleActionMode(data: TranscriptionData) {
        console.log('[HeyMike] Interpreting action command:', data.text);

        // Parse command from transcription
        const command = this.parseCommand(data.text);

        if (!command) {
            // Fallback: If we can't understand the command, just insert it as text
            console.log('[HeyMike] Command not recognized, falling back to text insertion');

            // Insert as plain text (fallback behavior) - silently
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                await editor.edit(editBuilder => {
                    editBuilder.insert(editor.selection.active, data.text);
                });
                // Just show status message, no warning popup
                vscode.window.setStatusBarMessage(
                    `✅ Inserted: ${data.text.substring(0, 50)}${data.text.length > 50 ? '...' : ''}`,
                    3000
                );
            }
            return;
        }

        // Execute command
        await this.executeCommand(command, data);
    }

    /**
     * Parse voice command from text
     */
    private parseCommand(text: string): { action: string, target?: string } | null {
        const lower = text.toLowerCase().trim();

        // Explain commands
        if (lower.includes('explain')) {
            return { action: 'explain' };
        }

        // Search commands
        if (lower.includes('search') || lower.includes('find')) {
            const searchTerm = lower.replace(/^(search|find)\s+/i, '').trim();
            return { action: 'search', target: searchTerm };
        }

        // Navigate commands
        if (lower.includes('open') || lower.includes('go to')) {
            const fileTerm = lower.replace(/^(open|go to)\s+/i, '').trim();
            return { action: 'navigate', target: fileTerm };
        }

        // Note capture commands
        if (lower.includes('note') || lower.includes('bug') || lower.includes('todo')) {
            return { action: 'note', target: text };
        }

        return null;
    }

    /**
     * Execute parsed command
     */
    private async executeCommand(command: { action: string, target?: string }, data: TranscriptionData) {
        try {
            switch (command.action) {
                case 'explain':
                    await this.explainCode();
                    break;

                case 'search':
                    await this.searchCode(command.target || '');
                    break;

                case 'navigate':
                    await this.navigateToFile(command.target || '');
                    break;

                case 'note':
                    await this.captureNote(command.target || '');
                    break;

                default:
                    vscode.window.showWarningMessage(`Unknown action: ${command.action}`);
            }
        } catch (error: any) {
            vscode.window.showErrorMessage(`Command failed: ${error.message}`);
        }
    }

    /**
     * Explain selected code
     */
    private async explainCode() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        const text = editor.document.getText(selection);

        if (!text) {
            vscode.window.showWarningMessage('No code selected');
            return;
        }

        vscode.window.showInformationMessage(`🤔 Explaining selected code...`);

        // This will be implemented when backend Code LLM is ready
        // For now, show a placeholder
        vscode.window.showInformationMessage(
            `📝 Code explanation will appear here (v2.0 feature - coming soon!)`
        );
    }

    /**
     * Search code by description
     */
    private async searchCode(query: string) {
        if (!query) {
            vscode.window.showWarningMessage('No search query provided');
            return;
        }

        vscode.window.showInformationMessage(`🔍 Searching for: ${query}...`);

        // Use VS Code's built-in search
        await vscode.commands.executeCommand('workbench.action.findInFiles', {
            query: query,
            isRegex: false,
            isCaseSensitive: false,
            matchWholeWord: false
        });
    }

    /**
     * Navigate to file
     */
    private async navigateToFile(fileName: string) {
        if (!fileName) {
            vscode.window.showWarningMessage('No file name provided');
            return;
        }

        // Use VS Code's quick open
        await vscode.commands.executeCommand('workbench.action.quickOpen', fileName);
    }

    /**
     * Capture voice note
     */
    private async captureNote(noteText: string) {
        if (!noteText) {
            vscode.window.showWarningMessage('No note text provided');
            return;
        }

        // Determine note type
        let noteType = 'note';
        const lower = noteText.toLowerCase();
        if (lower.includes('bug')) {
            noteType = 'bug';
        } else if (lower.includes('todo')) {
            noteType = 'todo';
        } else if (lower.includes('question')) {
            noteType = 'question';
        }

        const icon = noteType === 'bug' ? '🐛' : noteType === 'todo' ? '✅' : noteType === 'question' ? '❓' : '📝';

        vscode.window.showInformationMessage(
            `${icon} Captured ${noteType}: ${noteText.substring(0, 50)}${noteText.length > 50 ? '...' : ''}`
        );

        // TODO: Implement note storage (v2.0 feature)
    }

    /**
     * Handle LLM result from backend
     */
    async handleLLMResult(result: LLMResult) {
        console.log('[HeyMike] Handling LLM result');

        if (result.explanation) {
            // Show explanation in webview or notification
            this.showExplanation(result.explanation);
        }

        if (result.code) {
            // Insert code if provided
            await this.insertCode(result.code);
        }
    }

    /**
     * Show code explanation
     */
    private showExplanation(explanation: string) {
        // For now, use information message
        // In v2.0, this will be a webview overlay
        vscode.window.showInformationMessage(
            `💡 ${explanation.substring(0, 100)}${explanation.length > 100 ? '...' : ''}`,
            'See Full Explanation'
        ).then(selection => {
            if (selection === 'See Full Explanation') {
                // Open in new editor
                vscode.workspace.openTextDocument({
                    content: explanation,
                    language: 'markdown'
                }).then(doc => {
                    vscode.window.showTextDocument(doc);
                });
            }
        });
    }

    /**
     * Insert code at cursor
     */
    private async insertCode(code: string) {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }

        await editor.edit(editBuilder => {
            editBuilder.insert(editor.selection.active, code);
        });
    }
}
