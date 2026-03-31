# Doubao Real-time Simultaneous Interpreter

English | [简体中文](README_CN.md)

A real-time speech-to-speech translation application based on Doubao AST 2.0 API (WebSocket), supporting both speech-to-speech (s2s) and speech-to-text (s2t) translation.

## Features

- **All-in-One Solution**: STT + Translation + TTS in a single API call via Doubao AST 2.0
- **Ultra-Low Latency**: WebSocket streaming with only 1-2 seconds delay
- **Virtual Microphone**: Output to VB-Cable, works with any meeting software
- **Multi-Language Support**: Supports Chinese, English, Japanese, Korean, and more
- **User-Friendly GUI**: Clean and intuitive PyQt6 interface
- **Voice Cloning**: Zero-shot voice replication that preserves speaker's voice characteristics

## Use Cases

- Real-time translation for international meetings (Zoom, Teams, Google Meet, Tencent Meeting, etc.)
- Cross-language online education
- Real-time business communication
- Live event interpretation

## System Requirements

### Software
- OS: Windows 10/11
- Python: 3.12.7
- Conda environment: rttdb (recommended)

### Hardware
- Minimum: 4-core CPU, 8GB RAM
- Recommended: 8-core CPU, 16GB RAM
- Network: Stable internet connection

### Required Software
- **VB-Audio Virtual Cable**: Virtual audio driver
  - Download: https://vb-audio.com/Cable/

## Quick Start

### 1. Environment Setup

```bash
conda create -n rttdb python=3.12.7
conda activate rttdb
pip install -r requirements.txt
```

### 2. Install Virtual Audio Driver

1. Download VB-Audio Virtual Cable: https://vb-audio.com/Cable/
2. Run the installer as Administrator
3. Restart your computer
4. You should see "CABLE Input" and "CABLE Output" in Sound Settings

### 3. Configure API Keys

#### Option 1: Via GUI (Recommended)

1. Run the application: `python main.py`
2. Click the **"Settings"** button
3. Enter your API keys (App Key, Access Key)
4. Click **"Save"**

#### Option 2: Manual Configuration

Create a `.env` file:
```
DOUBAO_APP_KEY=your_app_key_here
DOUBAO_ACCESS_KEY=your_access_key_here
DOUBAO_RESOURCE_ID=volc.service_type.10053
```

#### Getting API Keys

