# 📘 SnapSum: Proje Dökümantasyonu ve Sistem Rehberi

**SnapSum**, kullanıcıların dökümanlarını (PDF, TXT, PNG, JPG, JPEG) yapay zeka desteğiyle özetleyebildiği, görsel/OCR analizi alabildiği, Türkçe ve İngilizce çift dil desteği sunan ve okuma geçmişine dayalı kişiselleştirilmiş kitap önerileri sunan reaktif mobil ve masaüstü uygulamasıdır.

---

## 1. 🚀 Proje Hakkında Genel Bakış

SnapSum, bilgi yoğun çağımızda metinlerin hızlı ve etkili şekilde analiz edilip özetlenmesini sağlar. **Mistral AI API** modellerini kullanarak kitapları ve dökümanları akıllıca parçalar (Chunking & Map-Reduce), kullanıcı tercihlerine göre farklı uzunluklarda ve dillerde özetler üretir.

### 🎯 Temel Hedefler
- **Hızlı Anlamlandırma:** Büyük PDF ve TXT belgelerini saniyeler içerisinde özetleyerek zamandan tasarruf ettirmek.
- **Pixtral Görsel Özetleme (OCR):** Kitap kapakları veya sayfalarının fotoğraflarını çekip yapay zekayla doğrudan OCR analizi yaparak özetlemek.
- **Okur Karakteri Analizi:** Okuma geçmişine ve kitap türlerine göre kullanıcıya dinamik profiller atamak.
- **Kişiselleştirilmiş Öneriler:** Kullanıcının okur profiline uygun yapay zeka destekli kitap önerileri sunmak.
- **Minimalist ve Premium Arayüz:** Indigo, Rose ve Slate renk tonlarıyla tasarlanmış, göz yormayan Cozy Cream Paper okuma zeminli Material 3 arayüzü.

### ⚙️ Teknik Özellikler
- **📄 PDF ve TXT Özetleme:** Dosya gezgininden yüklenen veya yerleşik kütüphanedeki dökümanlardan gürültüsüz metin ayıklama ve özetleme.
- **📷 Görsel & OCR Analizi:** Pixtral Vision API ile doğrudan resim dosyalarının çözümlenmesi.
- **📚 SQLite Kütüphane Yönetimi:** SQLite3 kalıcı veritabanı sayesinde kitaplar ve özetler yerel olarak saklanır.
- **✂️ Akıllı Map-Reduce Özetleme:** Kısa, Orta ve Uzun seçenekleriyle ayarlanabilir asenkron özet yapısı.
- **🧠 Okur Karakteri Analizi:** Kullanıcının okuduğu kitap kategorilerine dayalı profil oluşturma.
- **🌐 Çift Dil Desteği:** Türkçe ve İngilizce dilleri arasında dinamik arayüz geçişleri.

---

## 2. 👥 Görev Dağılımı ve Sorumluluklar

SnapSum projesinde ekip üyelerinin üstlendiği temel roller ve sorumluluklar aşağıda detaylandırılmıştır. Tüm roller başarıyla koordine edilmiş ve kararlı sürüm bu görev dağılımına uygun şekilde tamamlanmıştır.

- **İbrahim (Backend Dev):** Yapay Zeka entegrasyonu (Mistral API), Chunking & Map-Reduce algoritması tasarımı, prompt mühendisliği ve PDF/Metin temizleme mantığı (`backend_manager.py`).
- **Baran (Veritabanı & API):** Uygulama verilerinin SQLite üzerinde yönetimi (`DatabaseManager`), kütüphane ekleme/silme fonksiyonları ve API key konfigürasyonu.
- **Elif (Mobil Dev):** Flet framework ile uygulamanın mobil/masaüstü reaktif arayüzünün (Library, Upload, Profile sekmeleri) geliştirilmesi, dosya gezgini entegrasyonu ve uygulamanın genel UI navigasyonu (`main.py` ve bileşenler).
- **Sinem (UI/UX):** Uygulamanın renk paletleri, bileşenlerin konumlandırmaları, kart tasarımları ve genel kullanıcı deneyiminin planlanması.
- **Fatma (Veri İşleme & Test):** Hazır kütüphanede (`cleaned_texts`) bulunacak kitap metinlerinin hazırlanmesi, temizlenmesi ve sistemin farklı dosya türleri/büyüklükleriyle test edilmesi.

---

## 3. 🏗️ Teknik Mimari ve Çalışma Mantığı

