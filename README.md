# JARVIS — Local AI Agent

> A local-first AI desktop agent with a hacking aesthetic GUI, voice input, and the ability to control your system, browser, and apps — all offline.

---

## ✅ Current Status: Step 2 — Ollama Integration

The interface is live and connected to a local `qwen2.5:3b` model via Ollama.
Responses stream token-by-token directly into the chat display.

---

## 🗂 Project Structure

```
Jarvis/
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
├── backend/
│   ├── __init__.py
│   └── ollama_client.py  # Streaming Ollama client with conversation history
├── gui/
│   ├── __init__.py
│   ├── app.py            # Main window (JarvisApp)
│   ├── chat_display.py   # Scrollable chat log + streaming API
│   ├── status_bar.py     # Animated status bar (Idle/Listening/Thinking)
│   └── theme.py          # Color palette, fonts, size constants
└── README.md
```

---

## 🚀 Quick Start

```bash
# 0. Install and start Ollama (https://ollama.com)
ollama pull qwen2.5:3b     # one-time model download

# 1. Create & activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run (Ollama must be running in background)
python main.py
```

---

## 🖥 GUI Features (Step 1)

| Element | Description |
|---------|-------------|
| **Header** | Blinking green dot + `J A R V I S` title |
| **Chat log** | Scrollable, color-coded messages — green for user, cyan for bot |
| **Input box** | Monospace text field with focus glow |
| **🎙 Mic button** | Toggles listening state (visual only, Step 3 adds real audio) |
| **SEND button** | Sends typed message; `Enter` key also works |
| **Status bar** | Animated `IDLE / LISTENING / THINKING` with blinking indicator |
| **CLR button** | Clears the chat log |

---

## 🛠 Build Roadmap

| Step | Feature | Status |
|------|---------|--------|
| 1 | GUI Shell | ✅ Done |
| 2 | Ollama Integration (qwen2.5:3b) | ✅ Done |
| 3 | Voice Input (faster-whisper tiny) | ⏳ Pending |
| 4 | Intent Detection (structured JSON) | ⏳ Pending |
| 5 | File & Folder Actions | ⏳ Pending |
| 6 | Browser Control | ⏳ Pending |
| 7 | WhatsApp Messaging | ⏳ Pending |
| 8 | Urdu + English Support | ⏳ Pending |
| 9 | Background Service + System Tray | ⏳ Pending |

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Esc` | Clear input field |

---

## 🎨 Design Language

- **Palette**: Terminal green (`#00ff41`) + electric cyan (`#00e5ff`) on near-black (`#0a0a0f`)
- **Font**: Courier New (monospace) throughout
- **Animations**: Blinking power dot, animated status indicator
- **Theme**: Hacking / matrix aesthetic — no light mode

---

*Built with Python + CustomTkinter*