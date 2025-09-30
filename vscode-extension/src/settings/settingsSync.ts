/**
 * Settings Sync for Hey Mike!
 * Synchronizes VS Code settings with Python backend
 */

import * as vscode from 'vscode';
import { BackendClient } from '../connection/backendClient';

export class SettingsSync {
    private config = vscode.workspace.getConfiguration('heymike');

    constructor(private backendClient: BackendClient) {
        // Listen for configuration changes
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('heymike')) {
                this.syncToBackend();
            }
        });
    }

    /**
     * Sync VS Code settings to backend
     */
    async syncToBackend() {
        if (!this.backendClient.isConnected()) {
            console.log('[HeyMike] Not connected, skipping settings sync');
            return;
        }

        try {
            const settings = {
                whisperModel: this.config.get<string>('whisperModel', 'small'),
                textLLM: this.config.get<string>('textLLM', 'llama-3.2-1b'),
                codeLLM: this.config.get<string>('codeLLM', 'qwen-2.5-coder-3b'),
                enhancementStyle: this.config.get<string>('enhancementStyle', 'standard'),
                transcriptionMode: this.config.get<string>('currentMode', 'smart'),
                alwaysRaw: this.config.get<boolean>('alwaysRaw', false)
            };

            console.log('[HeyMike] Syncing settings to backend:', settings);
            await this.backendClient.updateSettings(settings);
            console.log('[HeyMike] Settings synced successfully');
        } catch (error: any) {
            console.error('[HeyMike] Failed to sync settings:', error);
            vscode.window.showErrorMessage(`Hey Mike! settings sync failed: ${error.message}`);
        }
    }

    /**
     * Sync backend settings to VS Code
     */
    async syncFromBackend() {
        try {
            const settings = await this.backendClient.getSettings();
            console.log('[HeyMike] Received settings from backend:', settings);

            // Update VS Code configuration
            const config = vscode.workspace.getConfiguration('heymike');

            if (settings.model) {
                await config.update('whisperModel', settings.model, true);
            }
            if (settings.llm_model) {
                await config.update('textLLM', settings.llm_model, true);
            }
            if (settings.enhancement_style) {
                await config.update('enhancementStyle', settings.enhancement_style, true);
            }
            if (settings.transcription_mode) {
                await config.update('currentMode', settings.transcription_mode, true);
            }
            if (settings.always_raw !== undefined) {
                await config.update('alwaysRaw', settings.always_raw, true);
            }

            console.log('[HeyMike] Settings synced from backend');
        } catch (error: any) {
            console.error('[HeyMike] Failed to sync from backend:', error);
        }
    }
}
