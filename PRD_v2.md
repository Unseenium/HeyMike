# Product Requirements Document (PRD) v2.0

## Hey Mike!: Intelligent Voice Assistant for macOS

### Version 2.0 - "Hey Mike!" Voice Commands
### Date: September 2025

---

## 1. Executive Summary

Hey Mike! v2.0 evolves from a speech-to-text dictation tool into an intelligent voice assistant for macOS. Building on the existing MLX Whisper foundation, v2.0 adds MLX-optimized LLM capabilities for natural language command interpretation, enabling users to control their Mac through conversational voice commands while maintaining complete privacy and offline operation.

**Key Evolution:**
- **v1.0**: "Press hotkey → Speak → Get text"
- **v2.0**: "Hey Mike, open Chrome and search for Python tutorials" → *Chrome opens with search results*

## 2. Product Vision & Strategy

### 2.1 Vision Statement
Transform Hey Mike! into the most intelligent, privacy-focused voice assistant for macOS, combining best-in-class speech recognition with natural language understanding to create a seamless voice-controlled computing experience.

### 2.2 Strategic Goals
1. **Expand Use Cases**: From dictation-only to comprehensive voice control
2. **Maintain Privacy Leadership**: Keep all AI processing local and offline
3. **Leverage Apple Silicon**: Maximize MLX performance for dual AI workloads
4. **Preserve Simplicity**: Add power without complexity
5. **Enable Workflows**: Voice control for common developer/professional tasks

### 2.3 Competitive Positioning
- **vs. Siri**: More capable, programmable, privacy-focused, works offline
- **vs. Talon Voice**: Simpler setup, broader appeal beyond developers
- **vs. Dragon**: Modern AI, Mac-native, affordable, privacy-first

## 3. Enhanced Target Users

### 3.1 Expanded Primary Users
- **Developers & Engineers**: Voice control for terminal, IDE, and development workflows
- **Content Creators**: Dictation + voice control for creative applications
- **Professionals**: Meeting notes + system control for productivity workflows  
- **Power Users**: Advanced Mac automation through natural language
- **Accessibility Users**: Comprehensive voice control alternative to mouse/keyboard

### 3.2 New User Personas

**David the Developer**
- *Need*: "Hey Magik, open terminal and cd to my project directory"
- *Workflow*: Code review while speaking commands to navigate files and run tests
- *Value*: Hands-free development workflow, especially during pair programming

**Emma the Executive**
- *Need*: "Hey Magik, take a screenshot and open Slack"
- *Workflow*: Quick system actions during video calls without keyboard noise
- *Value*: Professional efficiency without disrupting meetings

**Carlos the Content Creator**
- *Need*: "Hey Magik, open Final Cut Pro and create a new project called Tutorial 5"
- *Workflow*: Voice control creative applications while hands are busy
- *Value*: Seamless creative flow without breaking concentration

## 4. Core Features v2.0

### 4.1 Intelligent Command Processing (NEW)

#### 4.1.1 Wake Word Detection
- **Primary Wake Word**: "Hey Magik" (with variations: "Hey Magic", "Magik", "Magic")
- **Context-Aware**: Distinguishes commands from dictation content
- **Confidence Scoring**: Only activates on high-confidence wake word detection
- **False Positive Handling**: Graceful fallback to dictation mode

#### 4.1.2 Natural Language Understanding
- **MLX LLM Integration**: Local language model for command interpretation
- **Intent Classification**: Automatically categorize user intentions
- **Parameter Extraction**: Parse entities (app names, file paths, search queries)
- **Contextual Commands**: "Open that file" after discussing a specific file

#### 4.1.3 Command Categories

**Application Control**
- Launch applications: "Hey Magik, open Chrome"
- Application-specific actions: "Hey Magik, create new document in Pages"
- Window management: "Hey Magik, minimize all windows"

**Web & Search**
- Web searches: "Hey Magik, search for MLX tutorials"
- Site-specific: "Hey Magik, search GitHub for Python projects"
- Quick lookups: "Hey Magik, what's the weather like?"

