"""
StatusBar — bottom strip that shows the agent's current state.
Supports three modes: IDLE | LISTENING | THINKING
and animates a blinking cursor indicator when active.
"""

import tkinter as tk
import customtkinter as ctk
from gui.theme import (
    BG_PRIMARY, STATUS_IDLE, STATUS_LISTENING, STATUS_THINKING, STATUS_ERROR,
    FONT_STATUS, BORDER_COLOR, BG_SECONDARY,
)

_STATUS_CONFIG = {
    "idle":      ("■  IDLE",      STATUS_IDLE),
    "listening": ("◉  LISTENING", STATUS_LISTENING),
    "thinking":  ("◈  THINKING",  STATUS_THINKING),
    "error":     ("✖  ERROR",     STATUS_ERROR),
}


class StatusBar(ctk.CTkFrame):
    """Slim status bar that shows the agent's current operational state."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=BG_SECONDARY,
            corner_radius=0,
            border_width=1,
            border_color=BORDER_COLOR,
            height=36,
            **kwargs,
        )
        self.pack_propagate(False)

        # Left: status indicator
        self._status_label = ctk.CTkLabel(
            self,
            text="■  IDLE",
            text_color=STATUS_IDLE,
            font=FONT_STATUS,
            anchor="w",
        )
        self._status_label.pack(side="left", padx=16, pady=0)

        # Right: version / branding
        self._brand_label = ctk.CTkLabel(
            self,
            text="JARVIS v1.0  //  LOCAL AI AGENT",
            text_color=BORDER_COLOR,
            font=("Courier New", 9),
            anchor="e",
        )
        self._brand_label.pack(side="right", padx=16, pady=0)

        # Blink animation state
        self._blink_after_id = None
        self._blink_visible = True
        self._current_mode = "idle"

    # ── Public API ────────────────────────────────────────────────────────────

    def set_status(self, mode: str) -> None:
        """Set status to one of: 'idle', 'listening', 'thinking', 'error'."""
        mode = mode.lower()
        if mode not in _STATUS_CONFIG:
            mode = "idle"

        self._current_mode = mode
        label_text, color = _STATUS_CONFIG[mode]
        self._status_label.configure(text=label_text, text_color=color)

        # Stop any existing blink
        self._stop_blink()

        # Animate for active states
        if mode in ("listening", "thinking"):
            self._start_blink(label_text, color)

    def get_status(self) -> str:
        return self._current_mode

    # ── Blink animation ───────────────────────────────────────────────────────

    def _start_blink(self, label_text: str, color: str) -> None:
        self._blink_visible = True
        self._blink_tick(label_text, color)

    def _blink_tick(self, label_text: str, color: str) -> None:
        if self._current_mode not in ("listening", "thinking"):
            return
        if self._blink_visible:
            self._status_label.configure(text=label_text, text_color=color)
        else:
            # dim flash
            self._status_label.configure(text_color=BORDER_COLOR)
        self._blink_visible = not self._blink_visible
        self._blink_after_id = self.after(600, self._blink_tick, label_text, color)

    def _stop_blink(self) -> None:
        if self._blink_after_id:
            self.after_cancel(self._blink_after_id)
            self._blink_after_id = None
