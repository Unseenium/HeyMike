# MagikMike API Documentation

## 🎤 MLXWhisperManager

### Core Methods

#### `load_model(model_name: str) -> bool`
Load a specific Whisper model.

**Parameters:**
- `model_name`: One of 'tiny', 'base', 'small', 'medium', 'large'

**Returns:**
- `bool`: True if model loaded successfully

**Example:**
```python
whisper_manager = MLXWhisperManager()
success = whisper_manager.load_model('base')
```

#### `transcribe_audio(audio_data: np.ndarray, language: Optional[str] = None) -> Optional[str]`
Transcribe audio data to text.

**Parameters:**
- `audio_data`: NumPy array of audio samples (16kHz, mono)
- `language`: Optional language code ('en', 'es', etc.)

**Returns:**
- `str`: Transcribed text or None if failed

#### `predownload_all_models() -> None`
Download all Whisper models in background.

**Callbacks:**
- `on_predownload_start()`: Called when download begins
- `on_predownload_progress(model_name, current, total)`: Progress updates
- `on_predownload_complete()`: Called when all models downloaded

## 🎙️ AudioManager

### Core Methods

#### `start_recording() -> bool`
Start audio recording from microphone.

**Returns:**
- `bool`: True if recording started successfully

#### `stop_recording() -> Optional[np.ndarray]`
Stop recording and return audio data.

**Returns:**
- `np.ndarray`: Audio samples or None if failed

#### `get_input_devices() -> List[dict]`
Get list of available audio input devices.

**Returns:**
- `List[dict]`: List of device info dictionaries

**Example:**
```python
devices = audio_manager.get_input_devices()
# [{'index': 0, 'name': 'Built-in Microphone'}, ...]
```

## ⌨️ HotkeyManager

### Core Methods

#### `set_record_hotkey(hotkey: Set) -> bool`
Set the global hotkey for recording.

**Parameters:**
- `hotkey`: Set of keys (e.g., {Key.cmd, Key.shift, KeyCode.from_char(' ')})

**Returns:**
- `bool`: True if hotkey set successfully

#### `start_listening() -> None`
Start listening for global hotkeys.

#### `parse_hotkey_string(hotkey_string: str) -> Optional[Set]`
Parse hotkey string into key set.

**Parameters:**
- `hotkey_string`: String like "cmd+shift+space"

**Returns:**
- `Set`: Set of keys or None if invalid

## 📝 TextInsertionManager

### Core Methods

#### `insert_text(text: str, method: str = 'auto') -> bool`
Insert text at current cursor position.

**Parameters:**
- `text`: Text to insert
- `method`: 'auto', 'paste', or 'type'

**Returns:**
- `bool`: True if text inserted successfully

#### `check_text_field_available() -> bool`
Check if a text field is currently focused.

**Returns:**
- `bool`: True if text field available

## ⚙️ AppSettings

### Core Methods

#### `get(key: str, default=None) -> Any`
Get a setting value.

**Parameters:**
- `key`: Setting key name
- `default`: Default value if key not found

#### `set(key: str, value: Any) -> None`
Set a setting value.

**Parameters:**
- `key`: Setting key name
- `value`: Value to set

#### `save_settings() -> None`
Save settings to disk.

#### `load_settings() -> None`
Load settings from disk.

## 📱 MenuBarController

### Callback System

The MenuBarController uses a callback-based architecture for communication:

```python
# Audio callbacks
audio_manager.on_recording_start = self._on_recording_started
audio_manager.on_recording_stop = self._on_recording_stopped

# Whisper callbacks
whisper_manager.on_model_loaded = self._on_model_loaded
whisper_manager.on_transcription_complete = self._on_transcription_complete

# Error callbacks
manager.on_error = self._on_error
```

### Menu Actions

All menu actions are implemented as callback methods:
- `_menu_toggle_recording()`: Start/stop recording
- `_select_model(model_name)`: Switch Whisper models
- `_show_*_settings()`: Open settings dialogs
- `_test_text_insertion()`: Run insertion test

## 🔔 Event System

### Audio Events
- `on_recording_start()`: Recording started
- `on_recording_stop(audio_data)`: Recording stopped with data
- `on_audio_level(level)`: Real-time audio level

### Model Events
- `on_model_loading(model_name)`: Model loading started
- `on_model_loaded(model_name)`: Model ready for use
- `on_transcription_start()`: Transcription processing started
- `on_transcription_complete(text)`: Text result available

### Error Events
- `on_error(message)`: Error occurred in any component

## 🔧 Configuration Keys

### Available Settings
```python
SETTINGS_SCHEMA = {
    'model': str,                    # Active Whisper model
    'language': Optional[str],       # Language code or None for auto
    'hotkey': str,                   # Hotkey combination string
    'audio_device': Optional[int],   # Audio device index
    'max_recording_duration': float, # Max recording time (seconds)
    'silence_duration': float,       # Silence timeout (seconds)
    'silence_threshold': int,        # Silence detection threshold
    'insertion_method': str,         # 'auto', 'paste', or 'type'
    'add_space_after': bool,         # Add space after inserted text
    'add_space_before': bool,        # Add space before inserted text
    'audio_feedback': bool,          # Enable audio feedback
    'notifications': bool,           # Enable system notifications
    'first_run': bool               # Track first run state
}
```

## 🚀 Usage Examples

### Basic Recording and Transcription
```python
# Initialize managers
audio_manager = AudioManager()
whisper_manager = MLXWhisperManager()

# Load model
whisper_manager.load_model('base')

# Record audio
audio_manager.start_recording()
# ... user speaks ...
audio_data = audio_manager.stop_recording()

# Transcribe
text = whisper_manager.transcribe_audio(audio_data)
print(f"Transcribed: {text}")
```

### Custom Hotkey Setup
```python
hotkey_manager = HotkeyManager()

# Parse hotkey string
hotkey = HotkeyManager.parse_hotkey_string("ctrl+alt+r")

# Set hotkey
hotkey_manager.set_record_hotkey(hotkey)
hotkey_manager.on_record_toggle = lambda: print("Hotkey pressed!")

# Start listening
hotkey_manager.start_listening()
```

### Settings Management
```python
settings = AppSettings()

# Configure app
settings.set('model', 'large')
settings.set('language', 'en')
settings.set('notifications', True)

# Save to disk
settings.save_settings()

# Load on startup
settings.load_settings()
model = settings.get('model', 'base')
```