**Terminal & Development**
- Directory navigation: "Hey Magik, cd to Documents folder"
- File operations: "Hey Magik, list files in current directory"
- Development commands: "Hey Magik, run npm install"
- Git operations: "Hey Magik, commit changes with message 'fix bug'"

**System Control**
- Volume/brightness: "Hey Magik, increase volume to 50%"
- Screenshots: "Hey Magik, take a screenshot of this window"
- System preferences: "Hey Magik, open network settings"

**File Management**
- Create files: "Hey Magik, create a new Python file called main.py"
- File operations: "Hey Magik, move this file to Desktop"
- Quick access: "Hey Magik, open my Downloads folder"

### 4.2 Enhanced User Interface

#### 4.2.1 Dual-Mode Operation
- **Dictation Mode**: Traditional speech-to-text (existing functionality)
- **Command Mode**: Activated by wake word detection
- **Auto-Detection**: Seamless switching based on speech content
- **Manual Toggle**: Option to force specific mode

#### 4.2.2 Visual Feedback System
- **Mode Indicators**: 
  - 🎤 Dictation ready
  - 🧠 Command processing
  - ⚡ Executing command
  - ✅ Command completed
  - ❌ Command failed
- **Command Preview**: Show interpreted command before execution
- **Confirmation Prompts**: For potentially destructive actions

#### 4.2.3 Enhanced Menu Bar Interface
- **Mode Selection**: Toggle between dictation-only and intelligent modes
- **Command History**: Recent voice commands and their outcomes
- **Model Status**: Both Whisper and LLM model information
- **Quick Settings**: Rapid access to common configurations

### 4.3 Safety & Security Framework

#### 4.3.1 Command Validation
- **Whitelist Approach**: Only allow pre-approved command patterns
- **Confirmation Required**: Destructive operations require explicit confirmation
- **Sandbox Mode**: Test commands without actual execution
- **User Permissions**: Granular control over command categories

#### 4.3.2 Privacy Protection
- **Local Processing**: All LLM inference happens on-device
- **No Command Logging**: Voice commands processed in memory only
- **Encrypted Settings**: User preferences stored securely
- **Audit Trail**: Optional local logging for debugging (user-controlled)

## 5. Technical Architecture v2.0

### 5.1 Enhanced System Requirements
- **macOS Version**: macOS 13.0+ (for advanced MLX features)
- **Architecture**: Apple Silicon (M1/M2/M3/M4) required
- **Memory**: 4GB+ RAM (2GB for Whisper + 2GB for LLM)
- **Storage**: 3-8GB (Whisper models + LLM models)
- **Permissions**: Microphone, Accessibility, Automation (new)

### 5.2 Dual AI Architecture

#### 5.2.1 Speech Recognition Pipeline
```
Audio Input → MLX Whisper → Text Output → Wake Word Detection
                                      ↓
                              Command/Dictation Router
                                      ↓
                         ┌─────────────────────────┐
                         ↓                         ↓
                  Dictation Mode              Command Mode
                 (Text Insertion)         (LLM Processing)
```

#### 5.2.2 Command Processing Pipeline
```
Voice Command → Whisper → Wake Word Check → LLM Interpretation → Command Execution
                                    ↓              ↓                    ↓
                              "Hey Magik..."   Intent + Params    System Actions
```

### 5.3 New Core Components

#### 5.3.1 MLXLLMManager
- **Model Loading**: Efficient LLM model management
- **Inference Engine**: Fast command interpretation
- **Context Management**: Maintain conversation context
- **Fallback Handling**: Graceful degradation on errors

#### 5.3.2 CommandProcessor
- **Intent Classification**: Determine user's intended action
- **Parameter Extraction**: Parse command arguments
- **Validation**: Security and safety checks
- **Execution Routing**: Dispatch to appropriate handlers

#### 5.3.3 ActionExecutor
- **Application Control**: Launch and control macOS applications
- **Terminal Interface**: Execute shell commands safely
- **System Integration**: Control system settings and functions
- **Web Automation**: Browser control and search execution

#### 5.3.4 WakeWordDetector
- **Pattern Matching**: Detect "Hey Magik" variations
- **Confidence Scoring**: Minimize false positives
- **Context Awareness**: Distinguish commands from dictation
- **Performance Optimization**: Low-latency detection

