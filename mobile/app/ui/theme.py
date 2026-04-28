"""Theme definition for SnapSum."""

from __future__ import annotations

import flet as ft


def app_theme() -> ft.Theme:
    """Build a simple slate/indigo themed Material 3 look."""
    return ft.Theme(
        color_scheme_seed=ft.Colors.INDIGO,
        use_material3=True,
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
    )
