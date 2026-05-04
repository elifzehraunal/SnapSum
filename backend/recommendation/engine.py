"""Recommendation engine for assigning user characters and suggesting books."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass
class UserProfile:
    """Represents the generated profile of the user."""

    character_name: str
    dominant_category: str
    category_distribution: dict[str, float]
    description: str


class RecommendationEngine:
    """Analyzes reading history to build a profile and recommend books."""

    # Karakter isimleri ve açıklamaları
    CHARACTERS = {
        "Bilim": {
            "name": "Bilimkurgu Kaşifi",
            "desc": "Evrenin sırlarına ve geleceğin teknolojilerine meraklı, analitik bir okuyucu.",
        },
        "Tarih": {
            "name": "Tarih Kurdu",
            "desc": "Geçmişin tozlu sayfalarında dolaşmayı seven, olayların kökenini arayan okuyucu.",
        },
        "Dram": {
            "name": "Duygu Gezgini",
            "desc": "İnsan psikolojisini ve derin duygusal hikayeleri özümseyen empatik okuyucu.",
        },
        "Macera": {
            "name": "Aksiyon Tutkunu",
            "desc": "Heyecan verici serüvenlerin ve sürükleyici kurguların peşinden giden okuyucu.",
        },
        "Felsefe": {
            "name": "Düşünce Mimarı",
            "desc": "Hayatın anlamını sorgulayan, derin fikirleri inceleyen entelektüel okuyucu.",
        },
        "Genel": {
            "name": "Çok Yönlü Okur",
            "desc": "Her türden eseri okumayı seven, geniş bir perspektife sahip dengeli okuyucu.",
        },
    }

    def analyze_history(self, personal_books: list[Any]) -> UserProfile:
        """Analyze a list of books and determine the user's reading character."""
        if not personal_books:
            return UserProfile(
                character_name="Yeni Okur",
                dominant_category="Genel",
                category_distribution={},
                description="Henüz yeterli okuma geçmişin yok. Keşfetmeye başla!",
            )

        categories = [getattr(book, "category", "Genel") for book in personal_books]
        counts = Counter(categories)
        total = sum(counts.values())

        distribution = {cat: round((count / total) * 100, 1) for cat, count in counts.items()}
        dominant_category = counts.most_common(1)[0][0]

        char_info = self.CHARACTERS.get(
            dominant_category, 
            {"name": "Gizemli Okur", "desc": "Özgün zevkleri olan bir okuyucu."}
        )

        return UserProfile(
            character_name=char_info["name"],
            dominant_category=dominant_category,
            category_distribution=distribution,
            description=char_info["desc"],
        )

    def get_recommendations(self, profile: UserProfile, general_library: list[Any]) -> list[Any]:
        """Return books from general library that match the user's dominant category."""
        if not general_library:
            return []

        if profile.character_name == "Yeni Okur":
            # Yeni okurlara her kategoriden rastgele veya karma öneriler verilebilir.
            # Şimdilik genel listeden ilk 5 kitabı dönüyoruz.
            return general_library[:5]

        # Önce dominant kategoriye uyanları bul
        recommended = [
            book for book in general_library 
            if getattr(book, "category", "Genel") == profile.dominant_category
        ]

        # Eğer o kategoride yeterli kitap yoksa, genel kitaplarla tamamla
        if len(recommended) < 3:
            others = [b for b in general_library if b not in recommended]
            recommended.extend(others[: 3 - len(recommended)])

        return recommended
