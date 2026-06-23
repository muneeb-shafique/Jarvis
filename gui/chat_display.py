"""
ChatDisplay — scrollable, read-only message log widget.
Renders user messages in green and bot messages in cyan,
with timestamps and a subtle separator line.
"""

import tkinter as tk
from datetime import datetime
import customtkinter as ctk
from gui.theme import (
    BG_SECONDARY, ACCENT_GREEN, ACCENT_CYAN, ACCENT_MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT_MONO, FONT_MONO_SMALL,
    USER_BUBBLE_BG, USER_BUBBLE_FG, BOT_BUBBLE_BG, BOT_BUBBLE_FG,
    BORDER_COLOR, ACCENT_DIM,
)


class ChatDisplay(ctk.CTkFrame):
    """Scrollable chat log that shows user / assistant messages."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=BG_SECONDARY,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_COLOR,
            **kwargs,
        )

        # ── Text widget ───────────────────────────────────────────────────────
        self._text = tk.Text(
            self,
            bg=BG_SECONDARY,
            fg=TEXT_PRIMARY,
            font=FONT_MONO,
            wrap=tk.WORD,
            state=tk.DISABLED,
            cursor="arrow",
            relief=tk.FLAT,
            padx=14,
            pady=10,
            spacing1=4,   # space above each paragraph
            spacing3=4,   # space below each paragraph
            selectbackground=ACCENT_MUTED,
        )
        self._text.pack(fill="both", expand=True, padx=2, pady=2)

        # ── Scrollbar ─────────────────────────────────────────────────────────
        self._scrollbar = ctk.CTkScrollbar(
            self,
            command=self._text.yview,
            fg_color=BG_SECONDARY,
            button_color=ACCENT_MUTED,
            button_hover_color=ACCENT_GREEN,
        )
        self._scrollbar.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")
        self._text.configure(yscrollcommand=self._scrollbar.set)

        # ── Tags ──────────────────────────────────────────────────────────────
        self._text.tag_configure(
            "user_label",
            foreground=ACCENT_GREEN,
            font=("Courier New", 10, "bold"),
        )
        self._text.tag_configure(
            "user_text",
            foreground=USER_BUBBLE_FG,
            font=FONT_MONO,
            lmargin1=20,
            lmargin2=20,
        )
        self._text.tag_configure(
            "bot_label",
            foreground=ACCENT_CYAN,
            font=("Courier New", 10, "bold"),
        )
        self._text.tag_configure(
            "bot_text",
            foreground=BOT_BUBBLE_FG,
            font=FONT_MONO,
            lmargin1=20,
            lmargin2=20,
        )
        self._text.tag_configure(
            "timestamp",
            foreground=ACCENT_MUTED,
            font=FONT_MONO_SMALL,
        )
        self._text.tag_configure(
            "separator",
            foreground="#1a3a1a",
        )
        self._text.tag_configure(
            "system",
            foreground=ACCENT_DIM,
            font=("Courier New", 11, "italic"),
            lmargin1=20,
        )

        # Streaming state
        self._stream_mark = None   # tk index where current stream started

        # Boot message
        self._append_system("▸ JARVIS ONLINE — awaiting input …")

    # ── Public API ────────────────────────────────────────────────────────────

    def add_user_message(self, text: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._write(f"[{ts}] ", "timestamp")
        self._write("YOU ▸ ", "user_label")
        self._write(text + "\n", "user_text")
        self._write("─" * 72 + "\n", "separator")
        self._scroll_to_bottom()

    def add_bot_message(self, text: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._write(f"[{ts}] ", "timestamp")
        self._write("JARVIS ▸ ", "bot_label")
        self._write(text + "\n", "bot_text")
        self._write("─" * 72 + "\n", "separator")
        self._scroll_to_bottom()

    def add_system_message(self, text: str) -> None:
        self._append_system(text)
        self._scroll_to_bottom()

    # ── Streaming API (used by Ollama integration) ─────────────────────────

    def begin_bot_stream(self) -> None:
        """Open a new bot message slot for token-by-token streaming."""
        ts = datetime.now().strftime("%H:%M:%S")
        self._write(f"[{ts}] ", "timestamp")
        self._write("JARVIS ▸ ", "bot_label")
        # Remember where the streamed text starts so we can append to it
        self._text.configure(state=tk.NORMAL)
        self._stream_mark = self._text.index(tk.END)
        self._text.configure(state=tk.DISABLED)
        self._scroll_to_bottom()

    def append_bot_token(self, token: str) -> None:
        """Append a single token to the current streaming bot message."""
        self._write(token, "bot_text")
        self._scroll_to_bottom()

    def end_bot_stream(self) -> None:
        """Close the current streaming bot message and append separator."""
        self._write("\n", "bot_text")
        self._write("─" * 72 + "\n", "separator")
        self._stream_mark = None
        self._scroll_to_bottom()

    def clear(self) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.configure(state=tk.DISABLED)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _append_system(self, text: str) -> None:
        self._write(f"  {text}\n", "system")
        self._scroll_to_bottom()

    def _write(self, text: str, tag: str) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.insert(tk.END, text, tag)
        self._text.configure(state=tk.DISABLED)

    def _scroll_to_bottom(self) -> None:
        self._text.yview_moveto(1.0)
