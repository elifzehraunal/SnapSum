# 🔐 SnapSum API Dokümantasyonu

> **Versiyon:** 1.0.0 · **Son Güncelleme:** 2026-05-13 · **Dil:** Python 3.10+

---

## 📑 İçindekiler

1. [Genel Bakış](#1-genel-bakış)
2. [Kimlik Doğrulama & API Anahtarı](#2-kimlik-doğrulama--api-anahtarı)
3. [Güvenlik Katmanları](#3-güvenlik-katmanları)
4. [Backend API Referansı](#4-backend-api-referansı)
5. [Veritabanı API Referansı](#5-veritabanı-api-referansı)
6. [Öneri Motoru API](#6-öneri-motoru-api)
7. [Veri Modelleri](#7-veri-modelleri)
8. [Hata Kodları & Mesajları](#8-hata-kodları--mesajları)
9. [Kullanım Örnekleri](#9-kullanım-örnekleri)
10. [Güvenlik En İyi Uygulamaları](#10-güvenlik-en-i̇yi-uygulamaları)

---

## 1. Genel Bakış

SnapSum, **Mistral AI** API'sini kullanarak PDF, metin dosyaları ve görsellerdeki içerikleri özetleyen bir uygulamadır. Mimari olarak 3 ana katmandan oluşur:

```
┌─────────────────────────────────────────────────┐
│              Flet UI (mobile/main.py)            │
├─────────────────────────────────────────────────┤
│         BackendAdapter (Köprü Katmanı)           │
├──────────────┬──────────────┬────────────────────┤
│ BackendManager│ DatabaseMgr │ RecommendationEngine│
│ (AI + Cache) │  (SQLite)   │   (Profil + Öneri)  │
├──────────────┴──────────────┴────────────────────┤
│           API Security Layer (Güvenlik)           │
│   Rate Limiter · Key Validator · Input Validator  │
└─────────────────────────────────────────────────┘
```

### Teknoloji Yığını

| Bileşen | Teknoloji | Açıklama |
|---------|-----------|----------|
| **AI Modeli (Metin)** | `mistral-small-latest` | Metin özetleme |
| **AI Modeli (Görsel)** | `pixtral-large-latest` | OCR + Görsel özetleme |
| **API İletişimi** | `httpx` (HTTP/2) | Mistral REST API |
| **PDF İşleme** | `PyMuPDF (fitz)` | Metin ayıklama |
| **Veritabanı** | `SQLite3` | Kitap & özet depolama |
| **Önbellek** | `JSON (dosya)` | Özet cache |
| **UI Framework** | `Flet` | Çapraz platform UI |
| **Güvenlik** | `api_security.py` | Rate limiting, validation |

---

## 2. Kimlik Doğrulama & API Anahtarı

### Yapılandırma

API anahtarı **çevresel değişken** olarak yönetilir, asla kaynak kodda tutulmaz:

```bash
# .env dosyası (proje kök dizininde)
MISTRAL_API_KEY=your_api_key_here
```

### Anahtar Yükleme Zinciri

```python
# 1. .env dosyası yüklenir (dotenv)
load_dotenv(BASE_DIR / ".env")

# 2. Ortam değişkeninden okunur
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# 3. BackendAdapter üzerinden BackendManager'a iletilir
api_key = os.getenv("MISTRAL_API_KEY", MISTRAL_API_KEY)
```

### Güvenlik Kontrolleri

| Kontrol | Açıklama |
|---------|----------|
| **Boşluk kontrolü** | Anahtar tanımlı mı? |
| **Uzunluk kontrolü** | Min 20 karakter |
| **Format kontrolü** | Alfanümerik + `_-` |
| **Maskeleme** | Log'larda `****...r8k` formatında gösterilir |

### Mistral API Çağrısı

```
POST https://api.mistral.ai/v1/chat/completions
Authorization: Bearer <MISTRAL_API_KEY>
Content-Type: application/json
```

---

## 3. Güvenlik Katmanları

### 3.1 Rate Limiter

Token-bucket algoritması ile istek hızını kontrol eder:

| Parametre | Varsayılan | Açıklama |
|-----------|-----------|----------|
| `max_requests` | 10 | Pencere başına maks istek |
| `window_seconds` | 60 | Zaman penceresi (saniye) |
| `cooldown_seconds` | 30 | Limit aşıldığında bekleme |

```python
from backend.api_security import RateLimiter, RateLimitConfig

limiter = RateLimiter(RateLimitConfig(
    max_requests=10,
    window_seconds=60,
    cooldown_seconds=30,
))

allowed, message = limiter.allow_request()
print(f"Kalan hak: {limiter.remaining_requests}")
```

### 3.2 API Key Validator

```python
from backend.api_security import APIKeyValidator

# Doğrulama
is_valid, msg = APIKeyValidator.validate(api_key)

# Maskeleme (log'lar için)
masked = APIKeyValidator.mask(api_key)  # "****...r8k"

# Kod tarama (CI/CD için)
exposed = APIKeyValidator.is_exposed_in_file("backend_manager.py")
```

### 3.3 Input Validator

```python
from backend.api_security import InputValidator

# Dosya doğrulama
valid, msg = InputValidator.validate_file_path("document.pdf")

# Parametre doğrulama
valid, msg = InputValidator.validate_summary_params("Short", "Full")

# Başlık sanitizasyonu
safe_title = InputValidator.sanitize_title(user_input)
```

**Desteklenen dosya formatları:**

| Tip | Uzantılar |
|-----|-----------|
| Doküman | `.pdf`, `.txt` |
| Görsel | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp` |

**Maks dosya boyutu:** 50 MB

### 3.4 Security Audit

```python
from backend.api_security import SecurityAudit

audit = SecurityAudit()
audit.log_api_call("chat/completions", success=True, response_time_ms=1250.5)
audit.log_security_event("rate_limit", "User exceeded 10 req/min")

summary = audit.get_summary()
# {"total_events": 5, "api_calls": 3, "failed_calls": 1, ...}
```

Log dosyası: `backend/logs/security.log`

---

## 4. Backend API Referansı

### 4.1 `BackendManager` Sınıfı

**Modül:** `backend/backend_manager.py`

#### Yapılandırıcı

```python
BackendManager(
    cache_path: str | Path = "backend/database/summary_cache.json",
    mistral_api_key: str | None = None,
    model_name: str = "mistral-small-latest",
    chunk_min: int = 20_000,
    chunk_max: int = 30_000,
)
```

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|-----------|----------|
| `cache_path` | `str \| Path` | `backend/database/summary_cache.json` | JSON önbellek yolu |
| `mistral_api_key` | `str \| None` | `None` | Mistral API anahtarı |
| `model_name` | `str` | `mistral-small-latest` | Metin modeli adı |
| `chunk_min` | `int` | `20000` | Min chunk boyutu (karakter) |
| `chunk_max` | `int` | `30000` | Maks chunk boyutu (karakter) |

---

#### `summarize_pdf()`

PDF veya TXT dosyasını özetler.

```python
def summarize_pdf(
    pdf_path: str | Path,
    summary_length: Literal["Short", "Medium", "Long"],
    text_coverage: Literal["Quarter", "Half", "Full"] = "Full",
) -> BackendResponse
```

**İş Akışı:**
```
Dosya → Cache Kontrol → Metin Ayıklama → Kapsam Kırpma → Chunking → MAP (parça özetleri) → REDUCE (master özet) → Cache Kayıt → Sonuç
```

**Metin Limitleri (summary_length'e göre):**

| Mod | Maks Karakter | Açıklama |
|-----|--------------|----------|
| `Short` | 50,000 | Tek paragraf özet |
| `Medium` | 150,000 | Madde imli liste |
| `Long` | 500,000 | Detaylı analiz |

**Metin Kapsamı (text_coverage):**

| Mod | Kapsam | Açıklama |
|-----|--------|----------|
| `Quarter` | %25 | İlk çeyrek |
| `Half` | %50 | İlk yarı |
| `Full` | %100 | Tamamı |

---

#### `summarize_image()`

Görseldeki metni OCR ile okuyup özetler.

```python
def summarize_image(
    image_path: str | Path,
    summary_length: Literal["Short", "Medium", "Long"],
    text_coverage: Literal["Quarter", "Half", "Full"] = "Full",
) -> BackendResponse
```

- **Model:** `pixtral-large-latest` (Vision)
- Görsel **base64** formatına çevrilir
- MIME tipi dosya uzantısından belirlenir

---

#### `extract_plain_text()`

PDF veya TXT'den düz metin ayıklar ve normalize eder.

```python
def extract_plain_text(pdf_path: str | Path) -> str
```

**Normalize işlemleri:**
- Sayfa numarası satırları kaldırılır (`12`, `Sayfa 12`, `- 12 -`)
- Tablo çizgileri (`|---|---`) filtrelenir
- Çoklu boşluklar düzenlenir

---

#### `chunk_text()`

Uzun metni paragraf-duyarlı parçalara böler.

```python
def chunk_text(text: str) -> list[str]
```

**Algoritma:**
1. Paragraf bazlı bölme (`\n\n`)
2. `chunk_max` (30K) limitine göre gruplama
3. Aşırı uzun paragraflar için karakter bazlı fallback
4. `chunk_min` (20K) altındaki son parçalar birleştirilir

---

#### `categorize_title()`

Kitap başlığını AI ile kategorize eder.

```python
def categorize_title(title: str) -> str
```

**Geçerli kategoriler:** `Bilim`, `Tarih`, `Dram`, `Macera`, `Felsefe`, `Genel`

---

### 4.2 `BackendAdapter` Sınıfı

**Modül:** `mobile/app/services/backend_adapter.py`

UI ile BackendManager arasındaki köprü katmanı.

| Metod | Açıklama |
|-------|----------|
| `available` | Backend hazır mı? (property) |
| `extract_text(pdf_path)` | Metin ayıklama |
| `summarize_pdf(pdf_path, length, coverage)` | PDF özetleme |
| `summarize_image(image_path, length, coverage)` | Görsel özetleme |
| `get_user_profile(personal_books)` | Kullanıcı profili |
| `get_recommendations(profile, general_library)` | Kitap önerileri |
| `categorize_title(title)` | Başlık kategorisi |

---

## 5. Veritabanı API Referansı

### `DatabaseManager` Sınıfı

**Modül:** `mobile/app/data/database.py`  
**Veritabanı:** SQLite3

#### Şema

```sql
CREATE TABLE books (
    id          TEXT    PRIMARY KEY,          -- UUID
    title       TEXT    NOT NULL,
    author      TEXT    DEFAULT 'Bilinmiyor',
    file_path   TEXT    NOT NULL,
    book_type   TEXT    DEFAULT 'general',    -- 'general' | 'personal'
    category    TEXT    DEFAULT 'Genel',
    upload_date DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE summaries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id      TEXT    NOT NULL,
    summary_type TEXT    NOT NULL,            -- 'Kısa' | 'Orta' | 'Uzun'
    content      TEXT    NOT NULL,
    created_at   DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE (book_id, summary_type)
);
```

#### Metodlar

| Metod | İmza | Açıklama |
|-------|------|----------|
| `add_book` | `(book: Book) -> None` | Kitap ekle (duplicate yoksay) |
| `get_book` | `(book_id: str) -> Book \| None` | UUID ile kitap getir |
| `list_books` | `(source: str \| None) -> list[Book]` | Kitapları listele |
| `delete_book` | `(book_id: str) -> None` | Kitap sil (cascade) |
| `save_summary` | `(book_id, type, content) -> None` | Özet kaydet (upsert) |
| `get_summary` | `(book_id, type) -> str \| None` | Önbellekli özet getir |
| `list_summaries` | `(book_id: str) -> list[dict]` | Tüm özetleri listele |
| `seed_general_books` | `(books: Iterable[Book]) -> None` | İlk çalıştırmada seed |

---

## 6. Öneri Motoru API

### `RecommendationEngine` Sınıfı

**Modül:** `backend/recommendation/engine.py`

#### `analyze_history()`

```python
def analyze_history(personal_books: list[Book]) -> UserProfile
```

**Dönen `UserProfile`:**

| Alan | Tip | Açıklama |
|------|-----|----------|
| `character_name` | `str` | Okuyucu karakteri adı |
| `dominant_category` | `str` | En çok okunan kategori |
| `category_distribution` | `dict[str, float]` | Yüzdelik dağılım |
| `description` | `str` | Karakter açıklaması |

**Karakter Tipleri:**

| Kategori | Karakter | Açıklama |
|----------|----------|----------|
| Bilim | 🔬 Bilimkurgu Kaşifi | Analitik okuyucu |
| Tarih | 📜 Tarih Kurdu | Olayların kökenini arar |
| Dram | 💔 Duygu Gezgini | Empatik okuyucu |
| Macera | ⚔️ Aksiyon Tutkunu | Sürükleyici kurgu sever |
| Felsefe | 🧠 Düşünce Mimarı | Entelektüel okuyucu |
| Genel | 📚 Çok Yönlü Okur | Dengeli okuyucu |

#### `get_recommendations()`

```python
def get_recommendations(
    profile: UserProfile,
    general_library: list[Book]
) -> list[Book]
```

Kullanıcının dominant kategorisine göre genel kütüphaneden eşleşen kitapları döndürür. Yetersiz eşleşme durumunda diğer kategorilerden tamamlar.

---

## 7. Veri Modelleri

### `Book`

```python
@dataclass
class Book:
    title: str              # Kitap başlığı
    file_path: str          # Dosya yolu
    source: str             # "general" | "personal"
    author: str = "Bilinmiyor"
    category: str = "Genel" # Bilim|Tarih|Dram|Macera|Felsefe|Genel
    summary: str = ""
    id: str = uuid4()
    created_at: str = utcnow().isoformat()
```

### `BackendResponse`

```python
@dataclass
class BackendResponse:
    success: bool       # İşlem başarılı mı?
    message: str        # Kullanıcı mesajı
    summary: str = ""   # Oluşturulan özet
    from_cache: bool = False  # Önbellekten mi geldi?
```

### `SummaryResult` (UI Adapter)

```python
@dataclass
class SummaryResult:
    success: bool
    message: str
    summary: str = ""
    from_cache: bool = False
```

---

## 8. Hata Kodları & Mesajları

| Hata Durumu | Mesaj | Çözüm |
|-------------|-------|-------|
| API key eksik | `Mistral API key is missing...` | `.env` dosyasına key ekleyin |
| API key geçersiz | `API anahtarı çok kısa` | Mistral Console'dan yeni key alın |
| Rate limit | `İstek limiti aşıldı (10/60sn)` | 30 saniye bekleyin |
| Dosya bulunamadı | `File not found: <path>` | Dosya yolunu kontrol edin |
| Dosya çok büyük | `Dosya çok büyük (X MB)` | 50 MB altında dosya seçin |
| Desteklenmeyen format | `Desteklenmeyen dosya formatı` | PDF, TXT veya resim kullanın |
| Bağlantı hatası | `Internet connection error` | İnternet bağlantısını kontrol edin |
| Zaman aşımı | `Mistral request timed out` | Tekrar deneyin |
| Metin bulunamadı | `No readable text found` | Metin içeren PDF seçin |
| Backend yüklenemedi | `Backend manager could not be loaded` | Bağımlılıkları kurun |

---

## 9. Kullanım Örnekleri

### PDF Özetleme

```python
from backend.backend_manager import BackendManager

manager = BackendManager(
    mistral_api_key="your_key_here",
    model_name="mistral-small-latest",
)

# Kısa özet, tüm metin
result = manager.summarize_pdf(
    pdf_path="library/kitap.pdf",
    summary_length="Short",
    text_coverage="Full",
)

if result.success:
    print(result.summary)
    print(f"Cache'den mi? {result.from_cache}")
else:
    print(f"Hata: {result.message}")
```

### Görsel Özetleme

```python
result = manager.summarize_image(
    image_path="data/uploads/photo.jpg",
    summary_length="Medium",
    text_coverage="Full",
)
```

### Kullanıcı Profili & Öneriler

```python
from backend.recommendation.engine import RecommendationEngine

engine = RecommendationEngine()

# Profil oluştur
profile = engine.analyze_history(personal_books)
print(f"Karakter: {profile.character_name}")
print(f"Dağılım: {profile.category_distribution}")

# Öneri al
recommendations = engine.get_recommendations(profile, general_library)
```

### Güvenlik Kontrolü

```python
from backend.api_security import APIKeyValidator, RateLimiter, InputValidator

# API key doğrula
valid, msg = APIKeyValidator.validate(api_key)

# Dosya doğrula
valid, msg = InputValidator.validate_file_path("document.pdf")

# Başlık temizle
safe = InputValidator.sanitize_title('<script>alert("xss")</script>')
# Sonuç: "scriptalert(xss)/script"
```

---

## 10. Güvenlik En İyi Uygulamaları

### ✅ Yapılması Gerekenler

| # | Uygulama | Açıklama |
|---|----------|----------|
| 1 | `.env` kullanın | API anahtarını çevresel değişkende tutun |
| 2 | `.gitignore` kontrol | `.env` dosyasının git'e dahil olmadığını doğrulayın |
| 3 | Key rotation | API anahtarını periyodik olarak yenileyin |
| 4 | Rate limiting | Varsayılan limitleri projenize göre ayarlayın |
| 5 | Log izleme | `backend/logs/security.log` dosyasını takip edin |
| 6 | Input validation | Tüm kullanıcı girdilerini doğrulayın |

### ❌ Yapılmaması Gerekenler

| # | Anti-pattern | Risk |
|---|-------------|------|
| 1 | Kodda hardcoded API key | GitHub'da ifşa |
| 2 | `.env` commit etmek | Anahtar sızıntısı |
| 3 | Rate limit olmadan API çağrısı | Maliyet patlaması |
| 4 | Dosya yolu doğrulamadan dosya okuma | Path traversal saldırısı |
| 5 | Log'larda API key göstermek | Anahtar ifşası |

### Dosya Yapısı (Güvenlik Perspektifi)

```
SnapSum/
├── .env                    # 🔒 GİT'E DAHİL DEĞİL (gizli)
├── .env.example            # ✅ Şablon dosya (git'te)
├── .gitignore              # ✅ Güvenlik kuralları
├── backend/
│   ├── api_security.py     # 🛡️ Güvenlik modülü
│   ├── backend_manager.py  # 🔐 Güvenlik entegrasyonlu
│   ├── logs/               # 🔒 GİT'E DAHİL DEĞİL
│   │   └── security.log    # Güvenlik olayları
│   └── database/
│       └── summary_cache.json
└── mobile/
    └── app/
        └── config.py       # os.getenv() ile key okuma
```

---

> **📌 Not:** Bu dokümantasyon SnapSum v1.0 API'sini kapsar. Sorular için proje ekibine başvurun.
