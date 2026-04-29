"""SnapSum - Flet mobile starter application."""

from __future__ import annotations

from pathlib import Path
import shutil
import uuid
import random

import flet as ft

from app.config import APP_NAME, UPLOADS_DIR
from app.data.repository import BookRepository
from app.models import Book
from app.services.backend_adapter import BackendAdapter
from app.ui.book_detail_view import build_book_dialog
from app.ui.theme import app_theme


def build_seed_books() -> list[Book]:
    """Create placeholder books using real PDFs from the books directory."""
    seeds: list[Book] = []
    categories = ["Bilim", "Tarih", "Dram", "Macera", "Felsefe", "Genel"]
    
    repo_root = Path(__file__).resolve().parents[1]
    books_dir = repo_root / "cleaned_texts"
    
    if books_dir.exists():
        for txt_file in books_dir.glob("*.txt"):
            seeds.append(
                Book(
                    title=txt_file.stem,
                    file_path=str(txt_file.resolve()),
                    source="general",
                    category=random.choice(categories),
                )
            )
    return seeds


def main(page: ft.Page) -> None:
    """Flet application entry point."""
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = app_theme()
    page.padding = 16
    page.window.width = 430
    page.window.height = 880

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    repository = BookRepository()
    repository.seed_general_books(build_seed_books())
    backend_adapter = BackendAdapter()
    
    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    # --- UI Elements ---
    general_list = ft.ListView(expand=True, spacing=8)
    personal_list = ft.ListView(expand=True, spacing=8)
    
    # Upload tab states
    upload_status = ft.Text("Henüz dosya seçilmedi.")
    selected_file = {"path": None, "type": None}
    file_path_input = ft.TextField(
        label="Dosya Yolu",
        hint_text=r"Örn: C:\...\kitap.pdf veya .jpg",
    )

    # Profile tab states
    profile_title = ft.Text("Profil Bilgisi", theme_style=ft.TextThemeStyle.HEADLINE_SMALL)
    profile_desc = ft.Text("Henüz yeterli veri yok.")
    recommendations_list = ft.ListView(expand=True, spacing=8)

    def open_book(book: Book) -> None:
        dialog = build_book_dialog(page, book, backend_adapter, repository.update_summary)
        page.show_dialog(dialog)

    def build_book_tile(book: Book) -> ft.Control:
        subtitle = f"Kategori: {book.category} | {'Özet mevcut' if book.summary else 'Özet yok'}"
        return ft.Card(
            content=ft.ListTile(
                leading=ft.Icon(ft.Icons.BOOKMARK_OUTLINE),
                title=ft.Text(book.title),
                subtitle=ft.Text(subtitle),
                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                on_click=lambda _: open_book(book),
            )
        )

    def refresh_library() -> None:
        general_books = repository.list_books(source="general")
        personal_books = repository.list_books(source="personal")
        general_list.controls = [build_book_tile(book) for book in general_books]
        personal_list.controls = [build_book_tile(book) for book in personal_books]

    def refresh_profile() -> None:
        personal_books = repository.list_books(source="personal")
        profile = backend_adapter.get_user_profile(personal_books)
        if profile:
            profile_title.value = f"Karakterin: {profile.character_name}"
            profile_desc.value = profile.description
            
            general_books = repository.list_books(source="general")
            recs = backend_adapter.get_recommendations(profile, general_books)
            recommendations_list.controls = [build_book_tile(b) for b in recs]

    def refresh_all() -> None:
        refresh_library()
        refresh_profile()
        page.update()

    # --- Upload Logic ---
    def apply_input_path(_: ft.ControlEvent) -> None:
        path_value = (file_path_input.value or "").strip().strip('"')
        if not path_value:
            upload_status.value = "Lütfen bir dosya yolu girin."
            selected_file["path"] = None
        else:
            selected_file["path"] = path_value
            ext = Path(path_value).suffix.lower()
            selected_file["type"] = "pdf" if ext == ".pdf" else "image"
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
            selected_file["path"] = None
            page.update()
            return

        picked = files[0]
        ext = Path(picked.name).suffix.lower()
        file_type = "pdf" if ext == ".pdf" else "image"
        
        if picked.path:
            selected_file["path"] = picked.path
            selected_file["type"] = file_type
            file_path_input.value = picked.path
            upload_status.value = f"Seçilen dosya: {picked.name}"
            page.update()
            return

        file_bytes = getattr(picked, "bytes", None)
        if file_bytes:
            target = UPLOADS_DIR / f"{Path(picked.name).stem}_{uuid.uuid4().hex[:8]}{ext}"
            target.write_bytes(file_bytes)
            selected_file["path"] = str(target)
            selected_file["type"] = file_type
            file_path_input.value = str(target)
            upload_status.value = f"Seçilen dosya: {picked.name}"
        else:
            upload_status.value = "Dosya okunamadı."
            selected_file["path"] = None
        page.update()

    def handle_upload(_: ft.ControlEvent) -> None:
        source_path = (file_path_input.value or "").strip().strip('"')
        if not source_path:
            upload_status.value = "Lütfen geçerli bir dosya yolu girin."
            page.update()
            return

        source = Path(source_path)
        if source.suffix.lower() not in [".pdf", ".jpg", ".jpeg", ".png"]:
            upload_status.value = "Sadece PDF veya Resim dosyaları destekleniyor."
            page.update()
            return

        target = UPLOADS_DIR / f"{source.stem}_{uuid.uuid4().hex[:8]}{source.suffix.lower()}"
        shutil.copy2(source, target)
        
        new_book = Book(
            title=source.stem, 
            file_path=str(target), 
            source="personal",
            category=backend_adapter.categorize_title(source.stem)
        )
        repository.add_book(new_book)

        upload_status.value = f"Yüklendi: {source.name}"
        selected_file["path"] = None
        refresh_all()

    # --- UI Layout ---
    library_content = ft.Column(
        [
            ft.Text("Genel Kütüphane", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Container(
                height=250, border=ft.Border.all(1, "#D0D0D0"), border_radius=10, padding=10,
                content=general_list,
            ),
            ft.Text("Şahsi Kütüphanem", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Container(
                height=250, border=ft.Border.all(1, "#D0D0D0"), border_radius=10, padding=10,
                content=personal_list,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )

    upload_content = ft.Container(
        padding=10,
        content=ft.Column(
            [
                ft.Text("PDF veya Resim Yükle", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Text("Metin tabanlı PDF veya fotoğraf (OCR) yükleyerek kütüphanenize ekleyin."),
                ft.Row(
                    [
                        ft.OutlinedButton("Dosya Seç", icon=ft.Icons.FOLDER_OPEN, on_click=pick_file),
                        ft.OutlinedButton("Yolu Onayla", icon=ft.Icons.CHECK, on_click=apply_input_path),
                    ]
                ),
                file_path_input,
                ft.ElevatedButton("Kütüphaneye Ekle", icon=ft.Icons.ADD, on_click=handle_upload),
                upload_status,
            ],
            spacing=16,
        ),
    )

    profile_content = ft.Column(
        [
            profile_title,
            profile_desc,
            ft.Divider(),
            ft.Text("Sizin İçin Önerilenler", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Container(
                height=400, border=ft.Border.all(1, "#D0D0D0"), border_radius=10, padding=10,
                content=recommendations_list,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        spacing=12,
    )

    main_content = ft.Container(content=library_content, expand=True)

    def on_nav_change(e):
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

    page.add(
        ft.Column(
            [
                ft.Text(APP_NAME, theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight=ft.FontWeight.BOLD),
                main_content,
            ],
            expand=True,
        )
    )
    
    refresh_all()


if __name__ == "__main__":
    ft.run(main)