### 🧠 Backend (Yapay Zeka & İş Mantığı)
- **Metin Normalizasyonu:** PDF/TXTs dosyasından okunan metindeki sayfa numaraları, boşluk artıkları ve tablo çizgileri regex yardımıyla temizlenerek normalize edilir.
- **Paragraf-Duyarlı Chunking:** Metinler 5000-8000 karakterlik parçalara bölünürken paragraf bütünlüğü korunur.
- **Map-Reduce Özetleme:** Mistral `mistral-small-latest` (metinler için) ve `pixtral-large-latest` (görsel/OCR için) API'leri ile asenkron Map-Reduce mekanizmasıyla çalışır.
- **Önbellek (Cache):** SHA-256 hash tabanlı `summary_cache.json` ve SQLite tabanlı önbellekleme sayesinde mükerrer API istekleri engellenir.
- **Güvenlik Katmanı (`api_security.py`):** Girdi doğrulayıcı, rate limiter, audit günlüğü ve API key maskeleme güvenliği sağlar.

### 📱 Mobil (Flet Frontend)
- **Flet Framework:** Python ile asenkron tabanlı reaktif mobil/masaüstü ön yüz arayüzü sağlar.
- **Asenkron FilePicker:** Flet v0.84+ standartlarına uygun, inline `await file_picker.pick_files()` asenkron yapısıyla çökmeyen, kararlı dosya seçimi sunar.

### 🏗️ Teknoloji Yığını
- **UI:** Flet v0.84.0+ (Python)
- **Backend:** Python 3.10+
- **AI/NLP:** Mistral AI API (mistral-small-latest / pixtral-large-latest)
- **Parsing:** PyMuPDF (fitz) / UTF-8 Plain TXT reader
- **Depolama:** SQLite3 (`snapsum.db`) / JSON Cache

---

## 4. 📅 Tamamlanan Yol Haritası ve Geliştirmeler

Tüm geliştirmeler başarıyla tamamlanmış ve kararlı sürüme entegre edilmiştir:
- **SQLite Yerel Depolama Entegrasyonu (%100):** Tüm veriler `snapsum.db` üzerinde kalıcıdır.
- **Dinamik Okur Karakteri & Öneri Sistemi (%100):** Kullanıcı okuma geçmişine dayalı karakter profilleri ve yapay zeka kitap önerileri.
- **OCR & Pixtral Görsel Desteği (%100):** PNG, JPG ve JPEG dosyalarından doğrudan OCR ile yapay zekalı görsel özetleme.
- **Türkçe & İngilizce Çift Dil Desteği (%100):** Tüm arayüz ve özetler iki dilde dinamik çalışmaktadır.
- **Premium UI Temalandırma (%100):** Indigo, Rose ve Slate Material 3 tasarımları ve Cozy Cream Paper okuyucu ekranı.

---

## 📁 Proje Yapısı

```text
SnapSum/
├── backend/            # API, AI, Güvenlik ve Veri İşleme mantığı
│   ├── database/       # JSON Önbellek dosyaları
│   ├── recommendation/ # Okur karakteri analiz motoru
│   └── api_security.py # Güvenlik katmanı
├── mobile/             # Flet mobil/masaüstü arayüz kodları
│   ├── app/            # SQLite, modeller, temalar ve servisler
│   └── main.py         # Giriş noktası ve yönlendirici
├── data/               # SQLite veritabanı (snapsum.db) ve yüklenen dosyalar
├── library/            # Hazır kütüphane kaynakları ve PDF'ler
├── cleaned_texts/      # Fatma tarafından hazırlanan 18 adet düz metin kitap dosyası
├── docs/               # Sistem dökümantasyon dosyaları
├── tests/              # Birim test dosyaları
└── README.md           # Ana dökümantasyon dosyası (Bu dosya)
```

---

## 🧪 Kurulum ve Çalıştırma

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/elifzehraunal/SnapSum
   cd SnapSum
   ```

2. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Çevresel değişkenleri hazırlayın:**
   Kök dizinde `.env` dosyası oluşturun ve Mistral API anahtarınızı tanımlayın:
   ```env
   MISTRAL_API_KEY=your_api_key_here
   ```

4. **Uygulamayı çalıştırın:**
   ```bash
   python mobile/main.py
   ```

---

> **Not:** Veritabanı ve tüm asenkron Mistral entegrasyonu tamamen kurulmuştur. Uygulama, hem API üzerinden canlı özet alabilmekte hem de yerel SQLite ve JSON önbelleği sayesinde internet olmasa dahi daha önce özetlenen tüm kitapları anında listeleyip okutabilmektedir.
