"""
VoiceRecorder — push-to-talk microphone recorder + Whisper transcription.

Flow:
  1. start_recording()  → opens a sounddevice InputStream, accumulates chunks
  2. stop_and_transcribe(on_result, on_error)
                        → stops stream, writes temp WAV, runs faster-whisper,
                          calls on_result(text) or on_error(msg) on main thread

The Whisper model is loaded lazily on first use (tiny model, ~75 MB).
All heavy work runs on background threads; callers must schedule GUI
updates via root.after() if necessary.
"""

from __future__ import annotations

import io
import threading
import wave
import tempfile
import os
from typing import Callable

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE    = 16_000   # Hz — Whisper's native rate
CHANNELS       = 1
DTYPE          = "float32"
WHISPER_MODEL  = "tiny"   # ~75 MB, fast on CPU
SILENCE_THRESH = 0.01     # RMS below this = silence (used for VAD hint)


class VoiceRecorder:
    """Handles microphone recording and Whisper transcription."""

    def __init__(self):
        self._model: WhisperModel | None = None
        self._model_lock = threading.Lock()
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._is_recording = False
        self._record_lock = threading.Lock()

    # ── Model loading ──────────────────────────────────────────────────────

    def load_model_async(
        self,
        on_ready: Callable[[], None],
        on_error: Callable[[str], None],
    ) -> None:
        """Load the Whisper model in a background thread."""
        threading.Thread(
            target=self._load_worker,
            args=(on_ready, on_error),
            daemon=True,
        ).start()

    def _load_worker(self, on_ready, on_error):
        try:
            with self._model_lock:
                if self._model is None:
                    self._model = WhisperModel(
                        WHISPER_MODEL,
                        device="cpu",
                        compute_type="int8",  # fastest on CPU
                    )
            on_ready()
        except Exception as exc:
            on_error(str(exc))

    # ── Recording ──────────────────────────────────────────────────────────

    def start_recording(self) -> None:
        """Open microphone stream and start buffering audio."""
        with self._record_lock:
            if self._is_recording:
                return
            self._chunks = []
            self._is_recording = True

        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._audio_callback,
            blocksize=1024,
        )
        self._stream.start()

    def stop_and_transcribe(
        self,
        on_result: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        """
        Stop recording, then transcribe in a background thread.
        on_result(text) or on_error(msg) is called when done.
        """
        with self._record_lock:
            if not self._is_recording:
                return
            self._is_recording = False

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        chunks = list(self._chunks)
        self._chunks = []

        threading.Thread(
            target=self._transcribe_worker,
            args=(chunks, on_result, on_error),
            daemon=True,
        ).start()

    def is_recording(self) -> bool:
        return self._is_recording

    # ── Internal ───────────────────────────────────────────────────────────

    def _audio_callback(self, indata: np.ndarray, frames, time, status):
        """Called by sounddevice on each audio block."""
        if self._is_recording:
            self._chunks.append(indata.copy())

    def _transcribe_worker(
        self,
        chunks: list[np.ndarray],
        on_result: Callable[[str], None],
        on_error: Callable[[str], None],
    ) -> None:
        try:
            if not chunks:
                on_error("No audio recorded")
                return

            # Ensure model is loaded (may already be done)
            with self._model_lock:
                if self._model is None:
                    self._model = WhisperModel(
                        WHISPER_MODEL,
                        device="cpu",
                        compute_type="int8",
                    )

            # Assemble audio buffer
            audio = np.concatenate(chunks, axis=0).flatten()

            # Check for near-silence
            rms = float(np.sqrt(np.mean(audio ** 2)))
            if rms < SILENCE_THRESH:
                on_error("Audio too quiet — please speak louder")
                return

            # Write to a temp WAV file (faster-whisper accepts file paths)
            tmp_path = self._write_wav(audio)
            try:
                segments, info = self._model.transcribe(
                    tmp_path,
                    beam_size=5,
                    language=None,        # auto-detect (handles Urdu + English)
                    vad_filter=True,      # skip silence segments
                    vad_parameters={"min_silence_duration_ms": 300},
                )
                text = " ".join(seg.text.strip() for seg in segments).strip()
                if not text:
                    on_error("Could not detect speech — please try again")
                else:
                    on_result(text)
            finally:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

        except Exception as exc:
            on_error(str(exc))

    @staticmethod
    def _write_wav(audio: np.ndarray) -> str:
        """Write float32 mono audio to a temp WAV file, return path."""
        # Convert float32 [-1, 1] → int16 for WAV
        pcm = (audio * 32767).astype(np.int16)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        with wave.open(tmp.name, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)           # 16-bit = 2 bytes
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm.tobytes())
        return tmp.name