**For Users in China:**
1. Visit [Volcengine Console](https://console.volcengine.com/)
2. Enable the **"Simultaneous Interpretation"** service
3. Create an application and get your App Key and Access Key

**For International Users:**
1. Visit [Volcengine International Console](https://console.volcengine.com/) or [ByteDance Cloud](https://www.bytedance.com/en/product)
2. Sign up with your email
3. Enable the **"Simultaneous Interpretation"** (AST) service
4. Create an application and obtain your App Key and Access Key

> **Note**: If the service is not available in your region, you may need to use a VPN or contact Volcengine support for access options.

### 4. Launch the Application

```bash
conda activate rttdb
python main.py
```

## Usage Guide

### UI Language

The application supports English and Chinese interface. Click the **🌐 English/中文** button in the main window to switch languages. Your preference is saved automatically.

### GUI Workflow

1. **Select Languages**: Source language (your spoken language) and target language (translation output)
2. **Select Mode**:
   - **s2s (Speech-to-Speech)**: Outputs audio, ready for meetings (recommended)
   - **s2t (Speech-to-Text)**: Text output only
3. **Click "Start Translation"**: Speak into your microphone
4. **View Results**: Original text on the left, translated text on the right
5. **Use in Meetings**: Select **"CABLE Output"** as microphone in your meeting software

### Zero-Shot Voice Cloning

S2S mode automatically enables zero-shot voice cloning:

- **Zero Configuration**: No pre-training required
- **Zero Wait**: No Speaker ID needed
- **Zero-Shot**: Learns voice characteristics in real-time
- **Real-Time Cloning**: Automatically applied to translation output

How it works:
```
You speak Chinese → System learns your voice → Translates → Speaks English in your voice
```

### Verify Voice Cloning

1. Click the **"Verify Clone"** button on the main interface
2. Click **"Start Test"**
3. Read the test text (about 10 seconds)
4. Click **"Play Cloned Audio"** to hear the result
5. Optionally **"Save Sample"** to save the audio

## Online Meeting Configuration

### Key Configuration Principles

1. **Windows Input Device**: Keep your real microphone (don't select CABLE Output)
2. **This Application**: Automatically captures real microphone, outputs to CABLE Input
3. **Meeting Software**: Select CABLE Output as microphone

### Audio Flow

```
[Real Microphone] → [App Captures & Translates] → [CABLE Input] → [VB-Cable] → [CABLE Output] → [Meeting Software]
```

### Platform Configuration

**Zoom**: Settings → Audio → Microphone: **CABLE Output**

**Microsoft Teams**: Settings → Devices → Microphone: **CABLE Output**

**Google Meet**: Settings → Audio → Microphone: **CABLE Output**

**Tencent Meeting**: Settings → Audio → Microphone: **CABLE Output**

## Project Structure

```
RealtimeASTTranslator/
├── main.py                 # GUI main entry point
├── translator_app.py       # Translation application core
├── config.py              # Configuration file
├── requirements.txt       # Python dependencies
│
├── modules/              # Core modules
│   ├── ast_client_protobuf.py  # WebSocket client (Protobuf)
│   ├── audio_capture.py        # Audio capture
│   └── virtual_audio.py        # Virtual audio output
│
├── gui/                  # GUI interface
│   ├── main_window.py          # Main window
│   ├── settings_dialog.py      # Settings dialog
│   └── voice_clone_test_dialog.py  # Voice clone verification
│
├── utils/                # Utility modules
│   └── logger.py               # Logging utility
│
├── python_protogen/      # Protobuf protocol definitions
│
├── logs/                 # Log directory
│
├── README.md             # This document
├── QUICK_START.md        # Quick start guide
├── PROJECT_SUMMARY.md    # Project summary
└── TROUBLESHOOTING.md    # Troubleshooting guide
```

## Technical Architecture

### Tech Stack

- **WebSocket**: websockets library for real-time bidirectional communication
- **Audio Processing**: sounddevice, numpy
- **GUI**: PyQt6
- **Protocol**: Protobuf
- **Configuration**: python-dotenv

### Data Flow

```
[Microphone 16kHz PCM]
    ↓
[AudioCapture]
    ↓
[ASTClient (WebSocket + Protobuf)]
    ↓
[Doubao AST 2.0 API Server]
    ├→ STT Recognition → Original subtitles
    ├→ Real-time Translation → Translated subtitles
    └→ TTS Synthesis → Audio stream (24kHz PCM)
          ↓
[VirtualAudioOutput]
    ↓
[VB-Cable Input]
    ↓
[Meeting Software selects CABLE Output]
```

### Key Features

1. **Async Processing**: asyncio event loop for WebSocket communication
2. **Streaming**: 80ms audio chunks for real-time transmission, minimizing latency
3. **Protobuf Protocol**: Efficient binary serialization
4. **Zero-Shot Voice Cloning**: Real-time voice learning and application

## FAQ

### Q1: "Virtual audio device not found" error

Install VB-Audio Virtual Cable and restart your computer.

### Q2: Meeting software cannot hear translated audio

1. Make sure you selected **"CABLE Output"** not "CABLE Input"
2. Test CABLE Output device in system sound settings
3. Verify the application is running in s2s mode

### Q3: Connection failed / Authentication error

1. Check if API keys in .env file are correct
2. Confirm you have enabled the service in Volcengine Console
3. Check your network connection

### Q4: What should Windows default input device be?

**Keep your real microphone**, don't select CABLE Output. See TROUBLESHOOTING.md for details.

### Q5: High latency

1. Check network conditions
2. Confirm you're using Doubao AST 2.0 API (only 1-2 seconds delay)

### Q6: Audio is choppy

1. Check CPU usage
2. Close other programs using audio devices

## Performance

| Metric | Value |
|--------|-------|
| End-to-end Latency | 1-2 seconds |
| Audio Capture Latency | 80ms |
| Network Transmission Latency | 500-800ms |
| TTS Synthesis Latency | 300-500ms |
| Memory Usage | ~200MB |
| CPU Usage | 5-10% (4 cores) |

## Supported Languages

- zh - Chinese
- en - English
- ja - Japanese
- ko - Korean
- es - Spanish
- fr - French
- de - German
- ru - Russian
- ar - Arabic

## Debug & Logs

Log file location: `logs/translator.log`

View real-time logs:
```bash
Get-Content logs/translator.log -Wait  # Windows PowerShell
```

Modify configuration: Edit `config.py`

## Version History

### v1.0.0 (2025-11-18)
- Doubao AST 2.0 API WebSocket integration
- Protobuf protocol support
- Virtual microphone output
- PyQt6 GUI interface
- Multi-language support
- Zero-shot voice cloning
- s2s and s2t modes

## License

This project is for learning and personal use only.

## Related Links

- [Doubao API Documentation](https://console.volcengine.com/)
- [Volcengine Console](https://console.volcengine.com/)
- [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
