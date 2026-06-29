# Koe 🎤

オンデバイス音声入力アプリ for macOS（Apple Silicon）

ホットキーを押している間マイクで録音し、離した瞬間に音声をテキストに変換してアクティブなアプリへ自動入力します。すべての処理はローカルで完結します。

**[English README](README.md)**

## デモ

![demo](docs/demo.gif)

## 特徴

- **完全オンデバイス** — 音声データは外部に送信されません
- **Apple Silicon 最適化** — mlx-whisper が ANE/GPU を活用した高速推論
- **日本語対応** — Whisper large-v3-turbo による高精度な日本語認識
- **AI 文章整形** — Ollama (qwen2.5:7b) によるフィラー語除去・句読点補完
- **Push-to-Talk** — ホットキーを押している間だけ録音
- **どのアプリにも挿入** — クリップボード経由で任意のテキストフィールドに入力

## 動作環境

- macOS 13 以上
- Apple Silicon (M1 / M2 / M3 / M4)
- Python 3.11 以上
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー
- [Ollama](https://ollama.com/)（LLM による文章整形を使う場合）

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/mnabu55/koe.git
cd koe
```

### 2. 依存パッケージをインストール

```bash
uv sync
```

### 3. Whisper モデルをダウンロード

```bash
mkdir -p ~/models/whisper-large-v3-turbo

curl -L "https://huggingface.co/mlx-community/whisper-large-v3-turbo/resolve/main/weights.safetensors" \
  -o ~/models/whisper-large-v3-turbo/weights.safetensors --progress-bar

curl -L "https://huggingface.co/mlx-community/whisper-large-v3-turbo/resolve/main/config.json" \
  -o ~/models/whisper-large-v3-turbo/config.json
```

### 4. Ollama をセットアップ（オプション）

```bash
# Ollama インストール: https://ollama.com/
ollama pull qwen2.5:7b
```

### 5. 設定ファイルを作成

```bash
cp .env.example .env
```

`.env` を編集:

```env
WHISPER_MODEL=/Users/YOUR_USERNAME/models/whisper-large-v3-turbo
WHISPER_LANGUAGE=ja
OLLAMA_MODEL=qwen2.5:7b
LLM_CLEANUP_ENABLED=true
HOTKEY=ctrl+shift+space
```

### 6. アクセシビリティ権限を付与

**システム設定 → プライバシーとセキュリティ → アクセシビリティ** で、使用するターミナルアプリを追加してオンにします。

## 起動

```bash
uv run koe
```

メニューバーに 🎤 が表示されれば起動完了です。

## 使い方

1. テキストを入力したいフィールドにカーソルを置く
2. **ホットキーを押しながら話す**（デフォルト: `ctrl+shift+space`）
3. **ホットキーを離す** → テキストが自動挿入される

### アイコンの意味

| アイコン | 状態   |
| -------- | ------ |
| 🎤       | 待機中 |
| 🔴       | 録音中 |
| ⏳       | 処理中 |

## 設定

`.env` ファイルで動作をカスタマイズできます。

| 項目                  | デフォルト                             | 説明                               |
| --------------------- | -------------------------------------- | ---------------------------------- |
| `WHISPER_MODEL`       | `mlx-community/whisper-large-v3-turbo` | モデルのパスまたは HuggingFace リポジトリ |
| `WHISPER_LANGUAGE`    | `ja`                                   | 認識言語                           |
| `OLLAMA_MODEL`        | `qwen2.5:7b`                           | 文章整形に使用する LLM             |
| `LLM_CLEANUP_ENABLED` | `true`                                 | フィラー語除去・句読点補完の有効/無効 |
| `HOTKEY`              | `ctrl+shift+space`                     | 録音ホットキー                     |

## アーキテクチャ

```
ホットキー押下
    ↓
AudioCapture (sounddevice, 16kHz)
    ↓
Silero VAD (無音スキップ)
    ↓
mlx-whisper (音声 → テキスト)
    ↓
Ollama LLM (文章整形) ※オプション
    ↓
TextInserter (クリップボード → Cmd+V)
    ↓
アクティブアプリのテキストフィールド
```

## ライセンス

MIT