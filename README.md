<div align="center">

<!-- Animated Header Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=AI%20Meeting%20Assistant&fontSize=52&fontColor=fff&animation=twinkling&fontAlignY=38&desc=Real-time%20AI-Powered%20Speech%20Intelligence%20Overlay&descAlignY=60&descSize=18" width="100%" />

<br/>

<!-- Badges Row -->
<p>
  <img src="https://img.shields.io/badge/Version-3.0-4F8EF7?style=for-the-badge&logo=github&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.8+-7C5CFC?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" />
  <img src="https://img.shields.io/badge/AI-OpenRouter-22C55E?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge" />
</p>

<!-- Typing SVG Animation -->
<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&duration=3000&pause=800&color=4F8EF7&center=true&vCenter=true&multiline=false&repeat=true&width=600&height=50&lines=🎙️+Listens+to+your+meetings...;🧠+Answers+questions+instantly...;🪟+Floats+above+every+window...;⚡+Powered+by+GPT-4o+%26+Claude...;✨+Your+invisible+AI+co-pilot." alt="Typing SVG" />
</a>

<br/><br/>

<!-- Quick Summary Cards -->
<img src="https://img.shields.io/badge/🎤_Speech_Recognition-Real--time-4F8EF7?style=flat-square&labelColor=0E0F13" />
<img src="https://img.shields.io/badge/🤖_AI_Models-GPT--4o_|_Claude_|_Gemini-7C5CFC?style=flat-square&labelColor=0E0F13" />
<img src="https://img.shields.io/badge/🪟_Interface-Always_On_Top_Overlay-22C55E?style=flat-square&labelColor=0E0F13" />
<img src="https://img.shields.io/badge/🔒_Privacy-Local_Config_Storage-F59E0B?style=flat-square&labelColor=0E0F13" />

</div>

---

<div align="center">

## 👨‍💻 Developer

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=6,11,20&height=3&section=header" width="60%" />

<br/>

<img src="https://img.shields.io/badge/Demiyan%20Dissanayake-Developer-4F8EF7?style=for-the-badge&logo=github&logoColor=white&labelColor=0E0F13" height="35"/>

*Crafted with precision — AI tools, clean code, beautiful interfaces.*

</div>

---

## 📖 Table of Contents

