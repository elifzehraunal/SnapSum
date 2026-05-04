"""Theme definition for SnapSum."""

from __future__ import annotations

import flet as ft

# ── Color Palette ──
PRIMARY = "#6C63FF"
SECONDARY = "#FF6584"
SURFACE = "#F5F6FA"
CARD_BG = "#FFFFFF"
BORDER = "#E2E2EA"
TEXT_PRIMARY = "#2D2D3F"
TEXT_SECONDARY = "#8E8EA0"
SUCCESS = "#43A047"
WARNING = "#FB8C00"
ERROR = "#E53935"

CAT_COLORS = {
    "Bilim": "#4CAF50",
    "Tarih": "#FF9800",
    "Dram": "#E91E63",
    "Macera": "#2196F3",
    "Felsefe": "#9C27B0",
    "Genel": "#607D8B",
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
