# Product Requirements Document (PRD)

## Hey Mike!: MLX Whisper Dictation System for macOS

### Version 1.0
### Date: August 2025

---

## 1. Executive Summary

Hey Mike! is a macOS application that provides offline, multilingual speech-to-text capabilities using OpenAI's Whisper ASR models optimized for Apple Silicon via the MLX framework. Like "Hey Siri" but actually useful, the application runs in the background, triggered by customizable keyboard shortcuts, and automatically types transcribed text into any active text field.

## 2. Product Overview

### 2.1 Purpose
Provide a privacy-focused, offline dictation system that can replace or supplement macOS's built-in dictation functionality with superior accuracy and multilingual support.

### 2.2 Key Features
- **Offline Operation**: All processing happens locally using MLX-optimized Whisper models
- **Multilingual Support**: Supports 99+ languages with configurable language hints
- **Background Operation**: Runs as a menu bar application
- **Keyboard Shortcuts**: Customizable hotkey combinations
- **Auto-typing**: Automatically types transcribed text into active applications
- **Multiple Model Options**: MLX Whisper model variants for different speed/accuracy trade-offs
- Menu bar UI (rumps), global hotkey , audio feedback, and minimal configuration.

## 3. Target Users

### 3.1 Primary Users
- **Writers and Content Creators:** Bloggers, journalists, authors who need quick speech-to-text
- **Professionals:** Business users who want to quickly capture thoughts during meetings or calls
- **Students:** Note-taking during lectures or study sessions
- **Accessibility Users:** Users with typing difficulties or repetitive strain injuries

### 3.2 User Personas
- **Sarah the Blogger:** Needs to quickly capture article ideas while away from keyboard
- **Mike the Manager:** Wants to dictate quick notes during back-to-back meetings
- **Alex the Student:** Takes lecture notes and wants to supplement typing with speech

## 4. Core Features

### 4.1 MLX Whisper Integration (MVP)
- **MLX Framework:** Uses MLX-optimized Whisper models for Apple Silicon
- **Offline Processing:** All transcription happens locally without internet connection
- **Model Variants:** Support for different Whisper model sizes (tiny, base, small, medium, large)
- **Multilingual:** 99+ language support with automatic language detection
- **High Accuracy:** Superior accuracy compared to built-in macOS dictation

### 4.2 Global Hotkeys (MVP)
- **Start Recording:** Configurable hotkey (default: ⌘ + Shift + Space)
- **Stop Recording:** Same hotkey toggles recording off, or automatic stop after silence
- **Cancel Recording:** Escape key or configurable hotkey to discard current recording
- **System-wide:** Works regardless of which application is currently focused

### 4.3 Text Insertion (MVP)
- **Cursor Detection:** Automatically detects current text cursor position
- **Universal Compatibility:** Works with any text input field (TextEdit, browsers, Slack, etc.)
- **Smart Insertion:** Respects existing text formatting and cursor position
- **Undo Support:** Inserted text can be undone with standard ⌘+Z

### 4.4 User Interface (MVP)
- **Menu Bar Icon:** Discrete menu bar presence with status indicator (using rumps)
- **Status Feedback:** Visual indication of recording state (idle/recording/processing)
- **Settings Panel:** Configuration for hotkeys, language, model selection, and behavior
- **Audio Feedback:** Optional sound cues for recording start/stop
- **Minimal Configuration:** Simple setup with sensible defaults

## 5. Technical Requirements

### 5.1 Platform Requirements
- **macOS Version:** macOS 12.0 (Monterey) or later (for MLX compatibility)
- **Architecture:** Apple Silicon (M1/M2/M3) required for MLX optimization
- **Permissions:** Microphone access, Accessibility permissions for text insertion
- **Framework:** Python with MLX framework, Swift for system integration

### 5.2 Core Technologies
- **Speech Recognition:** MLX-optimized Whisper models (`mlx-whisper`)
- **Audio Capture:** PyAudio or similar for microphone input
- **Global Events:** Python libraries for system-wide hotkey detection
- **Text Insertion:** Accessibility APIs for cursor detection and text insertion
- **UI Framework:** rumps for menu bar interface, minimal configuration UI

### 5.3 Performance Requirements
- **Startup Time:** < 5 seconds from launch to ready state (including model loading)
- **Recognition Latency:** Variable based on model size (tiny: <1s, large: <5s)
- **Memory Usage:** 200MB-2GB depending on selected Whisper model
- **Battery Impact:** Optimized for Apple Silicon efficiency during processing

## 6. User Experience Flow

### 6.1 First Launch Flow
1. User launches MagikMike (MLX Whisper Dictation)
2. App downloads and loads selected Whisper model
3. App requests microphone permission
4. App requests accessibility permission for text insertion
5. Quick onboarding showing hotkey usage
6. App minimizes to menu bar, ready for use

### 6.2 Primary Usage Flow
1. User positions cursor in any text field
2. User presses hotkey (⌘ + Shift + Space)
3. Menu bar icon shows recording indicator with audio feedback
4. User speaks (configurable duration, default 30 seconds)
5. User presses hotkey again or stops speaking
6. MLX processes audio through Whisper model
7. Text appears at cursor position with high accuracy
8. User can continue typing or use undo if needed