- [✨ Overview](#-overview)
- [🚀 Features](#-features)
- [🏗️ Architecture](#-architecture)
- [⚙️ Installation](#-installation)
- [🔧 Configuration](#-configuration)
- [🎮 Usage](#-usage)
- [⌨️ Hotkeys](#-hotkeys)
- [🤖 Supported AI Models](#-supported-ai-models)
- [🔊 System Audio Setup](#-system-audio-setup-windows)
- [📁 Project Structure](#-project-structure)
- [🛠️ Tech Stack](#-tech-stack)
- [🙏 Acknowledgements](#-acknowledgements)

---

## ✨ Overview

**AI Meeting Assistant** is a sleek, always-on-top floating desktop widget that silently listens to your online meetings and instantly answers questions — powered by state-of-the-art AI models via OpenRouter.

> 🎯 **Built for:** Undergrad students, professionals, and anyone who needs a discreet AI co-pilot during Zoom, Meet, or Teams calls.

```
╔══════════════════════════════════════════════════════════════════╗
║       AI MEETING ASSISTANT — Compact Overlay Edition            ║
║              Developer: Demiyan Dissanayake                      ║
║         Perplexity-style floating notification widget            ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🚀 Features

<table>
<tr>
<td width="50%">

### 🎙️ Audio Intelligence
- **Real-time speech recognition** via Google Speech API
- Automatic ambient noise calibration
- Configurable energy threshold & pause detection
- Supports microphone **and** system audio (Stereo Mix)

</td>
<td width="50%">

### 🧠 AI Engine
- Streamed token-by-token responses (no waiting!)
- Maintains last **6 exchanges** as conversation history
- Skips non-questions automatically with `[SKIP]`
- Professor-style structured answers

</td>
</tr>
<tr>
<td>

### 🪟 Overlay Interface
- Compact **340×52px** pill when idle
- Expands to **380×460px** on detection
- Draggable — repositions anywhere on screen
- 97% opacity, always above other windows
- Animated pulsing border while listening

</td>
<td>

### ⚙️ Smart Configuration
- Persistent config saved to `~/.ma_cfg.json`
- Settings panel with API key, model & audio device
- Multi-model support via OpenRouter
- Show/hide API key toggle

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Meeting Assistant                   │
│                                                          │
│   ┌──────────────┐     ┌──────────────┐                 │
│   │  AudioEngine │────▶│  Speech API  │                 │
│   │  (Threading) │     │  (Google)    │                 │
│   └──────┬───────┘     └──────────────┘                 │
│          │ on_text()                                     │
│          ▼                                               │
│   ┌──────────────┐     ┌──────────────┐                 │
│   │   App / UI   │────▶│  AI Engine   │                 │
│   │   (Tkinter)  │     │ (OpenRouter) │                 │
│   └──────────────┘     └──────────────┘                 │
│          │                    │ Streaming                │
│          └────── Queue ◀──────┘  chunks                 │
│                 (Thread-safe)                            │
└─────────────────────────────────────────────────────────┘
```

| Component | Responsibility |
|-----------|---------------|
| `AudioEngine` | Mic capture, noise calibration, Google STT |
| `AI` | OpenRouter API calls, streaming, error handling |
| `App` | Tkinter GUI, event loop, queue processing, persistence |

---

## ⚙️ Installation

### Prerequisites

- Python **3.8+**
- Windows OS (for Stereo Mix system audio support)
- An [OpenRouter](https://openrouter.ai) API key

### Step 1 — Clone the repository

```bash
git clone https://github.com/demiyan-dissanayake/ai-meeting-assistant.git
cd ai-meeting-assistant
```

### Step 2 — Install dependencies

```bash
pip install SpeechRecognition pyaudio requests
```

> ⚠️ **PyAudio on Windows:** If `pip install pyaudio` fails, download the prebuilt wheel from [Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install with:
> ```bash
> pip install PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl
> ```

### Step 3 — Run

```bash
python meeting_assistant.py
```

---

## 🔧 Configuration

Open **Settings** from the widget gear icon (⚙) or by clicking the tray.

| Setting | Description | Default |
|---------|-------------|---------|
| `API Key` | Your OpenRouter API key | *(required)* |
| `Model` | AI model to use | `openai/gpt-4o` |
| `Audio Device` | Microphone or Stereo Mix | `Default` |

Config is persisted at:
```
C:\Users\<you>\.ma_cfg.json
```

---

## 🎮 Usage

1. **Launch** `meeting_assistant.py` — a slim dark bar appears top-right of your screen
2. Click **⚙ Settings**, paste your OpenRouter API key, select model & audio device, hit **Save**
3. Press **`F2`** or click the mic button to start listening
4. Join your Zoom / Meet / Teams call — the assistant auto-detects questions
5. Answers stream in real-time in the expanded panel
6. Press **`F4`** to copy the last answer to clipboard

---

## ⌨️ Hotkeys

<div align="center">

| Key | Action |
|:---:|--------|
| <kbd>F2</kbd> | ▶ Start / ⏹ Stop listening |
| <kbd>F3</kbd> | Collapse widget to compact mode |
| <kbd>F4</kbd> | Copy last answer to clipboard |
| <kbd>Esc</kbd> | Stop listening immediately |

</div>

---

## 🤖 Supported AI Models

All models are accessed through **[OpenRouter](https://openrouter.ai)**:

<div align="center">

| Model | Provider | Best For |
|-------|----------|----------|
| `openai/gpt-4o` | OpenAI | Best overall accuracy |
| `openai/gpt-4o-mini` | OpenAI | Fast & cost-efficient |
| `anthropic/claude-3.5-sonnet` | Anthropic | Reasoning & analysis |
| `anthropic/claude-3-haiku` | Anthropic | Ultra-fast responses |
| `google/gemini-pro` | Google | Broad knowledge |
| `mistralai/mixtral-8x7b-instruct` | Mistral | Open-source quality |

</div>

---

## 🔊 System Audio Setup (Windows)

To capture audio from Zoom, Meet, or Teams *(not just your mic)*:

```
1. Right-click the speaker icon in the taskbar
2. Open "Sound Settings" → "More sound settings"
3. Go to the "Recording" tab
4. Right-click in empty space → "Show Disabled Devices"
5. Enable "Stereo Mix"
6. In the app Settings → Audio Device → select "Stereo Mix"
```

> 💡 This lets the assistant hear **what plays through your speakers**, including remote participants.

---

## 📁 Project Structure

```
ai-meeting-assistant/
│
├── 📄 meeting_assistant.py    # Main application (single-file)
├── 📄 README.md               # You are here
└── 📄 .ma_cfg.json            # Auto-generated user config (gitignored)
```

---

## 🛠️ Tech Stack

<div align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Tkinter-GUI-4F8EF7?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Google_Speech_API-4285F4?style=for-the-badge&logo=google&logoColor=white" />
<img src="https://img.shields.io/badge/OpenRouter_API-7C5CFC?style=for-the-badge&logo=openai&logoColor=white" />
<img src="https://img.shields.io/badge/SpeechRecognition-22C55E?style=for-the-badge&logo=soundcloud&logoColor=white" />
<img src="https://img.shields.io/badge/PyAudio-F59E0B?style=for-the-badge&logo=audacity&logoColor=white" />

</div>

---

## 🙏 Acknowledgements

- [OpenRouter](https://openrouter.ai) — unified AI model gateway
- [SpeechRecognition](https://github.com/Uberi/speech_recognition) — audio processing library
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) — real-time audio I/O
- Inspired by the idea of a *silent AI co-pilot* for learners everywhere

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=footer&text=Built%20by%20Demiyan%20Dissanayake&fontSize=24&fontColor=fff&animation=twinkling&fontAlignY=65" width="100%" />

<br/>

<sub>⭐ If this project helped you, consider giving it a star!</sub>

<br/><br/>

<img src="https://img.shields.io/badge/Made%20with-❤️%20%26%20Python-4F8EF7?style=flat-square&labelColor=0E0F13" />
<img src="https://img.shields.io/badge/Developer-Demiyan%20Dissanayake-7C5CFC?style=flat-square&labelColor=0E0F13" />

</div>
