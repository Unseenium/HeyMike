/**
 * Quick Pick Menu for Hey Mike!
 * Provides quick access to common actions
 */

import * as vscode from 'vscode';

interface QuickPickAction {
    label: string;
    description: string;
    icon: string;
    command: string;
}

export class QuickPickMenu {
    private actions: QuickPickAction[] = [
        {
            label: '$(record) Start Recording',
            description: 'Start voice recording (Cmd+Shift+Space)',
            icon: 'record',
            command: 'heymike.startRecording'
        },
        {
            label: '$(edit) Smart Mode',
            description: 'Auto-enhance English text (Cmd+Opt+1)',
            icon: 'edit',
            command: 'heymike.switchToSmartMode'
        },
        {
            label: '$(zap) Action Mode',
            description: 'Voice code commands (Cmd+Opt+2)',
            icon: 'zap',
            command: 'heymike.switchToActionMode'
        },
        {
            label: '$(question) Explain Code',
            description: 'Explain selected code',
            icon: 'question',
            command: 'heymike.explainCode'
        },
        {
            label: '$(search) Search Code',
            description: 'Search codebase by description',
            icon: 'search',
            command: 'heymike.searchCode'
        },
        {
            label: '$(gear) Settings',
            description: 'Configure Hey Mike!',
            icon: 'gear',
            command: 'heymike.openSettings'
        }
    ];

    /**
     * Show quick pick menu
     */
    async show() {
        const selected = await vscode.window.showQuickPick(
            this.actions,
            {
                placeHolder: 'Hey Mike! - Select an action',
                matchOnDescription: true,
                title: '🎙️ Hey Mike! Quick Actions'
            }
        );

        if (selected) {
            vscode.commands.executeCommand(selected.command);
        }
    }

    /**
     * Show mode selection quick pick
     */
    async showModeSelector() {
        const config = vscode.workspace.getConfiguration('heymike');
        const currentMode = config.get<string>('currentMode', 'smart');

        const modes = [
            {
                label: '$(edit) Smart Mode',
                description: currentMode === 'smart' ? '(Currently Active)' : 'Auto-enhance English text',
                mode: 'smart'
            },
            {
                label: '$(zap) Action Mode',
                description: currentMode === 'action' ? '(Currently Active)' : 'Voice code commands',
                mode: 'action'
            }
        ];

        const selected = await vscode.window.showQuickPick(
            modes,
            {
                placeHolder: 'Select transcription mode',
                title: '🎯 Hey Mike! Mode Selection'
            }
        );

        if (selected) {
            if (selected.mode === 'smart') {
                vscode.commands.executeCommand('heymike.switchToSmartMode');
            } else if (selected.mode === 'action') {
                vscode.commands.executeCommand('heymike.switchToActionMode');
            }
        }
    }

    /**
     * Show model selection quick pick
     */
    async showModelSelector(type: 'whisper' | 'text' | 'code') {
        const config = vscode.workspace.getConfiguration('heymike');
        let models: any[];
        let currentModel: string;
        let configKey: string;
        let title: string;

        if (type === 'whisper') {
            configKey = 'whisperModel';
            title = '🎙️ Select Whisper Model';
            currentModel = config.get<string>(configKey, 'small');
            models = [
                { label: '$(circle-filled) Tiny', description: '39MB (fastest)', size: '39MB', value: 'tiny' },
                { label: '$(circle-filled) Base', description: '74MB (fast)', size: '74MB', value: 'base' },
                { label: '$(circle-filled) Small', description: '244MB (balanced)', size: '244MB', value: 'small' },
                { label: '$(circle-filled) Medium', description: '769MB (accurate)', size: '769MB', value: 'medium' },
                { label: '$(circle-filled) Large', description: '1550MB (most accurate)', size: '1.5GB', value: 'large' }
            ];
        } else if (type === 'text') {
            configKey = 'textLLM';
            title = '🧠 Select Text Enhancement LLM';
            currentModel = config.get<string>(configKey, 'llama-3.2-1b');
            models = [
                { label: '$(circle-filled) Llama 3.2 1B', description: '800MB (very fast)', value: 'llama-3.2-1b' },
                { label: '$(circle-filled) Phi-3 Mini', description: '2.4GB (better quality)', value: 'phi-3-mini' },
                { label: '$(circle-filled) Qwen 2.5 1.5B', description: '1.5GB (balanced)', value: 'qwen-2.5-1.5b' }
            ];
        } else {
            configKey = 'codeLLM';
            title = '💻 Select Code LLM';
            currentModel = config.get<string>(configKey, 'qwen-2.5-coder-3b');
            models = [
                { label: '$(circle-filled) DeepSeek Coder 1.3B', description: '1.3GB (fastest)', value: 'deepseek-coder-1.3b' },
                { label: '$(circle-filled) Qwen 2.5 Coder 3B', description: '3GB (recommended)', value: 'qwen-2.5-coder-3b' },
                { label: '$(circle-filled) Qwen 2.5 Coder 7B', description: '7GB (best quality)', value: 'qwen-2.5-coder-7b' },
                { label: '$(circle-filled) DeepSeek Coder 6.7B', description: '6.7GB (excellent)', value: 'deepseek-coder-6.7b' }
            ];
        }

        // Add checkmark to current model
        models = models.map(m => ({
            ...m,
            label: m.value === currentModel ? `$(check) ${m.label.replace('$(circle-filled)', '')}` : m.label
        }));

        const selected = await vscode.window.showQuickPick(
            models,
            {
                placeHolder: `Current: ${currentModel}`,
                title: title,
                matchOnDescription: true
            }
        );

        if (selected && selected.value !== currentModel) {
            await config.update(configKey, selected.value, true);
            vscode.window.showInformationMessage(`✅ Switched to ${selected.label.replace('$(check)', '').replace('$(circle-filled)', '').trim()}`);
        }
    }
}
