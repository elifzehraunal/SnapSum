import flet as ft
import inspect

print("FilePicker methods:")
for name, member in inspect.getmembers(ft.FilePicker):
    if not name.startswith("_"):
        print(f"  {name}: {member}")

print("\npick_files signature:")
print(inspect.signature(ft.FilePicker.pick_files))
