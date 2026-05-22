"""Book detail view with reader and summarization controls."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable

import flet as ft

from app.models import Book
from app.services.backend_adapter import BackendAdapter
from app.ui.theme import PRIMARY, SECONDARY, SURFACE, CARD_BG, BORDER, TEXT_SECONDARY, SUCCESS, ERROR
from app.config import get_ui_language
from app.services.translations import t


def build_summary_dialog(page: ft.Page, book: Book) -> ft.AlertDialog:
    """Create modal dialog for reading an existing summary."""
    lang = get_ui_language()
    
    def copy_summary(_: ft.ControlEvent) -> None:
        if book.summary:
            page.set_clipboard(book.summary)
            status_text.value = t("copied_clipboard", lang)
            status_text.color = SUCCESS
            page.update()

    status_text = ft.Text("", size=12)
    copy_btn = ft.IconButton(
        ft.Icons.COPY_ROUNDED,
        tooltip=t("copy_summary", lang),
        icon_size=20,
        icon_color=PRIMARY,
        on_click=copy_summary,
    )

    summary_content = ft.Text(
        book.summary or t("summary_not_generated", lang),
        selectable=True,
        size=14,
        color="#2D3748",
    )

    return ft.AlertDialog(
        modal=True,
        title=ft.Text(
            book.title, 
            weight=ft.FontWeight.BOLD, 
            size=18, 
            color=PRIMARY,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=1
        ),
        content=ft.Container(
            width=600,
            height=400,
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Text(t("book_summary", lang), weight=ft.FontWeight.BOLD, size=15, color="#1A202C"),
                        copy_btn,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    status_text,
                    ft.Container(
                        expand=True,
                        padding=16,
                        border_radius=16,
                        border=ft.Border.all(1, BORDER),
                        bgcolor="#FAF9F6", # Premium eye-comfort cream paper color
                        content=ft.ListView([summary_content], auto_scroll=False),
                    ),
                ],
                spacing=8,
            ),
        ),
        actions=[
            ft.TextButton(
                t("close", lang), 
                on_click=lambda _: page.pop_dialog(),
                style=ft.ButtonStyle(color=PRIMARY)
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


def build_book_dialog(
    page: ft.Page,
    book: Book,
    backend_adapter: BackendAdapter,
    on_summary_saved: Callable[[str, str, str], None],
) -> ft.AlertDialog:
    """Create modal dialog for reading and summarizing selected PDF."""
    lang = get_ui_language()
    PAGE_SIZE = 1500
    state = {"current_page": 0, "extracted_text": ""}

    text_content = ft.Text(t("loading_text", lang), selectable=True, size=13)
    page_info = ft.Text("Page 1", weight=ft.FontWeight.BOLD, size=13)

    def update_text_view() -> None:
        if not state["extracted_text"]:
            text_content.value = t("no_readable_text", lang)
            page_info.value = ""
            return

        start_idx = state["current_page"] * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        text_content.value = state["extracted_text"][start_idx:end_idx]

        total_pages = max(1, (len(state["extracted_text"]) + PAGE_SIZE - 1) // PAGE_SIZE)
        page_info.value = t("page_info", lang, state['current_page'] + 1, total_pages)
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

    prev_btn = ft.IconButton(
        ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
        icon_color=PRIMARY,
        icon_size=18,
        tooltip="Geri" if lang == "tr" else "Back",
        on_click=go_prev
    )
    next_btn = ft.IconButton(
        ft.Icons.ARROW_FORWARD_IOS_ROUNDED,
        icon_color=PRIMARY,
        icon_size=18,
        tooltip="İleri" if lang == "tr" else "Next",
        on_click=go_next
    )
    pagination_row = ft.Row(
        [prev_btn, page_info, next_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )

    is_image = Path(book.file_path).suffix.lower() in [".jpg", ".jpeg", ".png"]

    try:
        if is_image:
            state["extracted_text"] = t("image_direct_analyze", lang) if "image_direct_analyze" in t("image_direct_analyze", lang) else "Görsel içeriği doğrudan analiz edilecektir."
        else:
            state["extracted_text"] = backend_adapter.extract_text(book.file_path)
        update_text_view()
    except Exception as error:  # pylint: disable=broad-except
        state["extracted_text"] = ""
        text_content.value = t("file_read_error", lang, error)

    summary_content = ft.Text(
        book.summary or t("summary_not_generated", lang),
        selectable=True,
        size=13,
        color="#2D3748",
    )
    
    summary_length = ft.RadioGroup(
        value="Medium",
        content=ft.Row(
            controls=[
                ft.Radio(value="Short", label=t("short", lang), active_color=PRIMARY),
                ft.Radio(value="Medium", label=t("medium", lang), active_color=PRIMARY),
                ft.Radio(value="Long", label=t("long", lang), active_color=PRIMARY),
            ],
            spacing=20,
        ),
    )
    text_coverage = ft.RadioGroup(
        value="Full",
        content=ft.Row(
            controls=[
                ft.Radio(value="Quarter", label=t("quarter", lang), active_color=PRIMARY),
                ft.Radio(value="Half", label=t("half", lang), active_color=PRIMARY),
                ft.Radio(value="Full", label=t("full", lang), active_color=PRIMARY),
            ],
            spacing=20,
        ),
    )
    loader = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2.5, color=PRIMARY)
    status_text = ft.Text("", size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.W_500)

    summarize_btn = ft.FilledButton(
        t("summarize", lang),
        icon=ft.Icons.AUTO_AWESOME_ROUNDED,
        on_click=lambda e: summarize_click(e),
        style=ft.ButtonStyle(
            bgcolor=PRIMARY,
            color="white",
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )

    def copy_summary(_: ft.ControlEvent) -> None:
        """Copy summary text to clipboard."""
        text = summary_content.value or ""
        if text and text != t("summary_not_generated", lang):
            page.set_clipboard(text)
            status_text.value = t("copied_clipboard", lang)
            status_text.color = SUCCESS
            page.update()

    copy_btn = ft.IconButton(
        ft.Icons.COPY_ROUNDED,
        tooltip=t("copy_summary", lang),
        icon_size=20,
        icon_color=PRIMARY,
        on_click=copy_summary,
    )

    def summarize_click(_: ft.ControlEvent) -> None:
        if not state["extracted_text"].strip():
            status_text.value = t("no_text_summarize", lang)
            page.update()
            return
        if not backend_adapter.available:
            status_text.value = t("backend_not_ready", lang)
            page.update()
            return

        loader.visible = True
        summarize_btn.disabled = True
        status_text.value = t("preparing_summary", lang)
        status_text.color = TEXT_SECONDARY
        page.update()

        def _run():
            try:
                if is_image:
                    result = backend_adapter.summarize_image(
                        image_path=book.file_path,
                        summary_length=summary_length.value or "Medium",
                        text_coverage=text_coverage.value or "Full",
                    )
                else:
                    result = backend_adapter.summarize_pdf(
                        pdf_path=book.file_path,
                        summary_length=summary_length.value or "Medium",
                        text_coverage=text_coverage.value or "Full",
                    )
                if result.success:
                    summary_content.value = result.summary
                    on_summary_saved(book.id, result.summary, summary_length.value or "Orta")
                    status_text.value = (
                        t("summary_loaded_cache", lang) if result.from_cache
                        else t("summary_generated_success", lang)
                    )
                    status_text.color = SUCCESS
                else:
                    status_text.value = result.message
                    status_text.color = ERROR
            except Exception as error:  # pylint: disable=broad-except
                status_text.value = t("summarization_error", lang, error)
                status_text.color = ERROR
            finally:
                loader.visible = False
                summarize_btn.disabled = False
                page.update()

        threading.Thread(target=_run, daemon=True).start()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            book.title, 
            weight=ft.FontWeight.BOLD, 
            size=18, 
            color=PRIMARY,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=1
        ),
        content=ft.Container(
            width=600,
            height=580,
            content=ft.Column(
                controls=[
                    ft.Text(t("book_image_text", lang), weight=ft.FontWeight.BOLD, size=14, color="#1A202C"),
                    ft.Container(
                        height=160,
                        padding=12,
                        border_radius=14,
                        border=ft.Border.all(1, BORDER),
                        bgcolor="#FAF9F6", # Cozy ivory reading paper bg
                        content=ft.ListView([text_content], auto_scroll=False),
                    ),
                    pagination_row,
                    ft.Divider(height=10, color="transparent"),
                    ft.Text(t("summary_length", lang), weight=ft.FontWeight.BOLD, size=14, color="#1A202C"),
                    summary_length,
                    ft.Text(t("text_coverage", lang), weight=ft.FontWeight.BOLD, size=14, color="#1A202C"),
                    ft.Row([text_coverage, summarize_btn, loader], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    status_text,
                    ft.Row([
                        ft.Text(t("book_summary", lang), weight=ft.FontWeight.BOLD, size=14, color="#1A202C"),
                        copy_btn,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        height=160,
                        padding=12,
                        border_radius=14,
                        border=ft.Border.all(1, BORDER),
                        bgcolor="#FAF9F6", # Cozy ivory reading paper bg
                        content=ft.ListView([summary_content], auto_scroll=False),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
            ),
        ),
        actions=[
            ft.TextButton(
                t("close", lang), 
                on_click=lambda _: page.pop_dialog(),
                style=ft.ButtonStyle(color=PRIMARY)
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    return dialog
