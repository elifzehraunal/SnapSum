📘 SnapSum

Mobil Dokuman Ozetleme ve Kitap Oneri Sistemi

🚀 Proje Tanimi

SnapSum, kullanicilarin dokumanlari (PDF, fotograf vb.) ozetleyebildigi ve okuma aliskanliklarina gore kitap onerileri alabilecegi mobil tabanli bir uygulamadir.

Kullanici:

PDF yukleyebilir
Fotograf cekerek metni okutabilir
Uygulama icindeki kutuphaneden kitap secerek ozet alabilir
Okuma gecmisine gore kendine ozel bir profil (karakter) olusturur
🎯 Amac
Kullanicilarin okuduklari metinleri hizli sekilde anlamalarini saglamak
Okuma aliskanliklarini analiz ederek kisilestirilmis oneriler sunmak
Yapay zeka destekli ozetleme sistemini mobil ortamda kullanmak
⚙️ Temel Ozellikler
📄 PDF yukleme ve ozetleme
📸 Fotografdan OCR ile metin cikarma
📚 Dahili kutuphane uzerinden kitap secme
✂️ Farkli uzunluklarda ozetleme (kisa / orta / uzun)
🧠 Kullanici karakteri olusturma
📊 Kitap onerme sistemi
🔍 Google Books entegrasyonu (kitap bilgisi ve aciklama)
🏗️ Sistem Mimarisi
📱 Mobil
Flutter / React Native
🧠 Backend
Python (Flask veya FastAPI)
🗄️ Veritabani
SQLite
🤖 NLP
Hugging Face Transformers
🔎 OCR
Tesseract + OpenCV
🔄 Calisma Mantigi
Kullanici PDF yukler veya fotograf ceker
Sistem metni cikarir (OCR gerekiyorsa kullanir)
Backend uzerinde metin ozetlenir
Kullaniciya ozet gosterilir
Kullanici davranislarina gore profil olusturulur
Profil bazli kitap onerileri sunulur
🧩 Karakter ve Oneri Sistemi
Kitaplar kategorilere ayrilir (dram, macera, bilim vb.)
Kullanici okuma gecmisi analiz edilir
Yuzdelik dagilim hesaplanir
Kullaniciya bir “okuyucu karakteri” atanir
En baskin kategoriye gore kitap onerileri sunulur
👥 Ekip ve Gorev Dagilimi
🔥 Ana Ekip
Ibrahim → Backend, ozetleme sistemi, karakter algoritmasi
Baran → Veritabani, kutuphane sistemi, API
Elif → Mobil uygulama, API entegrasyonu
⚙️ Destek Ekip
Sinem → UI/UX tasarim, ekran duzeni
Fatma → OCR entegrasyonu, test ve demo
🌿 Branch Yapisi
main → final versiyon
develop → aktif gelistirme
Feature Branchler
backend-ibrahim
backend-baran
mobile-elif
ui-sinem
ocr-fatma
📁 Proje Yapisi
SnapSum/
│
├── backend/
├── mobile/
├── library/
├── docs/
├── tests/
├── requirements.txt
└── README.md
🧪 Kurulum
git clone https://github.com/elifzehraunal/SnapSum
cd snapsum
pip install -r requirements.txt
python main.py
📌 Notlar
Bu proje bir donem projesi kapsaminda gelistirilmektedir
Sistem yayinlanmak uzere degildir
Kullanilan PDF dosyalari sadece demo amaclidir
🎯 Sonuc

SnapSum, yapay zeka destekli ozetleme ve kullanici bazli kitap onerme sistemini birlestiren, mobil tabanli modern bir uygulama olarak tasarlanmistir.
