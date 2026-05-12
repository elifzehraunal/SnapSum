# 📘 SnapSum: Kapsamlı Proje Dökümantasyonu

**SnapSum**, kullanıcıların dökümanlarını (PDF, metin dosyaları) ve fotoğraflarını yapay zeka (Mistral AI) desteğiyle özetleyebildiği, okuma alışkanlıklarına göre profil oluşturarak kişiselleştirilmiş kitap önerileri alabildiği modern bir mobil/masaüstü uygulamadır.

---

## 1. 🚀 Projenin Amacı ve Temel Çözümleri

SnapSum, yoğun bilgi çağında uzun metinlerin ve kitapların hızlıca analiz edilmesini ve anlamlandırılmasını sağlar. Mistral API'sini kullanarak yüklenen içerikleri analiz eder ve kullanıcının tercihine göre farklı uzunluklarda ve metnin farklı oranlarındaki kısımları üzerinden özetler sunar.

### 🎯 Çözüm Sunduğu Temel Noktalar:
- **Zaman Tasarrufu:** Yüzlerce sayfalık PDF'leri veya fotoğraflardaki metinleri saniyeler içinde okuyup özetler.
- **Kişiselleştirme:** "Kısa, Orta, Uzun" özet seçeneklerinin yanı sıra metnin sadece "Çeyrek, Yarım veya Tamamını" (Quarter, Half, Full) kapsayacak şekilde özetleme esnekliği sunar.
- **Akıllı Öneriler:** Kullanıcının okuma ve özetleme geçmişine dayalı olarak karakter profili oluşturur ve bu profile uygun olarak kütüphanedeki diğer kitaplardan öneriler sunar.

---

## 2. 🏗️ Teknik Mimari ve Kullanılan Teknolojiler

Proje, hem arayüz (frontend) hem de sunucu/iş mantığı (backend) tarafında ağırlıklı olarak **Python** kullanılarak geliştirilmiştir.

### 🛠️ Teknoloji Yığını:
- **Arayüz (UI):** Flet Framework (Python dilinde Flutter benzeri reaktif bir deneyim sunar).
- **Yapay Zeka (AI/NLP):** Mistral API (Metinler için `mistral-small-latest`, fotoğraflar/görseller için vision özellikli `pixtral-large-latest` modeli).
- **PDF/Metin İşleme (Parsing):** PyMuPDF (`fitz`). Sayfa numaraları, boşluklar vb. gürültülü verileri temizleyip normalize eder.
- **Veritabanı:** 
  - **Kullanıcı/Kütüphane Verileri:** SQLite (Veritabanı yöneticisi `app/data/database.py` üzerinden).
  - **Özet Ön belleği (Cache):** Yerel olarak `summary_cache.json` dosyasına kayıt yapılarak aynı doküman/ayarlar için tekrar API isteği atılması önlenir.

---

## 3. ⚙️ Temel Özellikler ve Çalışma Mantığı

### 📄 PDF ve Metin İşleme
- Kullanıcılar sisteme .pdf veya .txt dosyası yükleyebilir.
- Dosya sisteme girdiğinde PyMuPDF aracılığıyla saf metin (plain text) olarak ayıklanır ve normalize edilir (sayfa numaraları, tabloların çizgi izleri temizlenir).

### 📸 Fotoğraf (Görsel) Özetleme (OCR ve Vision)
- Kullanıcılar arayüzden fotoğraf çekip veya sistemden görsel (.png, .jpg, .jpeg) yükleyebilirler.
- Yüklenen görsel base64 formatına çevrilerek Mistral Vision (`pixtral-large-latest`) modeline gönderilir, resimdeki metinler yapay zeka tarafından okunup doğrudan özetlenir.

### ✂️ Akıllı Parçalama (Chunking) ve Map-Reduce Algoritması
- Mistral veya herhangi bir LLM'in token sınırına takılmamak için uzun metinler akıllıca parçalara bölünür (`chunking`). Sistem 5000-8000 karakterlik mantıksal (paragraf bütünlüğünü koruyan) parçalar oluşturur.
- **Map:** Her bir parça kendi içinde bağımsız olarak özetlenir.
- **Reduce:** Parça özetleri birleştirilerek nihai, tekil ve tutarlı bir **Master Özet** haline getirilir.

