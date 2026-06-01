# 📘 SnapSum: Proje Detayları ve Sistem Özellikleri Kılavuzu

SnapSum, akademik ve edebi metinlerin yapay zeka desteğiyle saniyeler içinde özetlenmesini, görseller üzerinden OCR analizi yapılabilmesini, Türkçe-İngilizce çift dil desteği sunmasını ve kullanıcı okuma geçmişine göre kişiselleştirilmiş okur profili ve kitap önerileri verilmesini sağlayan modern ve reaktif bir mobil/masaüstü platformdur.

Bu döküman, uygulamanın sunduğu tüm özellikleri, tasarım detaylarını, teknoloji yığınını ve tamamlanan geliştirme yol haritasını ayrıntılı bir şekilde açıklamaktadır.

---

## 📑 İçindekiler
1. [🏗️ Sistem Mimarisi ve Katmanlar](#1-sistem-mimarisi-ve-katmanlar)
2. [💡 Öne Çıkan Gelişmiş Özellikler](#2-öne-çıkan-gelişmiş-özellikler)
3. [🎨 Premium Material 3 Arayüz Tasarımı](#3-premium-material-3-arayüz-tasarımı)
4. [📊 Tamamlanan Geliştirme Yol Haritası](#4-tamamlanan-geliştirme-yol-haritası)
5. [📂 Dizin Yapısı ve Dosya Sorumlulukları](#5-dizin-yapısı-ve-dosya-sorumlulukları)

---

## 1. Sistem Mimarisi ve Katmanlar

SnapSum projesi, modüler, güvenli ve katmanlı bir yazılım mimarisiyle kurulmuştur:

### A. Backend (Python & Yapay Zeka Core)
Backend tarafı, verilerin işlenmesi, regex normalizasyonu, güvenlik denetimleri, asenkron yapay zeka entegrasyonu ve iş mantığının yürütülmesinden sorumludur.
*   **Metin Normalizasyonu:** `.txt` dosyaları doğrudan UTF-8 formatında okunurken, `.pdf` dosyalarından `PyMuPDF (fitz)` kütüphanesi kullanılarak saf metin ayıklar. Sayfa numaraları, boşluk artıkları ve tablo çizgileri regex kurallarıyla temizlenerek gürültüsüz bir metin elde edilir.
*   **Parçalama Algoritması (Chunking):** Uzun metinler, Mistral API'nin token limitlerine ve en yüksek doğruluk oranlarına uygun şekilde (5000-8000 karakterlik) paragraf yapısını koruyan asıllı parçalara bölünür.
*   **Yapay Zeka Servisleri (Mistral & Pixtral API):** Yapay zeka motoru olarak tamamen Mistral AI entegre edilmiştir. Metin özetlemelerinde `mistral-small-latest`, görsel/OCR özetlemelerinde ise `pixtral-large-latest` modelleri kullanılır. "Map-Reduce" stratejisi ile her parça önce ayrı ayrı özetlenir, ardından bu özetler birleştirilerek bütüncül bir ana özet (Master Summary) oluşturulur.
*   **Önbellekleme (Cache):** Aynı döküman için tekrar özet istenmesi durumunda, sistem SHA-256 tabanlı bir yerel cache (`summary_cache.json`) ve SQLite önbelleği üzerinden anında yanıt verir.
*   **Güvenlik Katmanı (`api_security.py`):** Token Bucket rate limiter, path traversal ve XSS girdi sanitizasyonu ile API anahtarı format doğrulayıcı maskeleme işlemlerini yürütür.

### B. Mobil Uygulama (Flet Frontend)
Kullanıcı arayüzü, Python tabanlı ve asenkron yapıya tam uyumlu **Flet** framework'ü ile geliştirilmiştir.
*   **Genel Kütüphane:** Sisteme kayıtlı hazır kitapların (Fatma tarafından hazırlanan 18 kitap) listelendiği, arama çubuğu ve dil filtrelemesi içeren alan.
*   **Şahsi Kütüphanem:** Kullanıcının kendi yüklediği dökümanların (PDF, TXT, PNG, JPG, JPEG) yönetildiği alan.
*   **Yükleme Alanı:** Dosyaların `FilePicker` doğrudan asenkron (async/await) çağrısıyla sisteme dahil edildiği sürükle-bırak görsel göstergeli reaktif panel.
*   **Özet Kontrolleri:** Kısa, Orta ve Uzun seçenekleri ve Türkçe/İngilizce çift dil desteği ile kişiselleştirilebilir özetleme deneyimi.
*   **Okuma Alanı:** Gözü yormayan Cozy Cream Paper zemin rengi, akıcı kaydırma ve genişletilebilir özet paneli.
*   **Profil ve Öneri Alanı:** Kullanıcının okuma geçmişine göre çıkarılan Okur Karakteri analizi ("🔬 Bilimkurgu Kaşifi", "🧠 Düşünce Mimarı" vb.) ve karakterine uygun yapay zeka destekli kitap önerileri.

---

## 2. Öne Çıkan Gelişmiş Özellikler

### 📸 Pixtral OCR & Görsel Çözümleme
Kullanıcılar, bir kitabın kapağını veya doğrudan bir sayfa fotoğrafını sisteme yükleyerek Pixtral API sayesinde OCR işleminden geçirebilirler. Sistem, görseldeki yazıları okuyarak kullanıcıya anında yapay zekalı görsel özetleme sunar.

### 🧠 Dinamik Okur Karakteri Analizi
Kullanıcının okuma geçmişini analiz eden ve buna göre kullanıcıya özel karakterler (örneğin `"🔬 Bilimkurgu Kaşifi"`, `"🧠 Düşünce Mimarı"`, `"🧭 Macera Tutkunu"`) atayarak kitap öneren algoritmik yapı kurulmuştur. Sistem, SQLite üzerindeki `reading_history` tablosunu sorgulayarak en çok okunan kategorileri belirler.

### 🌐 Dinamik Çift Dil Desteği
Uygulama, hem Türkçe hem de İngilizce dilleri arasında dinamik arayüz geçişleri sağlar. Ayarlar panelinden dil değiştirildiğinde, tüm sekmeler, arama filtreleri ve hatta LLM'den alınan özet çıktıları seçilen dile uygun şekilde üretilir.

---

## 3. Premium Material 3 Arayüz Tasarımı

Sinem tarafından geliştirilen UI/UX planları doğrultusunda, Flet arayüzünde premium Material 3 standartları uygulanmıştır:

*   **Cozy Cream Paper Okuma Modu:** Kitap okuma alanlarında gözü yormayan, krem rengi mat kağıt zemin HSL rengi tercih edilmiştir.
*   **Dinamik Renk Paletleri:** Uygulamada Indigo (Bilimsel/Ciddi), Rose (Yaratıcı/Sıcak) ve Slate (Modern/Minimal) temaları arasında dinamik geçişler sunulur.
*   **Arama Kapsülleri (Search Capsules):** Kütüphanede kitap aramayı kolaylaştıran oval, premium tasarımlı filtreleme elemanları.
*   **Bulut Yükleme Panel Göstergesi:** Dosya sürükleyip bırakıldığında reaktif olarak renk değiştiren modern görsel indikasyon.

---

## 4. Tamamlanan Geliştirme Yol Haritası

Uygulamanın son kararlı sürümünde aşağıdaki kritik özellikler başarıyla hayata geçirilmiştir:

*   **Tam SQLite Veritabanı Entegrasyonu (%100):** SQLite3 kullanılarak kitaplar, çıkarılan özetler, dil tercihleri ve kullanıcı profili kalıcı olarak yerel veritabanında (`snapsum.db`) depolanmaktadır.
*   **Dinamik Okur Karakteri ve Öneri Algoritması (%100):** Kullanıcının okuduğu kitapların kategorileri analiz edilerek dinamik okur profilleri atanmakta ve buna uygun yapay zeka destekli kitap önerileri sunulmaktadır.
*   **Pixtral Vision & OCR Entegrasyonu (%100):** Kullanıcılar artık kitap kapağı veya sayfa fotoğraflarını yükleyerek Pixtral API sayesinde doğrudan yapay zekayla OCR analizi ve görsel özetlemesi alabilmektedir.
*   **Çift Dil Desteği (%100):** Uygulama arayüzü, özetler ve öneriler Türkçe ve İngilizce dilleri arasında dinamik olarak senkronize çalışmaktadır.
*   **Asenkron FilePicker Devrimi (%100):** Mobil dosya seçme işlemleri doğrudan asenkron `await picker.pick_files()` çağrısıyla stabilize edilmiş, çökme ve donmalar tamamen giderilmiştir.

---

## 5. Dizin Yapısı ve Dosya Sorumlulukları

*   `backend/backend_manager.py`: Tüm iş mantığının (business logic), LLM çağrılarının ve normalizasyonun toplandığı ana backend yöneticisi.
*   `backend/api_security.py`: Güvenlik duvarı, rate limiter ve girdi doğrulamalarını gerçekleştiren güvenlik katmanı.
*   `mobile/main.py`: Uygulamanın giriş noktası, arayüz kurulumu ve sayfa yönlendiricisi.
*   `mobile/app/ui/theme.py`: Premium Indigo/Rose/Slate Material 3 tema tanımlamalarını içeren stil dosyası.
*   `cleaned_texts/`: Fatma tarafından hazırlanan ve genel kütüphaneyi besleyen 18 adet düz metin kitap dosyası.
*   `data/snapsum.db`: Baran tarafından tasarlanan SQLite3 yerel veritabanı.
