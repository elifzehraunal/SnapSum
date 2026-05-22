"""SnapSum – Flet mobile application."""

from __future__ import annotations

from pathlib import Path
import shutil
import uuid

import flet as ft

from app.config import (
    APP_NAME, UPLOADS_DIR, DB_FILE,
    get_ui_language, get_mistral_api_key, save_settings
)
from app.data.database import DatabaseManager
from app.models import Book
from app.services.backend_adapter import BackendAdapter
from app.ui.book_detail_view import build_book_dialog, build_summary_dialog
from app.ui.theme import (
    app_theme, PRIMARY, SECONDARY, SURFACE, CARD_BG, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, SUCCESS, ERROR, CAT_COLORS, CAT_ICONS,
)
from app.services.translations import t

# ── Known book → category mapping (replaces random.choice) ──
BOOK_CATEGORIES: dict[str, str] = {
    "Alice Miller - Beden Asla Yalan Söylemez": "Bilim",
    "Attila İlhan - Tutuklunun Günlüğü": "Dram",
    "Ayşe Kulin Hüzün Everest Yayınları": "Dram",
    "Beyaz Geceler Fyodor Mihailoviç Dostoyevski  2": "Dram",
    "Bir Bilim Adamın Serüveni _Celâl Şengör Kitabı_": "Bilim",
    "Franz Kafka - Dava": "Dram",
    "Franz Kafka - Milenaya Mektublar": "Dram",
    "Göz~Stephen King": "Macera",
    "J.R.R. Tolkien - Yüzüklerin Efendisi": "Macera",
    "Jean Paul Sartre - Bulantı": "Felsefe",
    "John Steinbeck Fareler ve İnsanlar Sel Yayınları": "Dram",
    "Khaled Hosseini Bin Muhteşem Güneş Everest Yayınları": "Dram",
    "Paulo Coelho Veronika Ölmek İstiyor Can Yayınları": "Felsefe",
    "Rıfat Ilgaz - Halime Kaptan (Çınar Yay.)": "Macera",
    "Stephen Hawking - Büyük Tasarım": "Bilim",
    "Stephen King Hayvan Mezarlığı Altın Kitaplar": "Macera",
    "Tolstoy - İvan İlyiç'in Ölümü": "Felsefe",
    "Zülfü Livaneli Konstantiniyye Oteli Doğan Kitap": "Tarih",
    "Çavdar Tarlasında Çocuklar - Jerome David Salinger": "Dram",
    "İLBER-ORTAYLI-Tarihin-İzinde": "Tarih",
}


def build_seed_books() -> list[Book]:
    """Create seed books from cleaned_texts with correct categories."""
    seeds: list[Book] = []
    repo_root = Path(__file__).resolve().parents[1]
    books_dir = repo_root / "cleaned_texts"

    if books_dir.exists():
        for txt_file in sorted(books_dir.glob("*.txt")):
            seeds.append(
                Book(
                    title=txt_file.stem,
                    file_path=str(txt_file.resolve()),
                    source="general",
                    category=BOOK_CATEGORIES.get(txt_file.stem, "Genel"),
                )
            )
    return seeds


