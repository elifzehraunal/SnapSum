# SnapSum: Proje Detayları ve Teknik Dökümantasyon

SnapSum, akademik ve edebi metinlerin hızlıca özetlenmesini, görseller üzerinden OCR analizi yapılabilmesini, çift dil desteği sunmasını ve kullanıcı okuma geçmişine göre kişiselleştirilmiş kitap önerileri verilmesini sağlayan modern ve reaktif bir mobil/masaüstü platformdur.

---

## 🏗️ Sistem Mimarisi

Proje, modern, modüler ve güvenli bir katmanlı yapı üzerine inşa edilmiştir. Temel olarak iki ana bileşenden oluşur:

### 1. Backend (Python & Yapay Zeka Core)
Backend tarafı, verilerin işlenmesi, normalizasyon, güvenlik denetimi, yapay zeka entegrasyonu ve iş mantığının yürütülmesinden sorumludur.

- **Metin İşleme (PDF & TXT Parsing):** `.txt` dosyaları doğrudan UTF-8 formatında okunurken, `.pdf` dosyalarından `PyMuPDF (fitz)` kütüphanesi kullanılarak saf metin ayıklanır. Sayfa numaraları, boşluk artıkları ve tablo çizgileri regex kurallarıyla temizlenerek gürültüsüz bir metin elde edilir.
- **Parçalama Algoritması (Chunking):** Uzun metinler, Mistral API'nin token limitlerine ve en yüksek doğruluk oranlarına uygun şekilde (5000-8000 karakterlik) paragraf yapısını koruyan asıllı parçalara bölünür.
- **Yapay Zeka Servisleri (Mistral & Pixtral API):** Yapay zeka motoru olarak tamamen Mistral AI entegre edilmiştir. Metin özetlemelerinde `mistral-small-latest`, görsel/OCR özetlemelerinde ise `pixtral-large-latest` modelleri kullanılır. "Map-Reduce" stratejisi ile her parça önce ayrı ayrı özetlenir, ardından bu özetler birleştirilerek bütüncül bir ana özet (Master Summary) oluşturulur.
- **Önbellekleme (Cache):** Aynı döküman için tekrar özet istenmesi durumunda, sistem SHA-256 tabanlı bir yerel cache (`summary_cache.json`) ve SQLite önbelleği üzerinden anında yanıt verir.
- **Güvenlik Katmanı (`api_security.py`):** Token Bucket rate limiter, path traversal ve XSS girdi sanitizasyonu ile API anahtarı format doğrulayıcı maskeleme işlemlerini yürütür.

### 2. Mobil Uygulama (Flet Frontend)
Kullanıcı arayüzü, Python tabanlı ve asenkron yapıya tam uyumlu **Flet** framework'ü ile geliştirilmiştir.

- **Genel Kütüphane:** Sisteme kayıtlı hazır kitapların (Fatma tarafından hazırlanan 18 kitap) listelendiği, arama çubuğu ve dil filtrelemesi içeren alan.
- **Şahsi Kütüphanem:** Kullanıcının kendi yüklediği dökümanların (PDF, TXT, PNG, JPG, JPEG) yönetildiği alan.
- **Yükleme Alanı:** Dosyaların `FilePicker` doğrudan asenkron (async/await) çağrısıyla sisteme dahil edildiği sürükle-bırak görsel göstergeli reaktif panel.
- **Özet Kontrolleri:** Kısa, Orta ve Uzun seçenekleri ve Türkçe/İngilizce çift dil desteği ile kişiselleştirilebilir özetleme deneyimi.
- **Okuma Alanı:** Gözü yormayan Cozy Cream Paper zemin rengi, akıcı kaydırma ve genişletilebilir özet paneli.
- **Profil ve Öneri Alanı:** Kullanıcının okuma geçmişine göre çıkarılan Okur Karakteri analizi ("🔬 Bilimkurgu Kaşifi", "🧠 Düşünce Mimarı" vb.) ve karakterine uygun yapay zeka destekli kitap önerileri.

---

## 👥 Ekip ve Görev Dağılımı

