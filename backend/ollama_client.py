"""
OllamaClient — thin wrapper around the ollama Python SDK.

Responsibilities:
  • Check that Ollama is reachable and the model is available.
  • Stream chat completions token-by-token.
  • Maintain a per-session conversation history so context is preserved.
  • Run everything on a background thread so the GUI stays responsive.
"""

from __future__ import annotations

import threading
from typing import Callable, Iterator
import ollama

MODEL = "qwen2.5:3b"

# System prompt that gives Jarvis its personality
SYSTEM_PROMPT = (
    "You are JARVIS, a concise and capable local AI assistant. "
    "You help the user with tasks on their computer, answer questions, "
    "and execute commands. Keep responses short and to the point. "
    "If the user writes in Urdu, respond in Urdu. "
    "If the user writes in English, respond in English."
)


class OllamaClient:
    """Manages communication with a locally running Ollama instance."""

    def __init__(self, model: str = MODEL):
        self.model = model
        self._history: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self._lock = threading.Lock()

    # ── Public API ─────────────────────────────────────────────────────────

    def is_available(self) -> tuple[bool, str]:
        """
        Check if Ollama is running and the model is pulled.
        Returns (ok: bool, message: str).
        """
        try:
            client = ollama.Client()
            models = client.list()
            names = [m.model for m in models.models]
            if not any(self.model in n for n in names):
                return False, (
                    f"Model '{self.model}' not found. "
                    f"Run:  ollama pull {self.model}"
                )
            return True, f"Ollama OK — model '{self.model}' ready"
        except Exception as e:
            return False, f"Ollama not reachable: {e}"

    def stream_chat(
        self,
        user_message: str,
        on_token: Callable[[str], None],
        on_done: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        """
        Send *user_message* to Ollama and stream the response.
        All callbacks are invoked on the calling thread (caller must
        schedule GUI updates via `root.after` if needed).

        Args:
            user_message: The raw user text.
            on_token:     Called for each text chunk as it arrives.
            on_done:      Called once with the full assembled response.
            on_error:     Called if anything goes wrong.
        """
        thread = threading.Thread(
            target=self._stream_worker,
            args=(user_message, on_token, on_done, on_error),
            daemon=True,
        )
        thread.start()

    def clear_history(self) -> None:
        """Reset conversation history (keep system prompt)."""
        with self._lock:
            self._history = [{"role": "system", "content": SYSTEM_PROMPT}]

    # ── Internal ───────────────────────────────────────────────────────────

    def _stream_worker(
        self,
        user_message: str,
        on_token: Callable[[str], None],
        on_done: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        with self._lock:
            self._history.append({"role": "user", "content": user_message})

        full_response = ""
        try:
            client = ollama.Client()
            stream: Iterator = client.chat(
                model=self.model,
                messages=self._history,
                stream=True,
            )
            for chunk in stream:
                token = chunk.message.content or ""
                full_response += token
                on_token(token)

            # Persist assistant turn in history
            with self._lock:
                self._history.append(
                    {"role": "assistant", "content": full_response}
                )
            on_done(full_response)

        except Exception as exc:
            # Remove the user turn we already added so history stays clean
            with self._lock:
                if self._history and self._history[-1]["role"] == "user":
                    self._history.pop()
            on_error(str(exc))
