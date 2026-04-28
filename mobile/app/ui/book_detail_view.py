"""Book detail view with reader and summarization controls."""

from __future__ import annotations

from typing import Callable

import flet as ft

from app.models import Book
from app.services.backend_adapter import BackendAdapter


def build_book_dialog(
    page: ft.Page,
    book: Book,
    backend_adapter: BackendAdapter,
    on_summary_saved: Callable[[str, str], None],
) -> ft.AlertDialog:
    """Create modal dialog for reading and summarizing selected PDF."""
    text_content = ft.Text("PDF metni yükleniyor...", selectable=True)
    summary_content = ft.Text(book.summary or "Henüz özet oluşturulmadı.", selectable=True)
    summary_length = ft.Dropdown(
        label="Özet Uzunluğu",
        value="Orta",
        options=[ft.dropdown.Option("Kısa"), ft.dropdown.Option("Orta"), ft.dropdown.Option("Uzun")],
    )
    loader = ft.ProgressRing(visible=False, width=24, height=24, stroke_width=3)
    status_text = ft.Text("", color=ft.Colors.GREY_700)

    try:
        extracted_text = backend_adapter.extract_text(book.file_path)
        text_content.value = extracted_text or "Bu PDF içinde metin bulunamadı."
    except Exception as error:  # pylint: disable=broad-except
        extracted_text = ""
        text_content.value = f"PDF okunamadı: {error}"

    async def summarize_click(_: ft.ControlEvent) -> None:
        if not extracted_text.strip():
            status_text.value = "Özetlenecek metin yok."
            page.update()
            return
        if not backend_adapter.available:
            status_text.value = "Backend bağlantısı hazır değil."
            page.update()
            return

        loader.visible = True
        status_text.value = "Özet hazırlanıyor..."
        page.update()
        try:
            result = await page.run_thread(
                backend_adapter.summarize_pdf,
                book.file_path,
                summary_length.value or "Orta",
            )
            if result.success:
                summary_content.value = result.summary
                on_summary_saved(book.id, result.summary)
                status_text.value = (
                    "Özet cache'den yüklendi." if result.from_cache else "Özet güncellendi."
                )
            else:
                status_text.value = result.message
        except Exception as error:  # pylint: disable=broad-except
            status_text.value = f"Özetleme hatası: {error}"
        finally:
            loader.visible = False
            page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(book.title),
        content=ft.Container(
            width=600,
            height=560,
            content=ft.Column(
                controls=[
                    ft.Text("Kitap Metni", weight=ft.FontWeight.BOLD),
                    ft.Container(
                        height=180,
                        padding=10,
                        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.INDIGO),
                        border_radius=10,
                        content=ft.ListView([text_content], auto_scroll=False),
                    ),
                    ft.Row([summary_length, ft.ElevatedButton("Özetle", on_click=summarize_click), loader]),
                    status_text,
                    ft.Text("Özet", weight=ft.FontWeight.BOLD),
                    ft.Container(
                        height=180,
                        padding=10,
                        bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.SLATE_600),
                        border_radius=10,
                        content=ft.ListView([summary_content], auto_scroll=False),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
        ),
        actions=[ft.TextButton("Kapat", on_click=lambda _: close_dialog(page))],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    return dialog


def close_dialog(page: ft.Page) -> None:
    """Close active dialog."""
    if page.dialog:
        page.dialog.open = False
    page.update()
