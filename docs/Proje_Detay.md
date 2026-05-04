# SnapSum: Proje Detayları ve Teknik Dökümantasyon

SnapSum, akademik ve edebi metinlerin hızlıca özetlenmesini ve kullanıcı tercihlerine göre kitap önerileri sunulmasını sağlayan bir mobil platformdur.

---

## 🏗️ Sistem Mimarisi

Proje, modern ve modüler bir yapı üzerine inşa edilmiştir. Temel olarak iki ana bileşenden oluşur:

### 1. Backend (Python & Yapay Zeka)
Backend tarafı, verilerin işlenmesi, yapay zeka entegrasyonu ve iş mantığının yürütülmesinden sorumludur.

- **Metin İşleme (PDF Parsing):** `PyMuPDF (fitz)` kütüphanesi kullanılarak PDF dosyalarından saf metin ayıklanır. Resimler ve tablolar temizlenerek gürültüsüz bir veri seti elde edilir.
- **Parçalama Algoritması (Chunking):** Uzun metinler, Gemini API'nin token limitlerine uygun şekilde (5000-8000 karakterlik) anlamlı parçalara bölünür.
- **Özetleme (Gemini API):** Google'ın en yeni modellerinden `gemini-1.5-flash` kullanılır. "Map-Reduce" stratejisi ile her parça önce ayrı ayrı özetlenir, ardından bu özetler birleştirilerek bütüncül bir ana özet (Master Summary) oluşturulur.
- **Önbellekleme (Cache):** Aynı döküman için tekrar özet istenmesi durumunda, sistem JSON tabanlı bir cache (`summary_cache.json`) üzerinden hızlı yanıt verir.

### 2. Mobil Uygulama (Flet)
Kullanıcı arayüzü, Python tabanlı **Flet** framework'ü ile geliştirilmiştir.

- **Genel Kütüphane:** Sisteme kayıtlı hazır kitapların listelendiği alan.
- **Şahsi Kütüphanem:** Kullanıcının kendi yüklediği dökümanların yönetildiği alan.
- **Yükleme Alanı:** PDF veya TXT dosyalarının sisteme dahil edildiği arayüz.
- **Özet Kontrolleri:** Kısa, Orta ve Uzun seçenekleri ile kişiselleştirilebilir özetleme deneyimi.

---

## 👥 Ekip ve Görev Dağılımı

Projemiz, her biri belirli alanlarda uzmanlaşmış 5 kişilik bir ekip tarafından yürütülmektedir:

| Üye | Rol | Temel Sorumluluklar |
| :--- | :--- | :--- |
| **İbrahim** | Backend Dev | Gemini API entegrasyonu, Chunking algoritması, PDF Parsing. |
| **Baran** | Veritabanı & API | Veritabanı mimarisi (SQLite/Cloud), Veri senkronizasyonu, API güvenliği. |
| **Elif** | Mobil Dev | Flet arayüz kodlama, Fonksiyon entegrasyonu, Dosya seçici. |
| **Sinem** | UI/UX | Minimalist tasarım, Okuma kolaylığı, Kullanıcı deneyimi optimizasyonu. |
| **Fatma** | Veri & Test | Veri temizliği (PDF to Text), Doğruluk kontrolü, Demo ve test süreçleri. |

---

## 📅 Gelecek Planları (Roadmap)

Uygulamanın şu anki sürümünde yer almayan ancak geliştirme aşamasında olan özellikler:

1. **Tam Veritabanı Entegrasyonu:** SQLite veya Firebase kullanılarak kullanıcı bazlı kalıcı depolama.
2. **Gelişmiş Öneri Algoritması:** Okunan kitapların kategorilerine göre kullanıcıya "Okur Karakteri" atanması ve buna uygun yeni kitapların önerilmesi.
3. **OCR Desteği:** Tesseract veya Google Vision API ile görsel/fotoğraf üzerinden metin okuma ve özetleme.
4. **Google Books API:** Kitap kapak fotoğrafları ve detaylı meta-verilerin otomatik çekilmesi.

---

## 📁 Dosya Yapısı ve Dosya Amaçları

- `backend/backend_manager.py`: Tüm iş mantığının (business logic) toplandığı ana sınıf.
- `mobile/main.py`: Uygulamanın giriş noktası ve navigasyon yapısı.
- `cleaned_texts/`: Fatma tarafından hazırlanan ve sistemin kullandığı temizlenmiş kitap metinleri.
- `docs/Gorev_Dagilimi.md`: Ekip içi sorumlulukların detaylı dökümü.

---

> **Not:** Veritabanı bağlantısı şu an planlama aşamasındadır. Uygulama şu an için dosya sistemi ve JSON cache üzerinden çalışmaktadır.
