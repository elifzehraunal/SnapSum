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
    page.window.width = 430
    page.window.height = 880

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    repository = BookRepository()
    repository.seed_general_books(build_seed_books())
    backend_adapter = BackendAdapter()
    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    general_list = ft.ListView(expand=True, spacing=8)
    personal_list = ft.ListView(expand=True, spacing=8)
    upload_status = ft.Text("Henüz dosya seçilmedi.")
    selected_file = {"path": None}
    file_path_input = ft.TextField(
        label="PDF dosya yolu",
        hint_text=r"Ornek: C:\Users\ibrah\Documents\kitap.pdf",
    )

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

    def apply_input_path(_: ft.ControlEvent) -> None:
        path_value = (file_path_input.value or "").strip().strip('"')
        if not path_value:
            upload_status.value = "Lutfen PDF dosya yolunu girin."
            selected_file["path"] = None
        else:
            selected_file["path"] = path_value
            upload_status.value = f"Secilen dosya: {Path(path_value).name}"
        page.update()

    async def pick_file(_: ft.ControlEvent) -> None:
        files = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["pdf"],
            with_data=True,
        )
        if not files:
            upload_status.value = "Dosya secimi iptal edildi."
            selected_file["path"] = None
            page.update()
            return

        picked = files[0]
        if picked.path:
            selected_file["path"] = picked.path
            file_path_input.value = picked.path
            upload_status.value = f"Secilen dosya: {picked.name}"
            page.update()
            return

        # Web gibi ortamlarda path gelmeyebilir; bytes ile yerel kopya olustururuz.
        file_bytes = getattr(picked, "bytes", None)
        if file_bytes:
            target = UPLOADS_DIR / f"{Path(picked.name).stem}_{uuid.uuid4().hex[:8]}.pdf"
            target.write_bytes(file_bytes)
            selected_file["path"] = str(target)
            file_path_input.value = str(target)
            upload_status.value = f"Secilen dosya: {picked.name}"
        else:
            upload_status.value = "Dosya okunamadi. Lutfen tekrar deneyin."
            selected_file["path"] = None
        page.update()

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

    upload_panel = ft.Container(
        padding=10,
        border=ft.Border.all(1, "#D0D0D0"),
        border_radius=10,
        content=ft.Column(
            controls=[
                ft.Text("PDF Yukle", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text("Metin tabanli PDF yukleyerek kitapliginiza ekleyin."),
                ft.Row(
                    controls=[
                        ft.OutlinedButton(
                            "Dosya Sec",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=pick_file,
                        ),
                        ft.OutlinedButton(
                            "Yolu Onayla",
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                            on_click=apply_input_path,
                        ),
                        ft.Button("Yukle", on_click=handle_upload),
                    ]
                ),
                file_path_input,
                upload_status,
            ],
            spacing=12,
        ),
    )

    page.add(
        ft.Column(
            controls=[
                ft.Text(APP_NAME, theme_style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("PDF metinlerini okuyun ve Gemini ile ozetleyin."),
                ft.Divider(),
                ft.Text("Genel Kutuphane", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Container(
                    height=220,
                    padding=10,
                    border=ft.Border.all(1, "#D0D0D0"),
                    border_radius=10,
                    content=general_list,
                ),
                ft.Text("Sahsi Kutuphanem", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Container(
                    height=220,
                    padding=10,
                    border=ft.Border.all(1, "#D0D0D0"),
                    border_radius=10,
                    content=personal_list,
                ),
                upload_panel,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    )
    refresh_lists()


if __name__ == "__main__":
    ft.run(main)
