# 👥 SnapSum: Görev Dağılımı ve Sorumluluklar

SnapSum projesinde ekip üyelerinin üstlendiği temel roller, sorumluluklar ve sisteme yaptıkları kritik katkılar aşağıda detaylandırılmıştır. Tüm roller ekip üyeleri arasında başarıyla koordine edilmiş ve SnapSum uygulamasının son kararlı sürümü bu görev dağılımına uygun olarak %100 çalışır ve tamamlanmış bir şekilde teslim edilmiştir.

---

### 👤 Ekip Sorumluluk Tablosu

| Ekip Üyesi | Rolü | Temel Katkıları & Sorumlulukları |
| :--- | :--- | :--- |
| **İbrahim** | **Backend & AI Developer** | Mistral AI Entegrasyonu, Chunking & Map-Reduce Tasarımı, Normalizasyon Algoritmaları, Prompt Mühendisliği. |
| **Baran** | **Database & Config Developer** | SQLite3 Tablo Tasarımları, Kalıcı Veri Erişim Katmanı, settings.json ve .env Ayarları, Cache Entegrasyonu. |
| **Elif** | **Mobile Developer (Flet)** | Reaktif Arayüz Tasarımı, Asenkron FilePicker, Navigasyon ve Sayfa Yönlendirici, Kitap Detay Modalı. |
| **Sinem** | **UI/UX Designer** | Renk Paletleri (Indigo, Rose, Slate), Cozy Cream Paper Okuyucu Teması, Kartlar ve Ergonomik Sayfa Düzeni. |
| **Fatma** | **Data Cleaning & Tester** | 18 Hazır Kitap Dosyasının Scrubbing (Temizleme) İşlemleri, Çift Dil Testleri, Kararlılık ve Edge-Case Testleri. |

---

### 👨‍💻 İbrahim (Backend Dev)
**Rol:** Backend ve Yapay Zeka Entegrasyon Lideri
*   **Yapay Zeka Entegrasyonu (Mistral & Pixtral API):** Mistral AI API bağlantılarının asenkron kurulması, metin özetlemelerinde `mistral-small-latest`, görsel/OCR analizlerinde ise `pixtral-large-latest` modellerinin sisteme entegre edilmesi.
*   **Chunking & Map-Reduce Tasarımı:** Uzun dokümanları modelin token limitlerine uygun olarak (5000-8000 karakterlik) paragraf bütünlüğünü koruyarak bölen ve parça özetlerini birleştirerek tek bir master özet üreten algoritmanın kodlanması.
*   **Prompt Mühendisliği:** Kısa, Orta ve Uzun özet seçenekleri için optimize edilmiş, sistemin Türkçe ve İngilizce çıktı vermesini sağlayan AI sistem talimatlarının (system prompts) hazırlanması.
*   **PDF/Metin Temizleme Mantığı:** `backend_manager.py` içerisinde dosyalardan gürültülü verileri (sayfa numaraları, boşluk artıkları, tablo bölücüler) regex yardımıyla ayıklayan temizleme kodlarının yazılması.

---

### 📊 Baran (Veritabanı & API)
**Rol:** Veri Yönetimi ve Yapılandırma Sorumlusu
*   **Veritabanı Yönetimi (`DatabaseManager` & SQL):** SQLite3 veritabanı şemasının kurulması, kitaplar, kullanıcı profilleri, okuma geçmişi ve çıkarılan özetler için kalıcı depolama sisteminin oluşturulması.
*   **Kütüphane Yönetim Fonksiyonları:** Arayüz üzerinden kişisel kitap ekleme ve silme süreçlerinin SQLite işlemlerini sarmalayan repository katmanının kodlanması.
*   **API Key & Konfigürasyon Yapısı:** API anahtarlarının ve dil ayarlarının yerel sistemde (`data/settings.json`) güvenli ve git-çakışmasız şekilde saklanmasını sağlayacak JSON altyapısının tasarlanması.

---

### 📱 Elif (Mobil Dev)
**Rol:** Mobil Uygulama Geliştirme (Flet UI)
*   **Reaktif Arayüz Geliştirme:** Flet framework'ünü kullanarak uygulamanın tüm ekran ve sekmelerinin (Library, Upload, Profile) dinamik ve modern Material 3 standartlarında kodlanması.
*   **Dosya Gezgini Entegrasyonu:** Kullanıcının telefon veya bilgisayar hafızasından PDF ve görselleri seçebilmesini sağlayan `FilePicker` entegrasyonunun doğrudan asenkron (async/await) yapıyla gerçekleştirilmesi.
*   **UI Navigasyonu (`main.py`):** Sekmeler arası geçişlerin, arama çubuğu filtrelemesinin, Ayarlar menüsünün ve detay/okuma ekranlarının (`book_detail_view.py` ile birlikte) entegre edilmesi.

---

### 🎨 Sinem (UI/UX)
**Rol:** Tasarım ve Kullanıcı Deneyimi Planlayıcısı
*   **Renk Paleti & Kimlik:** Uygulamaya premium bir hava katan Indigo, Rose ve Slate bazlı renk paletlerinin ve Cozy Cream Paper göz yormayan okuyucu zemin tasarımlarının belirlenmesi.
*   **Bileşen Konumlandırmaları:** Arama kutusu kapsülü, bulut yükleme alanı kartı, profil istatistik sütunları ve sekmelerin en ergonomik yerleşimlerinin planlanması.
*   **Kart & UI Tasarımları:** Kitap listelerinin, öneriler alanının, geçiş animasyonlarının ve dialog pencerelerinin görsel standartlarının hazırlanması.

---

### 📸 Fatma (Veri İşleme & Test)
**Rol:** Veri Kalitesi ve Kararlılık Analisti
*   **Kitap Metinlerinin Hazırlanması:** Genel kütüphanede (`cleaned_texts` klasöründe) varsayılan olarak sunulacak 18 adet klasik kitabın düz metin (.txt) dosyalarının hazırlanması ve sisteme yerleştirilmesi.
*   **Döküman Temizleme:** PDF ve metin kaynaklarındaki tablo çizgileri, görsel artıkları ve sayfa gürültülerinin temizlenerek sisteme saf metin olarak entegre edilmesi.
*   **Test ve Kalite Kontrol:** Uygulamanın farklı boyutlardaki PDF/TXT/Görsel dosya türleriyle kararlılık testlerinin yapılması ve sistemin genel olarak test edilmesi.

---

> **Not:** Tüm roller ekip üyeleri arasında başarıyla koordine edilmiş ve SnapSum uygulamasının son kararlı sürümü %100 çalışan bir şekilde bu görev dağılımına uygun olarak tamamlanmıştır.
