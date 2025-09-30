/**
 * Status Bar Manager for Hey Mike!
 * Manages the VS Code status bar item with synchronized state
 */

import * as vscode from 'vscode';

export enum HeyMikeStatus {
    Ready = 'ready',
    Recording = 'recording',
    Processing = 'processing',
    SmartMode = 'smart',
    ActionMode = 'action',
    Disconnected = 'disconnected',
    Error = 'error'
}

export class StatusBarManager {
    private statusBarItem: vscode.StatusBarItem;
    private currentStatus: HeyMikeStatus = HeyMikeStatus.Disconnected;
    private currentMode: 'smart' | 'action' = 'smart';
    private recordingTimer?: NodeJS.Timeout;
    private processingTimer?: NodeJS.Timeout;

    constructor() {
        // Create status bar item (right side, high priority)
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100 // High priority
        );

        this.statusBarItem.command = 'heymike.showQuickPick';
        this.statusBarItem.tooltip = 'Hey Mike! - AI Voice Assistant';

        this.updateDisplay();

        // Only show if enabled in settings
        const config = vscode.workspace.getConfiguration('heymike');
        if (config.get('showStatusBar', true)) {
            this.statusBarItem.show();
        }
    }

    /**
     * Update status to Ready
     */
    showReady() {
        this.currentStatus = HeyMikeStatus.Ready;
        this.clearTimers();
        this.updateDisplay();
    }

    /**
     * Update status to Recording with pulsing animation
     */
    showRecording() {
        this.currentStatus = HeyMikeStatus.Recording;
        this.clearTimers();

        // Animate recording (pulsing icon)
        let frame = 0;
        this.recordingTimer = setInterval(() => {
            frame = (frame + 1) % 4;
            const icon = frame % 2 === 0 ? '$(record)' : '$(circle-filled)';
            this.statusBarItem.text = `${icon} Recording...`;
            this.statusBarItem.backgroundColor = new vscode.ThemeColor(
                'statusBarItem.errorBackground'
            );
        }, 500);
    }

    /**
     * Update status to Processing with spinner animation
     */
    showProcessing(message: string = 'Transcribing...') {
        this.currentStatus = HeyMikeStatus.Processing;
        this.clearTimers();

        // Animate processing (spinning icon)
        const spinFrames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
        let frame = 0;

        this.processingTimer = setInterval(() => {
            frame = (frame + 1) % spinFrames.length;
            this.statusBarItem.text = `${spinFrames[frame]} ${message}`;
            this.statusBarItem.backgroundColor = new vscode.ThemeColor(
                'statusBarItem.warningBackground'
            );
        }, 100);
    }

    /**
     * Update to Smart Mode
     */
    showSmartMode() {
        this.currentMode = 'smart';
        this.currentStatus = HeyMikeStatus.SmartMode;
        this.clearTimers();
        this.updateDisplay();
    }

    /**
     * Update to Action Mode
     */
    showActionMode() {
        this.currentMode = 'action';
        this.currentStatus = HeyMikeStatus.ActionMode;
        this.clearTimers();
        this.updateDisplay();
    }

    /**
     * Update status to Disconnected
     */
    showDisconnected() {
        this.currentStatus = HeyMikeStatus.Disconnected;
        this.clearTimers();
        this.updateDisplay();
    }

    /**
     * Update status to Error
     */
    showError(message: string) {
        this.currentStatus = HeyMikeStatus.Error;
        this.clearTimers();
        this.statusBarItem.text = `$(error) ${message}`;
        this.statusBarItem.backgroundColor = new vscode.ThemeColor(
            'statusBarItem.errorBackground'
        );
        this.statusBarItem.tooltip = `Hey Mike! Error: ${message}`;

        // Auto-clear error after 5 seconds
        setTimeout(() => this.showReady(), 5000);
    }

    /**
     * Update the display based on current status
     */
    private updateDisplay() {
        // Reset background color
        this.statusBarItem.backgroundColor = undefined;

        switch (this.currentStatus) {
            case HeyMikeStatus.Ready:
                const modeIcon = this.currentMode === 'smart' ? '$(edit)' : '$(zap)';
                const modeName = this.currentMode === 'smart' ? 'Smart' : 'Action';
                this.statusBarItem.text = `$(mic) Hey Mike (${modeName})`;
                this.statusBarItem.tooltip = `Hey Mike! - ${modeName} Mode\nClick for quick actions`;
                break;

            case HeyMikeStatus.SmartMode:
                this.statusBarItem.text = `$(edit) Smart Mode`;
                this.statusBarItem.tooltip = 'Hey Mike! - Smart Mode\nAI text enhancement enabled';
                break;

            case HeyMikeStatus.ActionMode:
                this.statusBarItem.text = `$(zap) Action Mode`;
                this.statusBarItem.tooltip = 'Hey Mike! - Action Mode\nVoice code commands enabled';
                break;

            case HeyMikeStatus.Disconnected:
                this.statusBarItem.text = `$(debug-disconnect) Hey Mike`;
                this.statusBarItem.tooltip = 'Hey Mike! - Disconnected\nBackend not running';
                this.statusBarItem.backgroundColor = new vscode.ThemeColor(
                    'statusBarItem.warningBackground'
                );
                break;

            default:
                this.statusBarItem.text = `$(mic) Hey Mike`;
                break;
        }
    }

    /**
     * Show custom status (for temporary messages)
     */
    showCustomStatus(icon: string, text: string, duration: number = 3000) {
        const previousStatus = this.currentStatus;
        this.clearTimers();

        this.statusBarItem.text = `${icon} ${text}`;

        setTimeout(() => {
            this.currentStatus = previousStatus;
            this.updateDisplay();
        }, duration);
    }

    /**
     * Update tooltip with additional info
     */
    updateTooltip(info: string) {
        this.statusBarItem.tooltip = `Hey Mike!\n${info}`;
    }

    /**
     * Clear all timers
     */
    private clearTimers() {
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = undefined;
        }
        if (this.processingTimer) {
            clearInterval(this.processingTimer);
            this.processingTimer = undefined;
        }
    }

    /**
     * Show or hide status bar
     */
    setVisible(visible: boolean) {
        if (visible) {
            this.statusBarItem.show();
        } else {
            this.statusBarItem.hide();
        }
    }

    /**
     * Dispose of resources
     */
    dispose() {
        this.clearTimers();
        this.statusBarItem.dispose();
    }
}
