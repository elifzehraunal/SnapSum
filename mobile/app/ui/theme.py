"""Theme definition for SnapSum."""

from __future__ import annotations

import flet as ft

# ── Color Palette ──
PRIMARY = "#4F46E5"      # Premium Indigo 600
SECONDARY = "#EC4899"    # Vibrant Rose 500
SURFACE = "#F8FAFC"      # Clean Slate 50
CARD_BG = "#FFFFFF"      # Pure White
BORDER = "#E2E8F0"       # Soft Slate 200
TEXT_PRIMARY = "#0F172A" # Dark Slate 900
TEXT_SECONDARY = "#64748B"# Sakin Slate 500
SUCCESS = "#10B981"      # Elegant Emerald 500
WARNING = "#F59E0B"      # Warm Amber 500
ERROR = "#EF4444"        # Clean Red 500

CAT_COLORS = {
    "Bilim": "#10B981",    # Emerald
    "Tarih": "#F59E0B",    # Amber
    "Dram": "#EC4899",     # Rose
    "Macera": "#06B6D4",   # Cyan
    "Felsefe": "#8B5CF6",  # Violet
    "Genel": "#6366F1",    # Indigo
}

CAT_ICONS = {
    "Bilim": ft.Icons.SCIENCE,
    "Tarih": ft.Icons.HISTORY_EDU,
    "Dram": ft.Icons.THEATER_COMEDY,
    "Macera": ft.Icons.EXPLORE,
    "Felsefe": ft.Icons.PSYCHOLOGY,
    "Genel": ft.Icons.AUTO_STORIES,
}


def app_theme() -> ft.Theme:
    """Build SnapSum's branded Material 3 theme."""
    return ft.Theme(
        use_material3=True,
        color_scheme_seed=PRIMARY,
    )