Projemiz, her biri belirli alanlarda uzmanlaşmış 5 kişilik bir ekip tarafından başarıyla yürütülmüş ve tamamlanmıştır:

| Üye | Rol | Temel Sorumluluklar |
| :--- | :--- | :--- |
| **İbrahim** | Backend Dev | Yapay Zeka entegrasyonu (Mistral API), Chunking & Map-Reduce algoritması tasarımı, prompt mühendisliği ve PDF/Metin temizleme mantığı (`backend_manager.py`). |
| **Baran** | Veritabanı & API | Uygulama verilerinin SQLite üzerinde yönetimi (`DatabaseManager`), kütüphane ekleme/silme fonksiyonları ve API key konfigürasyonu. |
| **Elif** | Mobil Dev | Flet framework ile uygulamanın mobil/masaüstü reaktif arayüzünün (Library, Upload, Profile sekmeleri) geliştirilmesi, dosya gezgini entegrasyonu ve uygulamanın genel UI navigasyonu (`main.py` ve bileşenler). |
| **Sinem** | UI/UX | Uygulamanın renk paletleri, bileşenlerin konumlandırmaları, kart tasarımları ve genel kullanıcı deneyiminin planlanması. |
| **Fatma** | Veri İşleme & Test | Hazır kütüphanede (`cleaned_texts`) bulunacak kitap metinlerinin hazırlanmesi, temizlenmesi ve sistemin farklı dosya türleri/büyüklükleriyle test edilmesi. |

---

## 📅 Tamamlanan Yol Haritası (Completed Roadmap)

Uygulamanın son kararlı sürümünde aşağıdaki kritik özellikler başarıyla hayata geçirilmiştir:

1. **Tam SQLite Veritabanı Entegrasyonu (%100):** SQLite3 kullanılarak kitaplar, çıkarılan özetler, dil tercihleri ve kullanıcı profili kalıcı olarak yerel veritabanında (`snapsum.db`) depolanmaktadır.
2. **Dinamik Okur Karakteri ve Öneri Algoritması (%100):** Kullanıcının okuduğu kitapların kategorileri analiz edilerek dinamik okur profilleri atanmakta ve buna uygun yapay zeka destekli kitap önerileri sunulmaktadır.
3. **Pixtral Vision & OCR Entegrasyonu (%100):** Kullanıcılar artık kitap kapağı veya sayfa fotoğraflarını yükleyerek Pixtral API sayesinde doğrudan yapay zekayla OCR analizi ve görsel özetlemesi alabilmektedir.
4. **Çift Dil Desteği (%100):** Uygulama arayüzü, özetler ve öneriler Türkçe ve İngilizce dilleri arasında dinamik olarak senkronize çalışmaktadır.
5. **Asenkron FilePicker Devrimi (%100):** Mobil dosya seçme işlemleri doğrudan asenkron `await picker.pick_files()` çağrısıyla stabilize edilmiş, çökme ve donmalar tamamen giderilmiştir.

---

## 📁 Dizin Yapısı ve Dosya Amaçları

- `backend/backend_manager.py`: Tüm iş mantığının (business logic), LLM çağrılarının ve normalizasyonun toplandığı ana backend yöneticisi.
- `backend/api_security.py`: Güvenlik duvarı, rate limiter ve girdi doğrulamalarını gerçekleştiren güvenlik katmanı.
- `mobile/main.py`: Uygulamanın giriş noktası, arayüz kurulumu ve sayfa yönlendiricisi.
- `mobile/app/ui/theme.py`: Premium Indigo/Rose/Slate Material 3 tema tanımlamalarını içeren stil dosyası.
- `cleaned_texts/`: Fatma tarafından hazırlanan ve genel kütüphaneyi besleyen 18 adet düz metin kitap dosyası.
- `data/snapsum.db`: Baran tarafından tasarlanan SQLite3 yerel veritabanı.

---

> **Not:** Veritabanı bağlantısı ve yerel depolama altyapısı tamamen kurulmuş olup, uygulama internet bağlantısı olduğu sürece yapay zeka ile senkronize, internet olmadığında ise yerel önbellek ve veritabanı üzerinden %100 kararlı çalışmaktadır.
