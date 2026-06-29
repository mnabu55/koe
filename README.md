# Koe 🎤

On-device voice dictation app for macOS (Apple Silicon)

Hold the hotkey to record, release to transcribe — text is instantly inserted into any active app. Everything runs locally on your machine.

**[日本語版 README はこちら](README.ja.md)**

## Demo

![demo](docs/demo.gif)

## Features

- **Fully on-device** — your voice never leaves your machine
- **Apple Silicon optimized** — mlx-whisper leverages ANE/GPU for fast inference
- **Japanese support** — high-accuracy transcription with Whisper large-v3-turbo
- **AI text cleanup** — Ollama (qwen2.5:7b) removes filler words and adds punctuation
- **Push-to-Talk** — records only while the hotkey is held
- **Works in any app** — inserts text via clipboard into any text field

## Requirements

- macOS 13 or later
- Apple Silicon (M1 / M2 / M3 / M4)
- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) package manager
- [Ollama](https://ollama.com/) (optional, for AI text cleanup)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/mnabu55/koe.git
cd koe
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Download the Whisper model

```bash
mkdir -p ~/models/whisper-large-v3-turbo

curl -L "https://huggingface.co/mlx-community/whisper-large-v3-turbo/resolve/main/weights.safetensors" \
  -o ~/models/whisper-large-v3-turbo/weights.safetensors --progress-bar

curl -L "https://huggingface.co/mlx-community/whisper-large-v3-turbo/resolve/main/config.json" \
  -o ~/models/whisper-large-v3-turbo/config.json
```

### 4. Set up Ollama (optional)

```bash
# Install Ollama: https://ollama.com/
ollama pull qwen2.5:7b
```

### 5. Create configuration file

```bash
cp .env.example .env
```

Edit `.env`:

```env
WHISPER_MODEL=/Users/YOUR_USERNAME/models/whisper-large-v3-turbo
WHISPER_LANGUAGE=ja
OLLAMA_MODEL=qwen2.5:7b
LLM_CLEANUP_ENABLED=true
HOTKEY=ctrl+shift+space
```

### 6. Grant Accessibility permission

Go to **System Settings → Privacy & Security → Accessibility** and add your terminal app.

## Usage

```bash
uv run koe
```

A 🎤 icon will appear in the menu bar when the app is ready.

1. Place your cursor in any text field
2. **Hold the hotkey** and speak (`ctrl+shift+space` by default)
3. **Release the hotkey** → transcribed text is inserted automatically

### Icon states

| Icon | State      |
| ---- | ---------- |
| 🎤   | Idle       |
| 🔴   | Recording  |
| ⏳   | Processing |

## Configuration

Customize behavior via the `.env` file:

| Key                   | Default                                | Description                     |
| --------------------- | -------------------------------------- | ------------------------------- |
| `WHISPER_MODEL`       | `mlx-community/whisper-large-v3-turbo` | Model path or HuggingFace repo  |
| `WHISPER_LANGUAGE`    | `ja`                                   | Recognition language            |
| `OLLAMA_MODEL`        | `qwen2.5:7b`                           | LLM for text cleanup            |
| `LLM_CLEANUP_ENABLED` | `true`                                 | Enable/disable AI text cleanup  |
| `HOTKEY`              | `ctrl+shift+space`                     | Recording hotkey                |

## Architecture

```
Hotkey pressed
    ↓
AudioCapture (sounddevice, 16kHz)
    ↓
Silero VAD (skip silence)
    ↓
mlx-whisper (audio → text)
    ↓
Ollama LLM (text cleanup) — optional
    ↓
TextInserter (clipboard → Cmd+V)
    ↓
Active app text field
```

## License

MIT