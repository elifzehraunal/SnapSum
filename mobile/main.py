"""SnapSum – Flet mobile application."""

from __future__ import annotations

from pathlib import Path
import shutil
import uuid

import flet as ft

from app.config import APP_NAME, UPLOADS_DIR, DB_FILE
from app.data.database import DatabaseManager
from app.models import Book
from app.services.backend_adapter import BackendAdapter
from app.ui.book_detail_view import build_book_dialog
from app.ui.theme import (
    app_theme, PRIMARY, SECONDARY, SURFACE, CARD_BG,
    TEXT_SECONDARY, SUCCESS, ERROR, CAT_COLORS, CAT_ICONS,
)

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
        border=ft.Border.all(1, "#E8E8EE"),
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
def main(page: ft.Page) -> None:
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
        hint_text="Kitap veya kategori ara…",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=12,
        height=44,
        text_size=14,
        on_change=lambda _: refresh_library_and_update(),
    )
    general_list = ft.ListView(expand=True, spacing=6)
    personal_list = ft.ListView(expand=True, spacing=6)

    # Upload tab
    upload_status = ft.Text("Henüz dosya seçilmedi.", color=TEXT_SECONDARY, size=13)
    file_path_input = ft.TextField(
        label="Dosya Yolu",
        hint_text="Örn: /Users/.../kitap.pdf veya .jpg",
        border_radius=12,
    )

    # Profile tab
    profile_title = ft.Text("Profil Bilgisi", size=20, weight=ft.FontWeight.BOLD)
    profile_desc = ft.Text("Henüz yeterli veri yok.", color=TEXT_SECONDARY)
    stats_row = ft.Row(spacing=10)
    category_bars = ft.Column(spacing=6)
    recommendations_list = ft.ListView(expand=True, spacing=6)

    # ── Book tile builder ──
    def open_book(book: Book) -> None:
        dialog = build_book_dialog(page, book, backend_adapter, db.update_summary)
        page.show_dialog(dialog)

    def delete_book(book: Book) -> None:
        db.delete_book(book.id)
        show_snackbar(f"'{book.title}' silindi.", ERROR)
        refresh_all()

    def build_book_tile(book: Book, deletable: bool = False) -> ft.Control:
        cat_color = CAT_COLORS.get(book.category, "#607D8B")
        cat_icon = CAT_ICONS.get(book.category, ft.Icons.AUTO_STORIES)
        parts = [book.category]
        if book.summary:
            parts.append("✓ Özet mevcut")

        trailing_controls: list[ft.Control] = []
        if deletable:
            trailing_controls.append(
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_color=ERROR,
                    icon_size=18,
                    on_click=lambda _, b=book: delete_book(b),
                    tooltip="Sil",
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

    # ── Refresh logic ──
    def refresh_library() -> None:
        query = (search_field.value or "").lower()
        general_books = db.list_books(source="general")
        personal_books = db.list_books(source="personal")

        if query:
            general_books = [b for b in general_books if query in b.title.lower() or query in b.category.lower()]
            personal_books = [b for b in personal_books if query in b.title.lower() or query in b.category.lower()]

        general_list.controls = (
            [build_book_tile(b) for b in general_books]
            if general_books
            else [_empty(ft.Icons.LIBRARY_BOOKS, "Sonuç bulunamadı" if query else "Kütüphane boş")]
        )
        personal_list.controls = (
            [build_book_tile(b, deletable=True) for b in personal_books]
            if personal_books
            else [_empty(ft.Icons.ADD_CIRCLE_OUTLINE, "Henüz kitap eklenmedi")]
        )

    def refresh_library_and_update() -> None:
        refresh_library()
        page.update()

    def refresh_profile() -> None:
        personal_books = db.list_books(source="personal")
        summarized = sum(1 for b in personal_books if b.summary)
        profile = backend_adapter.get_user_profile(personal_books)

        stats_row.controls = [
            _stat_card("Kitap", str(len(personal_books)), ft.Icons.MENU_BOOK),
            _stat_card("Özet", str(summarized), ft.Icons.SUMMARIZE),
        ]

        if profile:
            profile_title.value = profile.character_name
            profile_desc.value = profile.description

            category_bars.controls = []
            if profile.category_distribution:
                for cat, pct in sorted(
                    profile.category_distribution.items(), key=lambda x: -x[1]
                ):
                    color = CAT_COLORS.get(cat, "#607D8B")
                    category_bars.controls.append(
                        ft.Row(
                            [
                                ft.Text(cat, width=60, size=12),
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
                else [_empty(ft.Icons.RECOMMEND, "Henüz öneri yok")]
            )

    def refresh_all() -> None:
        refresh_library()
        refresh_profile()
        page.update()

    # ── Upload logic ──
    def apply_input_path(_: ft.ControlEvent) -> None:
        path_value = (file_path_input.value or "").strip().strip('"')
        if not path_value:
            upload_status.value = "Lütfen bir dosya yolu girin."
        else:
            upload_status.value = f"Seçilen dosya: {Path(path_value).name}"
        page.update()

    async def pick_file(_: ft.ControlEvent) -> None:
        files = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["pdf", "png", "jpg", "jpeg"],
            with_data=True,
        )
        if not files:
            upload_status.value = "Dosya seçimi iptal edildi."
            page.update()
            return

        picked = files[0]
        ext = Path(picked.name).suffix.lower()

        if picked.path:
            file_path_input.value = picked.path
            upload_status.value = f"Seçilen dosya: {picked.name}"
            page.update()
            return

        file_bytes = getattr(picked, "bytes", None)
        if file_bytes:
            target = UPLOADS_DIR / f"{Path(picked.name).stem}_{uuid.uuid4().hex[:8]}{ext}"
            target.write_bytes(file_bytes)
            file_path_input.value = str(target)
            upload_status.value = f"Seçilen dosya: {picked.name}"
        else:
            upload_status.value = "Dosya okunamadı."
        page.update()

    def handle_upload(_: ft.ControlEvent) -> None:
        source_path = (file_path_input.value or "").strip().strip('"')
        if not source_path:
            show_snackbar("Lütfen geçerli bir dosya yolu girin.", WARNING)
            return

        source = Path(source_path)
        if source.suffix.lower() not in [".pdf", ".jpg", ".jpeg", ".png"]:
            show_snackbar("Sadece PDF veya Resim dosyaları destekleniyor.", WARNING)
            return

        try:
            target = UPLOADS_DIR / f"{source.stem}_{uuid.uuid4().hex[:8]}{source.suffix.lower()}"
            shutil.copy2(source, target)
        except FileNotFoundError:
            show_snackbar(f"Dosya bulunamadı: {source.name}", ERROR)
            return
        except PermissionError:
            show_snackbar("Dosya erişim izni reddedildi.", ERROR)
            return
        except Exception as err:
            show_snackbar(f"Dosya kopyalama hatası: {err}", ERROR)
            return

        new_book = Book(
            title=source.stem,
            file_path=str(target),
            source="personal",
            category=backend_adapter.categorize_title(source.stem),
        )
        db.add_book(new_book)

        file_path_input.value = ""
        upload_status.value = "Henüz dosya seçilmedi."
        show_snackbar(f"✓ '{source.name}' kütüphaneye eklendi!", SUCCESS)
        refresh_all()

    # ══════════════════════════
    #  UI LAYOUT
    # ══════════════════════════

    # ── AppBar ──
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.AUTO_STORIES, color="white", size=28),
        title=ft.Text(APP_NAME, weight=ft.FontWeight.BOLD, color="white"),
        bgcolor=PRIMARY,
        center_title=False,
    )

    # ── Library tab ──
    library_content = ft.Column(
        [
            ft.Container(padding=ft.Padding(left=16, right=16, top=0, bottom=0), content=search_field),
            ft.Container(
                padding=ft.Padding(left=16, right=16, top=0, bottom=0),
                content=ft.Text("Genel Kütüphane", weight=ft.FontWeight.BOLD, size=15),
            ),
            ft.Container(
                height=230, margin=ft.Margin(left=12, right=12, top=0, bottom=0),
                border=ft.Border.all(1, "#E8E8EE"), border_radius=12,
                padding=8, bgcolor=CARD_BG,
                content=general_list,
            ),
            ft.Container(
                padding=ft.Padding(left=16, right=16, top=0, bottom=0),
                content=ft.Text("Şahsi Kütüphanem", weight=ft.FontWeight.BOLD, size=15),
            ),
            ft.Container(
                height=230, margin=ft.Margin(left=12, right=12, top=0, bottom=0),
                border=ft.Border.all(1, "#E8E8EE"), border_radius=12,
                padding=8, bgcolor=CARD_BG,
                content=personal_list,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )

    # ── Upload tab ──
    upload_content = ft.Container(
        padding=ft.Padding(left=20, right=20, top=10, bottom=10),
        content=ft.Column(
            [
                ft.Text("PDF veya Resim Yükle", size=18, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Metin tabanlı PDF veya fotoğraf (OCR) yükleyerek kütüphanenize ekleyin.",
                    color=TEXT_SECONDARY, size=13,
                ),
                ft.Row(
                    [
                        ft.OutlinedButton("Dosya Seç", icon=ft.Icons.FOLDER_OPEN, on_click=pick_file),
                        ft.OutlinedButton("Yolu Onayla", icon=ft.Icons.CHECK, on_click=apply_input_path),
                    ]
                ),
                file_path_input,
                ft.Button("Kütüphaneye Ekle", icon=ft.Icons.ADD, on_click=handle_upload),
                upload_status,
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
                content=ft.Text("Sizin İçin Önerilenler", weight=ft.FontWeight.BOLD, size=15),
            ),
            ft.Container(
                height=320, margin=ft.Margin(left=12, right=12, top=0, bottom=0),
                border=ft.Border.all(1, "#E8E8EE"), border_radius=12,
                padding=8, bgcolor=CARD_BG,
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
            ft.NavigationBarDestination(icon=ft.Icons.LIBRARY_BOOKS, label="Kütüphane"),
            ft.NavigationBarDestination(icon=ft.Icons.UPLOAD_FILE, label="Yükle"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Profilim"),
        ],
        on_change=on_nav_change,
    )

    page.add(ft.Column([main_content], expand=True, spacing=0))
    refresh_all()


if __name__ == "__main__":
    ft.run(main)
