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
    on_summary_saved: Callable[[str, str, str], None],
    repository=None,
) -> ft.AlertDialog:
    """Create modal dialog for reading and summarizing selected PDF.

    repository parametresi verilirse özetleme öncesi DB'den cache kontrol edilir.
    """
    text_content = ft.Text("PDF metni yükleniyor...", selectable=True)
    summary_content = ft.Text(book.summary or "Henüz özet oluşturulmadı.", selectable=True)
    summary_length = ft.RadioGroup(
        value="Orta",
        content=ft.Row(
            controls=[
                ft.Radio(value="Kısa", label="Kısa"),
                ft.Radio(value="Orta", label="Orta"),
                ft.Radio(value="Uzun", label="Uzun"),
            ],
            spacing=12,
        ),
    )
    loader = ft.ProgressRing(visible=False, width=24, height=24, stroke_width=3)
    status_text = ft.Text("")

    try:
        extracted_text = backend_adapter.extract_text(book.file_path) if backend_adapter.available else ""
        text_content.value = extracted_text or "Bu dosyada metin bulunamadı."
    except Exception as error:
        extracted_text = ""
        text_content.value = f"Dosya okunamadı: {error}"

    def summarize_click(_: ft.ControlEvent) -> None:
        sel_type = summary_length.value or "Orta"

        # 1) Önce DB cache'i kontrol et
        if repository:
            cached = repository.get_summary(book.id, sel_type)
            if cached:
                summary_content.value = cached
                on_summary_saved(book.id, cached, sel_type)
                status_text.value = f"✅ Özet veritabanından getirildi ({sel_type})."
                page.update()
                return

        if not backend_adapter.available:
            status_text.value = "⚠️ Backend bağlantısı hazır değil."
            page.update()
            return

        loader.visible = True
        status_text.value = "Özet hazırlanıyor..."
        page.update()
        try:
            result = backend_adapter.summarize(
                file_path=book.file_path,
                summary_type=sel_type,
                book_id=book.id,
                repository=repository,
            )
            if result.success:
                summary_content.value = result.summary
                on_summary_saved(book.id, result.summary, sel_type)
                status_text.value = (
                    f"✅ Özet DB'den yüklendi ({sel_type})."
                    if result.from_cache
                    else f"✅ Özet oluşturuldu ve kaydedildi ({sel_type})."
                )
            else:
                status_text.value = f"❌ {result.message}"
        except Exception as error:
            status_text.value = f"❌ Özetleme hatası: {error}"
        finally:
            loader.visible = False
            page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(book.title),
        content=ft.Container(
            width=600,
            height=580,
            content=ft.Column(
                controls=[
                    ft.Text("Kitap Metni", weight=ft.FontWeight.BOLD),
                    ft.Container(
                        height=180,
                        padding=10,
                        border_radius=10,
                        border=ft.Border.all(1, "#D0D0D0"),
                        content=ft.ListView([text_content], auto_scroll=False),
                    ),
                    ft.Text("Özet Uzunluğu", weight=ft.FontWeight.BOLD),
                    ft.Row([summary_length, ft.TextButton("Özetle", on_click=summarize_click), loader]),
                    status_text,
                    ft.Text("Özet", weight=ft.FontWeight.BOLD),
                    ft.Container(
                        height=180,
                        padding=10,
                        border_radius=10,
                        border=ft.Border.all(1, "#D0D0D0"),
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
