# 📘 SnapSum: Proje Dökümantasyonu

**SnapSum**, kullanıcıların dökümanlarını (PDF, metin vb.) yapay zeka desteğiyle özetleyebildiği ve okuma alışkanlıklarına göre kişiselleştirilmiş kitap önerileri alabildiği modern bir mobil uygulamadır.

---

## 1. 🚀 Proje Hakkında Genel Bakış

SnapSum, yoğun bilgi çağında kullanıcıların metinleri hızlıca anlamlandırmasını sağlar. Mistral AI API kullanarak kitapları ve dökümanları analiz eder, kullanıcı tercihlerine göre farklı uzunluklarda özetler sunar.


### 🎯 Temel Hedefler
- Metinlerin hızlı ve etkili bir şekilde anlaşılmasını sağlamak.
- Kullanıcıların okuma geçmişine dayalı kişiselleştirilmiş kitap önerileri sunmak.
- Minimalist ve metin odaklı bir kullanıcı deneyimi yaratmak.

### ⚙️ Teknik Özellikler
- **📄 PDF Özetleme:** Yüklenen PDF dökümanlarından metin ayıklama ve özetleme.
- **📚 Kütüphane Yönetimi:** Hazır kitaplar ve kullanıcıya özel döküman listesi.
- **✂️ Akıllı Özetleme:** Kısa, Orta ve Uzun seçenekleriyle ayarlanabilir özet uzunluğu.
- **🧠 Karakter Analizi:** Okuma alışkanlıklarına göre kullanıcı profili oluşturma.
- **📊 Öneri Sistemi:** Kullanıcı karakterine uygun kitap önerileri.

---

## 2. 👥 Görev Dağılımı ve Sorumluluklar

- **İbrahim (Backend Dev):** Yapay Zeka entegrasyonu (Mistral API), Chunking & Map-Reduce algoritması tasarımı, prompt mühendisliği ve PDF/Metin temizleme mantığı (`backend_manager.py`).
- **Baran (Veritabanı & API):** Uygulama verilerinin SQLite üzerinde yönetimi (`DatabaseManager`), kütüphane ekleme/silme fonksiyonları ve API key konfigürasyonu.
- **Elif (Mobil Dev):** Flet framework ile uygulamanın mobil/masaüstü reaktif arayüzünün (Library, Upload, Profile sekmeleri) geliştirilmesi, dosya gezgini entegrasyonu ve uygulamanın genel UI navigasyonu (`main.py` ve bileşenler).
- **Sinem (UI/UX):** Uygulamanın renk paletleri, bileşenlerin konumlandırmaları, kart tasarımları ve genel kullanıcı deneyiminin planlanması.
- **Fatma (Veri İşleme & Test):** Hazır kütüphanede (`cleaned_texts`) bulunacak kitap metinlerinin hazırlanması, temizlenmesi ve sistemin farklı dosya türleri/büyüklükleriyle test edilmesi.

---

## 3. 🏗️ Teknik Mimari ve Çalışma Mantığı

### 🧠 Backend (Yapay Zeka & İş Mantığı)
- **Metin İşleme:** `PyMuPDF` ile PDF'lerden metin ayıklanır, gürültülü veriler (sayfa numaraları, boşluklar vb.) temizlenir.
- **Map-Reduce Özetleme:** Uzun metinler parçalara (chunks) ayrılır, her parça Mistral ile özetlenir ve sonunda bu özetler tek bir master özet haline getirilir.
- **JSON Cache:** Aynı dökümanlar için tekrar API isteği atmamak adına `summary_cache.json` üzerinden yerel depolama yapılır.

### 📱 Mobil (UI & UX)
- **Flet Framework:** Python dilinde Flutter benzeri bir deneyim sunan Flet ile geliştirilmiştir.
- **Reaktif Arayüz:** Kullanıcı etkileşimleri anlık olarak backend fonksiyonlarını tetikler ve UI üzerinde güncellenir.

### 🏗️ Teknoloji Yığını
- **UI:** Flet (Python)
- **Backend:** Python
- **AI/NLP:** Mistral AI API (mistral-small-latest / pixtral-large-latest)
- **Parsing:** PyMuPDF (fitz) / Plain TXT reader
- **Depolama:** JSON Cache / SQLite (Aktif)

---

## 4. 📅 Tamamlanan Aşamalar ve Geliştirmeler (Completed Features)

- **Tam SQLite Veritabanı Entegrasyonu:** Kullanıcı profil verileri, kütüphane kayıtları ve çıkarılan özetler SQLite üzerinde kalıcı olarak saklanmaktadır (`snapsum.db`).
- **Gelişmiş Öneri Motoru (Okur Karakteri Analizi):** Okuma geçmişine ve kitap kategorilerine dayalı dinamik kullanıcı profili ve kişiselleştirilmiş öneri motoru entegre edilmiştir.
- **OCR & Pixtral Görsel Desteği:** Pixtral Vision API entegrasyonu ile görsellerin (`.png`, `.jpg`, `.jpeg`) doğrudan yapay zeka ile OCR analizi ve özetlenmesi sağlanmıştır.
- **Çift Dil Desteği:** Türkçe ve İngilizce dilleri arasında dinamik arayüz, profil ve özet desteği tamamen entegre edilmiştir.

---

## 📁 Proje Yapısı

```text
SnapSum/
├── backend/        # API, AI ve Veri İşleme mantığı
├── mobile/         # Flet mobil uygulama arayüzü
├── library/        # Kitap verileri ve PDF'ler
├── cleaned_texts/  # Temizlenmiş kitap metinleri
├── docs/           # Dökümantasyon dosyaları
├── tests/          # Test senaryoları
└── README.md       # Ana döküman (Bu dosya veya referans)
```

---

> **Not:** Veritabanı bağlantısı Baran tarafından SQLite tabanlı olarak tamamen kurulmuş ve kalıcı depolama arayüzle entegre bir şekilde aktifleştirilmiştir.
