/**
 * Type definitions for Hey Mike! VS Code extension
 */

export interface TranscriptionData {
    text: string;
    mode: 'smart' | 'action';
    context: {
        timestamp: number;
        language?: string;
        [key: string]: any;
    };
}

export interface LLMResult {
    explanation?: string;
    code?: string;
    context?: any;
}

export interface RecordingState {
    state: 'recording' | 'ready';
    timestamp: number;
}

export interface ProcessingState {
    state: 'processing' | 'ready';
    message?: string;
    timestamp: number;
}

export interface ModeChangedData {
    mode: 'smart' | 'action';
    timestamp: number;
}

export interface SettingsData {
    [key: string]: any;
}

export interface StatusData {
    status: string;
    details?: {
        [key: string]: any;
    };
    timestamp: number;
}

export interface BackendSettings {
    whisperModel?: string;
    textLLM?: string;
    codeLLM?: string;
    enhancementStyle?: string;
    transcriptionMode?: string;
    alwaysRaw?: boolean;
}
