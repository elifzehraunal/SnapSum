# 👥 SnapSum: Görev Dağılımı ve Sorumluluklar

SnapSum projesinde ekip üyelerinin üstlendiği temel roller, sorumluluklar ve katkıları aşağıda detaylandırılmıştır. Tüm roller ekip üyeleri arasında başarıyla koordine edilmiş ve SnapSum uygulamasının son kararlı sürümü bu görev dağılımına uygun olarak %100 çalışır ve tamamlanmış bir şekilde teslim edilmiştir.

---

### 👨‍💻 İbrahim (Backend Dev)
**Rol:** Backend ve Yapay Zeka Entegrasyonu
- **Yapay Zeka Entegrasyonu (Mistral API):** Mistral AI API bağlantılarının kurulması, metin ve görsel/OCR analizleri için en uygun LLM modellerinin sisteme entegre edilmesi.
- **Chunking & Map-Reduce Tasarımı:** Uzun dokümanları akıllı parçalara ayıran ve parça özetlerini birleştirerek tek bir master özet üreten algoritmanın tasarlanması ve kodlanması.
- **Prompt Mühendisliği:** Kısa, Orta ve Uzun özet seçenekleri için optimize edilmiş yapay zeka sistem talimatlarının (system prompts) hazırlanması.
- **PDF/Metin Temizleme Mantığı:** `backend_manager.py` içerisinde dosyalardan gürültülü verileri (sayfa numaraları, separator karakterler) ayıklayan normalizasyon kodlarının yazılması.

---

### 📊 Baran (Veritabanı & API)
**Rol:** Veri Yönetimi ve Yapılandırma
- **Veritabanı Yönetimi (`DatabaseManager`):** SQLite3 veritabanı şemasının kurulması, kitaplar, kullanıcı profilleri ve çıkarılan özetler için kalıcı depolama sisteminin oluşturulması.
- **Kütüphane Yönetim Fonksiyonları:** Arayüz üzerinden kişisel kitap ekleme ve silme süreçlerinin SQL veritabanı işlemlerinin programlanması.
- **API Key & Konfigürasyon Yapısı:** API anahtarlarının ve dil ayarlarının yerel sistemde (`data/settings.json`) güvenli ve çakışmasız şekilde saklanmasını sağlayacak altyapının tasarlanması.

---

### 📱 Elif (Mobil Dev)
**Rol:** Mobil Uygulama Geliştirme (Flet)
- **Reaktif Arayüz Geliştirme:** Flet framework'ünü kullanarak uygulamanın tüm ekran ve sekmelerinin (Library, Upload, Profile) dinamik ve modern Material 3 standartlarında kodlanması.
- **Dosya Gezgini Entegrasyonu:** Kullanıcının telefon veya bilgisayar hafızasından PDF ve görselleri seçebilmesini sağlayan `FilePicker` entegrasyonunun doğrudan asenkron (async/await) yapıyla gerçekleştirilmesi.
- **UI Navigasyonu (`main.py`):** Sekmeler arası geçişlerin, arama çubuğu filtrelemesinin, Ayarlar menüsünün ve detay/okuma ekranlarının (`book_detail_view.py` ile birlikte) entegre edilmesi.

---

### 🎨 Sinem (UI/UX)
**Rol:** Tasarım ve Kullanıcı Deneyimi
- **Renk Paleti & Kimlik:** Uygulamaya premium bir hava katan Indigo, Rose ve Slate bazlı renk paletlerinin ve Cozy Cream Paper göz yormayan okuyucu zemin tasarımlarının belirlenmesi.
- **Bileşen Konumlandırmaları:** Arama kutusu kapsülü, bulut yükleme alanı kartı, profil istatistik sütunları ve sekmelerin en ergonomik yerleşimlerinin planlanması.
- **Kart & UI Tasarımları:** Kitap listelerinin, öneriler alanının, geçiş animasyonlarının ve dialog pencerelerinin görsel standartlarının hazırlanması.

---

### 📸 Fatma (Veri İşleme & Test)
**Rol:** Veri Kalitesi ve Doğrulama
- **Kitap Metinlerinin Hazırlanması:** Genel kütüphanede (`cleaned_texts` klasöründe) varsayılan olarak sunulacak kitap metinlerinin hazırlanması ve sisteme yerleştirilmesi.
- **Döküman Temizleme:** PDF ve metin kaynaklarındaki tablo çizgileri, görsel artıkları ve sayfa gürültülerinin temizlenerek sisteme saf metin olarak entegre edilmesi.
- **Test ve Kalite Kontrol:** Uygulamanın farklı boyutlardaki PDF/TXT/Görsel dosya türleriyle kararlılık testlerinin yapılması ve sistemin genel olarak test edilmesi.

---

> **Not:** Tüm roller ekip üyeleri arasında başarıyla koordine edilmiş ve SnapSum uygulamasının son kararlı sürümü %100 çalışan bir şekilde bu görev dağılımına uygun olarak tamamlanmıştır.
