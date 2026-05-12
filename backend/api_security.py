"""SnapSum API Security Module.

Bu modül Mistral API anahtarını koruma altına almak ve kötüye
kullanımı engellemek için çeşitli güvenlik katmanları sunar:

- API anahtarı doğrulama ve maskeleme
- Rate limiting (istek hız sınırlama)
- Input validation (girdi doğrulama)
- Güvenlik loglaması
- Dosya yolu sanitizasyonu
"""

from __future__ import annotations

import logging
import os
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ── Güvenlik Logger'ı ──
_log_dir = Path(__file__).resolve().parent / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)

_formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)-8s %(name)s → %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_file_handler = logging.FileHandler(_log_dir / "security.log", encoding="utf-8")
_file_handler.setFormatter(_formatter)

security_logger = logging.getLogger("snapsum.security")
security_logger.setLevel(logging.INFO)
security_logger.addHandler(_file_handler)


# ═══════════════════════════════════════════════════════════════
#  API Key Validator
# ═══════════════════════════════════════════════════════════════
class APIKeyValidator:
    """API anahtarının varlığını, formatını ve güvenliğini doğrular."""

    MIN_KEY_LENGTH = 20

    @staticmethod
    def validate(api_key: str | None) -> tuple[bool, str]:
        """API anahtarını doğrula.

        Returns:
            (is_valid, message) tuple'ı.
        """
        if not api_key:
            security_logger.warning("API key is missing or empty.")
            return False, "MISTRAL_API_KEY tanımlı değil. .env dosyasını kontrol edin."

        if len(api_key) < APIKeyValidator.MIN_KEY_LENGTH:
            security_logger.warning("API key is too short (%d chars).", len(api_key))
            return False, "API anahtarı çok kısa. Geçerli bir Mistral API key giriniz."

        # Basit format doğrulaması — alfanümerik karakter kontrolü
        if not re.match(r"^[A-Za-z0-9_\-]+$", api_key):
            security_logger.warning("API key contains invalid characters.")
            return False, "API anahtarı geçersiz karakterler içeriyor."

        security_logger.info("API key validated successfully (masked: %s).", APIKeyValidator.mask(api_key))
        return True, "API anahtarı geçerli."

    @staticmethod
    def mask(api_key: str) -> str:
        """API anahtarının sadece son 4 karakterini göster, geri kalanını gizle.

        Örn: QBGLXGpod4vPjdq... → ****...r8k
        """
        if not api_key or len(api_key) < 8:
            return "****"
        return f"{'*' * (len(api_key) - 4)}{api_key[-4:]}"

    @staticmethod
    def is_exposed_in_file(filepath: str | Path) -> bool:
        """Verilen dosyada hardcoded API anahtarı olup olmadığını kontrol eder.

        Bu fonksiyon pre-commit hook veya CI/CD pipeline'larında kullanılabilir.
        """
        path = Path(filepath)
        if not path.exists():
            return False

        content = path.read_text(encoding="utf-8", errors="replace")
        # Mistral API key pattern: uzun alfanümerik string
        patterns = [
            r"MISTRAL_API_KEY\s*=\s*['\"]?[A-Za-z0-9_\-]{20,}['\"]?",
            r"Bearer\s+[A-Za-z0-9_\-]{20,}",
            r"api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}['\"]?",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # .env dosyası ve placeholder'lar hariç tut
                if "sizin_api" in match or "your_api" in match or "os.getenv" in match:
                    continue
                if path.name == ".env":
                    continue  # .env dosyasında olması normal
                security_logger.critical(
                    "EXPOSED API KEY detected in %s: %s",
                    filepath,
                    APIKeyValidator.mask(match),
                )
                return True
        return False


# ═══════════════════════════════════════════════════════════════
#  Rate Limiter
# ═══════════════════════════════════════════════════════════════
@dataclass
class RateLimitConfig:
    """Rate limiting yapılandırması."""

    max_requests: int = 10           # Pencere başına max istek
    window_seconds: float = 60.0     # Zaman penceresi (saniye)
    cooldown_seconds: float = 30.0   # Limit aşıldığında bekleme süresi


class RateLimiter:
    """Token bucket tabanlı istek hız sınırlayıcı.

    Mistral API'sine gönderilen istek sayısını kontrol ederek:
    - Yanlışlıkla yapılan çok fazla istek (UI bug'ları vs.) engellenir.
    - API maliyetleri kontrol altında tutulur.
    - Kötüye kullanım önlenir.
    """

    def __init__(self, config: RateLimitConfig | None = None) -> None:
        self.config = config or RateLimitConfig()
        self._requests: list[float] = []
        self._cooldown_until: float = 0.0

    def allow_request(self) -> tuple[bool, str]:
        """İstek yapılmasına izin verilip verilmediğini kontrol eder.

        Returns:
            (allowed, message) tuple'ı.
        """
        now = time.time()

        # Cooldown süresi devam ediyorsa reddet
        if now < self._cooldown_until:
            remaining = int(self._cooldown_until - now)
            security_logger.warning("Rate limit cooldown active. %ds remaining.", remaining)
            return False, f"Çok fazla istek gönderildi. Lütfen {remaining} saniye bekleyin."

        # Eski istekleri temizle (pencere dışında kalanlar)
        cutoff = now - self.config.window_seconds
        self._requests = [t for t in self._requests if t > cutoff]

        # Limit kontrolü
        if len(self._requests) >= self.config.max_requests:
            self._cooldown_until = now + self.config.cooldown_seconds
            security_logger.warning(
                "Rate limit exceeded: %d requests in %.0fs. Cooldown: %.0fs.",
                len(self._requests),
                self.config.window_seconds,
                self.config.cooldown_seconds,
            )
            return False, (
                f"İstek limiti aşıldı ({self.config.max_requests} istek/"
                f"{int(self.config.window_seconds)}sn). "
                f"Lütfen {int(self.config.cooldown_seconds)} saniye bekleyin."
            )

        # İzin ver ve kaydet
        self._requests.append(now)
        return True, "OK"

    @property
    def remaining_requests(self) -> int:
        """Pencere içinde kalan istek hakkı."""
        now = time.time()
        cutoff = now - self.config.window_seconds
        active = [t for t in self._requests if t > cutoff]
        return max(0, self.config.max_requests - len(active))

    def reset(self) -> None:
        """Rate limiter'ı sıfırlar (test amaçlı)."""
        self._requests.clear()
        self._cooldown_until = 0.0


# ═══════════════════════════════════════════════════════════════
#  Input Validator
# ═══════════════════════════════════════════════════════════════
class InputValidator:
    """Kullanıcı girdilerini doğrular ve sanitize eder."""

    # İzin verilen dosya uzantıları
    ALLOWED_DOCUMENT_EXT = {".pdf", ".txt"}
    ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    ALLOWED_ALL_EXT = ALLOWED_DOCUMENT_EXT | ALLOWED_IMAGE_EXT

    # Maks dosya boyutu (50 MB)
    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024

    # Geçerli özet tipleri
    VALID_SUMMARY_LENGTHS = {"Short", "Medium", "Long"}
    VALID_TEXT_COVERAGES = {"Quarter", "Half", "Full"}

    @staticmethod
    def validate_file_path(file_path: str | Path) -> tuple[bool, str]:
        """Dosya yolunu doğrula ve güvenlik kontrolü yap."""
        path = Path(file_path)

        if not path.exists():
            return False, f"Dosya bulunamadı: {path.name}"

        if not path.is_file():
            return False, f"Geçersiz dosya yolu: {path.name}"

        # Uzantı kontrolü
        ext = path.suffix.lower()
        if ext not in InputValidator.ALLOWED_ALL_EXT:
            return False, (
                f"Desteklenmeyen dosya formatı: {ext}. "
                f"İzin verilen: {', '.join(sorted(InputValidator.ALLOWED_ALL_EXT))}"
            )

        # Boyut kontrolü
        file_size = path.stat().st_size
        if file_size > InputValidator.MAX_FILE_SIZE_BYTES:
            max_mb = InputValidator.MAX_FILE_SIZE_BYTES / (1024 * 1024)
            return False, f"Dosya çok büyük ({file_size / 1024 / 1024:.1f} MB). Maks: {max_mb:.0f} MB."

        if file_size == 0:
            return False, "Dosya boş."

        # Path traversal saldırısı kontrolü
        try:
            resolved = path.resolve()
            # Sembolik link kontrolü
            if path.is_symlink():
                security_logger.warning("Symbolic link detected: %s -> %s", path, resolved)
                return False, "Güvenlik: Sembolik linkler desteklenmiyor."
        except (OSError, ValueError) as e:
            return False, f"Dosya yolu çözümlenemedi: {e}"

        return True, "Dosya geçerli."

    @staticmethod
    def validate_summary_params(
        summary_length: str,
        text_coverage: str = "Full",
    ) -> tuple[bool, str]:
        """Özetleme parametrelerini doğrular."""
        if summary_length not in InputValidator.VALID_SUMMARY_LENGTHS:
            return False, (
                f"Geçersiz özet uzunluğu: '{summary_length}'. "
                f"Geçerli değerler: {', '.join(InputValidator.VALID_SUMMARY_LENGTHS)}"
            )

        if text_coverage not in InputValidator.VALID_TEXT_COVERAGES:
            return False, (
                f"Geçersiz metin kapsamı: '{text_coverage}'. "
                f"Geçerli değerler: {', '.join(InputValidator.VALID_TEXT_COVERAGES)}"
            )

        return True, "Parametreler geçerli."

    @staticmethod
    def sanitize_title(title: str) -> str:
        """Kitap başlığını güvenli hale getirir."""
        if not title:
            return "Untitled"

        # HTML injection ve script enjeksiyonunu önle
        sanitized = re.sub(r"[<>\"'&;]", "", title)
        # Fazla boşlukları temizle
        sanitized = re.sub(r"\s+", " ", sanitized).strip()
        # Makul uzunluk limiti
        return sanitized[:200] if len(sanitized) > 200 else sanitized


# ═══════════════════════════════════════════════════════════════
#  Security Audit
# ═══════════════════════════════════════════════════════════════
class SecurityAudit:
    """Güvenlik olaylarını izler ve raporlar."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def log_api_call(
        self,
        endpoint: str,
        success: bool,
        response_time_ms: float = 0.0,
        error: str | None = None,
    ) -> None:
        """API çağrısını kaydet."""
        event = {
            "timestamp": time.time(),
            "type": "api_call",
            "endpoint": endpoint,
            "success": success,
            "response_time_ms": round(response_time_ms, 2),
        }
        if error:
            event["error"] = error

        self._events.append(event)
        if success:
            security_logger.info(
                "API call to %s succeeded (%.0fms).", endpoint, response_time_ms
            )
        else:
            security_logger.error(
                "API call to %s failed: %s (%.0fms).", endpoint, error, response_time_ms
            )

    def log_security_event(self, event_type: str, detail: str) -> None:
        """Güvenlik olayı kaydet."""
        self._events.append({
            "timestamp": time.time(),
            "type": event_type,
            "detail": detail,
        })
        security_logger.warning("Security event [%s]: %s", event_type, detail)

    def get_summary(self) -> dict[str, Any]:
        """Güvenlik özeti döndürür."""
        total = len(self._events)
        api_calls = [e for e in self._events if e["type"] == "api_call"]
        failed = [e for e in api_calls if not e.get("success")]
        security_events = [e for e in self._events if e["type"] != "api_call"]

        return {
            "total_events": total,
            "api_calls": len(api_calls),
            "failed_calls": len(failed),
            "security_events": len(security_events),
            "avg_response_ms": (
                round(sum(e.get("response_time_ms", 0) for e in api_calls) / len(api_calls), 2)
                if api_calls
                else 0
            ),
        }