### 5.4 Updated App Structure
```
MagikMike/
├── Core/
│   ├── MLXWhisperManager.py      # Speech recognition (existing)
│   ├── MLXLLMManager.py          # Language model integration (NEW)
│   ├── CommandProcessor.py       # Command interpretation (NEW)
│   ├── ActionExecutor.py         # System action execution (NEW)
│   ├── WakeWordDetector.py       # Wake word detection (NEW)
│   ├── HotkeyManager.py          # Global hotkey handling (enhanced)
│   ├── TextInsertionManager.py   # Text insertion (existing)
│   └── AudioManager.py           # Audio capture (existing)
├── UI/
│   ├── MenuBarController.py      # Menu bar interface (enhanced)
│   ├── CommandModeUI.py          # Command mode interface (NEW)
│   ├── SettingsView.py          # Configuration interface (enhanced)
│   └── StatusIndicator.py        # Visual feedback (enhanced)
├── Models/
│   ├── WhisperModels/           # Whisper model files (existing)
│   ├── LLMModels/               # LLM model files (NEW)
│   ├── CommandSchemas/          # Command validation schemas (NEW)
│   ├── RecognitionResult.py     # Transcription results (existing)
│   └── AppSettings.py           # User configuration (enhanced)
├── Actions/                      # Command execution modules (NEW)
│   ├── AppActions.py            # Application control
│   ├── TerminalActions.py       # Terminal/shell commands
│   ├── SystemActions.py         # System control
│   ├── WebActions.py            # Web/search actions
│   └── FileActions.py           # File management
└── Security/                     # Safety and security (NEW)
    ├── CommandValidator.py       # Command validation
    ├── PermissionManager.py      # Permission handling
    └── SafetyFilters.py         # Safety checks
```

## 6. User Experience Flows v2.0

### 6.1 Enhanced First Launch Flow
1. User launches MagikMike v2.0
2. App downloads Whisper model (existing)
3. **NEW**: App downloads lightweight LLM model
4. Permission requests: Microphone, Accessibility, **Automation**
5. **NEW**: Command mode introduction and demo
6. **NEW**: Safety settings configuration
7. App ready with both dictation and command capabilities

### 6.2 Command Mode Usage Flow
1. User presses hotkey (⌘⇧Space) or uses always-on listening
2. User says "Hey Magik, [command]"
3. Wake word detected → Command mode activated
4. Speech transcribed via Whisper
5. **NEW**: LLM interprets command intent and parameters
6. **NEW**: Command validated for safety
7. **NEW**: System action executed
8. **NEW**: Visual confirmation of completion
9. Return to ready state

### 6.3 Hybrid Usage Examples

**Dictation + Commands in Same Session:**
```
User: "Hey Magik, open TextEdit"
→ TextEdit opens

User: [Presses hotkey] "Dear John, I hope this email finds you well..."
→ Text appears in TextEdit

User: "Hey Magik, save this document as letter.txt"
→ Document saved with specified name
```

**Development Workflow:**
```
User: "Hey Magik, open terminal and cd to my projects folder"
→ Terminal opens, navigates to ~/Projects

User: "Hey Magik, create a new Python file called calculator.py"
→ File created and opened in default editor

User: [Dictation mode] "def add(a, b): return a + b"
→ Code appears in editor
```

## 7. Model Selection & Performance

### 7.1 LLM Model Options
- **Lightweight**: Llama 3.2 1B (800MB, <1s inference)
- **Balanced**: Phi-3 Mini (2.4GB, ~2s inference)  
- **Capable**: Qwen 2.5 3B (1.8GB, ~3s inference)

### 7.2 Performance Targets
- **Wake Word Detection**: <100ms latency
- **Command Processing**: <3s end-to-end (Whisper + LLM + Execution)
- **Memory Usage**: 3-6GB total (Whisper + LLM + overhead)
- **Battery Impact**: <10% additional drain during active use

### 7.3 Optimization Strategies
- **Model Caching**: Keep both models loaded for instant switching
- **Inference Optimization**: MLX quantization and optimization
- **Smart Loading**: Load LLM only when command mode enabled
- **Background Processing**: Async command processing

