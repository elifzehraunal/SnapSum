import flet as ft
from flet.controls.services.file_picker import FilePickerFile
import inspect

print("FilePickerFile fields:")
for name, member in inspect.getmembers(FilePickerFile):
    if not name.startswith("_"):
        print(f"  {name}: {member}")
