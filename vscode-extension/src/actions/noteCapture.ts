/**
 * Voice Note Capture for Hey Mike!
 * Captures voice notes with code context
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export interface VoiceNote {
    type: 'bug' | 'todo' | 'note' | 'question' | 'enhancement';
    description: string;
    file?: string;
    line?: number;
    functionName?: string;
    codeSnippet?: string;
    timestamp: Date;
}

export class NoteCapture {
    private notesFilePath: string | null = null;

    /**
     * Extract code context from active editor
     */
    async extractContext(note: VoiceNote): Promise<VoiceNote> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return note;
        }

        const document = editor.document;
        const position = editor.selection.active;

        // Get file path (relative to workspace)
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            const relativePath = path.relative(workspaceFolder.uri.fsPath, document.uri.fsPath);
            note.file = relativePath;
        } else {
            note.file = path.basename(document.uri.fsPath);
        }

        // Get line number (1-indexed for display)
        note.line = position.line + 1;

        // Get function name (if available)
        note.functionName = await this.getFunctionName(document, position);

        // Get code snippet (5 lines before and after)
        note.codeSnippet = this.getCodeSnippet(document, position);

        return note;
    }

    /**
     * Get function/class name at current position
     */
    private async getFunctionName(document: vscode.TextDocument, position: vscode.Position): Promise<string | undefined> {
        try {
            // Use VS Code's symbol provider to find containing function/class
            const symbols = await vscode.commands.executeCommand<vscode.DocumentSymbol[]>(
                'vscode.executeDocumentSymbolProvider',
                document.uri
            );

            if (!symbols) {
                return undefined;
            }

            // Find the symbol containing current position
            const findContainingSymbol = (symbols: vscode.DocumentSymbol[]): vscode.DocumentSymbol | undefined => {
                for (const symbol of symbols) {
                    if (symbol.range.contains(position)) {
                        // Check children first (more specific)
                        const child = findContainingSymbol(symbol.children);
                        if (child) {
                            return child;
                        }
                        // Return this symbol if it's a function/method
                        if (
                            symbol.kind === vscode.SymbolKind.Function ||
                            symbol.kind === vscode.SymbolKind.Method ||
                            symbol.kind === vscode.SymbolKind.Constructor
                        ) {
                            return symbol;
                        }
                    }
                }
                return undefined;
            };

            const symbol = findContainingSymbol(symbols);
            return symbol?.name;
        } catch (error) {
            console.log('[HeyMike] Could not get function name:', error);
            return undefined;
        }
    }

    /**
     * Get code snippet around current line
     */
    private getCodeSnippet(document: vscode.TextDocument, position: vscode.Position): string {
        const lineNumber = position.line;
        const totalLines = document.lineCount;

        // Get 5 lines before and after (or less if near start/end)
        const startLine = Math.max(0, lineNumber - 5);
        const endLine = Math.min(totalLines - 1, lineNumber + 5);

        const lines: string[] = [];
        for (let i = startLine; i <= endLine; i++) {
            const lineText = document.lineAt(i).text;
            const marker = i === lineNumber ? ' // ← Note captured here' : '';
            lines.push(lineText + marker);
        }

        return lines.join('\n');
    }

    /**
     * Save note to NOTES.md
     */
    async saveNote(note: VoiceNote): Promise<void> {
        const notesPath = await this.getNotesFilePath();
        if (!notesPath) {
            throw new Error('Could not determine workspace folder');
        }

        // Read existing content or create new file
        let content = '';
        if (fs.existsSync(notesPath)) {
            content = fs.readFileSync(notesPath, 'utf-8');
        } else {
            content = '# Hey Mike! Voice Notes\n\n';
        }

        // Format the note
        const noteMarkdown = this.formatNote(note);

        // Find the appropriate section or create it
        const sectionHeader = this.getSectionHeader(note.type);
        const sectionIndex = content.indexOf(sectionHeader);

        if (sectionIndex !== -1) {
            // Insert after section header
            const insertPosition = content.indexOf('\n', sectionIndex) + 1;
            content = content.slice(0, insertPosition) + noteMarkdown + '\n' + content.slice(insertPosition);
        } else {
            // Add new section at the end
            if (!content.endsWith('\n\n')) {
                content += content.endsWith('\n') ? '\n' : '\n\n';
            }
            content += sectionHeader + '\n' + noteMarkdown + '\n';
        }

        // Write to file
        fs.writeFileSync(notesPath, content, 'utf-8');
    }

    /**
     * Get section header for note type
     */
    private getSectionHeader(type: VoiceNote['type']): string {
        const headers = {
            bug: '## 🐛 Bugs',
            todo: '## ✅ TODOs',
            note: '## 📝 Notes',
            question: '## 🤔 Questions',
            enhancement: '## ✨ Enhancements'
        };
        return headers[type];
    }

    /**
     * Format note as markdown
     */
    private formatNote(note: VoiceNote): string {
        const timestamp = note.timestamp.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });

        let markdown = `- [ ] **${note.description}**\n`;

        if (note.file) {
            markdown += `  - File: \`${note.file}${note.line ? ':' + note.line : ''}\`\n`;
        }

        if (note.functionName) {
            markdown += `  - Function: \`${note.functionName}()\`\n`;
        }

        markdown += `  - Captured: ${timestamp}\n`;

        if (note.codeSnippet) {
            const language = this.getLanguageFromFile(note.file || '');
            markdown += `  - Context:\n    \`\`\`${language}\n`;
            // Indent code snippet
            const indentedSnippet = note.codeSnippet.split('\n').map(line => '    ' + line).join('\n');
            markdown += indentedSnippet + '\n    ```\n';
        }

        return markdown;
    }

    /**
     * Get language identifier from file extension
     */
    private getLanguageFromFile(filePath: string): string {
        const ext = path.extname(filePath).toLowerCase();
        const languageMap: { [key: string]: string } = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.cs': 'csharp',
            '.md': 'markdown',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sh': 'bash',
        };
        return languageMap[ext] || '';
    }

    /**
     * Get path to NOTES.md
     */
    private async getNotesFilePath(): Promise<string | null> {
        if (this.notesFilePath) {
            return this.notesFilePath;
        }

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            return null;
        }

        this.notesFilePath = path.join(workspaceFolder.uri.fsPath, 'NOTES.md');
        return this.notesFilePath;
    }

    /**
     * Open NOTES.md in editor
     */
    async openNotes(): Promise<void> {
        const notesPath = await this.getNotesFilePath();
        if (!notesPath) {
            vscode.window.showWarningMessage('No workspace folder found');
            return;
        }

        // Create file if it doesn't exist
        if (!fs.existsSync(notesPath)) {
            fs.writeFileSync(notesPath, '# Hey Mike! Voice Notes\n\n', 'utf-8');
        }

        // Open in editor
        const document = await vscode.workspace.openTextDocument(notesPath);
        await vscode.window.showTextDocument(document);
    }
}
