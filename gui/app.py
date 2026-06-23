"""
JarvisApp — main application window.
Step 3: Voice input via faster-whisper + sounddevice.
"""

import customtkinter as ctk
import tkinter as tk
from gui.theme import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_MUTED, ACCENT_DIM,
    TEXT_PRIMARY, FONT_MONO, FONT_MONO_SMALL, FONT_TITLE,
    CORNER_RADIUS, PAD, BORDER_COLOR,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    STATUS_ERROR,
)
from gui.chat_display import ChatDisplay
from gui.status_bar import StatusBar
from backend.ollama_client import OllamaClient
from backend.voice_input import VoiceRecorder

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class JarvisApp:
    """Main application controller and window."""

    def __init__(self):
        self._root = ctk.CTk()
        self._is_thinking  = False   # Ollama busy guard
        self._whisper_ready = False  # model loaded flag

        self._ollama  = OllamaClient()
        self._voice   = VoiceRecorder()

        self._setup_window()
        self._build_ui()

        # Deferred startup tasks
        self._root.after(300,  self._check_ollama)
        self._root.after(1500, self._load_whisper)   # load after UI paints

    # ── Window ────────────────────────────────────────────────────────────────

    def _setup_window(self):
        self._root.title("JARVIS — Local AI Agent")
        self._root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self._root.minsize(700, 500)
        self._root.configure(fg_color=BG_PRIMARY)

        self._root.update_idletasks()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x  = (sw - WINDOW_WIDTH)  // 2
        y  = (sh - WINDOW_HEIGHT) // 2
        self._root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        self._root.resizable(True, True)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_chat_area()
        self._build_input_area()
        self._build_status_bar()
        self._bind_keys()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        header = ctk.CTkFrame(
            self._root,
            fg_color=BG_SECONDARY,
            corner_radius=0,
            border_width=1,
            border_color=BORDER_COLOR,
            height=56,
        )
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        self._power_dot = ctk.CTkLabel(
            header, text="●", text_color=ACCENT_GREEN,
            font=("Courier New", 20), width=30,
        )
        self._power_dot.pack(side="left", padx=(16, 4))
        self._blink_power_dot()

        ctk.CTkLabel(
            header, text="J A R V I S", text_color=ACCENT_GREEN,
            font=FONT_TITLE, anchor="w",
        ).pack(side="left", padx=4)

        ctk.CTkLabel(
            header, text="// LOCAL AI AGENT", text_color=ACCENT_MUTED,
            font=("Courier New", 11), anchor="w",
        ).pack(side="left", padx=8)

        self._model_label = ctk.CTkLabel(
            header, text="⬡  qwen2.5:3b",
            text_color=ACCENT_MUTED, font=("Courier New", 10),
        )
        self._model_label.pack(side="right", padx=(0, 8))

        ctk.CTkButton(
            header, text="CLR", width=48, height=28,
            fg_color="transparent", text_color=ACCENT_MUTED,
            hover_color=BG_TERTIARY, border_width=1,
            border_color=ACCENT_MUTED, corner_radius=4,
            font=FONT_MONO_SMALL, command=self._clear_chat,
        ).pack(side="right", padx=(0, 8))

    def _blink_power_dot(self):
        cur = self._power_dot.cget("text_color")
        nxt = ACCENT_MUTED if cur == ACCENT_GREEN else ACCENT_GREEN
        self._power_dot.configure(text_color=nxt)
        self._root.after(900, self._blink_power_dot)

    # ── Chat ──────────────────────────────────────────────────────────────────

    def _build_chat_area(self):
        self._chat = ChatDisplay(self._root)
        self._chat.pack(fill="both", expand=True, padx=PAD, pady=(PAD, 0))

    # ── Input row ─────────────────────────────────────────────────────────────

    def _build_input_area(self):
        row = ctk.CTkFrame(self._root, fg_color="transparent", corner_radius=0)
        row.pack(fill="x", padx=PAD, pady=PAD)

        self._entry = ctk.CTkEntry(
            row,
            placeholder_text="  type a command …",
            placeholder_text_color=ACCENT_MUTED,
            fg_color=BG_TERTIARY,
            text_color=ACCENT_GREEN,
            border_color=ACCENT_MUTED,
            border_width=1,
            corner_radius=CORNER_RADIUS,
            font=FONT_MONO,
            height=44,
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._entry.bind("<FocusIn>",  lambda e: self._entry.configure(border_color=ACCENT_GREEN))
        self._entry.bind("<FocusOut>", lambda e: self._entry.configure(border_color=ACCENT_MUTED))

        # ── Mic button ────────────────────────────────────────────────────────
        self._mic_btn = ctk.CTkButton(
            row,
            text="🎙",
            width=48, height=44,
            fg_color=BG_TERTIARY,
            text_color=ACCENT_CYAN,
            hover_color=BG_SECONDARY,
            border_width=1,
            border_color=ACCENT_CYAN,
            corner_radius=CORNER_RADIUS,
            font=("Courier New", 18),
            command=self._toggle_mic,
        )
        self._mic_btn.pack(side="left", padx=(0, 8))

        # ── Send button ───────────────────────────────────────────────────────
        self._send_btn = ctk.CTkButton(
            row,
            text="SEND ▶",
            width=90, height=44,
            fg_color=BG_TERTIARY,
            text_color=ACCENT_GREEN,
            hover_color="#0d2b0d",
            border_width=1,
            border_color=ACCENT_GREEN,
            corner_radius=CORNER_RADIUS,
            font=("Courier New", 12, "bold"),
            command=self._on_send,
        )
        self._send_btn.pack(side="left")

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_status_bar(self):
        self._status_bar = StatusBar(self._root)
        self._status_bar.pack(fill="x", side="bottom")

    # ── Keybinds ──────────────────────────────────────────────────────────────

    def _bind_keys(self):
        self._root.bind("<Return>", lambda e: self._on_send())
        self._root.bind("<Escape>", lambda e: self._entry.delete(0, "end"))

    # ── Startup checks ────────────────────────────────────────────────────────

    def _check_ollama(self):
        import threading
        def _w():
            ok, msg = self._ollama.is_available()
            self._root.after(0, lambda: self._on_ollama_check(ok, msg))
        threading.Thread(target=_w, daemon=True).start()

    def _on_ollama_check(self, ok: bool, msg: str):
        if ok:
            self._chat.add_system_message(f"▸ {msg}")
            self._model_label.configure(text_color=ACCENT_GREEN)
        else:
            self._chat.add_system_message(f"⚠  {msg}")
            self._status_bar.set_status("error")
            self._model_label.configure(text_color="#ff4444")

    def _load_whisper(self):
        """Load the Whisper tiny model asynchronously after boot."""
        self._chat.add_system_message("▸ Loading Whisper tiny model …")
        self._mic_btn.configure(state="disabled", text_color=ACCENT_MUTED)
        self._voice.load_model_async(
            on_ready=lambda: self._root.after(0, self._on_whisper_ready),
            on_error=lambda e: self._root.after(0, lambda: self._on_whisper_error(e)),
        )

    def _on_whisper_ready(self):
        self._whisper_ready = True
        self._mic_btn.configure(state="normal", text_color=ACCENT_CYAN)
        self._chat.add_system_message("▸ Whisper tiny ready — mic button enabled")

    def _on_whisper_error(self, err: str):
        self._chat.add_system_message(f"⚠  Whisper failed to load: {err}")

    # ── Send (text) ───────────────────────────────────────────────────────────

    def _on_send(self):
        if self._is_thinking:
            return
        text = self._entry.get().strip()
        if not text:
            return
        self._entry.delete(0, "end")
        self._dispatch_to_ollama(text)

    def _dispatch_to_ollama(self, text: str):
        """Shared entry point for both typed and transcribed input."""
        self._chat.add_user_message(text)
        self._set_thinking(True)
        self._chat.begin_bot_stream()
        self._ollama.stream_chat(
            user_message=text,
            on_token=self._on_token,
            on_done=self._on_done,
            on_error=self._on_ollama_error,
        )

    # ── Mic (voice) ───────────────────────────────────────────────────────────

    def _toggle_mic(self):
        if self._is_thinking:
            return
        if not self._whisper_ready:
            self._chat.add_system_message("⚠  Whisper model still loading …")
            return

        if self._voice.is_recording():
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        self._voice.start_recording()
        self._mic_btn.configure(
            text="⏹",
            fg_color="#1a0000",
            text_color="#ff4444",
            border_color="#ff4444",
        )
        self._status_bar.set_status("listening")
        self._send_btn.configure(state="disabled")
        self._entry.configure(state="disabled")
        self._chat.add_system_message("▸ Recording … click ⏹ to stop")

    def _stop_recording(self):
        # Reset mic button immediately so it looks responsive
        self._mic_btn.configure(
            text="🎙",
            fg_color=BG_TERTIARY,
            text_color=ACCENT_MUTED,
            border_color=ACCENT_MUTED,
            state="disabled",
        )
        self._status_bar.set_status("thinking")
        self._chat.add_system_message("▸ Transcribing …")

        self._voice.stop_and_transcribe(
            on_result=self._on_transcription,
            on_error=self._on_transcription_error,
        )

    def _on_transcription(self, text: str):
        """Called from worker thread — schedule on main thread."""
        self._root.after(0, lambda: self._handle_transcription(text))

    def _handle_transcription(self, text: str):
        self._mic_btn.configure(
            text_color=ACCENT_CYAN,
            border_color=ACCENT_CYAN,
            state="normal",
        )
        self._chat.add_system_message(f"▸ Heard: \"{text}\"")
        self._entry.configure(state="normal")
        self._send_btn.configure(state="normal")
        # Auto-send the transcribed text
        self._dispatch_to_ollama(text)

    def _on_transcription_error(self, msg: str):
        self._root.after(0, lambda: self._handle_transcription_error(msg))

    def _handle_transcription_error(self, msg: str):
        self._mic_btn.configure(
            text_color=ACCENT_CYAN,
            border_color=ACCENT_CYAN,
            state="normal",
        )
        self._entry.configure(state="normal")
        self._send_btn.configure(state="normal")
        self._chat.add_system_message(f"⚠  Transcription error: {msg}")
        self._status_bar.set_status("idle")

    # ── Ollama callbacks ──────────────────────────────────────────────────────

    def _on_token(self, token: str):
        self._root.after(0, lambda t=token: self._chat.append_bot_token(t))

    def _on_done(self, _full: str):
        self._root.after(0, self._finish_response)

    def _on_ollama_error(self, err: str):
        self._root.after(0, lambda: self._handle_ollama_error(err))

    def _finish_response(self):
        self._chat.end_bot_stream()
        self._set_thinking(False)

    def _handle_ollama_error(self, err: str):
        self._chat.end_bot_stream()
        self._chat.add_system_message(f"⚠  Ollama error: {err}")
        self._status_bar.set_status("error")
        self._root.after(3000, lambda: self._status_bar.set_status("idle"))
        self._set_thinking(False)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_thinking(self, active: bool):
        self._is_thinking = active
        if active:
            self._status_bar.set_status("thinking")
            self._send_btn.configure(state="disabled", text="  …  ")
            self._entry.configure(state="disabled")
            self._mic_btn.configure(state="disabled")
        else:
            self._status_bar.set_status("idle")
            self._send_btn.configure(state="normal", text="SEND ▶")
            self._entry.configure(state="normal")
            if self._whisper_ready:
                self._mic_btn.configure(state="normal")
            self._entry.focus()

    def _clear_chat(self):
        self._ollama.clear_history()
        self._chat.clear()
        self._chat.add_system_message("▸ Chat cleared — conversation history reset")

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        self._root.mainloop()
