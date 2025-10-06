/**
 * Action Router for Hey Mike!
 * Routes transcriptions and commands to appropriate actions
 */

import * as vscode from 'vscode';
import { TranscriptionData, LLMResult } from '../types';
import { NoteCapture } from './noteCapture';

export class ActionRouter {
    private noteCapture: NoteCapture;

    constructor() {
        this.noteCapture = new NoteCapture();
    }

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
        // Use clipboard + paste approach to work everywhere (editors, chat, etc.)
        await vscode.env.clipboard.writeText(data.text);
        await vscode.commands.executeCommand('editor.action.clipboardPasteAction');

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

        // Check if backend classified this as a note (from context.note)
        if (data.context.note) {
            console.log('[HeyMike] Note classification from backend:', data.context.note.type);
            await this.captureBackendNote(data.context.note);
            return;
        }

        // Parse command from transcription (for other actions like explain, search, etc.)
        const command = this.parseCommand(data.text);

        if (!command) {
            // Fallback: If we can't understand the command, just insert it as text
            console.log('[HeyMike] Command not recognized, falling back to text insertion');

            // Insert as plain text using clipboard (works in chat, editors, etc.)
            await vscode.env.clipboard.writeText(data.text);
            await vscode.commands.executeCommand('editor.action.clipboardPasteAction');

            // Just show status message, no warning popup
            vscode.window.setStatusBarMessage(
                `✅ Inserted: ${data.text.substring(0, 50)}${data.text.length > 50 ? '...' : ''}`,
                3000
            );
            return;
        }

        // Execute command
        await this.executeCommand(command, data);
    }

    /**
     * Parse voice command from text
     * Note: Backend handles note detection via smart_detect_intent()
     */
    private parseCommand(text: string): { action: string, target?: string } | null {
        const lower = text.toLowerCase().trim();

        // Explain commands (future feature)
        if (lower.includes('explain')) {
            return { action: 'explain' };
        }

        // Search commands (future feature)
        if (lower.includes('search') || lower.includes('find')) {
            const searchTerm = lower.replace(/^(search|find)\s+/i, '').trim();
            return { action: 'search', target: searchTerm };
        }

        // Navigate commands (future feature)
        if (lower.includes('open') || lower.includes('go to')) {
            const fileTerm = lower.replace(/^(open|go to)\s+/i, '').trim();
            return { action: 'navigate', target: fileTerm };
        }

        return null;
    }

    /**
     * Execute parsed command
     * Note: Voice note capture is handled by backend's smart_detect_intent()
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
     * Capture voice note with full context
     * (Legacy method - kept for potential direct use)
     */
    private async captureVoiceNote(note: any) {
        try {
            // Extract code context
            const noteWithContext = await this.noteCapture.extractContext(note);

            // Save to NOTES.md
            await this.noteCapture.saveNote(noteWithContext);

            // Show confirmation
            const icon = this.getNoteIcon(note.type);
            vscode.window.showInformationMessage(
                `${icon} Captured ${note.type}: ${note.description.substring(0, 50)}${note.description.length > 50 ? '...' : ''}`,
                'Open Notes'
            ).then(selection => {
                if (selection === 'Open Notes') {
                    this.noteCapture.openNotes();
                }
            });

            console.log('[HeyMike] Voice note saved successfully');
        } catch (error: any) {
            vscode.window.showErrorMessage(`Failed to capture note: ${error.message}`);
            console.error('[HeyMike] Note capture error:', error);
        }
    }

    /**
     * Capture note classified by backend (from NoteData in context)
     */
    private async captureBackendNote(noteData: any) {
        try {
            console.log('[HeyMike] Capturing backend-classified note:', noteData);

            // Convert backend note data to frontend format
            const note = {
                type: noteData.type,
                description: noteData.description,
                timestamp: new Date(),
                explicit: noteData.explicit || false
            };

            // Extract code context
            const noteWithContext = await this.noteCapture.extractContext(note);

            // Save to NOTES.md
            await this.noteCapture.saveNote(noteWithContext);

            // Show confirmation with detection method
            const icon = this.getNoteIcon(note.type);
            const confidenceText = noteData.confidence
                ? ` (${Math.round(noteData.confidence * 100)}% confidence)`
                : '';

            vscode.window.showInformationMessage(
                `${icon} Captured ${note.type}${confidenceText}: ${note.description.substring(0, 50)}${note.description.length > 50 ? '...' : ''}`,
                'Open Notes'
            ).then(selection => {
                if (selection === 'Open Notes') {
                    this.noteCapture.openNotes();
                }
            });

            console.log('[HeyMike] Backend-classified note saved successfully');
        } catch (error: any) {
            vscode.window.showErrorMessage(`Failed to capture note: ${error.message}`);
            console.error('[HeyMike] Note capture error:', error);
        }
    }

    /**
     * Get emoji icon for note type
     */
    private getNoteIcon(type: string): string {
        const icons: { [key: string]: string } = {
            bug: '🐛',
            todo: '✅',
            note: '📝',
            question: '🤔',
            enhancement: '✨'
        };
        return icons[type] || '📝';
    }

    /**
     * Open NOTES.md file
     */
    async openNotes() {
        await this.noteCapture.openNotes();
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
