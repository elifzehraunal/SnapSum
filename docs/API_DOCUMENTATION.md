# 🔌 SnapSum: API and Architectural Integration Reference

This document provides a highly detailed, technical reference of all API layers, artificial intelligence integration protocols (Mistral & Pixtral), SQLite database schemas, security validation modules, and local configuration standards utilized in the **SnapSum** project. It is designed to facilitate seamless data communication between frontend and backend developers.

---

## 📑 Table of Contents
1. [🔌 AI API Integration (Mistral AI & Pixtral)](#1-ai-api-integration-mistral-ai--pixtral)
2. [⚙️ Backend Module API (BackendManager Reference)](#2-backend-module-api-backendmanager-reference)
3. [💾 Database API and Schemas (DatabaseManager)](#3-database-api-and-schemas-databasemanager)
4. [🛡️ Security and Validation API (api_security.py)](#4-security-and-validation-api-api_securitypy)
5. [📦 Local Settings and Configuration (Settings API)](#5-local-settings-and-configuration-settings-api)

---

## 1. AI API Integration (Mistral AI & Pixtral)

SnapSum uses the asynchronous-ready **Mistral AI HTTP REST API** as its core intelligence layer for processing texts and images.

### 📡 API Endpoint
*   **POST** `https://api.mistral.ai/v1/chat/completions`

### 🧠 LLM Models Used
*   **Text Summarization (Text):** `mistral-small-latest` (Offers high speed, low latency, exceptional Turkish/English capability, and optimized token costs).
*   **Image & OCR Analysis (Vision):** `pixtral-large-latest` (Utilized for multimodal image analysis, book cover text recognition, and page extraction).

### 🛠️ HTTP Request Headers
```json
{
  "Authorization": "Bearer <MISTRAL_API_KEY>",
  "Content-Type": "application/json"
}
```

---

## 2. Backend Module API (BackendManager Reference)

The `BackendManager` class, implemented inside `backend/backend_manager.py`, wraps all the business logic, PyMuPDF text extractions, normalizations, paragraph chunking, and the AI Map-Reduce summarization execution.

### 🔑 Constructor Signature
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

### 📡 Class Methods Reference

#### `summarize_pdf(pdf_path, summary_length, text_coverage="Full") -> BackendResponse`
Handles the entire summarization request flow (cache lookup ➔ text extraction ➔ normalization ➔ paragraph-aware chunking ➔ Map-Reduce API requests ➔ SQLite storage persistence).
*   **Parameters:**
    *   `pdf_path (str | Path)`: The absolute file path to the target PDF or TXT file.
    *   `summary_length (str)`: Desired summary size; accepts `"Short"`, `"Medium"`, or `"Long"` (supports Turkish inputs `"kısa"`, `"orta"`, `"uzun"` dynamically).
    *   `text_coverage (str)`: Processes `"Quarter"`, `"Half"`, or `"Full"` document scope.
*   **Return Type:** Returns a `BackendResponse` dataclass:
    ```python
    @dataclass
    class BackendResponse:
        success: bool
        message: str
        summary: str = ""
        from_cache: bool = False
    ```

#### `summarize_image(image_path, summary_length, text_coverage="Full") -> BackendResponse`
Encodes the target image file into base64 and performs OCR-guided vision summarization using the Pixtral Vision model.
*   **Parameters:**
    *   `image_path (str | Path)`: The absolute file path to the target image file (`.png`, `.jpg`, `.jpeg`, etc.).
    *   `summary_length (str)`: Desired summary size; accepts `"Short"`, `"Medium"`, or `"Long"`.
*   **Return Type:** Returns a `BackendResponse` detailing success/failure, text output, and cache hit metrics.

#### `extract_plain_text(pdf_path: str | Path) -> str`
Detects the file extension. If the file is a plain `.txt` file, it reads it directly with UTF-8 encoding. If it is a `.pdf` file, it extracts clean plain text using `PyMuPDF (fitz)` and sends it to the regex text normalizer.

#### `chunk_text(text: str) -> list[str]`
Segments long text streams into balanced blocks of 5,000–8,000 characters while strictly respecting paragraph boundaries (`\n\n`) to prevent truncation of conceptual blocks. If a single paragraph exceeds the maximum size limit, it falls back to a character-based splitting mechanism safely.

#### `categorize_title(title: str) -> str`
Analyzes a book's title via a quick Mistral zero-shot prompt to categorize the document under one of the primary archetypes: `"Bilim"`, `"Tarih"`, `"Dram"`, `"Macera"`, `"Felsefe"`, or `"Genel"`.

---

## 3. Database API and Schemas (DatabaseManager)

The local SQLite3 storage engine resides in `mobile/app/data/database.py` and is saved locally at `data/snapsum.db`.

### 📊 SQL Table Schemas

#### 1. `books` (Library Registry Table)
Maintains all general (preloaded) and personal (user-uploaded) book details, summaries, and categories.
```sql
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    source TEXT NOT NULL,       -- 'general' or 'personal'
    summary TEXT,               -- The compiled Master Summary
    category TEXT DEFAULT 'Genel',
    language TEXT DEFAULT 'tr', -- Interface language; 'tr' or 'en'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. `reading_history` (Reading Log Table)
Logs all user reading activities to supply the personalized reader archetype suggestion engine.
```sql
CREATE TABLE IF NOT EXISTS reading_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
);
```

---

## 4. Security and Validation API (api_security.py)

The defensive security suite implemented inside `backend/api_security.py` acts as a request firewall protecting SnapSum from system exploits and credential leaks.

### 🛡️ Core Security Providers

#### 1. `APIKeyValidator`
*   **`validate_format(key: str) -> bool`:** Evaluates API key strings using character lengths and standard vendor headers to verify validity before calling the endpoints.
*   **`mask_key(key: str) -> str`:** Redacts sensitive credentials in security audits and logs (e.g., masking `MSTR_xyz...92r` as `MSTR****92r`).

#### 2. `InputValidator`
*   **`validate_file(file_path: Path, max_size_mb: int = 50) -> tuple[bool, str]`:** Enforces file size limitations, restricts file extensions to authorized types (`.pdf`, `.txt`, `.png`, `.jpg`, `.jpeg`), and validates absolute paths to protect the host machine against **Path Traversal** and malicious **Symbolic Link** redirects.
*   **`sanitize_string(input_str: str) -> str`:** Strips structural HTML, CSS, and script tags from book titles and search keywords to mitigate **XSS (Cross-Site Scripting)** exploits.

#### 3. `RateLimiter`
*   **`allow_request(client_id: str) -> bool`:** Utilizes a Token Bucket rate limiting algorithm to cap outbound requests at a safe maximum of 10 API queries per minute per instance.

---

## 5. Local Settings and Configuration (Settings API)

User-specific configurations (including the API key and UI/summary language preferences) are stored outside the Git repository in a localized `data/settings.json` file for maximum security.

### 📁 settings.json Schema
```json
{
  "mistral_api_key": "YOUR_MISTRAL_API_KEY_HERE",
  "language": "tr"
}
```

*   **Credential Search Order (Priority):**
    1.  **`data/settings.json`:** The system always checks local settings first to see if a custom `mistral_api_key` has been saved via the UI.
    2.  **`.env` file:** If local settings are empty, the backend falls back to checking the system environment variable `MISTRAL_API_KEY` defined in the root directory.
