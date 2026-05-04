# SnapSum: Görev Dağılımı ve Sorumluluklar

SnapSum projesinde ekip üyelerinin üstlendiği temel roller ve sorumluluklar aşağıda detaylandırılmıştır.

---

### 👨‍💻 İbrahim (Backend Dev)
**Rol:** Backend ve Yapay Zeka Entegrasyonu
- **Özetleme Sistemi:** Google Gemini API (Öğrenci Planı) bağlantısını kurmak ve özetleme mantığını Python ile yazmak.
- **Karakter & Metin Algoritması:** Kitap metinlerini Gemini'nin okuma limitlerine göre parçalara bölen (chunking) ve özetleri birleştiren algoritmayı geliştirmek.
- **Metin Ayıklama (PDF Parsing):** PDF dosyalarından sadece saf metni (plain text) çeken, resimleri ve grafikleri tamamen yok sayan yapyı kurmak.
- **Prompt Yönetimi:** "Kısa, Orta, Uzun" seçenekleri için farklılaştırılmış yapay zeka komutlarını (prompts) optimize etmek.

---

### 📊 Baran (Veritabanı & API)
**Rol:** Veri Yönetimi ve Güvenlik
- **Veritabanı Entegrasyonu:** Seçilecek olan veritabanının (Local SQLite, JSON veya Bulut DB) mimarisini kurmak ve Python bağlantısını sağlamak. *(Planlama aşamasında)*
- **Kütüphane Yönetimi:** 20 adet hazır kitabın ve kullanıcı tarafından yüklenen PDF'lerin veritabanındaki kayıt süreçlerini yönetmek.
- **Veri Senkronizasyonu:** Uygulama her açıldığında mevcut kitap listesinin ve daha önce çıkarılmış özetlerin veritabanından hızlıca çekilmesini sağlamak.
- **API Güvenliği:** API anahtarlarının ve veritabanı bilgilerinin güvenli yönetimi için gerekli konfigürasyonları yapmak.

---

### 📱 Elif (Mobil Dev)
**Rol:** Mobil Uygulama Geliştirme (Flet)
- **Mobil Uygulama Arayüzü:** Flet kullanarak uygulamanın ana ekranlarını (Genel Kütüphane, Şahsi Kütüphanem, Yükleme Alanı) kodlamak.
- **Fonksiyon Entegrasyonu:** İbrahim'in yazdığı özetleme fonksiyonlarını ve Baran'ın veritabanı kodlarını mobil arayüze bağlamak.
- **Özet Uzunluğu Seçimi:** Kullanıcının kısa, orta veya uzun özet tercihini yapabileceği arayüz bileşenlerini (Buton/Toggle) eklemek.
- **Dosya Seçici:** Kullanıcının telefon hafızasından PDF seçip sisteme dahil edebileceği dosya gezgini özelliğini entegre etmek.

---

### 🎨 Sinem (UI/UX)
**Rol:** Tasarım ve Kullanıcı Deneyimi
- **Ekran Düzeni:** Metin odaklı bir uygulama olduğu için okuma kolaylığını ön planda tutan minimalist bir ekran tasarımı yapmak.
- **Kullanıcı Deneyimi (UX):** Kullanıcının kütüphaneler arası geçişini ve özet alma sürecini en basit (en az tıklama ile) hale getirmek.
- **Geri Bildirim Tasarımı:** Özetleme işlemi sırasında görünecek yükleme animasyonları ve işlem tamamlandı uyarılarını belirlemek.
- **Görsel Kimlik:** Uygulamanın renk paletini ve tipografisini (metin odaklı olduğu için font seçimi kritik) belirlemek.

---

### 📸 Fatma (Veri İşleme & Test)
**Rol:** Veri Kalitesi ve Doğrulama
- **Metin Hazırlığı & Temizlik:** Hazır verilecek 20 kitabın PDF'lerini bulmak, içlerindeki resim/tablo gibi fazlalıkları temizleyip saf metni PDF haline getirmek.
- **Test ve Demo:** Uygulamayı farklı uzunluktaki metinlerle test ederek hataları ayıklamak; sunum için demo videoları ve ekran görüntüleri hazırlamak.
- **Doğruluk Kontrolü:** Gemini'den gelen özetlerin seçilen uzunluklara (kısa/orta/uzun) uygunluğunu ve Türkçe karakterlerin düzgün göründüğünü denetlemek.

---

> **Not:** Veritabanı entegrasyonu şu an için aktif değildir; ancak mimari Baran tarafından planlanmış ve dökümantasyona dahil edilmiştir.
