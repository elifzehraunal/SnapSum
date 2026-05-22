import flet as ft
from pathlib import Path

async def main(page: ft.Page):
    print("Flet main started!")
    file_picker = ft.FilePicker()
    page.services.append(file_picker)
    
    async def pick_click(e):
        print("pick_click triggered!")
        res = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["pdf", "png", "jpg", "jpeg"]
        )
        print("res returned:", res)
        # res should be FilePickerResultEvent or a list of files or FilePickerResult
        if res:
            print("res files:", getattr(res, "files", None))
            if getattr(res, "files", None):
                print("First file path:", res.files[0].path)
        page.update()

    page.add(
        ft.ElevatedButton("Pick File Test", on_click=pick_click)
    )

if __name__ == "__main__":
    ft.app(target=main)
