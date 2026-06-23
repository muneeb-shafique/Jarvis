"""
Jarvis Theme — Hacking Aesthetic
Terminal-green / cyan on black with glow-inspired colors.
All color / font constants live here so they can be reused across widgets.
"""

# ── Palette ──────────────────────────────────────────────────────────────────
BG_PRIMARY      = "#0a0a0f"     # near-black app background
BG_SECONDARY    = "#0d1117"     # slightly lighter panel bg
BG_TERTIARY     = "#111827"     # input / card surface
BORDER_COLOR    = "#1a2f1a"     # subtle green-tinted border

ACCENT_GREEN    = "#00ff41"     # classic matrix green
ACCENT_CYAN     = "#00e5ff"     # electric cyan
ACCENT_DIM      = "#00cc33"     # dimmer green for secondary text
ACCENT_MUTED    = "#006622"     # very dim green (timestamps, hints)

TEXT_PRIMARY    = "#e0ffe8"     # near-white with green tint
TEXT_SECONDARY  = "#7aff9a"     # medium green
TEXT_MUTED      = "#3a6b3a"     # dim green

STATUS_IDLE      = "#3a6b3a"
STATUS_LISTENING = "#00ff41"
STATUS_THINKING  = "#00e5ff"
STATUS_ERROR     = "#ff4444"

# User bubble
USER_BUBBLE_BG   = "#0d2b0d"
USER_BUBBLE_FG   = "#00ff41"

# Bot bubble
BOT_BUBBLE_BG    = "#071420"
BOT_BUBBLE_FG    = "#00e5ff"

# ── Typography ────────────────────────────────────────────────────────────────
FONT_MONO        = ("Courier New", 13)
FONT_MONO_SMALL  = ("Courier New", 10)
FONT_MONO_LARGE  = ("Courier New", 15, "bold")
FONT_TITLE       = ("Courier New", 22, "bold")
FONT_STATUS      = ("Courier New", 11, "bold")

# ── Sizes ─────────────────────────────────────────────────────────────────────
WINDOW_WIDTH     = 900
WINDOW_HEIGHT    = 680
CORNER_RADIUS    = 8
PAD              = 12
