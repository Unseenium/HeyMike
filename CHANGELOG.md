# Changelog

All notable changes to Hey Mike! will be documented in this file.

## [2.0.0] - 2025-09-26 🎉

### 🚀 Major Features Added
- **🧠 Voice Commands**: Natural language command interpretation with "Hey Mike!" wake word
- **🎤 Dual-Mode Operation**: Seamless switching between dictation and voice commands
- **⚡ Local LLM Integration**: MLX-optimized language models for command understanding
- **🔒 Comprehensive Safety Framework**: 3-tier validation system for secure execution
- **🎯 Wake Word Detection**: Advanced pattern matching with confidence scoring

### 🏗️ New Components
- **MLXLLMManager**: Local language model integration for command interpretation
- **WakeWordDetector**: "Hey Mike!" activation system with multiple pattern support
- **CommandProcessor**: Intent classification and parameter extraction
- **ActionExecutor**: Coordinated command execution across action modules
- **CommandValidator**: Comprehensive safety validation and security checks

### 📱 Action Modules
- **AppActions**: Application control (launch, quit, switch apps)
- **WebActions**: Web search and browser control
- **SystemActions**: System control (volume, screenshots, power management)
- **TerminalActions**: Safe terminal command execution
- **FileActions**: File and folder management operations

### 🎨 UI Enhancements
- **Enhanced Menu Bar**: Dual-mode indicators and LLM model selection
- **Command Mode Toggle**: Easy switching between dictation and command modes
- **LLM Model Menu**: Selection between different language models
- **Visual Feedback**: Clear indicators for current mode and processing state

### ⚙️ Configuration
- **Extended Settings**: 10+ new configuration options for v2.0 features
- **Permission Management**: Granular control over command categories
- **Safety Configuration**: Customizable validation and confirmation settings
- **Model Selection**: Choose between different LLM models for speed vs capability

### 🔒 Security Features
- **Command Whitelisting**: Only approved command patterns allowed
- **3-Tier Safety Levels**: Safe, Caution, and Restricted command categories
- **Parameter Validation**: Strict input sanitization and type checking
- **Path Protection**: System directories and critical files protected
- **User Confirmation**: High-risk operations require explicit approval

### 🎯 Voice Command Examples
- "Hey Mike, open Chrome" - Launch applications
- "Hey Mike, search for Python tutorials" - Web searches
- "Hey Mike, take a screenshot" - System control
- "Hey Mike, create a new file called notes.txt" - File operations
- "Hey Mike, list files in current directory" - Terminal commands

### 📊 Technical Improvements
- **MLX Optimization**: Leverages Apple Silicon for both Whisper and LLM processing
- **Async Processing**: Non-blocking command interpretation and execution
- **Memory Efficiency**: Smart model loading and resource management
- **Error Handling**: Comprehensive error recovery and user feedback
- **Extensible Architecture**: Easy addition of new command types and actions

### 🧪 Testing & Quality
- **Integration Test Suite**: Comprehensive testing framework with 90.9% success rate
- **End-to-End Testing**: Complete workflow validation from voice to execution
- **Safety Testing**: Validation of security measures and dangerous command blocking
- **Performance Testing**: Response time and resource usage optimization

### 📋 Dependencies Added
- **mlx-lm**: MLX language model support
- **transformers**: Hugging Face model integration
- **tokenizers**: Text tokenization for LLM processing

### 🎉 Achievements
- ✅ All PRD v2.0 requirements implemented
- ✅ 90.9% integration test success rate
- ✅ Complete backward compatibility with v1.0
- ✅ Privacy-first architecture maintained
- ✅ Production-ready codebase with comprehensive documentation

## [1.0.0] - 2025-09-26

### Added
- 🎤 MLX Whisper-based speech recognition system
- 📱 Native macOS menu bar interface with rumps
- 🧠 Support for 5 Whisper model sizes (tiny, base, small, medium, large)
- ⚡ Pre-downloading of all models for instant switching
- 🎙️ Real-time audio recording and transcription
- ⌨️ Customizable global hotkeys (default: Cmd+Shift+Space)
- 🎯 Intelligent text insertion at cursor position
- 🌍 Multi-language support (99+ languages)
- ⚙️ Comprehensive settings system
- 🔐 Privacy-focused offline processing
- 📊 Visual feedback and status indicators
- 🧪 Comprehensive test suite (68 tests)

### Technical Features
- MLX-optimized Whisper models for Apple Silicon
- PyAudio integration for microphone access
- macOS Accessibility API for text insertion
- Global hotkey detection with pynput
- Settings persistence with JSON storage
- Error handling and graceful degradation
- Memory-efficient model management

### UI/UX Features
- 🎨 Modern emoji-based menu interface
- 📈 Real-time visual feedback
- 🔔 System notifications for all actions
- 📋 Detailed system status and diagnostics
- 🛠️ Easy permission management
- 🚀 One-click model downloading

### Performance
- ⚡ Startup time: < 3 seconds
- 🔄 Model switching: < 2 seconds  
- 🎙️ Recording latency: < 100ms
- 💾 Memory usage: < 500MB with all models
- 🔋 Optimized for Apple Silicon efficiency

### Security & Privacy
- 🔒 100% offline processing
- 🚫 No data sent to external servers
- 🏠 Local model storage only
- 🔐 Secure permission handling
- 🛡️ No telemetry or tracking
