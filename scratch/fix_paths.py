import json

f = 'data/books.json'
with open(f, 'r', encoding='utf-8') as file:
    d = json.load(file)

for b in d.get('books', []):
    path = b['file_path']
    if "C:\\Users\\ibrah\\Documents\\GitHub\\SnapSum\\" in path:
        b['file_path'] = path.replace("C:\\Users\\ibrah\\Documents\\GitHub\\SnapSum\\", "").replace("\\", "/")
    
with open(f, 'w', encoding='utf-8') as file:
    json.dump(d, file, ensure_ascii=False, indent=2)

print("Tamamlandı.")
