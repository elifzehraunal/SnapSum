"""SnapSum - Flet mobile starter application."""

from __future__ import annotations

from pathlib import Path
import shutil
import uuid

import flet as ft

from app.config import APP_NAME, UPLOADS_DIR
from app.data.repository import BookRepository
from app.models import Book
from app.services.backend_adapter import BackendAdapter
from app.ui.book_detail_view import build_book_dialog
from app.ui.theme import app_theme


def build_seed_books() -> list[Book]:
    """Create 20 placeholder books for general library."""
    seeds: list[Book] = []
    for i in range(1, 21):
        seeds.append(
            Book(
                title=f"Hazır Kitap {i:02d}",
                file_path=str(UPLOADS_DIR / f"sample_{i:02d}.pdf"),
                source="general",
            )
        )
    return seeds


def main(page: ft.Page) -> None:
    """Flet application entry point."""
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = app_theme()
    page.padding = 16
    page.bgcolor = ft.Colors.SLATE_50
    page.window.width = 430
    page.window.height = 880

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    repository = BookRepository()
    repository.seed_general_books(build_seed_books())
    backend_adapter = BackendAdapter()

    general_list = ft.ListView(expand=True, spacing=8)
    personal_list = ft.ListView(expand=True, spacing=8)
    upload_status = ft.Text("Henüz dosya seçilmedi.", color=ft.Colors.GREY_700)
    selected_file = {"path": None}

    def open_book(book: Book) -> None:
        dialog = build_book_dialog(page, book, backend_adapter, repository.update_summary)
        page.dialog = dialog
        dialog.open = True
        page.update()

    def build_book_tile(book: Book) -> ft.Control:
        subtitle = "Özet mevcut" if book.summary else "Özet yok"
        return ft.Card(
            content=ft.ListTile(
                leading=ft.Icon(ft.Icons.BOOKMARK_OUTLINE),
                title=ft.Text(book.title),
                subtitle=ft.Text(subtitle),
                trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                on_click=lambda _: open_book(book),
            )
        )

    def refresh_lists() -> None:
        general_books = repository.list_books(source="general")
        personal_books = repository.list_books(source="personal")
        general_list.controls = [build_book_tile(book) for book in general_books]
        personal_list.controls = [build_book_tile(book) for book in personal_books]
        page.update()

    def pick_result(event: ft.FilePickerResultEvent) -> None:
        if not event.files:
            upload_status.value = "Dosya seçimi iptal edildi."
            selected_file["path"] = None
        else:
            selected_file["path"] = event.files[0].path
            upload_status.value = f"Seçilen dosya: {Path(selected_file['path']).name}"
        page.update()

    file_picker = ft.FilePicker(on_result=pick_result)
    page.overlay.append(file_picker)

    def handle_upload(_: ft.ControlEvent) -> None:
        source_path = selected_file.get("path")
        if not source_path:
            upload_status.value = "Lütfen önce bir PDF seç."
            page.update()
            return

        source = Path(source_path)
        if source.suffix.lower() != ".pdf":
            upload_status.value = "Sadece PDF dosyaları destekleniyor."
            page.update()
            return

        # Aynı isimli dosyaların ezilmesini engellemek için benzersiz dosya adı.
        target = UPLOADS_DIR / f"{source.stem}_{uuid.uuid4().hex[:8]}{source.suffix.lower()}"
        shutil.copy2(source, target)
        new_book = Book(title=source.stem, file_path=str(target), source="personal")
        repository.add_book(new_book)

        upload_status.value = f"Yüklendi: {source.name}\nYerel yol: {target}"
        selected_file["path"] = None
        refresh_lists()

    tabs = ft.Tabs(
        expand=1,
        tabs=[
            ft.Tab(
                text="Genel Kütüphane",
                content=ft.Container(
                    padding=10,
                    content=general_list,
                ),
            ),
            ft.Tab(
                text="Şahsi Kütüphanem",
                content=ft.Container(
                    padding=10,
                    content=personal_list,
                ),
            ),
            ft.Tab(
                text="PDF Yükle",
                content=ft.Container(
                    padding=10,
                    content=ft.Column(
                        controls=[
                            ft.Text("Yeni PDF Ekle", style=ft.TextThemeStyle.TITLE_MEDIUM),
                            ft.Text(
                                "Metin tabanlı PDF yükleyerek kitaplığınıza ekleyin.",
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Row(
                                controls=[
                                    ft.OutlinedButton(
                                        "Dosya Seç",
                                        icon=ft.Icons.UPLOAD_FILE,
                                        on_click=lambda _: file_picker.pick_files(
                                            allow_multiple=False,
                                            allowed_extensions=["pdf"],
                                        ),
                                    ),
                                    ft.ElevatedButton("Yükle", on_click=handle_upload),
                                ]
                            ),
                            upload_status,
                        ],
                        spacing=14,
                    ),
                ),
            ),
        ],
    )

    page.add(
        ft.Column(
            controls=[
                ft.Text(APP_NAME, style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("PDF metinlerini okuyun ve Gemini ile özetleyin.", color=ft.Colors.GREY_700),
                ft.Divider(),
                tabs,
            ],
            expand=True,
        )
    )
    refresh_lists()


if __name__ == "__main__":
    ft.app(target=main)
