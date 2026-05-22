# 🧠 SnapSum Mimari Analiz ve Sistem Dökümantasyonu

Bu döküman, SnapSum projesinin genel yapısını, dizin mimarisini, veri akışlarını, güvenlik katmanlarını ve mevcut geliştirme durumunu ayrıntılı bir şekilde analiz etmek ve belgelemek amacıyla hazırlanmıştır.

---

## 📑 İçindekiler
1. [Proje Genel Tanımı ve Teknolojik Altyapı](#1-proje-genel-tanımı-ve-teknolojik-altyapı)
2. [Genel Dizin Yapısı (Workspace Directory Structure)](#2-genel-dizin-yapısı-workspace-directory-structure)
3. [Katmanlı Mimari ve Bileşen Analizi](#3-katmanlı-mimari-ve-bileşen-analizi)
   - [3.1. Ön-Yüz (Frontend - Flet Mobile)](#31-ön-yüz-frontend---flet-mobile)
   - [3.2. Arka-Yüz (Backend Core)](#32-arka-yüz-backend-core)
   - [3.3. Güvenlik Katmanı (api_security.py)](#33-güvenlik-katmanı-api_securitypy)
4. [Veri ve İletişim Akışı (Data Flow)](#4-veri-ve-iletişim-akışı-data-flow)
   - [4.1. Kitap Ekleme/Yükleme Akışı](#41-kitap-ekleme-yükleme-akışı)
   - [4.2. PDF/Metin Özetleme İstek Akışı (Map-Reduce)](#42-pdfmetin-özetleme-istek-akışı-map-reduce)
5. [👥 Görev Dağılımı ve Sorumluluklar](#5-görev-dağılımı-ve-sorumluluklar)
6. [🛠️ Başarıyla Çözülen Kritik Sorunlar](#6-başarıyla-çözülen-kritik-sorunlar)
7. [📅 Tamamlanan Geliştirme Yol Haritası](#7-tamamlanan-geliştirme-yol-haritası)

---

## 1. Proje Genel Tanımı ve Teknolojik Altyapı

**SnapSum**, kullanıcıların yerel veya genel kütüphanelerindeki metin tabanlı PDF ve düz metin (.txt) dosyalarını yükleyerek içeriklerini okumalarını ve gelişmiş Yapay Zeka (LLM) modellerini kullanarak bu içerikleri özetlemelerini sağlayan çapraz platform uyumlu bir mobil uygulamadır.

Mimarisi, ön-yüz ve arka-yüz kodlarını tek bir Python sürecinde (in-process) çalıştırabilen veya gelecekte bir HTTP REST API ile ayrıştırılmaya uygun modüler bir yapıda tasarlanmıştır.

### Teknolojik Bileşenler:
* **Ön-Yüz (Frontend):** Python tabanlı, hızlı prototipleme ve çoklu platform (Android, iOS, Masaüstü) desteği sunan **Flet** framework'ü.
* **Metin Ayıklama (OCR / PDF Parser):** PDF belgelerinden metin katmanını hızlıca okumak için **PyMuPDF (fitz)** kütüphanesi.
* **Yapay Zeka Servisleri:** Metin özetleme ve analiz işlemleri için tamamen entegre edilmiş **Mistral AI API** (metinler için `mistral-small-latest` ve görsel/OCR analizleri için `pixtral-large-latest` modeli). Google Gemini API bağımlılıkları tamamen temizlenmiştir.
* **Güvenlik Modülü:** Rate limiting (Token Bucket), girdi sanitizasyonu (path traversal ve XSS engelleme) ve API anahtar maskeleme katmanları.
* **Önbellek (Cache) Mekanizması:** Yapay zeka maliyetlerini düşürmek amacıyla SHA-256 tabanlı benzersiz sorgu kimlikleri üreten **JSON dosya tabanlı** yerel önbellek ve SQLite önbelleği.


---

## 2. Genel Dizin Yapısı (Workspace Directory Structure)

SnapSum projesinin kök dizini altındaki klasör ve kritik dosya yapısı aşağıdaki gibidir:

```
SnapSum/
│
├── .env                        # 🔒 Çevresel değişkenler ve API anahtarı (Git tarafından yoksayılır)
├── .gitignore                  # ⚙️ Git dışı bırakılacak klasör kuralları
├── LICENSE                     # 📄 MIT Lisans dosyası
├── README.md                   # 📄 Proje başlangıç kılavuzu
│
├── backend/                    # ⚙️ Arka-Yüz (Backend) Kaynak Kodları
│   ├── api_security.py         # 🛡️ Güvenlik katmanı (Limiter, Validator, Audit)
│   ├── backend_manager.py      # ⚙️ Özetleme, normalizasyon ve LLM entegrasyon yöneticisi (Kritik Çelişkili Dosya)
│   │
│   ├── database/               # 💾 Arka-yüz veritabanı/önbellek klasörü
│   │   └── summary_cache.json  # 📦 LLM özet çıktı önbelleği
│   ├── logs/                   # 📝 Güvenlik logları (Git dışı)
│   ├── ocr/                    # 📷 İleride yapılması planlanan OCR modülü placeholder'ı
│   ├── recommendation/         # 🧠 İleride yapılması planlanan Kitap Öneri Motoru placeholder'ı
│   └── summarization/          # 📄 Özetleyici placeholder'ı
│
├── cleaned_texts/              # 📚 Fatma tarafından hazırlanmış 18 adet düz metin (.txt) kitap dosyası
│
├── data/                       # 📂 Uygulama Veri Depolama Klasörü
│   ├── uploads/                # 📄 Kullanıcılar tarafından yüklenen kişisel PDF/Görsel dosyaları
│   └── snapsum.db              # 💾 SQLite3 yerel veritabanı dosyası (Kitaplar ve özetler kalıcıdır)
│
├── docs/                       # 📄 Proje Dökümantasyonları
│   └── SnapSum_Dökümantasyon.md # 📑 Bu dökümantasyon dosyası
│
├── library/                    # 📚 Genel Kütüphane Kaynakları
│   ├── metadata/               # 📄 Varsayılan kitap metadata'ları
│   └── pdfs/                   # 📄 Sistemde varsayılan olarak gelen hazır PDF'ler
│
├── mobile/                     # 📱 Ön-Yüz (Flet Mobile Frontend)
│   ├── main.py                 # 🚀 Uygulama ana giriş noktası ve UI yönlendiricisi
│   ├── requirements.txt        # 📦 Mobil arayüz Python bağımlılıkları
│   ├── assets/                 # 🎨 Görsel ve medya dosyaları
│   ├── components/             # 🧱 Tekrar kullanılabilir UI bileşenleri
│   ├── screens/                # 🖥️ Arayüz ekranları (Boş, main.py içinde birleştirilmiş)
│   │
│   └── app/                    # ⚙️ Ön-yüz İş Mantığı Katmanı
│       ├── __init__.py
│       ├── config.py           # ⚙️ Uygulama yapılandırma değerleri (API Keys, Chunk ayarları vb.)
│       ├── models.py           # 🧱 Veri modelleri (Book veri sınıfı)
│       │
│       ├── data/               # 💾 Veri erişim katmanı
│       │   ├── database.py     # 💾 SQLite3 yerel veritabanı şeması ve SQL yöneticisi
│       │   └── repository.py   # 🧱 SQLite3 veritabanını sarmalayan repository katmanı
│       │
│       ├── services/           # 🔌 Yardımcı servisler
│       │   └── backend_adapter.py # 🌉 Mobil UI ile BackendManager arasındaki dinamik import köprüsü
│       │
│       └── ui/                 # 🎨 Arayüz elemanları ve temalandırma
│           ├── book_detail_view.py # 🖥️ Kitap detay, okuma ve özetleme modal diyaloğu
│           └── theme.py        # 🎨 Özelleştirilmiş Flet UI Renk Teması
│
└── tests/                      # 🧪 Birim testler klasörü
```

---

## 3. Katmanlı Mimari ve Bileşen Analizi

SnapSum projesi katmanlı bir yazılım mimarisiyle kurulmuştur. Bu katmanlar arasındaki ilişkiler şöyledir:

### 3.1. Ön-Yüz (Frontend - Flet Mobile)
Mobil arayüz `mobile/` dizininde konumlandırılmıştır.
* **`main.py`:** Uygulama başlatıldığında Flet penceresini oluşturur, genel kütüphaneyi `cleaned_texts/` klasöründeki Fatma'nın 18 adet hazır kitabı ile tohumlar (`seed_general_books`) ve arayüz yapısını (Genel Kütüphane listesi, Şahsi Kütüphane listesi ve PDF Yükleme Paneli) çizer.
* **`app/models.py`:** Uygulamadaki temel veri birimi olan `Book` yapısını içerir. `id`, `title`, `file_path`, `source`, `summary`, `created_at` gibi alanları barındıran bir `dataclass`'tır.
* **`app/data/database.py` ve `repository.py`:** Arayüz bileşenlerinin veri ekleme ve listeleme işlemlerini gerçekleştirdiği katmandır. **SQLite3** tabanlıdır ve `data/snapsum.db` üzerinde kalıcı veri depolama sağlar.
* **`app/services/backend_adapter.py`:** Bu sınıf arayüzün backend işlevlerine doğrudan bağımlı kalmasını önler. Uygulama çalışırken dinamik olarak Python `sys.path` listesine proje kökünü ekler ve `backend/backend_manager.py` içerisindeki `BackendManager`'ı yüklemeye çalışır.

### 3.2. Arka-Yüz (Backend Core)
İş mantığı ve ağır işlemlerin yürütüldüğü arka plan servisleridir.
* **`backend/backend_manager.py`:** 
  - **Metin Normalizasyonu:** PDF/Metin dosyasından okunan metindeki sayfa numaraları (`Sayfa 12`, `- 12 -`), tablo bölücüler (`|---`) ve gereksiz ardışık boşluklar regex kullanılarak temizlenir.
  - **Paragraf-Duyarlı Chunking:** LLM'e gönderilecek metinlerin model limitlerini aşmaması için metni 5000-8000 karakterlik parçalara böler. Bu bölme işlemini paragrafları koruyarak yapar (`\n\n`), eğer tek bir paragraf çok uzunsa karakter bazlı güvenli fallback uygular.
  - **Map-Reduce Özetleme:** Metin parçaları tek tek LLM'e gönderilerek parça özetleri alınır (**MAP**). Daha sonra bu parça özetleri birleştirilerek tek bir tutarlı ana özet elde edilir (**REDUCE**).
  - **Ön-bellek (Cache):** Üretilen özetler, dosya yolu, istenen özet uzunluğu ve kullanılan model parametreleri ile hashlenerek `backend/database/summary_cache.json` dosyasına yazılır. Böylece aynı kitaba ikinci kez özet istendiğinde LLM API'sine gitmeden anında sonuç dönülür.

### 3.3. Güvenlik Katmanı (api_security.py)
Backend üzerinde çalışan ve uygulamanın güvenli çalışmasını sağlayan kritik bileşendir.
* **APIKeyValidator:** API anahtarının formatını kontrol eder, loglama esnasında maskeler (`****...r8k`) ve proje dosyalarında kazara hardcoded API key ifşa edilip edilmediğini regex ile tarar.
* **RateLimiter:** Token Bucket yöntemi ile kullanıcının dakikada maksimum 10 istek yapmasını sınırlar.
* **InputValidator:** Kullanıcının seçtiği PDF/Metin/görsel dosyasını boyut (maks 50 MB), desteklenen uzantı (`.pdf`, `.txt`, `.jpg` vb.) ve **Sembolik Link / Path Traversal** güvenlik risklerine karşı denetler. Kitap başlıklarındaki HTML/Script etiketlerini temizleyerek XSS açıklarını engeller.
* **SecurityAudit:** Tüm API çağrı sürelerini, başarı durumlarını ve güvenlik ihlallerini `backend/logs/security.log` dosyasına yazarak denetim geçmişi oluşturur.

---

## 4. Veri ve İletişim Akışı (Data Flow)

Uygulamanın çalışması sırasındaki iki kritik akış aşağıda görselleştirilmiş ve açıklanmıştır:

### 4.1. Kitap Ekleme/Yükleme Akışı
```mermaid
sequenceDiagram
    autonumber
    actor Kullanıcı
    participant UI as mobile/main.py
    participant Repo as mobile/app/data/repository.py
    participant DB as mobile/app/data/database.py
    participant Storage as data/uploads/
    
    Kullanıcı->>UI: PDF/Görsel Dosyası Seç / Yol Gir
    Kullanıcı->>UI: "Yükle" Butonuna Basar
    UI->>UI: Uzantının .pdf veya .jpg olduğunu doğrular
    UI->>Storage: Dosyayı benzersiz UUID ismiyle kopyalar
    UI->>Repo: add_book(Book nesnesi) çağırır
    Repo->>DB: SQLite3 veritabanına kalıcı olarak yazar
    UI->>Kullanıcı: Arayüz listesini yeniler ve başarı mesajı gösterir
```

---

### 4.2. PDF/Metin Özetleme İstek Akışı (Map-Reduce)
```mermaid
sequenceDiagram
    autonumber
    actor Kullanıcı
    participant UI as mobile/app/ui/book_detail_view.py
    participant Adapter as mobile/app/services/backend_adapter.py
    participant Backend as backend/backend_manager.py
    participant Sec as backend/api_security.py
    participant DB as mobile/app/data/database.py
    participant LLM as Mistral AI API

    Kullanıcı->>UI: Kitaba Tıklar ve Özet Uzunluğu Seçer ("Ozetle")
    UI->>UI: Spinner'ı Aktif Eder
    UI->>Adapter: summarize_pdf(file_path, length) çağırır
    
    rect rgb(240, 240, 240)
        Note over Adapter, Backend: Dinamik Import ve Köprü Katmanı
        Adapter->>Backend: summarize_pdf(...) delegasyonu
    end
    
    Backend->>Sec: Girdi ve Parametre Doğrulaması İster
    Sec-->>Backend: Geçerli (True)
    
    Backend->>DB: Özet veritabanında mevcut mu? (Summary Cache)
    alt Önbellek Mevcut (Cache Hit)
        DB-->>Backend: Hazır özet metni döndürür
        Backend-->>Adapter: BackendResponse(success=True, from_cache=True)
    else Önbellek Yok (Cache Miss)
        Backend->>Backend: .txt ise doğrudan okur, .pdf ise PyMuPDF ile ayıklar
        Backend->>Backend: Metni Paragraf Duyarlı Chunk'lara Böler (5K-8K Karakter)
        
        loop Her Chunk İçin (MAP Fazı)
            Backend->>LLM: chat/completions (Sistem Talimatı + Parça Metni)
            LLM-->>Backend: Kısmi Özet Çıktısı
        end
        
        rect rgb(255, 240, 240)
            Note over Backend, LLM: Birden fazla parça varsa REDUCE Fazı
            Backend->>LLM: chat/completions (Parça Özetlerini Birleştir)
            LLM-->>Backend: Tek Master Özet Çıktısı
        end
        
        Backend->>DB: Master Özeti SQLite veritabanına kaydeder
        Backend-->>Adapter: BackendResponse(success=True, from_cache=False)
    end
    
    Adapter-->>UI: SummaryResult nesnesi döndürür
    UI->>UI: Özet alanını günceller ve Spinner'ı kapatır
    UI->>Kullanıcı: Sonucu ekranda gösterir
```

---

## 5. 👥 Görev Dağılımı ve Sorumluluklar

SnapSum projesinde ekip üyelerinin üstlendiği temel roller, sorumluluklar ve katkıları aşağıda detaylandırılmıştır. Tüm roller ekip üyeleri arasında başarıyla koordine edilmiş ve SnapSum uygulamasının son kararlı sürümü bu görev dağılımına uygun olarak %100 çalışır ve tamamlanmış bir şekilde teslim edilmiştir.

- **İbrahim (Backend Dev):** Yapay Zeka entegrasyonu (Mistral API), Chunking & Map-Reduce algoritması tasarımı, prompt mühendisliği ve PDF/Metin temizleme mantığı (`backend_manager.py`).
- **Baran (Veritabanı & API):** Uygulama verilerinin SQLite üzerinde yönetimi (`DatabaseManager`), kütüphane ekleme/silme fonksiyonları ve API key konfigürasyonu.
- **Elif (Mobil Dev):** Flet framework ile uygulamanın mobil/masaüstü reaktif arayüzünün (Library, Upload, Profile sekmeleri) geliştirilmesi, dosya gezgini entegrasyonu ve uygulamanın genel UI navigasyonu (`main.py` ve bileşenler).
- **Sinem (UI/UX):** Uygulamanın renk paletleri, bileşenlerin konumlandırmaları, kart tasarımları ve genel kullanıcı deneyiminin planlanması.
- **Fatma (Veri İşleme & Test):** Hazır kütüphanede (`cleaned_texts`) bulunacak kitap metinlerinin hazırlanmesi, temizlenmesi ve sistemin farklı dosya türleri/büyüklükleriyle test edilmesi.

---

## 6. 🛠️ Başarıyla Çözülen Kritik Sorunlar

Yapılan derinlemesine geliştirme ve stabilizasyon çalışmaları sonucunda, uygulamayı engelleyen tüm **kritik sorunlar tamamen çözülmüştür**:

### ✅ 1. Git Çakışmaları ve Mistral AI Geçişi (Çözüldü)
`backend/backend_manager.py` dosyası içerisindeki git birleştirme çakışma etiketleri tamamen temizlenmiş, Gemini kodları kaldırılarak yerine kararlı, asenkron ve modern **Mistral AI API** entegrasyonu kurulmuştur.

### ✅ 2. Düz Metin (.txt) / PDF Çift Dosya Desteği (Çözüldü)
Hazır kitapların `.txt` olması durumunda doğrudan UTF-8 formatında okunması, `.pdf` dökümanlarda ise `PyMuPDF (fitz)` kullanılarak sayfa bazlı metin ayıklanması sağlanmıştır. Sistem dosya uzantısına göre dinamik olarak doğru okuyucu metodunu seçmektedir.

### ✅ 3. Dil Parametresi ve Güvenlik Duvarı Normalizasyonu (Çözüldü)
Flet UI ve `api_security.py` güvenlik modülü arasındaki parametre uyuşmazlığı giderilmiştir. Güvenlik katmanı hem Türkçe (`"Kısa"`, `"Orta"`, `"Uzun"`) hem de İngilizce (`"Short"`, `"Medium"`, `"Long"`) parametrelerini kabul edecek şekilde güncellenmiştir.

### ✅ 4. Reaktif FilePicker ve Asenkron Dosya İşleme (Çözüldü)
Arayüzde eski ve stabil olmayan `on_result` callback tabanlı dosya seçici mekanizması yerine doğrudan asenkron inline `await file_picker.pick_files()` yapısına geçilmiştir. Bu sayede görsel yükleme, PDF ekleme ve fotoğraf çekip özetleme süreçleri kesintisiz ve hatasız çalışmaktadır.

---

## 7. 📅 Tamamlanan Geliştirme Yol Haritası

1. **SQLite Kalıcı Depolama Entegrasyonu:** Tüm kullanıcı geçmişi, şahsi kitaplar ve özetler `snapsum.db` üzerinde SQLite3 ile başarıyla saklanmaktadır.
2. **Kişiselleştirilmiş Öneri Motoru:** Kullanıcının okuma geçmişini analiz eden ve buna göre kullanıcıya özel karakterler (örneğin `"🔬 Bilimkurgu Kaşifi"`, `"🧠 Düşünce Mimarı"`) atayarak kitap öneren algoritmik yapı kurulmuştur.
3. **Mevcut Görsel OCR Analizi (Pixtral Vision):** PNG, JPG, JPEG görsel dosyalarından Pixtral API kullanılarak doğrudan OCR ile analiz ve özetleme yapılabilmektedir.
4. **Çift Dil Desteği:** Türkçe ve İngilizce dilleri arasında dinamik arayüz geçişleri tamamen entegredir.
5. **Modern Material 3 Arayüz Tasarımı:** Cozy Cream Paper okuma arka planı, arama kapsülleri, bulut sürükle-bırak göstergesi ile zengin ve premium HSL renk şemaları (Indigo, Rose, Slate) tamamlanmıştır.