## 8. Safety & Security Framework

### 8.1 Command Safety Levels

**Level 1 - Safe (Auto-execute)**
- Open applications
- Web searches  
- Volume/brightness control
- Take screenshots

**Level 2 - Caution (Confirm first)**
- File operations (create, move, delete)
- Terminal commands
- System preference changes

**Level 3 - Restricted (Require explicit enable)**
- Administrative commands
- Network configuration
- Security settings

### 8.2 Security Measures
- **Command Whitelisting**: Only approved command patterns allowed
- **Parameter Validation**: Strict input sanitization
- **Execution Sandboxing**: Limit command scope and permissions
- **Audit Logging**: Optional local command history
- **Emergency Stop**: Panic button to halt all command processing

## 9. Development Roadmap

### 9.1 Phase 1: Foundation (Weeks 1-2)
- MLX LLM integration and model loading
- Basic wake word detection
- Command/dictation mode switching
- Simple application launch commands

### 9.2 Phase 2: Core Commands (Weeks 3-4)
- Web search and browser control
- Basic terminal command execution
- File management operations
- System control (volume, screenshots)

### 9.3 Phase 3: Advanced Features (Weeks 5-6)
- Context-aware commands
- Command history and learning
- Advanced safety validation
- Performance optimization

### 9.4 Phase 4: Polish & Testing (Weeks 7-8)
- Comprehensive testing across command types
- UI/UX refinement
- Documentation and user guides
- Beta testing with power users

## 10. Success Metrics v2.0

### 10.1 Adoption Metrics
- **Command Mode Usage**: 60% of users try command mode within first week
- **Command Frequency**: Average 5+ voice commands per active user per day
- **Feature Retention**: 70% of users continue using commands after 30 days

### 10.2 Performance Metrics
- **Command Accuracy**: >90% successful command interpretation
- **Execution Success**: >95% of validated commands execute successfully
- **User Satisfaction**: >4.5/5 rating for command mode functionality

### 10.3 Technical Metrics
- **Response Time**: <3s average for command processing
- **Memory Efficiency**: <6GB peak memory usage
- **Reliability**: <0.1% crash rate during command processing

## 11. Risk Assessment & Mitigation

### 11.1 Technical Risks

**Dual Model Memory Usage**
- *Risk*: Running Whisper + LLM simultaneously may exceed memory limits
- *Mitigation*: Smart model loading, memory optimization, model size options

**Command Execution Safety**
- *Risk*: Voice commands could trigger unintended or harmful actions
- *Mitigation*: Comprehensive validation, confirmation prompts, command whitelisting

**Performance Impact**
- *Risk*: LLM processing may slow down dictation performance
- *Mitigation*: Async processing, model optimization, performance monitoring

### 11.2 User Experience Risks

**Complexity Creep**
- *Risk*: Adding commands may make the app too complex
- *Mitigation*: Progressive disclosure, simple defaults, optional advanced features

**False Wake Word Activation**
- *Risk*: Accidental command mode activation during dictation
- *Mitigation*: High confidence thresholds, context awareness, easy cancellation

**Learning Curve**
- *Risk*: Users may not discover or adopt command features
- *Mitigation*: Interactive onboarding, command suggestions, usage examples

## 12. Future Vision (v3.0+)

### 12.1 Advanced AI Features
- **Contextual Memory**: Remember previous commands and user preferences
- **Workflow Learning**: Automatically suggest command sequences
- **Custom Commands**: User-defined voice shortcuts for complex workflows
- **Multi-Modal**: Combine voice with screen understanding

### 12.2 Integration Opportunities
- **IDE Integration**: Deep integration with VS Code, Xcode
- **Workflow Automation**: Integration with Shortcuts, Automator
- **Third-Party APIs**: Control Slack, Notion, other productivity apps
- **Developer SDK**: Allow other apps to register voice commands

---

This PRD v2.0 transforms MagikMike from a dictation tool into an intelligent voice assistant while maintaining its core privacy and performance advantages. The phased approach ensures we can deliver value incrementally while building toward a comprehensive voice-controlled computing experience.
