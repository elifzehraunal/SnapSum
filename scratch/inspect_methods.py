import flet as ft
import asyncio

async def test():
    file_picker = ft.FilePicker()
    print("Is pick_files coroutine?", asyncio.iscoroutinefunction(file_picker.pick_files))

asyncio.run(test())
