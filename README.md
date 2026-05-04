# 📘 SnapSum: Proje Dökümantasyonu

**SnapSum**, kullanıcıların dökümanlarını (PDF, metin vb.) yapay zeka desteğiyle özetleyebildiği ve okuma alışkanlıklarına göre kişiselleştirilmiş kitap önerileri alabildiği modern bir mobil uygulamadır.

---

## 1. 🚀 Proje Hakkında Genel Bakış

SnapSum, yoğun bilgi çağında kullanıcıların metinleri hızlıca anlamlandırmasını sağlar. Google Gemini API kullanarak kitapları ve dökümanları analiz eder, kullanıcı tercihlerine göre farklı uzunluklarda özetler sunar.

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

SnapSum projesinde ekip üyelerinin üstlendiği temel roller ve sorumluluklar aşağıda detaylandırılmıştır.

### 👨‍💻 İbrahim (Backend Dev)
**Rol:** Backend ve Yapay Zeka Entegrasyonu
- **Özetleme Sistemi:** Google Gemini API (Öğrenci Planı) bağlantısını kurmak ve özetleme mantığını Python ile yazmak.
- **Karakter & Metin Algoritması:** Kitap metinlerini Gemini'nin okuma limitlerine göre parçalara bölen (chunking) ve özetleri birleştiren algoritmayı geliştirmek.
- **Metin Ayıklama (PDF Parsing):** PDF dosyalarından sadece saf metni (plain text) çeken, resimleri ve grafikleri tamamen yok sayan yapıyı kurmak.
- **Prompt Yönetimi:** "Kısa, Orta, Uzun" seçenekleri için farklılaştırılmış yapay zeka komutlarını (prompts) optimize etmek.

### 📊 Baran (Veritabanı & API)
**Rol:** Veri Yönetimi ve Güvenlik
- **Veritabanı Entegrasyonu:** Seçilecek olan veritabanının (Local SQLite, JSON veya Bulut DB) mimarisini kurmak ve Python bağlantısını sağlamak. *(Planlama aşamasında)*
- **Kütüphane Yönetimi:** 20 adet hazır kitabın ve kullanıcı tarafından yüklenen PDF'lerin veritabanındaki kayıt süreçlerini yönetmek.
- **Veri Senkronizasyonu:** Uygulama her açıldığında mevcut kitap listesinin ve daha önce çıkarılmış özetlerin veritabanından hızlıca çekilmesini sağlamak.
- **API Güvenliği:** API anahtarlarının ve veritabanı bilgilerinin güvenli yönetimi için gerekli konfigürasyonları yapmak.

### 📱 Elif (Mobil Dev)
**Rol:** Mobil Uygulama Geliştirme (Flet)
- **Mobil Uygulama Arayüzü:** Flet kullanarak uygulamanın ana ekranlarını (Genel Kütüphane, Şahsi Kütüphanem, Yükleme Alanı) kodlamak.
- **Fonksiyon Entegrasyonu:** İbrahim'in yazdığı özetleme fonksiyonlarını ve Baran'ın veritabanı kodlarını mobil arayüze bağlamak.
- **Özet Uzunluğu Seçimi:** Kullanıcının kısa, orta veya uzun özet tercihini yapabileceği arayüz bileşenlerini (Buton/Toggle) eklemek.
- **Dosya Seçici:** Kullanıcının telefon hafızasından PDF seçip sisteme dahil edebileceği dosya gezgini özelliğini entegre etmek.

### 🎨 Sinem (UI/UX)
**Rol:** Tasarım ve Kullanıcı Deneyimi
- **Ekran Düzeni:** Metin odaklı bir uygulama olduğu için okuma kolaylığını ön planda tutan minimalist bir ekran tasarımı yapmak.
- **Kullanıcı Deneyimi (UX):** Kullanıcının kütüphaneler arası geçişini ve özet alma sürecini en basit (en az tıklama ile) hale getirmek.
- **Geri Bildirim Tasarımı:** Özetleme işlemi sırasında görünecek yükleme animasyonları ve işlem tamamlandı uyarılarını belirlemek.
- **Görsel Kimlik:** Uygulamanın renk paletini ve tipografisini (metin odaklı olduğu için font seçimi kritik) belirlemek.

### 📸 Fatma (Veri İşleme & Test)
**Rol:** Veri Kalitesi ve Doğrulama
- **Metin Hazırlığı & Temizlik:** Hazır verilecek 20 kitabın PDF'lerini bulmak, içlerindeki resim/tablo gibi fazlalıkları temizleyip saf metni haline getirmek.
- **Test ve Demo:** Uygulamayı farklı uzunluktaki metinlerle test ederek hataları ayıklamak; sunum için demo videoları ve ekran görüntüleri hazırlamak.
- **Doğruluk Kontrolü:** Gemini'den gelen özetlerin seçilen uzunluklara (kısa/orta/uzun) uygunluğunu ve Türkçe karakterlerin düzgün göründüğünü denetlemek.

---

## 3. 🏗️ Teknik Mimari ve Çalışma Mantığı

### 🧠 Backend (Yapay Zeka & İş Mantığı)
- **Metin İşleme:** `PyMuPDF` ile PDF'lerden metin ayıklanır, gürültülü veriler (sayfa numaraları, boşluklar vb.) temizlenir.
- **Map-Reduce Özetleme:** Uzun metinler parçalara (chunks) ayrılır, her parça Gemini ile özetlenir ve sonunda bu özetler tek bir master özet haline getirilir.
- **JSON Cache:** Aynı dökümanlar için tekrar API isteği atmamak adına `summary_cache.json` üzerinden yerel depolama yapılır.

### 📱 Mobil (UI & UX)
- **Flet Framework:** Python dilinde Flutter benzeri bir deneyim sunan Flet ile geliştirilmiştir.
- **Reaktif Arayüz:** Kullanıcı etkileşimleri anlık olarak backend fonksiyonlarını tetikler ve UI üzerinde güncellenir.

### 🏗️ Teknoloji Yığını
- **UI:** Flet (Python)
- **Backend:** Python
- **AI/NLP:** Google Gemini API (gemini-1.5-flash)
- **Parsing:** PyMuPDF (fitz)
- **Depolama:** JSON Cache / SQLite (Planlanıyor)

---

## 4. 📅 Gelecek Planları (Roadmap)

- **Tam Veritabanı Entegrasyonu:** Kullanıcı profil verilerinin ve kütüphane kayıtlarının SQLite üzerinde kalıcı hale getirilmesi.
- **Gelişmiş Öneri Algoritması:** Okuma tercihlerine göre "Okur Karakteri" analizi.
- **OCR Desteği:** Resim ve fotoğraflar üzerindeki metinleri okuyabilme.
- **Google Books Entegrasyonu:** Kitap meta-verilerinin otomatik çekilmesi.

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
└── README.md       # Ana döküman
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

3. **Uygulamayı çalıştırın:**
   ```bash
   python mobile/main.py
   ```

---

> **Not:** Veritabanı bağlantısı şu an için aktif değildir; ancak mimari Baran tarafından planlanmış ve dökümantasyona dahil edilmiştir.
