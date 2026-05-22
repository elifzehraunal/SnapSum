from flet.controls.services.file_picker import FilePickerFile
import inspect

f = FilePickerFile(path="test/path.txt", bytes=None)
print("dir of f:", dir(f))
print("name attribute exists?", hasattr(f, "name"))
print("path:", f.path)