# ── Helpers ──
def _stat_card(label: str, value: str, icon: str) -> ft.Container:
    return ft.Container(
        bgcolor=CARD_BG,
        border_radius=12,
        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        border=ft.Border.all(1, BORDER),
        expand=True,
        content=ft.Row(
            [
                ft.Icon(icon, color=PRIMARY, size=22),
                ft.Column(
                    [
                        ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(label, size=11, color=TEXT_SECONDARY),
                    ],
                    spacing=0,
                ),
            ],
            spacing=10,
        ),
    )


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
async def main(page: ft.Page) -> None:
    """Flet application entry point."""
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = app_theme()
    page.padding = 0
    page.window.width = 430
    page.window.height = 880
    page.bgcolor = SURFACE

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    db = DatabaseManager(DB_FILE)
    db.seed_general_books(build_seed_books())
    backend_adapter = BackendAdapter()

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    # Load initial language
    lang = get_ui_language()

    # ── Snackbar helper ──
    def show_snackbar(msg: str, bg: str = PRIMARY) -> None:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=bg,
        )
        page.snack_bar.open = True
        page.update()

    # ── UI State / widgets ──
    search_field = ft.TextField(
        hint_text=t("search_hint", lang),
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_radius=24,
        height=46,
        text_size=13,
        filled=True,
        bgcolor="#FFFFFF",
        border_color=BORDER,
        focused_border_color=PRIMARY,
        focused_border_width=1.5,
        content_padding=ft.Padding(left=16, right=16, top=8, bottom=8),
        on_change=lambda _: refresh_library_and_update(),
    )
    general_list = ft.ListView(expand=True, spacing=6)
    personal_list = ft.ListView(expand=True, spacing=6)

    # translatable section titles
    general_lib_header = ft.Text(t("general_library", lang), weight=ft.FontWeight.W_600, size=16, color=PRIMARY)
    personal_lib_header = ft.Text(t("personal_library", lang), weight=ft.FontWeight.W_600, size=16, color=PRIMARY)

    # ── Refresh logic ──
    def refresh_library() -> None:
        current_lang = get_ui_language()
        query = (search_field.value or "").lower()
        general_books = db.list_books(source="general")
        personal_books = db.list_books(source="personal")

        if query:
            general_books = [b for b in general_books if query in b.title.lower() or query in t(f"cat_{b.category}", current_lang).lower()]
            personal_books = [b for b in personal_books if query in b.title.lower() or query in t(f"cat_{b.category}", current_lang).lower()]

        general_list.controls = (
            [build_book_tile(b) for b in general_books]
            if general_books
            else [_empty(ft.Icons.LIBRARY_BOOKS, t("no_results", current_lang) if query else t("library_empty", current_lang))]
        )
        personal_list.controls = (
            [build_book_tile(b, deletable=True) for b in personal_books]
            if personal_books
            else [_empty(ft.Icons.ADD_CIRCLE_OUTLINE, t("no_books_added", current_lang))]
        )

    def refresh_library_and_update() -> None:
        refresh_library()
        page.update()

    def refresh_profile() -> None:
        current_lang = get_ui_language()
        personal_books = db.list_books(source="personal")
        summarized = sum(1 for b in personal_books if b.summary)
        profile = backend_adapter.get_user_profile(personal_books)

        stats_row.controls = [
            _stat_card(t("stat_book", current_lang), str(len(personal_books)), ft.Icons.MENU_BOOK),
            _stat_card(t("stat_summary", current_lang), str(summarized), ft.Icons.SUMMARIZE),
        ]

        if profile:
            # Map dynamic user profile character names
            char_key = f"char_{profile.character_name.replace(' ', '_')}"
            translated_char_name = t(char_key, current_lang)
            translated_char_desc = t(f"{char_key}_desc", current_lang)
            
            # Fallbacks
            if translated_char_name == char_key:
                translated_char_name = profile.character_name
            if translated_char_desc == f"{char_key}_desc":
                translated_char_desc = profile.description

            profile_title.value = translated_char_name
            profile_desc.value = translated_char_desc

            category_bars.controls = []
            if profile.category_distribution:
                for cat, pct in sorted(
                    profile.category_distribution.items(), key=lambda x: -x[1]
                ):
                    color = CAT_COLORS.get(cat, "#607D8B")
                    category_bars.controls.append(
                        ft.Row(
                            [
                                ft.Text(t(f"cat_{cat}", current_lang), width=80, size=12),
                                ft.ProgressBar(
                                    value=pct / 100, width=160,
                                    color=color, bgcolor="#E8E8EE",
                                ),
                                ft.Text(f"%{pct}", size=12, color=TEXT_SECONDARY),
                            ],
                            spacing=8,
                        )
                    )

            general_books = db.list_books(source="general")
            recs = backend_adapter.get_recommendations(profile, general_books)
            recommendations_list.controls = (
                [build_book_tile(b) for b in recs]
                if recs
                else [_empty(ft.Icons.RECOMMEND, t("no_recs", current_lang))]
            )

    def refresh_all() -> None:
        refresh_library()
        refresh_profile()
        page.update()

    # ── Upload logic ──
    async def take_photo_and_summarize(_: ft.ControlEvent) -> None:
        current_lang = get_ui_language()
        files = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg"],
        )
        if not files:
            return

        picked = files[0]
        ext = Path(picked.name).suffix.lower()
        target = UPLOADS_DIR / f"photo_{uuid.uuid4().hex[:8]}{ext}"

        if picked.path:
            shutil.copy2(picked.path, target)
        elif getattr(picked, "bytes", None):
            target.write_bytes(picked.bytes)
        else:
            upload_status.value = t("could_not_read_photo", current_lang)
            page.update()
            return

        new_book = Book(
            title=f"Photo ({target.name[:5]})",
            file_path=str(target),
            source="personal",
            category="Genel",
        )
        db.add_book(new_book)
        refresh_all()
        
        # Navigate back to library and open dialog
        page.navigation_bar.selected_index = 0
        main_content.content = library_content
        open_book(new_book)
        page.update()

    async def pick_file(_: ft.ControlEvent) -> None:
        current_lang = get_ui_language()
        files = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["pdf", "png", "jpg", "jpeg"],
        )
        if not files:
            upload_status.value = t("file_selection_cancelled", current_lang)
            page.update()
            return

        picked = files[0]
        ext = Path(picked.name).suffix.lower()

        if picked.path:
            file_path_input.value = picked.path
            upload_status.value = t("selected_file", current_lang, picked.name)
        else:
            file_bytes = getattr(picked, "bytes", None)
            if file_bytes:
                target = UPLOADS_DIR / f"{Path(picked.name).stem}_{uuid.uuid4().hex[:8]}{ext}"
                target.write_bytes(file_bytes)
                file_path_input.value = str(target)
                upload_status.value = t("selected_file", current_lang, picked.name)
            else:
                upload_status.value = t("file_could_not_be_read", current_lang)
        page.update()

    def handle_upload(_: ft.ControlEvent) -> None:
        current_lang = get_ui_language()
        source_path = (file_path_input.value or "").strip().strip('"')
        if not source_path:
            show_snackbar(t("enter_valid_path", current_lang), ERROR)
            return

        source = Path(source_path)
        if source.suffix.lower() not in [".pdf", ".jpg", ".jpeg", ".png"]:
            show_snackbar(t("only_pdf_images", current_lang), ERROR)
            return

        try:
            target = UPLOADS_DIR / f"{source.stem}_{uuid.uuid4().hex[:8]}{source.suffix.lower()}"
            shutil.copy2(source, target)
        except FileNotFoundError:
            show_snackbar(t("file_not_found", current_lang, source.name), ERROR)
            return
        except PermissionError:
            show_snackbar(t("file_access_denied", current_lang), ERROR)
            return
        except Exception as err:
            show_snackbar(t("file_copy_error", current_lang, err), ERROR)
            return

        new_book = Book(
            title=source.stem,
            file_path=str(target),
            source="personal",
            category=backend_adapter.categorize_title(source.stem),
        )
        db.add_book(new_book)

        file_path_input.value = ""
        upload_status.value = t("no_file_selected", current_lang)
        show_snackbar(t("added_to_library_success", current_lang, source.name), SUCCESS)
        refresh_all()

    # ── Upload tab elements ──
    upload_title = ft.Text(t("upload_pdf_image", lang), size=18, weight=ft.FontWeight.BOLD)
    upload_desc = ft.Text(t("upload_desc", lang), color=TEXT_SECONDARY, size=13)
    
    choose_file_btn = ft.Button(
        t("choose_file", lang),
        icon=ft.Icons.FOLDER_OPEN_ROUNDED,
        on_click=pick_file,
        style=ft.ButtonStyle(
            color=PRIMARY,
            bgcolor="#E0E7FF", # Modern Slate/Indigo soft tint
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        expand=True,
    )
    
    take_photo_btn = ft.Button(
        t("take_photo", lang),
        icon=ft.Icons.CAMERA_ALT_ROUNDED,
        on_click=take_photo_and_summarize,
        style=ft.ButtonStyle(
            color=SECONDARY,
            bgcolor="#FCE7F3", # Modern Rose soft tint
            elevation=0,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        expand=True,
    )

    upload_status = ft.Text(t("no_file_selected", lang), color=TEXT_SECONDARY, size=13)
    file_path_input = ft.TextField(
        label=t("file_path", lang),
        hint_text="e.g., C:/.../book.pdf or .jpg",
        prefix_icon=ft.Icons.INSERT_DRIVE_FILE_OUTLINED,
        border_color=BORDER,
        focused_border_color=PRIMARY,
        focused_border_width=1.5,
        border_radius=12,
        filled=True,
        bgcolor="#F8FAFC",
        focused_bgcolor="#FFFFFF",
    )
    
    add_to_lib_btn = ft.FilledButton(
        t("add_to_library", lang),
        icon=ft.Icons.ADD_ROUNDED,
        on_click=handle_upload,
        style=ft.ButtonStyle(
            bgcolor=PRIMARY,
            color="white",
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        height=48,
        width=float("inf"),
    )

    # Profile tab
    profile_title = ft.Text(t("profile_info", lang), size=20, weight=ft.FontWeight.BOLD)
    profile_desc = ft.Text(t("not_enough_data", lang), color=TEXT_SECONDARY)
    stats_row = ft.Row(spacing=10)
    category_bars = ft.Column(spacing=6)
    recommendations_list = ft.ListView(expand=True, spacing=6)
    profile_rec_header = ft.Text(t("recommended_for_you", lang), weight=ft.FontWeight.BOLD, size=15)

    # ── Book tile builder ──
    def open_book(book: Book) -> None:
        def _save_summary(book_id: str, summary: str, summary_type: str = "Orta") -> None:
            db.update_summary(book_id, summary, summary_type)
            refresh_library()
        if book.summary:
            dialog = build_summary_dialog(page, book)
        else:
            dialog = build_book_dialog(page, book, backend_adapter, _save_summary)
        page.show_dialog(dialog)

    def delete_book(book: Book) -> None:
        current_lang = get_ui_language()
        db.delete_book(book.id)
        show_snackbar(t("deleted_success", current_lang, book.title), ERROR)
        refresh_all()

    def build_book_tile(book: Book, deletable: bool = False) -> ft.Control:
        current_lang = get_ui_language()
        cat_color = CAT_COLORS.get(book.category, "#607D8B")
        cat_icon = CAT_ICONS.get(book.category, ft.Icons.AUTO_STORIES)
        parts = [t(f"cat_{book.category}", current_lang)]
        if book.summary:
            parts.append(t("summary_available", current_lang))

        trailing_controls: list[ft.Control] = []
        if deletable:
            trailing_controls.append(
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_color=ERROR,
                    icon_size=18,
                    on_click=lambda _, b=book: delete_book(b),
                    tooltip="Sil" if current_lang == "tr" else "Delete",
                )
            )
        trailing_controls.append(ft.Icon(ft.Icons.CHEVRON_RIGHT, color=TEXT_SECONDARY))

        return ft.Card(
            elevation=1,
            content=ft.Container(
                padding=ft.Padding(left=2, right=2, top=0, bottom=0),
                content=ft.ListTile(
                    leading=ft.CircleAvatar(
                        content=ft.Icon(cat_icon, color="white", size=18),
                        bgcolor=cat_color,
                        radius=18,
                    ),
                    title=ft.Text(
                        book.title, max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        weight=ft.FontWeight.W_500, size=14,
                    ),
                    subtitle=ft.Text(" · ".join(parts), color=TEXT_SECONDARY, size=11),
                    trailing=ft.Row(trailing_controls, spacing=0, tight=True),
                    on_click=lambda _, b=book: open_book(b),
                ),
            ),
        )

    # ── Empty state helper ──
    def _empty(icon: str, text: str) -> ft.Control:
        return ft.Container(
            padding=30,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                [
                    ft.Icon(icon, color=TEXT_SECONDARY, size=40),
                    ft.Text(text, color=TEXT_SECONDARY, size=13),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
        )

    # ── Settings Dialog ──
    def open_settings_dialog() -> None:
        current_lang = get_ui_language()
        current_api_key = get_mistral_api_key()

        api_key_field = ft.TextField(
            label=t("api_key_label", current_lang),
            hint_text=t("api_key_hint", current_lang),
            value=current_api_key,
            password=True,
            can_reveal_password=True,
            border_radius=12,
        )

        lang_dropdown = ft.Dropdown(
            label=t("language_label", current_lang),
            value=current_lang,
            options=[
                ft.dropdown.Option("tr", "Türkçe (TR)"),
                ft.dropdown.Option("en", "English (EN)"),
            ],
            border_radius=12,
        )

        def save_click(_: ft.ControlEvent) -> None:
            key_val = api_key_field.value.strip()
            if not key_val:
                show_snackbar(t("api_key_empty", current_lang), ERROR)
                return

            save_settings({
                "mistral_api_key": key_val,
                "language": lang_dropdown.value,
            })

            # Reload Adapter with new api key
            backend_adapter.reload()

            # Close Settings Dialog
            page.pop_dialog()

            # Re-apply translations across the UI
            apply_translations()

            # Refresh all content components
            refresh_all()

            # Display localized success banner
            new_lang = lang_dropdown.value
            show_snackbar(t("settings_saved", new_lang), SUCCESS)

        settings_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(t("settings", current_lang), weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=350,
                height=180,
                content=ft.Column([
                    api_key_field,
                    lang_dropdown,
                ], spacing=12),
            ),
            actions=[
                ft.TextButton(t("cancel", current_lang), on_click=lambda _: page.pop_dialog()),
                ft.Button(t("save", current_lang), on_click=save_click, bgcolor=PRIMARY, color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(settings_dialog)

    # ── UI Translations Applier ──
    def apply_translations() -> None:
        current_lang = get_ui_language()

        # Update controls
        search_field.hint_text = t("search_hint", current_lang)
        general_lib_header.value = t("general_library", current_lang)
        personal_lib_header.value = t("personal_library", current_lang)
        upload_title.value = t("upload_pdf_image", current_lang)
        upload_desc.value = t("upload_desc", current_lang)
        choose_file_btn.text = t("choose_file", current_lang)
        take_photo_btn.text = t("take_photo", current_lang)
        file_path_input.label = t("file_path", current_lang)
        add_to_lib_btn.text = t("add_to_library", current_lang)

        # Reset select status translation
        if upload_status.value in [
            "No file selected yet.", "Henüz dosya seçilmedi.",
            t("no_file_selected", "tr"), t("no_file_selected", "en")
        ]:
            upload_status.value = t("no_file_selected", current_lang)

        profile_rec_header.value = t("recommended_for_you", current_lang)

        # Navigation destinations
        page.navigation_bar.destinations[0].label = t("library", current_lang)
        page.navigation_bar.destinations[1].label = t("upload", current_lang)
        page.navigation_bar.destinations[2].label = t("profile", current_lang)

        # AppBar Action tooltip update
        if page.appbar and page.appbar.actions:
            page.appbar.actions[0].tooltip = t("settings", current_lang)

        page.update()

    # ══════════════════════════
    #  UI LAYOUT
    # ══════════════════════════

    # ── AppBar ──
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.AUTO_STORIES_ROUNDED, color=PRIMARY, size=26),
        title=ft.Text(
            APP_NAME,
            weight=ft.FontWeight.W_800,
            color=PRIMARY,
            size=20,
        ),
        bgcolor=SURFACE,
        elevation=0,
        center_title=False,
        actions=[
            ft.IconButton(
                ft.Icons.SETTINGS_ROUNDED,
                icon_color=PRIMARY,
                icon_size=24,
                tooltip=t("settings", lang),
                on_click=lambda _: open_settings_dialog(),
            )
        ]
    )

    # ── Library tab ──
    library_content = ft.Column(
        [
            ft.Container(padding=ft.Padding(left=16, right=16, top=10, bottom=0), content=search_field),
            ft.Container(
                padding=ft.Padding(left=16, right=16, top=0, bottom=0),
                content=general_lib_header,
            ),
            ft.Container(
                height=230, margin=ft.Margin(left=12, right=12, top=0, bottom=0),
                border=ft.Border.all(1, BORDER), border_radius=16,
                padding=8, bgcolor=CARD_BG,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=12,
                    color="#0D000000",
                    offset=ft.Offset(0, 4),
                ),
                content=general_list,
            ),
            ft.Container(
                padding=ft.Padding(left=16, right=16, top=0, bottom=0),
                content=personal_lib_header,
            ),
            ft.Container(
                height=230, margin=ft.Margin(left=12, right=12, top=0, bottom=0),
                border=ft.Border.all(1, BORDER), border_radius=16,
                padding=8, bgcolor=CARD_BG,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=12,
                    color="#0D000000",
                    offset=ft.Offset(0, 4),
                ),
                content=personal_list,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )

    # ── Upload tab ──
    upload_content = ft.Container(
        padding=ft.Padding(left=20, right=20, top=16, bottom=16),
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Column([
                        upload_title,
                        upload_desc,
                    ], spacing=4),
                    margin=ft.Margin(0, 0, 0, 6)
                ),
                ft.Container(
                    bgcolor=CARD_BG,
                    padding=20,
                    border_radius=20,
                    border=ft.Border.all(1, BORDER),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=16,
                        color="#0D000000",
                        offset=ft.Offset(0, 6),
                    ),
                    content=ft.Column([
                        # Sleek visual drag & drop indicator area
                        ft.Container(
                            alignment=ft.Alignment(0, 0),
                            padding=ft.Padding(20, 24, 20, 24),
                            border=ft.Border.all(1, "#E0E7FF"), # Soft Indigo border
                            border_radius=14,
                            bgcolor="#F5F6FE", # Very soft Indigo/Slate tint
                            content=ft.Column([
                                ft.Icon(ft.Icons.CLOUD_UPLOAD_ROUNDED, color=PRIMARY, size=46),
                                ft.Text(
                                    t("choose_file", lang) + " / " + t("take_photo", lang),
                                    weight=ft.FontWeight.BOLD,
                                    size=14,
                                    color=TEXT_PRIMARY,
                                ),
                                ft.Text(
                                    "PDF, PNG, JPG, JPEG",
                                    size=11,
                                    color=TEXT_SECONDARY,
                                )
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6)
                        ),
                        ft.Container(height=2),
                        ft.Row(
                            [
                                choose_file_btn,
                                take_photo_btn,
                            ],
                            spacing=12,
                        ),
                        ft.Container(height=2),
                        file_path_input,
                        ft.Container(height=2),
                        add_to_lib_btn,
                    ], spacing=16)
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color=TEXT_SECONDARY, size=15),
                        upload_status,
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                    padding=10,
                    alignment=ft.Alignment(0, 0),
                )
            ],
            spacing=16,
        ),
    )

    # ── Profile tab ──
    profile_content = ft.Column(
        [
            ft.Container(
                padding=ft.Padding(left=20, right=20, top=8, bottom=8),
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.CircleAvatar(
                                    content=ft.Icon(ft.Icons.PERSON, color="white", size=28),
                                    bgcolor=PRIMARY, radius=28,
                                ),
                                ft.Column(
                                    [profile_title, profile_desc],
                                    spacing=2,
                                ),
                            ],
                            spacing=14,
                        ),
                        ft.Container(height=6),
                        stats_row,
                        ft.Container(height=4),
                        category_bars,
                    ],
                    spacing=6,
                ),
            ),
            ft.Divider(),
            ft.Container(
                padding=ft.Padding(left=20, right=20, top=0, bottom=0),
                content=profile_rec_header,
            ),
            ft.Container(
                height=320, margin=ft.Margin(left=12, right=12, top=0, bottom=0),
                border=ft.Border.all(1, BORDER), border_radius=16,
                padding=8, bgcolor=CARD_BG,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=12,
                    color="#0D000000",
                    offset=ft.Offset(0, 4),
                ),
                content=recommendations_list,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=8,
    )

    # ── Navigation ──
    main_content = ft.Container(content=library_content, expand=True)

    def on_nav_change(e: ft.ControlEvent) -> None:
        idx = e.control.selected_index
        if idx == 0:
            main_content.content = library_content
        elif idx == 1:
            main_content.content = upload_content
        else:
            main_content.content = profile_content
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.LIBRARY_BOOKS_ROUNDED, label=t("library", lang)),
            ft.NavigationBarDestination(icon=ft.Icons.UPLOAD_FILE_ROUNDED, label=t("upload", lang)),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON_ROUNDED, label=t("profile", lang)),
        ],
        on_change=on_nav_change,
        bgcolor=CARD_BG,
        elevation=0,
    )

    page.add(ft.Column([main_content], expand=True, spacing=0))
    
    # Initialize UI elements state
    apply_translations()
    refresh_all()


if __name__ == "__main__":
    ft.run(main)
