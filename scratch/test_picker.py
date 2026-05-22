import flet as ft

def main(page: ft.Page):
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    async def handle_result(e: ft.FilePickerResultEvent):
        print("on_result triggered!")
        print("files:", e.files)
        if e.files:
            print("Selected file path:", e.files[0].path)

    file_picker.on_result = handle_result

    async def btn_click(e):
        print("Button clicked, calling pick_files...")
        res = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["pdf", "png", "jpg", "jpeg"]
        )
        print("pick_files returned:", res)

    page.add(
        ft.ElevatedButton("Pick File", on_click=btn_click)
    )

ft.run(main)
