"""
JarvisApp — main application window.
Step 2: Ollama integration with streaming responses.
"""

import customtkinter as ctk
import tkinter as tk
from gui.theme import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_MUTED, ACCENT_DIM,
    TEXT_PRIMARY, FONT_MONO, FONT_MONO_SMALL, FONT_TITLE,
    CORNER_RADIUS, PAD, BORDER_COLOR,
    WINDOW_WIDTH, WINDOW_HEIGHT,
)
from gui.chat_display import ChatDisplay
from gui.status_bar import StatusBar
from backend.ollama_client import OllamaClient

# Force dark mode globally
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class JarvisApp:
    """Main application controller and window."""

    def __init__(self):
        self._root = ctk.CTk()
        self._mic_active = False
        self._is_thinking = False          # guard against double-send
        self._ollama = OllamaClient()

        self._setup_window()
        self._build_ui()

        # Check Ollama availability after the window is ready
        self._root.after(300, self._check_ollama)

    # ── Window setup ──────────────────────────────────────────────────────────

    def _setup_window(self):
        self._root.title("JARVIS — Local AI Agent")
        self._root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self._root.minsize(700, 500)
        self._root.configure(fg_color=BG_PRIMARY)

        self._root.update_idletasks()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x = (sw - WINDOW_WIDTH) // 2
        y = (sh - WINDOW_HEIGHT) // 2
        self._root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        self._root.resizable(True, True)

    # ── UI construction ───────────────────────────────────────────────────────

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
            header,
            text="●",
            text_color=ACCENT_GREEN,
            font=("Courier New", 20),
            width=30,
        )
        self._power_dot.pack(side="left", padx=(16, 4), pady=0)
        self._blink_power_dot()

        ctk.CTkLabel(
            header,
            text="J A R V I S",
            text_color=ACCENT_GREEN,
            font=FONT_TITLE,
            anchor="w",
        ).pack(side="left", padx=4, pady=0)

        ctk.CTkLabel(
            header,
            text="// LOCAL AI AGENT",
            text_color=ACCENT_MUTED,
            font=("Courier New", 11),
            anchor="w",
        ).pack(side="left", padx=8, pady=0)

        # Model badge (right side)
        self._model_label = ctk.CTkLabel(
            header,
            text="⬡  qwen2.5:3b",
            text_color=ACCENT_MUTED,
            font=("Courier New", 10),
        )
        self._model_label.pack(side="right", padx=(0, 8), pady=0)

        # Clear button
        ctk.CTkButton(
            header,
            text="CLR",
            width=48,
            height=28,
            fg_color="transparent",
            text_color=ACCENT_MUTED,
            hover_color=BG_TERTIARY,
            border_width=1,
            border_color=ACCENT_MUTED,
            corner_radius=4,
            font=FONT_MONO_SMALL,
            command=self._clear_chat,
        ).pack(side="right", padx=(0, 8), pady=0)

    def _blink_power_dot(self):
        current = self._power_dot.cget("text_color")
        next_color = ACCENT_MUTED if current == ACCENT_GREEN else ACCENT_GREEN
        self._power_dot.configure(text_color=next_color)
        self._root.after(900, self._blink_power_dot)

    # ── Chat area ─────────────────────────────────────────────────────────────

    def _build_chat_area(self):
        self._chat = ChatDisplay(self._root)
        self._chat.pack(fill="both", expand=True, padx=PAD, pady=(PAD, 0))

    # ── Input area ────────────────────────────────────────────────────────────

    def _build_input_area(self):
        input_frame = ctk.CTkFrame(
            self._root,
            fg_color="transparent",
            corner_radius=0,
        )
        input_frame.pack(fill="x", padx=PAD, pady=PAD)

        self._entry = ctk.CTkEntry(
            input_frame,
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

        self._mic_btn = ctk.CTkButton(
            input_frame,
            text="🎙",
            width=48,
            height=44,
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

        self._send_btn = ctk.CTkButton(
            input_frame,
            text="SEND ▶",
            width=90,
            height=44,
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

    # ── Key bindings ──────────────────────────────────────────────────────────

    def _bind_keys(self):
        self._root.bind("<Return>", lambda e: self._on_send())
        self._root.bind("<Escape>", lambda e: self._entry.delete(0, "end"))

    # ── Ollama availability check ─────────────────────────────────────────────

    def _check_ollama(self):
        """Non-blocking: check in a thread, then update GUI via after()."""
        import threading
        def _worker():
            ok, msg = self._ollama.is_available()
            self._root.after(0, lambda: self._on_ollama_check(ok, msg))
        threading.Thread(target=_worker, daemon=True).start()

    def _on_ollama_check(self, ok: bool, msg: str):
        if ok:
            self._chat.add_system_message(f"▸ {msg}")
            self._model_label.configure(text_color=ACCENT_GREEN)
        else:
            self._chat.add_system_message(f"⚠  {msg}")
            self._status_bar.set_status("error")
            self._model_label.configure(text_color="#ff4444")

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_send(self):
        if self._is_thinking:
            return
        text = self._entry.get().strip()
        if not text:
            return

        self._entry.delete(0, "end")
        self._chat.add_user_message(text)
        self._set_thinking(True)

        # Start streaming from Ollama
        self._chat.begin_bot_stream()
        self._ollama.stream_chat(
            user_message=text,
            on_token=self._on_token,
            on_done=self._on_done,
            on_error=self._on_error,
        )

    def _on_token(self, token: str):
        """Called from worker thread — schedule GUI update on main thread."""
        self._root.after(0, lambda t=token: self._chat.append_bot_token(t))

    def _on_done(self, _full_response: str):
        """Called from worker thread when streaming is complete."""
        self._root.after(0, self._finish_response)

    def _on_error(self, error_msg: str):
        """Called from worker thread on failure."""
        self._root.after(0, lambda: self._handle_error(error_msg))

    def _finish_response(self):
        self._chat.end_bot_stream()
        self._set_thinking(False)

    def _handle_error(self, error_msg: str):
        self._chat.end_bot_stream()
        self._chat.add_system_message(f"⚠  Error: {error_msg}")
        self._status_bar.set_status("error")
        self._root.after(3000, lambda: self._status_bar.set_status("idle"))
        self._set_thinking(False)

    def _set_thinking(self, active: bool):
        self._is_thinking = active
        if active:
            self._status_bar.set_status("thinking")
            self._send_btn.configure(state="disabled", text="  …  ")
            self._entry.configure(state="disabled")
        else:
            self._status_bar.set_status("idle")
            self._send_btn.configure(state="normal", text="SEND ▶")
            self._entry.configure(state="normal")
            self._entry.focus()

    def _toggle_mic(self):
        self._mic_active = not self._mic_active
        if self._mic_active:
            self._mic_btn.configure(
                fg_color="#0d2020",
                text_color=ACCENT_GREEN,
                border_color=ACCENT_GREEN,
            )
            self._status_bar.set_status("listening")
            self._chat.add_system_message(
                "▸ Microphone active — voice input not yet connected (Step 3)"
            )
        else:
            self._mic_btn.configure(
                fg_color=BG_TERTIARY,
                text_color=ACCENT_CYAN,
                border_color=ACCENT_CYAN,
            )
            self._status_bar.set_status("idle")
            self._chat.add_system_message("▸ Microphone off")

    def _clear_chat(self):
        self._ollama.clear_history()
        self._chat.clear()
        self._chat.add_system_message("▸ Chat cleared — conversation history reset")

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        self._root.mainloop()