### 🎛️ Kullanıcı Kontrolleri (Kapsam ve Uzunluk)
Kullanıcı bir dökümanı özetlerken 2 temel tercih yapar:
1. **Özet Uzunluğu (Summary Length):** Kısa (Tek paragraf), Orta (Madde imli liste), Uzun (Detaylı analiz).
2. **Metin Kapsamı (Text Coverage):** Quarter (Çeyrek, %25), Half (Yarım, %50), Full (Tamamı, %100). Karakter limitini buna göre kırparak kitabın sadece belli bir kısmının özetini almayı sağlar.

### 👤 Profilleme ve Öneri Sistemi (Recommendation)
- Uygulamanın "Profil" sekmesinde kullanıcının veritabanındaki (kişisel kütüphane) okuduğu kitap kategorilerine (Bilim, Dram, Macera vb.) göre bir dağılım grafiği çıkarılır.
- Kullanıcının okuma karakteri belirlenir ve genel kütüphanedeki diğer eserler arasından bu profile uygun akıllı kitap önerileri sunulur.

---

## 4. 📁 Proje Dosya Yapısı

```text
SnapSum/
├── .env                  # Çevresel değişkenler (MISTRAL_API_KEY vb.)
├── README.md             # Ana tanıtım dokümanı
├── PROJE_DOKUMANTASYONU.md # Bu detaylı proje anlatım dosyası
├── backend/              # Sunucu/İş Mantığı klasörü
│   ├── backend_manager.py # AI entegrasyonu, PDF chunking ve cache yönetimi ana sınıfı
│   └── database/         # JSON önbellek dosyaları
├── mobile/               # Flet Mobil Uygulama klasörü
│   ├── main.py           # Uygulamanın ana giriş noktası (Entry Point)
│   ├── requirements.txt  # Projenin bağımlılıkları listesi
│   └── app/              # UI Bileşenleri, DB katmanı, Config dosyaları
├── cleaned_texts/        # Test ve tohum (seed) amaçlı temizlenmiş kitap metinleri
└── library/              # İndirilmiş PDF'ler ve ek metadatalar
```

---

## 5. 👥 Görev Dağılımı ve Sorumluluklar

- **İbrahim (Backend Dev):** Yapay Zeka entegrasyonu (Mistral API), Chunking & Map-Reduce algoritması tasarımı, prompt mühendisliği ve PDF/Metin temizleme mantığı (`backend_manager.py`).
- **Baran (Veritabanı & API):** Uygulama verilerinin SQLite üzerinde yönetimi (`DatabaseManager`), kütüphane ekleme/silme fonksiyonları ve API key konfigürasyonu.
- **Elif (Mobil Dev):** Flet framework ile uygulamanın mobil/masaüstü reaktif arayüzünün (Library, Upload, Profile sekmeleri) geliştirilmesi, dosya gezgini entegrasyonu ve uygulamanın genel UI navigasyonu (`main.py` ve bileşenler).
- **Sinem (UI/UX):** Uygulamanın renk paletleri, bileşenlerin konumlandırmaları, kart tasarımları ve genel kullanıcı deneyiminin planlanması.
- **Fatma (Veri İşleme & Test):** Hazır kütüphanede (`cleaned_texts`) bulunacak kitap metinlerinin hazırlanması, temizlenmesi ve sistemin farklı dosya türleri/büyüklükleriyle test edilmesi.

---

## 6. 🧪 Kurulum ve Çalıştırma

Sistemi kendi bilgisayarınızda kurup çalıştırmak için aşağıdaki adımları izleyin:

1. **Projeyi Bilgisayarınıza Klonlayın:**
   ```bash
   git clone https://github.com/elifzehraunal/SnapSum.git
   cd SnapSum
   ```

2. **Gerekli Python Kütüphanelerini Yükleyin:**
   Bağımlılıkları yüklemek için terminalden şu komutu çalıştırın:
   ```bash
   pip install -r mobile/requirements.txt
   ```
   *(Not: Sisteme `flet`, `PyMuPDF`, `httpx` vb. kütüphaneler dahil edilecektir.)*

3. **API Anahtarını Ayarlayın:**
   Ana dizinde `.env` isimli bir dosya oluşturun ve Mistral AI'dan aldığınız API anahtarınızı aşağıdaki gibi ekleyin:
   ```env
   MISTRAL_API_KEY=sizin_api_anahtariniz_buraya
   ```

4. **Uygulamayı Başlatın:**
   Tüm kurulumlar tamamlandıktan sonra uygulamayı çalıştırmak için:
   ```bash
   python mobile/main.py
   ```

*(Uygulama başarıyla başlatıldığında, yerel Flet masaüstü penceresi açılacaktır.)*