### 6.3 Configuration Flow
1. User clicks menu bar icon
2. Settings panel opens
3. User can modify:
   - Hotkey combinations
   - Whisper model selection (speed vs accuracy)
   - Recognition language hints
   - Auto-stop timeout
   - Audio input device
   - Audio feedback settings

## 7. Security & Privacy

### 7.1 Privacy Principles
- **Local Processing Only:** All MLX Whisper processing happens locally, no cloud services
- **No Data Storage:** Audio is processed in memory and immediately discarded
- **No Analytics:** No usage tracking or telemetry
- **Model Privacy:** Whisper models run entirely offline
- **Minimal Permissions:** Only requests necessary system permissions

### 7.2 Security Measures
- **Open Source Models:** Uses publicly auditable Whisper models
- **Local Execution:** All processing contained within user's device
- **Permission Transparency:** Clear explanation of why permissions are needed
- **No Network Access:** Application can function completely offline

## 8. Success Metrics

### 8.1 User Engagement
- **Daily Active Users:** Target 70% of installed users using app daily
- **Session Frequency:** Average 10+ transcriptions per active user per day
- **Retention:** 80% 7-day retention, 60% 30-day retention

### 8.2 Technical Performance
- **Recognition Accuracy:** >98% accuracy leveraging Whisper's superior multilingual capabilities
- **Response Time:** Variable by model (tiny: <1s, large: <5s) but higher accuracy than native
- **Crash Rate:** <0.1% crash rate across all sessions
- **Model Efficiency:** Optimal MLX performance on Apple Silicon

## 9. Future Enhancements (Post-MVP)

### 9.1 Version 1.1 Features
- **Custom Model Training:** Fine-tuning Whisper models with user-specific vocabulary
- **Real-time Streaming:** Live transcription as user speaks
- **Language Auto-detection:** Automatic language switching within conversations
- **Advanced Audio Processing:** Noise reduction and audio enhancement

### 9.2 Version 1.2 Features
- **Multi-speaker Support:** Speaker diarization for meeting transcription
- **Voice Commands:** Beyond transcription - system commands via voice
- **Integration APIs:** Hooks for other applications to use MagikMike's transcription
- **Cloud Model Sync:** Optional cloud storage for custom model weights

## 10. Technical Architecture

### 10.1 App Structure
```
MagikMike/
├── Core/
│   ├── MLXWhisperManager.py      # MLX Whisper model integration
│   ├── HotkeyManager.py          # Global hotkey handling
│   ├── TextInsertionManager.py   # Accessibility-based text insertion
│   └── AudioManager.py           # Audio capture and processing
├── UI/
│   ├── MenuBarController.py      # rumps-based menu bar interface
│   ├── SettingsView.py          # Configuration interface
│   └── StatusIndicator.py        # Visual feedback system
├── Models/
│   ├── WhisperModels/           # Downloaded Whisper model files
│   ├── RecognitionResult.py     # Transcription result handling
│   └── AppSettings.py           # User configuration management
└── Resources/
    ├── requirements.txt         # Python dependencies
    └── Assets/                  # Icons and resources
```

### 10.2 Key Components
- **MLXWhisperManager:** Handles MLX Whisper model loading and inference
- **HotkeyManager:** Global hotkey registration and handling using Python libraries
- **TextInsertionManager:** Accessibility-based text insertion via macOS APIs
- **MenuBarController:** rumps-based menu bar UI and status management

## 11. Development Timeline

### Phase 1: Core MVP (Weeks 1-3)
- Set up Python project structure with MLX dependencies
- Implement MLX Whisper model integration and loading
- Basic audio capture and processing pipeline
- Simple text insertion at cursor position using accessibility APIs

### Phase 2: Integration & UI (Weeks 4-5)
- rumps-based menu bar UI and status indicators
- Global hotkey detection and handling
- Settings interface for model selection and configuration
- Permission handling and user onboarding flow

### Phase 3: Polish & Distribution (Weeks 6-7)
- Performance optimization for different Whisper model sizes
- Comprehensive testing across Apple Silicon devices
- Package as standalone macOS application
- Documentation and user guides

## 12. Risks & Mitigation

### 12.1 Technical Risks
- **MLX Compatibility:** MLX framework requires Apple Silicon, limiting device support
  - *Mitigation:* Clear system requirements, fallback to CPU inference if needed
- **Model Size:** Large Whisper models may consume significant memory/storage
  - *Mitigation:* Multiple model size options, user choice of speed vs accuracy
- **Python Distribution:** Packaging Python app for macOS distribution
  - *Mitigation:* Use PyInstaller or similar for standalone executable

### 12.2 User Experience Risks
- **Processing Latency:** Larger models may have noticeable processing delays
  - *Mitigation:* Clear user expectations, model selection guidance
- **Hotkey Conflicts:** May conflict with other applications
  - *Mitigation:* Customizable hotkeys, conflict detection
- **Learning Curve:** Users may not understand model trade-offs
  - *Mitigation:* Simple onboarding with recommended settings

This PRD serves as the foundation for building MagikMike, ensuring we create a focused, user-friendly, and technically robust MLX Whisper-based speech-to-text solution for macOS users with Apple Silicon devices.
