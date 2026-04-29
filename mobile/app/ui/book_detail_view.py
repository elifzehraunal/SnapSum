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
    PAGE_SIZE = 1000
    state = {"current_page": 0, "extracted_text": ""}

    text_content = ft.Text("Metin yükleniyor...", selectable=True)
    page_info = ft.Text("Sayfa 1", weight=ft.FontWeight.BOLD)
    
    def update_text_view() -> None:
        if not state["extracted_text"]:
            text_content.value = "Bu dosya içinde okunabilir metin bulunamadı."
            page_info.value = ""
            return
            
        start_idx = state["current_page"] * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        
        text_content.value = state["extracted_text"][start_idx:end_idx]
        
        total_pages = max(1, (len(state["extracted_text"]) + PAGE_SIZE - 1) // PAGE_SIZE)
        page_info.value = f"Sayfa {state['current_page'] + 1} / {total_pages}"
        
        page.update()

    def go_prev(_: ft.ControlEvent) -> None:
        if state["current_page"] > 0:
            state["current_page"] -= 1
            update_text_view()

    def go_next(_: ft.ControlEvent) -> None:
        total_pages = max(1, (len(state["extracted_text"]) + PAGE_SIZE - 1) // PAGE_SIZE)
        if state["current_page"] < total_pages - 1:
            state["current_page"] += 1
            update_text_view()

    prev_btn = ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_prev)
    next_btn = ft.IconButton(ft.Icons.ARROW_FORWARD, on_click=go_next)
    pagination_row = ft.Row([prev_btn, page_info, next_btn], alignment=ft.MainAxisAlignment.CENTER)

    from pathlib import Path
    is_image = Path(book.file_path).suffix.lower() in [".jpg", ".jpeg", ".png"]

    try:
        if is_image:
            state["extracted_text"] = "Görsel içeriği doğrudan analiz edilerek özetlenecektir."
        else:
            state["extracted_text"] = backend_adapter.extract_text(book.file_path)
        update_text_view()
    except Exception as error:  # pylint: disable=broad-except
        state["extracted_text"] = ""
        text_content.value = f"Dosya okunamadı: {error}"

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

    def summarize_click(_: ft.ControlEvent) -> None:
        if not state["extracted_text"].strip():
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
            if is_image:
                result = backend_adapter.summarize_image(
                    image_path=book.file_path,
                    summary_length=summary_length.value or "Orta",
                )
            else:
                result = backend_adapter.summarize_pdf(
                    pdf_path=book.file_path,
                    summary_length=summary_length.value or "Orta",
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
                    ft.Text("Kitap/Görsel Metni", weight=ft.FontWeight.BOLD),
                    ft.Container(
                        height=180,
                        padding=10,
                        border_radius=10,
                        border=ft.Border.all(1, "#D0D0D0"),
                        content=ft.ListView([text_content], auto_scroll=False),
                    ),
                    pagination_row,
                    ft.Text("Özet Uzunluğu", weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            summary_length,
                            ft.ElevatedButton("Özetle", icon=ft.Icons.AUTO_AWESOME, on_click=summarize_click),
                            loader,
                        ]
                    ),
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
    page.pop_dialog()
