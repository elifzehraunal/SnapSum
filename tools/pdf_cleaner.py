import fitz  # PyMuPDF
import os
import re

def profesyonel_temizlik(metin):
    # 1. Attilâ İlhan ve benzeri kitaplardaki özel karakterleri düzelt
    metin = metin.replace('Â', 'a').replace('İ', 'i').replace('Î', 'i').replace('û', 'u')
    
    # 2. Satır sonuna denk gelen tireli kelimeleri birleştir (Örn: "ge-le-cek" -> "gelecek")
    metin = re.sub(r'(\w+)-\s*\n(\w+)', r'\1\2', metin)
    
    # 3. Sayfa numaralarını ve sadece rakam kalan satırları temizle
    metin = re.sub(r'^\d+$', '', metin, flags=re.MULTILINE)
    
    # 4. Garip sembolleri temizle
    metin = re.sub(r'[■●○•♦*#_|]', '', metin)
    
    # 5. Gereksiz boşlukları temizle
    metin = re.sub(r' +', ' ', metin)
    
    temiz_satirlar = []
    for satir in metin.split('\n'):
        s = satir.strip()
        # 3 karakterden kısa olan çöpleri (sayfa başı artıkları vb.) ele
        if len(s) > 3:
            temiz_satirlar.append(s)
            
    return "\n".join(temiz_satirlar)

if __name__ == "__main__":
    input_folder = 'books'
    output_folder = 'cleaned_texts'

    # Klasör kontrolü
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"Hata: '{input_folder}' klasörü bulunamadı!")
    else:
        files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
        
        if not files:
            print("Hata: 'books' klasöründe temizlenecek PDF bulunamadı!")
        else:
            print(f"--- SnapSum Veri Temizleme Başladı (Toplam: {len(files)} Kitap) ---")
            
            for filename in files:
                try:
                    pdf_path = os.path.join(input_folder, filename)
                    doc = fitz.open(pdf_path)
                    
                    full_text = ""
                    for page in doc:
                        ham_metin = page.get_text("text")
                        full_text += profesyonel_temizlik(ham_metin) + "\n"
                    
                    # .txt olarak kaydet
                    txt_filename = filename.replace('.pdf', '.txt')
                    with open(os.path.join(output_folder, txt_filename), 'w', encoding='utf-8') as f:
                        f.write(full_text)
                    print(f"✅ Başarıyla Temizlendi: {filename}")
                    
                except Exception as e:
                    print(f"❌ Hata ({filename}): {e}")
            
            print("\n--------------------------------------------------")
            print(f"🎉 İŞLEM TAMAMLANDI!")
            print(f"Fatma, {len(files)} adet kitap 'cleaned_texts' klasörüne hazırlandı.")
            print("--------------------------------------------------")
