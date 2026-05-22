# 🔌 SnapSum: API ve Mimari Entegrasyon Dökümantasyonu

Bu döküman, SnapSum projesinin sahip olduğu tüm API katmanlarını, yapay zeka entegrasyon protokollerini (Mistral & Pixtral), veritabanı şemasını ve güvenlik katmanlarını detaylandırmaktadır. Ekip üyelerinin backend, frontend ve veritabanı arasındaki veri akışını kolaylıkla takip etmesi için tasarlanmıştır.

---

## 📑 İçindekiler
1. [Yapay Zeka API Entegrasyonu (Mistral AI)](#1-yapay-zeka-api-entegrasyonu-mistral-ai)
2. [Arka-Yüz Modül API (BackendManager)](#2-arka-yüz-modül-api-backendmanager)
3. [Veritabanı API ve Şeması (DatabaseManager)](#3-veritabanı-api-ve-şeması-databasemanager)
4. [Güvenlik ve Validasyon API (api_security.py)](#4-güvenlik-ve-validasyon-api-api_securitypy)
5. [Yerel Ayarlar Yapılandırması (Settings API)](#5-yerel-ayarlar-yapılandırması-settings-api)

---

## 1. Yapay Zeka API Entegrasyonu (Mistral AI)

SnapSum, tüm metin ve görsel işleme operasyonlarında **Mistral AI HTTP REST API** altyapısını kullanmaktadır.

### 🔌 API Uç Noktası (Endpoint)
- **POST** `https://api.mistral.ai/v1/chat/completions`

### 🧠 Kullanılan LLM Modelleri
- **Metin Özetleme (Text):** `mistral-small-latest` (Yüksek hız, düşük maliyet ve yüksek dil uyumluluğu).
- **Görsel/Fotoğraf OCR Analizi (Vision):** `pixtral-large-latest` (Görsel bazlı metin okuma ve detay çıkarma).

### 🛠️ HTTP Başlıkları (Headers)
```json
{
  "Authorization": "Bearer <MISTRAL_API_KEY>",
  "Content-Type": "application/json"
}
```

---

## 2. Arka-Yüz Modül API (BackendManager)

`backend/backend_manager.py` içerisinde tanımlanan `BackendManager` sınıfı, uygulamanın ana iş mantığını ve LLM isteklerini sarmalar.

### 🔑 Temel Sınıf Yapılandırıcı (Constructor)
```python
def __init__(
    self,
    cache_path: str | Path = "backend/database/summary_cache.json",
    mistral_api_key: str | None = None,
    model_name: str = "mistral-small-latest",
    chunk_min: int = 20_000,
    chunk_max: int = 30_000,
) -> None
```

### 📡 API Metotları ve İmzaları

#### `summarize_pdf(pdf_path, summary_length, text_coverage="Full") -> BackendResponse`
Bu metot tüm özetleme akışını yönetir (önbellek kontrolü -> metin ayıklama -> chunking -> Map-Reduce).
- **Parametreler:**
  - `pdf_path (str | Path)`: Özetlenecek PDF veya TXT dosyasının absolute yolu.
  - `summary_length (str)`: `"kısa"` ("Short"), `"orta"` ("Medium"), `"uzun"` ("Long") değerlerini alabilir.
  - `text_coverage (str)`: `"çeyrek"`, `"yarım"` veya `"tam"` özetleme kapsamı.
- **Dönen Değer:** `BackendResponse` (success: bool, message: str, summary: str, from_cache: bool).

#### `extract_plain_text(pdf_path: str | Path) -> str`
Verilen dosya uzantısını kontrol eder, `.txt` ise doğrudan okur, `.pdf` ise `PyMuPDF (fitz)` ile saf metin ayıklar ve normalize eder.

#### `chunk_text(text: str) -> list[str]`
Uzun metinleri paragraf bütünlüğünü koruyarak `chunk_min` ve `chunk_max` sınırları arasında anlamlı parçalara böler.

#### `categorize_title(title: str) -> str`
Mistral API aracılığıyla kitap başlığını analiz ederek `"Bilim"`, `"Tarih"`, `"Dram"`, `"Macera"`, `"Felsefe"`, `"Genel"` kategorilerinden birini döndürür.

---

## 3. Veritabanı API ve Şeması (DatabaseManager)

SQLite3 yerel veritabanı altyapısı `mobile/app/data/database.py` modülü altında programlanmıştır ve yerel olarak `data/snapsum.db` dosyasında saklanır.

### 📊 Tablo Şemaları

#### 1. `books` (Kütüphane Tablosu)
Sistemdeki hazır ve kişisel olarak yüklenen tüm kitapların kayıtlarını saklar.
```sql
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    source TEXT NOT NULL,       -- 'general' veya 'personal'
    summary TEXT,               -- Üretilen özet
    category TEXT DEFAULT 'Genel',
    language TEXT DEFAULT 'tr',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. `reading_history` (Okuma Geçmişi Tablosu)
Kullanıcının okuduğu kitapları ve öneri motorunun analiz edeceği istatistikleri tutar.
```sql
CREATE TABLE IF NOT EXISTS reading_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
);
```

---

## 4. Güvenlik ve Validasyon API (api_security.py)

`backend/api_security.py` modülü, uygulamanın dış tehditlerden korunmasını ve API anahtarlarının güvenliğini üstlenir.

### 🛡️ Sağlanan API Koruma Servisleri

#### 1. `APIKeyValidator`
- **`validate_format(key: str) -> bool`:** API anahtarının geçerli Mistral formatında olup olmadığını kontrol eder.
- **`mask_key(key: str) -> str`:** Log kayıtlarında güvenlik amacıyla API anahtarını maskeler (Örn: `QBGLX****r8k`).

#### 2. `InputValidator`
- **`validate_file(file_path: Path, max_size_mb: int = 50) -> tuple[bool, str]`:** Yüklenen dosyanın uzantısını denetler (`.pdf`, `.txt`, `.png`, `.jpg`, `.jpeg`), dosya boyutunu sınırlar ve **Path Traversal / Symbolic Link** açıklarına karşı koruma sağlar.
- **`sanitize_string(input_str: str) -> str`:** Kitap başlığı ve yazar adlarındaki XSS (HTML/Script) girdilerini temizler.

#### 3. `RateLimiter`
- **`allow_request(client_id: str) -> bool`:** Token Bucket algoritması kullanarak kullanıcıların dakikada maksimum 10 API çağrısı yapmasını sınırlandırır.

---

## 5. Yerel Ayarlar Yapılandırması (Settings API)

Kullanıcının API anahtarı, arayüz dil tercihi gibi hassas ve yerel konfigürasyonları git güvenliği amacıyla yerel diskte `data/settings.json` formatında saklanır.

### 📁 settings.json Şeması
```json
{
  "mistral_api_key": "YOUR_MISTRAL_API_KEY_HERE",
  "language": "tr"
}
```

- **Lokal Erişim Önceliği:** Uygulama çalışırken özetleme isteklerinde öncelikle `data/settings.json` içerisindeki `mistral_api_key` değeri okunur. Eğer boşsa, kök dizindeki `.env` dosyasında yer alan `MISTRAL_API_KEY` değeri fallback olarak devreye girer.
